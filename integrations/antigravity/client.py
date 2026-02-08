"""
AntiGravity Integration — Hybrid local/cloud agent execution platform.

AntiGravity enables:
- Running AI agents on local hardware with cloud fallback
- Multi-agent orchestration with built-in coordination
- Cost optimization through smart routing
- Privacy-preserving local inference

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
class AntiGravityResponse:
    content: str
    tokens_in: int
    tokens_out: int
    model: str
    execution_mode: str  # "local" or "cloud"
    cost_usd: float


class AntiGravityClient:
    """
    Client for AntiGravity hybrid AI platform.

    AntiGravity serves as a middleware layer that:
    1. Attempts local inference first (free)
    2. Falls back to cloud if local can't handle the task
    3. Provides cost tracking per request
    4. Supports multi-agent coordination
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: float = 120.0,
    ):
        self.base_url = base_url or settings.antigravity_url
        self.api_key = api_key or settings.antigravity_api_key
        self.timeout = timeout

    def _headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def chat(
        self,
        messages: list[dict],
        max_tokens: int = 4096,
        temperature: float = 0.7,
        prefer_local: bool = True,
    ) -> AntiGravityResponse:
        """Send a chat completion through AntiGravity."""
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

        return AntiGravityResponse(
            content=choice["message"]["content"],
            tokens_in=usage.get("prompt_tokens", 0),
            tokens_out=usage.get("completion_tokens", 0),
            model=data.get("model", "antigravity"),
            execution_mode=data.get("execution_mode", "unknown"),
            cost_usd=data.get("cost_usd", 0.0),
        )

    async def run_agent_task(
        self,
        task_type: str,
        context: dict,
        tools: Optional[list[dict]] = None,
    ) -> dict:
        """
        Run a specialized agent task through AntiGravity's agent framework.
        This leverages AntiGravity's built-in agent coordination.
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
            return response.json()

    async def is_available(self) -> bool:
        """Check if AntiGravity service is running."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(
                    f"{self.base_url}/health",
                    headers=self._headers(),
                )
                return resp.status_code == 200
        except Exception:
            return False
