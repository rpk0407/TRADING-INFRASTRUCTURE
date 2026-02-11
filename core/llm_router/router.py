"""
Intelligent LLM Router — Routes each task to the cheapest capable model.
This is the key cost optimization: 90%+ of tasks run on FREE local models.
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
    Routes LLM requests to the optimal provider based on:
    1. Task complexity requirements
    2. Provider availability
    3. Cost (prefer free local models)
    4. Latency requirements
    5. Monthly budget constraints

    Fallback chain: Kimi K2.5 → Ollama → AntiGravity → Claude
    """

    def __init__(self):
        self._providers: dict[LLMProvider, Any] = {}
        self._health: dict[LLMProvider, ProviderHealth] = {}
        self._cache: dict[str, LLMResponse] = {}
        self._task_preferences: dict[str, str] = {}  # task_type -> preferred provider
        self._monthly_spend: float = 0.0
        self._request_count: int = 0
        self._cache_hits: int = 0

    async def initialize(self):
        """Initialize all configured LLM providers."""
        logger.info("llm_router.initializing")

        # Register providers based on configuration
        if settings.kimi_local_enabled:
            await self._register_provider(LLMProvider.KIMI_LOCAL)

        if settings.ollama_enabled:
            await self._register_provider(LLMProvider.OLLAMA)

        if settings.deepseek_enabled:
            await self._register_provider(LLMProvider.DEEPSEEK)

        if settings.gemini_enabled and settings.gemini_api_key:
            await self._register_provider(LLMProvider.GEMINI)

        if settings.groq_enabled and settings.groq_api_key:
            await self._register_provider(LLMProvider.GROQ)

        if settings.antigravity_enabled:
            await self._register_provider(LLMProvider.ANTIGRAVITY)

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
        """
        Generate text using the optimal LLM provider.

        Args:
            prompt: The user/agent prompt
            task_type: Type of task (used for routing decisions)
            max_tokens: Maximum response tokens
            temperature: Creativity level
            system_prompt: Optional system-level instructions
            force_provider: Override automatic routing
            skip_cache: Bypass response cache
        """
        self._request_count += 1

        # Check cache first
        if settings.llm_cache_enabled and not skip_cache:
            cache_key = self._cache_key(prompt, task_type, system_prompt)
            if cache_key in self._cache:
                self._cache_hits += 1
                cached = self._cache[cache_key]
                cached.cached = True
                logger.debug("llm_router.cache_hit", task_type=task_type)
                return cached

        # Determine provider
        if force_provider:
            providers_to_try = [force_provider]
        else:
            providers_to_try = self._select_providers(task_type)

        # Try each provider in order
        last_error = None
        for provider_id in providers_to_try:
            if not self._is_available(provider_id):
                continue

            # Budget check for paid providers
            if provider_id == LLMProvider.CLAUDE:
                if self._monthly_spend >= settings.claude_monthly_budget_usd:
                    logger.warning(
                        "llm_router.budget_exceeded",
                        spend=self._monthly_spend,
                        budget=settings.claude_monthly_budget_usd,
                    )
                    continue

            try:
                start = time.monotonic()
                response = await self._call_provider(
                    provider_id, prompt, system_prompt, max_tokens, temperature
                )
                response.latency_ms = (time.monotonic() - start) * 1000

                # Calculate cost
                costs = PROVIDER_COSTS[provider_id]
                response.cost_usd = (
                    (response.tokens_in / 1000) * costs["input"]
                    + (response.tokens_out / 1000) * costs["output"]
                )
                self._monthly_spend += response.cost_usd

                # Cache the response
                if settings.llm_cache_enabled and not skip_cache:
                    self._cache[cache_key] = response

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
            f"All LLM providers failed for task '{task_type}'. "
            f"Last error: {last_error}"
        )

    def set_preference(self, task_type: str, provider_name: str):
        """Set a preferred provider for a task type (from feedback loop)."""
        self._task_preferences[task_type] = provider_name
        logger.info(
            "llm_router.preference_set",
            task_type=task_type,
            provider=provider_name,
        )

    def _select_providers(self, task_type: str) -> list[LLMProvider]:
        """Select providers based on task requirements and routing strategy."""
        # Check if feedback loop has a preference
        if task_type in self._task_preferences:
            try:
                preferred = LLMProvider(self._task_preferences[task_type])
                if preferred in self._providers and self._is_available(preferred):
                    others = self._get_fallback_chain()
                    return [preferred] + [p for p in others if p != preferred]
            except ValueError:
                pass

        requirements = TASK_CAPABILITY_REQUIREMENTS.get(
            task_type, {"reasoning": 5}
        )

        # Score each provider
        scored = []
        for provider_id in LLMProvider:
            if provider_id not in self._providers:
                continue

            caps = PROVIDER_CAPABILITIES[provider_id]
            meets_requirements = all(
                caps.get(cap, 0) >= min_score
                for cap, min_score in requirements.items()
            )

            if not meets_requirements and settings.llm_router_strategy.value == "cost_optimized":
                continue

            cost = sum(PROVIDER_COSTS[provider_id].values())
            capability_score = sum(caps.values())

            if settings.llm_router_strategy.value == "cost_optimized":
                # Prefer cheapest that meets requirements
                score = -cost * 1000 + capability_score
            elif settings.llm_router_strategy.value == "quality_first":
                # Prefer highest capability
                score = capability_score * 1000 - cost
            else:
                score = capability_score - cost * 100

            scored.append((provider_id, score, meets_requirements))

        # Sort: providers meeting requirements first, then by score
        scored.sort(key=lambda x: (-x[2], -x[1]))

        result = [p[0] for p in scored]

        # Always include fallback chain
        for provider_id in self._get_fallback_chain():
            if provider_id not in result and provider_id in self._providers:
                result.append(provider_id)

        return result

    async def _call_provider(
        self,
        provider_id: LLMProvider,
        prompt: str,
        system_prompt: Optional[str],
        max_tokens: int,
        temperature: float,
    ) -> LLMResponse:
        """Call a specific LLM provider."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        if provider_id == LLMProvider.KIMI_LOCAL:
            return await self._call_kimi(messages, max_tokens, temperature)
        elif provider_id == LLMProvider.OLLAMA:
            return await self._call_ollama(messages, max_tokens, temperature)
        elif provider_id == LLMProvider.DEEPSEEK:
            return await self._call_deepseek(messages, max_tokens, temperature)
        elif provider_id == LLMProvider.GEMINI:
            return await self._call_gemini(messages, max_tokens, temperature)
        elif provider_id == LLMProvider.GROQ:
            return await self._call_groq(messages, max_tokens, temperature)
        elif provider_id == LLMProvider.ANTIGRAVITY:
            return await self._call_antigravity(messages, max_tokens, temperature)
        elif provider_id == LLMProvider.CLAUDE:
            return await self._call_claude(messages, max_tokens, temperature)
        else:
            raise ValueError(f"Unknown provider: {provider_id}")

    async def _call_kimi(
        self, messages: list, max_tokens: int, temperature: float
    ) -> LLMResponse:
        """Call Kimi K2.5 via OpenAI-compatible local endpoint."""
        import httpx

        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{settings.kimi_local_url}/chat/completions",
                json={
                    "model": settings.kimi_model_name,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                },
            )
            resp.raise_for_status()
            data = resp.json()

        choice = data["choices"][0]
        usage = data.get("usage", {})

        return LLMResponse(
            content=choice["message"]["content"],
            provider=LLMProvider.KIMI_LOCAL,
            model=settings.kimi_model_name,
            tokens_in=usage.get("prompt_tokens", 0),
            tokens_out=usage.get("completion_tokens", 0),
        )

    async def _call_ollama(
        self, messages: list, max_tokens: int, temperature: float
    ) -> LLMResponse:
        """Call Ollama local models."""
        import httpx

        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{settings.ollama_url}/api/chat",
                json={
                    "model": settings.ollama_default_model,
                    "messages": messages,
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": temperature,
                    },
                    "stream": False,
                },
            )
            resp.raise_for_status()
            data = resp.json()

        return LLMResponse(
            content=data["message"]["content"],
            provider=LLMProvider.OLLAMA,
            model=settings.ollama_default_model,
            tokens_in=data.get("prompt_eval_count", 0),
            tokens_out=data.get("eval_count", 0),
        )

    async def _call_deepseek(
        self, messages: list, max_tokens: int, temperature: float
    ) -> LLMResponse:
        """Call DeepSeek R1 via Ollama (local, free, chain-of-thought reasoning)."""
        import httpx

        async with httpx.AsyncClient(timeout=180.0) as client:
            resp = await client.post(
                f"{settings.ollama_url}/api/chat",
                json={
                    "model": settings.deepseek_model,
                    "messages": messages,
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": temperature,
                    },
                    "stream": False,
                },
            )
            resp.raise_for_status()
            data = resp.json()

        return LLMResponse(
            content=data["message"]["content"],
            provider=LLMProvider.DEEPSEEK,
            model=settings.deepseek_model,
            tokens_in=data.get("prompt_eval_count", 0),
            tokens_out=data.get("eval_count", 0),
        )

    async def _call_gemini(
        self, messages: list, max_tokens: int, temperature: float
    ) -> LLMResponse:
        """Call Google Gemini API (FREE tier: 15 RPM, 1M context)."""
        import httpx

        # Convert messages to Gemini format
        contents = []
        system_instruction = None
        for msg in messages:
            if msg["role"] == "system":
                system_instruction = msg["content"]
            else:
                role = "user" if msg["role"] == "user" else "model"
                contents.append({
                    "role": role,
                    "parts": [{"text": msg["content"]}],
                })

        body: dict = {
            "contents": contents,
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": temperature,
            },
        }
        if system_instruction:
            body["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }

        url = (
            f"https://generativelanguage.googleapis.com/v1beta/"
            f"models/{settings.gemini_model}:generateContent"
            f"?key={settings.gemini_api_key}"
        )

        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(url, json=body)
            resp.raise_for_status()
            data = resp.json()

        text = data["candidates"][0]["content"]["parts"][0]["text"]
        usage = data.get("usageMetadata", {})

        return LLMResponse(
            content=text,
            provider=LLMProvider.GEMINI,
            model=settings.gemini_model,
            tokens_in=usage.get("promptTokenCount", 0),
            tokens_out=usage.get("candidatesTokenCount", 0),
        )

    async def _call_groq(
        self, messages: list, max_tokens: int, temperature: float
    ) -> LLMResponse:
        """Call Groq API (FREE tier: 30 RPM, ultra-fast inference)."""
        import httpx

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.groq_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.groq_model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                },
            )
            resp.raise_for_status()
            data = resp.json()

        choice = data["choices"][0]
        usage = data.get("usage", {})

        return LLMResponse(
            content=choice["message"]["content"],
            provider=LLMProvider.GROQ,
            model=settings.groq_model,
            tokens_in=usage.get("prompt_tokens", 0),
            tokens_out=usage.get("completion_tokens", 0),
        )

    async def _call_antigravity(
        self, messages: list, max_tokens: int, temperature: float
    ) -> LLMResponse:
        """Call AntiGravity hybrid platform."""
        import httpx

        headers = {}
        if settings.antigravity_api_key:
            headers["Authorization"] = f"Bearer {settings.antigravity_api_key}"

        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{settings.antigravity_url}/v1/chat/completions",
                headers=headers,
                json={
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                },
            )
            resp.raise_for_status()
            data = resp.json()

        choice = data["choices"][0]
        usage = data.get("usage", {})

        return LLMResponse(
            content=choice["message"]["content"],
            provider=LLMProvider.ANTIGRAVITY,
            model="antigravity",
            tokens_in=usage.get("prompt_tokens", 0),
            tokens_out=usage.get("completion_tokens", 0),
        )

    async def _call_claude(
        self, messages: list, max_tokens: int, temperature: float
    ) -> LLMResponse:
        """Call Claude API (premium fallback)."""
        import anthropic

        client = anthropic.AsyncAnthropic(api_key=settings.claude_api_key)

        # Convert messages format for Anthropic API
        system_msg = None
        api_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                api_messages.append(msg)

        kwargs = {
            "model": settings.claude_model,
            "max_tokens": max_tokens,
            "messages": api_messages,
        }
        if system_msg:
            kwargs["system"] = system_msg

        response = await client.messages.create(**kwargs)

        return LLMResponse(
            content=response.content[0].text,
            provider=LLMProvider.CLAUDE,
            model=settings.claude_model,
            tokens_in=response.usage.input_tokens,
            tokens_out=response.usage.output_tokens,
        )

    # ─── Health & Availability ───

    async def _register_provider(self, provider_id: LLMProvider):
        """Register a provider as available."""
        self._providers[provider_id] = True
        self._health[provider_id] = ProviderHealth(
            provider=provider_id, is_available=True
        )

    async def _health_check_all(self):
        """Check health of all providers."""
        for provider_id in list(self._providers.keys()):
            try:
                health = self._health[provider_id]
                # Simple ping test
                if provider_id == LLMProvider.KIMI_LOCAL:
                    import httpx
                    async with httpx.AsyncClient(timeout=5.0) as client:
                        resp = await client.get(f"{settings.kimi_local_url}/models")
                        health.is_available = resp.status_code == 200
                elif provider_id == LLMProvider.OLLAMA:
                    import httpx
                    async with httpx.AsyncClient(timeout=5.0) as client:
                        resp = await client.get(f"{settings.ollama_url}/api/tags")
                        health.is_available = resp.status_code == 200
                elif provider_id == LLMProvider.DEEPSEEK:
                    import httpx
                    async with httpx.AsyncClient(timeout=5.0) as client:
                        resp = await client.get(f"{settings.ollama_url}/api/tags")
                        health.is_available = resp.status_code == 200
                elif provider_id == LLMProvider.GEMINI:
                    health.is_available = bool(settings.gemini_api_key)
                elif provider_id == LLMProvider.GROQ:
                    health.is_available = bool(settings.groq_api_key)
                elif provider_id == LLMProvider.CLAUDE:
                    health.is_available = bool(settings.claude_api_key)
                else:
                    health.is_available = True

                health.last_checked = datetime.now(timezone.utc).isoformat()
            except Exception:
                health = self._health[provider_id]
                health.is_available = False

    def _is_available(self, provider_id: LLMProvider) -> bool:
        health = self._health.get(provider_id)
        if not health:
            return False
        if health.consecutive_failures >= 5:
            return False
        return health.is_available

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
        self, prompt: str, task_type: str, system_prompt: Optional[str]
    ) -> str:
        content = f"{task_type}:{system_prompt or ''}:{prompt}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    # ─── Stats ───

    def get_stats(self) -> dict:
        return {
            "total_requests": self._request_count,
            "cache_hits": self._cache_hits,
            "cache_hit_rate": (
                self._cache_hits / max(self._request_count, 1) * 100
            ),
            "monthly_spend_usd": round(self._monthly_spend, 4),
            "budget_remaining_usd": round(
                settings.claude_monthly_budget_usd - self._monthly_spend, 4
            ),
            "providers": {
                p.value: {
                    "available": h.is_available,
                    "failures": h.consecutive_failures,
                }
                for p, h in self._health.items()
            },
        }
