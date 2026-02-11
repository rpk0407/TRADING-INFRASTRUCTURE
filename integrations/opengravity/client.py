"""
OpenGravity Client — Hybrid local/cloud agent execution platform.

OpenGravity enables:
- Running AI agents on local hardware with cloud fallback
- Multi-agent orchestration with built-in coordination
- Cost optimization through smart routing
- Privacy-preserving local inference
- Cross-agent task coordination

Integration with NEXUS:
- Acts as an additional inference provider in the LLM Router
- Can run specialized agent tasks that benefit from its coordination layer
- Provides a middle-ground between fully local and fully cloud
"""

import httpx
from typing import Optional
from dataclasses import dataclass

from config.settings import settings


@dataclass
class OpenGravityResponse:
    """Structured response from OpenGravity inference."""
    content: str
    tokens_in: int
    tokens_out: int
    model: str
    execution_mode: str  # "local" or "cloud"
    cost_usd: float


class OpenGravityClient:
    """
    Client for OpenGravity hybrid AI platform.

    OpenGravity serves as a middleware layer that:
    1. Attempts local inference first (free)
    2. Falls back to cloud if local can't handle the task
    3. Provides cost tracking per request
    4. Supports multi-agent coordination
    5. Offers privacy-preserving inference for sensitive data
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: float = 120.0,
    ):
        self.base_url = (base_url or settings.opengravity_url).rstrip("/")
        self.api_key = api_key or settings.opengravity_api_key
        self.timeout = timeout
        self._cost_log: list[dict] = []

    def _headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _track_cost(self, model: str, mode: str, cost: float) -> None:
        """Record a cost entry for reporting."""
        self._cost_log.append({
            "model": model,
            "execution_mode": mode,
            "cost_usd": cost,
        })

    # ── Core API ─────────────────────────────────────────────────

    async def chat(
        self,
        messages: list[dict],
        max_tokens: int = 4096,
        temperature: float = 0.7,
        prefer_local: bool = True,
    ) -> OpenGravityResponse:
        """Send a chat completion through OpenGravity."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/v1/chat/completions",
                headers=self._headers(),
                json={
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "prefer_local": prefer_local,
                },
            )
            response.raise_for_status()
            data = response.json()

        choice = data["choices"][0]
        usage = data.get("usage", {})
        model = data.get("model", "opengravity")
        mode = data.get("execution_mode", "unknown")
        cost = data.get("cost_usd", 0.0)

        self._track_cost(model, mode, cost)

        return OpenGravityResponse(
            content=choice["message"]["content"],
            tokens_in=usage.get("prompt_tokens", 0),
            tokens_out=usage.get("completion_tokens", 0),
            model=model,
            execution_mode=mode,
            cost_usd=cost,
        )

    async def run_agent_task(
        self,
        task_type: str,
        context: dict,
        tools: Optional[list[dict]] = None,
    ) -> dict:
        """
        Run a specialized agent task through OpenGravity's agent framework.

        This leverages OpenGravity's built-in agent coordination for tasks
        like web scraping, data analysis, or content generation.
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/v1/agents/execute",
                headers=self._headers(),
                json={
                    "task_type": task_type,
                    "context": context,
                    "tools": tools or [],
                },
            )
            response.raise_for_status()
            result = response.json()

        # Track cost if present
        if "cost_usd" in result:
            self._track_cost(
                result.get("model", "opengravity-agent"),
                result.get("execution_mode", "unknown"),
                result["cost_usd"],
            )

        return result

    # ── Multi-Agent Coordination ────────────────────────────────

    async def coordinate_agents(
        self,
        agent_tasks: list[dict],
    ) -> dict:
        """
        Coordinate multiple agent tasks in parallel or sequentially.

        Each task in agent_tasks should contain:
        - task_type (str): The type of task to execute.
        - context (dict): Context / input data for the task.
        - tools (list[dict], optional): Tools the agent may use.
        - depends_on (list[int], optional): Indices of tasks that must
          complete before this one starts (for DAG execution).

        Returns a dict with:
        - results: list of individual task results
        - total_cost_usd: combined cost for all tasks
        - execution_summary: timing and mode info per task
        """
        async with httpx.AsyncClient(timeout=self.timeout * 2) as client:
            response = await client.post(
                f"{self.base_url}/v1/agents/coordinate",
                headers=self._headers(),
                json={"tasks": agent_tasks},
            )
            response.raise_for_status()
            data = response.json()

        # Track aggregate cost
        total_cost = data.get("total_cost_usd", 0.0)
        if total_cost > 0:
            self._track_cost("opengravity-coordinator", "mixed", total_cost)

        return data

    # ── Privacy-Preserving Inference ────────────────────────────

    async def execute_with_privacy(
        self,
        messages: list[dict],
        sensitive_fields: list[str],
    ) -> OpenGravityResponse:
        """
        Run inference with privacy preservation for sensitive data.

        OpenGravity will:
        1. Redact sensitive_fields from messages before any cloud routing.
        2. Force local-only execution when possible.
        3. If cloud is required, apply differential privacy / masking.

        Args:
            messages: Standard chat messages.
            sensitive_fields: Field names or patterns to protect
                (e.g. ["email", "ssn", "credit_card"]).

        Returns:
            OpenGravityResponse with the inference result.
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/v1/chat/completions",
                headers=self._headers(),
                json={
                    "messages": messages,
                    "max_tokens": 4096,
                    "temperature": 0.7,
                    "prefer_local": True,
                    "privacy": {
                        "enabled": True,
                        "sensitive_fields": sensitive_fields,
                        "force_local": True,
                    },
                },
            )
            response.raise_for_status()
            data = response.json()

        choice = data["choices"][0]
        usage = data.get("usage", {})
        model = data.get("model", "opengravity-private")
        mode = data.get("execution_mode", "local")
        cost = data.get("cost_usd", 0.0)

        self._track_cost(model, mode, cost)

        return OpenGravityResponse(
            content=choice["message"]["content"],
            tokens_in=usage.get("prompt_tokens", 0),
            tokens_out=usage.get("completion_tokens", 0),
            model=model,
            execution_mode=mode,
            cost_usd=cost,
        )

    # ── Cost Tracking ───────────────────────────────────────────

    def get_cost_report(self) -> dict:
        """
        Get a summary of costs incurred during this client session.

        Returns:
            dict with:
            - total_cost_usd: Total cost across all requests.
            - request_count: Number of tracked requests.
            - by_mode: Cost breakdown by execution mode (local vs cloud).
            - by_model: Cost breakdown by model.
            - entries: Raw list of all cost entries.
        """
        total = sum(e["cost_usd"] for e in self._cost_log)

        by_mode: dict[str, float] = {}
        by_model: dict[str, float] = {}
        for entry in self._cost_log:
            mode = entry["execution_mode"]
            model = entry["model"]
            by_mode[mode] = by_mode.get(mode, 0.0) + entry["cost_usd"]
            by_model[model] = by_model.get(model, 0.0) + entry["cost_usd"]

        return {
            "total_cost_usd": round(total, 6),
            "request_count": len(self._cost_log),
            "by_mode": by_mode,
            "by_model": by_model,
            "entries": list(self._cost_log),
        }

    # ── Utility ──────────────────────────────────────────────────

    async def is_available(self) -> bool:
        """Check if OpenGravity service is running."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(
                    f"{self.base_url}/health",
                    headers=self._headers(),
                )
                return resp.status_code == 200
        except Exception:
            return False
