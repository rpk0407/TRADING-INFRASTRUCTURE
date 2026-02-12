"""
Intelligent LLM Router — Routes each task to the optimal provider.
4 Core Providers: Ollama → OpenCode → OpenGravity → Claude

Routing Logic:
  Code tasks → OpenCode (DeepSeek Coder V2, CodeLlama, Qwen2.5-Coder)
  General tasks → Ollama (Mixtral, Llama 3.1)
  Agent coordination → OpenGravity (hybrid local/cloud)
  Complex reasoning / fallback → Claude (Anthropic API, budget-capped)
"""

import asyncio
import hashlib
import json
import time
from datetime import datetime, timezone
from typing import Any, Optional

import structlog

from config.settings import settings
from core.llm_router.models import (
    LLMProvider,
    LLMResponse,
    ProviderHealth,
    PROVIDER_COSTS,
    PROVIDER_CAPABILITIES,
    TASK_CAPABILITY_REQUIREMENTS,
)

logger = structlog.get_logger(__name__)


class LLMRouter:
    """
    Routes LLM requests to the optimal provider.
    Fallback chain: Ollama → OpenCode → OpenGravity → Claude
    Self-improving via feedback loop auto-tuning.
    """

    def __init__(self):
        self._providers: dict[LLMProvider, Any] = {}
        self._health: dict[LLMProvider, ProviderHealth] = {}
        self._cache: dict[str, tuple[LLMResponse, float]] = {}  # (response, cached_at)
        self._task_preferences: dict[str, str] = {}
        self._monthly_spend: float = 0.0
        self._request_count: int = 0
        self._cache_hits: int = 0

    async def initialize(self):
        """Initialize all configured LLM providers."""
        logger.info("llm_router.initializing")

        if settings.ollama_enabled:
            await self._register_provider(LLMProvider.OLLAMA)

        if settings.opencode_enabled:
            await self._register_provider(LLMProvider.OPENCODE)

        if settings.opengravity_enabled:
            await self._register_provider(LLMProvider.OPENGRAVITY)

        if settings.claude_api_key:
            await self._register_provider(LLMProvider.CLAUDE)

        await self._health_check_all()
        logger.info(
            "llm_router.ready",
            providers=[p.value for p in self._providers],
            strategy=settings.llm_router_strategy.value,
        )

    async def shutdown(self):
        """Clean up provider connections."""
        for provider in self._providers.values():
            if hasattr(provider, "close"):
                await provider.close()

    # ═══════════════════════════════════════════════════════════
    # GENERATE — Main entry point
    # ═══════════════════════════════════════════════════════════

    async def generate(
        self,
        prompt: str,
        task_type: str = "general",
        max_tokens: int = 2048,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None,
        force_provider: Optional[LLMProvider] = None,
        skip_cache: bool = False,
    ) -> LLMResponse:
        self._request_count += 1

        # Check cache (with TTL expiration)
        cache_key = None
        if settings.llm_cache_enabled and not skip_cache:
            cache_key = self._cache_key(prompt, task_type, system_prompt, max_tokens, temperature)
            if cache_key in self._cache:
                cached_response, cached_at = self._cache[cache_key]
                if (time.monotonic() - cached_at) < settings.llm_cache_ttl:
                    self._cache_hits += 1
                    cached_response.cached = True
                    return cached_response
                else:
                    del self._cache[cache_key]  # Expired

        # Determine provider order
        if force_provider:
            providers_to_try = [force_provider]
        else:
            providers_to_try = self._select_providers(task_type)

        # Try each provider
        last_error = None
        for provider_id in providers_to_try:
            if not self._is_available(provider_id):
                continue

            if provider_id == LLMProvider.CLAUDE:
                if self._monthly_spend >= settings.claude_monthly_budget_usd:
                    logger.warning("llm_router.budget_exceeded", spend=self._monthly_spend)
                    continue

            try:
                start = time.monotonic()
                response = await self._call_provider(
                    provider_id, prompt, system_prompt, max_tokens, temperature, task_type
                )
                response.latency_ms = (time.monotonic() - start) * 1000
                self._record_success(provider_id)

                costs = PROVIDER_COSTS[provider_id]
                response.cost_usd = (
                    (response.tokens_in / 1000) * costs["input"]
                    + (response.tokens_out / 1000) * costs["output"]
                )
                self._monthly_spend += response.cost_usd

                if settings.llm_cache_enabled and not skip_cache and cache_key:
                    self._cache[cache_key] = (response, time.monotonic())

                logger.info(
                    "llm_router.success",
                    provider=provider_id.value,
                    task_type=task_type,
                    tokens=response.total_tokens,
                    cost=response.cost_usd,
                    latency_ms=round(response.latency_ms),
                )
                return response

            except Exception as e:
                last_error = e
                self._record_failure(provider_id)
                logger.warning(
                    "llm_router.provider_failed",
                    provider=provider_id.value,
                    error=str(e),
                )
                continue

        raise RuntimeError(
            f"All LLM providers failed for task '{task_type}'. Last error: {last_error}"
        )

    # ═══════════════════════════════════════════════════════════
    # PROVIDER SELECTION — Smart routing with feedback learning
    # ═══════════════════════════════════════════════════════════

    def set_preference(self, task_type: str, provider_name: str):
        """Set a preferred provider for a task type (from feedback loop)."""
        self._task_preferences[task_type] = provider_name
        logger.info("llm_router.preference_set", task_type=task_type, provider=provider_name)

    def _select_providers(self, task_type: str) -> list[LLMProvider]:
        """Select providers: feedback preference → capability match → fallback chain."""
        # 1. Feedback loop learned preference
        if task_type in self._task_preferences:
            try:
                preferred = LLMProvider(self._task_preferences[task_type])
                if preferred in self._providers and self._is_available(preferred):
                    others = self._get_fallback_chain()
                    return [preferred] + [p for p in others if p != preferred]
            except ValueError:
                pass

        # 2. Capability-based scoring
        requirements = TASK_CAPABILITY_REQUIREMENTS.get(task_type, {"reasoning": 5})

        scored = []
        for provider_id in LLMProvider:
            if provider_id not in self._providers:
                continue

            caps = PROVIDER_CAPABILITIES[provider_id]
            meets = all(caps.get(c, 0) >= v for c, v in requirements.items())

            if not meets and settings.llm_router_strategy.value == "cost_optimized":
                continue

            cost = sum(PROVIDER_COSTS[provider_id].values())
            cap_score = sum(caps.values())

            if settings.llm_router_strategy.value == "cost_optimized":
                score = -cost * 1000 + cap_score
            elif settings.llm_router_strategy.value == "quality_first":
                score = cap_score * 1000 - cost
            else:
                score = cap_score - cost * 100

            scored.append((provider_id, score, meets))

        scored.sort(key=lambda x: (-x[2], -x[1]))
        result = [p[0] for p in scored]

        # 3. Always include fallback chain
        for p in self._get_fallback_chain():
            if p not in result and p in self._providers:
                result.append(p)

        return result

    # ═══════════════════════════════════════════════════════════
    # PROVIDER CALLS — Full API integrations
    # ═══════════════════════════════════════════════════════════

    async def _call_provider(
        self, provider_id: LLMProvider, prompt: str, system_prompt: Optional[str],
        max_tokens: int, temperature: float, task_type: str = "general",
    ) -> LLMResponse:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        if provider_id == LLMProvider.OLLAMA:
            return await self._call_ollama(messages, max_tokens, temperature, task_type)
        elif provider_id == LLMProvider.OPENCODE:
            return await self._call_opencode(messages, max_tokens, temperature, task_type)
        elif provider_id == LLMProvider.OPENGRAVITY:
            return await self._call_opengravity(messages, max_tokens, temperature)
        elif provider_id == LLMProvider.CLAUDE:
            return await self._call_claude(messages, max_tokens, temperature)
        else:
            raise ValueError(f"Unknown provider: {provider_id}")

    async def _call_ollama(
        self, messages: list, max_tokens: int, temperature: float, task_type: str = "general"
    ) -> LLMResponse:
        """
        Ollama — Local general-purpose models.
        Smart model selection: llama3.1:8b for simple tasks, mixtral for complex.
        """
        import httpx

        simple_tasks = {"classification", "summarization", "customer_support"}
        model = (
            settings.ollama_fast_model if task_type in simple_tasks
            else settings.ollama_default_model
        )

        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{settings.ollama_url}/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "options": {"num_predict": max_tokens, "temperature": temperature},
                    "stream": False,
                },
            )
            resp.raise_for_status()
            data = resp.json()

        return LLMResponse(
            content=data["message"]["content"],
            provider=LLMProvider.OLLAMA,
            model=model,
            tokens_in=data.get("prompt_eval_count", 0),
            tokens_out=data.get("eval_count", 0),
        )

    async def _call_opencode(
        self, messages: list, max_tokens: int, temperature: float, task_type: str = "general"
    ) -> LLMResponse:
        """
        OpenCode — Coding specialist models via Ollama.
        3 specialized models:
          - DeepSeek Coder V2 → code generation, debugging
          - CodeLlama → code completion
          - Qwen2.5-Coder → code review
        """
        import httpx

        model_map = {
            "code_generation": settings.opencode_primary_model,
            "code_debugging": settings.opencode_primary_model,
            "website_structure": settings.opencode_primary_model,
            "code_completion": settings.opencode_completion_model,
            "code_review": settings.opencode_review_model,
        }
        model = model_map.get(task_type, settings.opencode_primary_model)

        # Inject coding system prompt if not present
        has_system = any(m["role"] == "system" for m in messages)
        if not has_system:
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are an expert software engineer. Write clean, "
                        "production-ready code. Follow best practices with proper "
                        "error handling and types. Return ONLY code unless asked "
                        "for explanation."
                    ),
                },
                *messages,
            ]

        async with httpx.AsyncClient(timeout=180.0) as client:
            resp = await client.post(
                f"{settings.ollama_url}/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": max(temperature, 0.2),
                    },
                    "stream": False,
                },
            )
            resp.raise_for_status()
            data = resp.json()

        return LLMResponse(
            content=data["message"]["content"],
            provider=LLMProvider.OPENCODE,
            model=model,
            tokens_in=data.get("prompt_eval_count", 0),
            tokens_out=data.get("eval_count", 0),
        )

    async def _call_opengravity(
        self, messages: list, max_tokens: int, temperature: float
    ) -> LLMResponse:
        """
        OpenGravity — Hybrid local/cloud agent platform.
        Local-first with cloud fallback, agent coordination, privacy-preserving.
        """
        import httpx

        headers: dict[str, str] = {"Content-Type": "application/json"}
        if settings.opengravity_api_key:
            headers["Authorization"] = f"Bearer {settings.opengravity_api_key}"

        body: dict[str, Any] = {
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "prefer_local": settings.opengravity_prefer_local,
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{settings.opengravity_url}/v1/chat/completions",
                headers=headers,
                json=body,
            )
            resp.raise_for_status()
            data = resp.json()

        choice = data["choices"][0]
        usage = data.get("usage", {})

        return LLMResponse(
            content=choice["message"]["content"],
            provider=LLMProvider.OPENGRAVITY,
            model=data.get("model", "opengravity"),
            tokens_in=usage.get("prompt_tokens", 0),
            tokens_out=usage.get("completion_tokens", 0),
            metadata={
                "execution_mode": data.get("execution_mode", "local"),
                "cost_breakdown": data.get("cost_breakdown", {}),
            },
        )

    async def _call_claude(
        self, messages: list, max_tokens: int, temperature: float
    ) -> LLMResponse:
        """
        Claude — Anthropic API premium fallback.
        200K context, tool use, vision, top-tier reasoning.
        """
        import anthropic

        client = anthropic.AsyncAnthropic(api_key=settings.claude_api_key)

        system_msg = None
        api_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                api_messages.append(msg)

        kwargs: dict[str, Any] = {
            "model": settings.claude_model,
            "max_tokens": max_tokens,
            "messages": api_messages,
            "temperature": temperature,
        }
        if system_msg:
            kwargs["system"] = system_msg

        response = await client.messages.create(**kwargs)

        content_text = ""
        for block in response.content:
            if hasattr(block, "text"):
                content_text += block.text

        return LLMResponse(
            content=content_text,
            provider=LLMProvider.CLAUDE,
            model=settings.claude_model,
            tokens_in=response.usage.input_tokens,
            tokens_out=response.usage.output_tokens,
            metadata={"stop_reason": response.stop_reason},
        )

    # ═══════════════════════════════════════════════════════════
    # HEALTH & AVAILABILITY
    # ═══════════════════════════════════════════════════════════

    async def _register_provider(self, provider_id: LLMProvider):
        self._providers[provider_id] = True
        self._health[provider_id] = ProviderHealth(
            provider=provider_id, is_available=True
        )

    async def _health_check_all(self):
        """Check health of all registered providers."""
        for provider_id in list(self._providers.keys()):
            try:
                health = self._health[provider_id]

                if provider_id == LLMProvider.OLLAMA:
                    import httpx
                    async with httpx.AsyncClient(timeout=5.0) as client:
                        resp = await client.get(f"{settings.ollama_url}/api/tags")
                        health.is_available = resp.status_code == 200

                elif provider_id == LLMProvider.OPENCODE:
                    import httpx
                    async with httpx.AsyncClient(timeout=5.0) as client:
                        resp = await client.get(f"{settings.ollama_url}/api/tags")
                        if resp.status_code == 200:
                            models = resp.json().get("models", [])
                            model_names = [m.get("name", "") for m in models]
                            health.is_available = any(
                                settings.opencode_primary_model.split(":")[0] in n
                                for n in model_names
                            ) if model_names else True
                        else:
                            health.is_available = False

                elif provider_id == LLMProvider.OPENGRAVITY:
                    import httpx
                    try:
                        async with httpx.AsyncClient(timeout=5.0) as client:
                            resp = await client.get(f"{settings.opengravity_url}/health")
                            health.is_available = resp.status_code == 200
                    except Exception:
                        health.is_available = bool(settings.opengravity_api_key)

                elif provider_id == LLMProvider.CLAUDE:
                    health.is_available = bool(settings.claude_api_key)

                health.last_checked = datetime.now(timezone.utc).isoformat()

            except Exception:
                self._health[provider_id].is_available = False

    def _is_available(self, provider_id: LLMProvider) -> bool:
        health = self._health.get(provider_id)
        if not health:
            return False
        if health.consecutive_failures >= 5:
            return False
        return health.is_available

    def _record_success(self, provider_id: LLMProvider):
        """Reset failure counter on successful call."""
        if provider_id in self._health:
            self._health[provider_id].consecutive_failures = 0

    def _record_failure(self, provider_id: LLMProvider):
        if provider_id in self._health:
            self._health[provider_id].consecutive_failures += 1

    def _get_fallback_chain(self) -> list[LLMProvider]:
        chain = []
        for name in settings.fallback_chain:
            try:
                chain.append(LLMProvider(name))
            except ValueError:
                pass
        return chain

    def _cache_key(
        self, prompt: str, task_type: str, system_prompt: Optional[str],
        max_tokens: int = 2048, temperature: float = 0.7,
    ) -> str:
        content = f"{task_type}:{system_prompt or ''}:{max_tokens}:{temperature}:{prompt}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    # ═══════════════════════════════════════════════════════════
    # STATS
    # ═══════════════════════════════════════════════════════════

    def get_stats(self) -> dict:
        return {
            "total_requests": self._request_count,
            "cache_hits": self._cache_hits,
            "cache_hit_rate": round(self._cache_hits / max(self._request_count, 1) * 100, 1),
            "monthly_spend_usd": round(self._monthly_spend, 4),
            "budget_remaining_usd": round(settings.claude_monthly_budget_usd - self._monthly_spend, 4),
            "task_preferences": dict(self._task_preferences),
            "providers": {
                p.value: {"available": h.is_available, "failures": h.consecutive_failures}
                for p, h in self._health.items()
            },
        }
