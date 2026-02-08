"""
Base Agent — Foundation class for all NEXUS agents.
Every agent inherits this and implements execute().
"""

import asyncio
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Optional

import structlog

from core.llm_router.router import LLMRouter
from core.orchestrator.memory_manager import MemoryManager

logger = structlog.get_logger(__name__)


class BaseAgent(ABC):
    """
    Abstract base class for all NEXUS agents.

    Each agent:
    - Has a unique ID, name, and list of capabilities
    - Has access to the LLM router (for smart model selection)
    - Has access to the memory manager (for persistent context)
    - Can spawn sub-tasks and coordinate with other agents
    - Tracks its own execution cost
    """

    def __init__(
        self,
        agent_id: str,
        name: str,
        capabilities: list[str],
        cost_tier: int = 1,
        llm_router: Optional[LLMRouter] = None,
        memory: Optional[MemoryManager] = None,
    ):
        self.agent_id = agent_id
        self.name = name
        self.capabilities = capabilities
        self.cost_tier = cost_tier
        self.llm_router = llm_router
        self.memory = memory
        self._execution_count = 0
        self._total_cost = 0.0

    @abstractmethod
    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        Execute the agent's primary task.

        Args:
            context: {
                "client_id": str,
                "workflow_params": dict,
                "previous_results": dict,
                "client_memory": dict,
            }

        Returns:
            Result dict with at minimum: {"status": "success", "cost_usd": 0.0}
        """
        ...

    async def think(
        self,
        prompt: str,
        task_type: str = "general",
        system_prompt: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> str:
        """Use the LLM router to generate a response."""
        if not self.llm_router:
            raise RuntimeError(f"Agent {self.name} has no LLM router")

        response = await self.llm_router.generate(
            prompt=prompt,
            task_type=task_type,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        self._total_cost += response.cost_usd
        return response.content

    async def remember(self, client_id: str, key: str) -> Any:
        """Recall something about a client."""
        if not self.memory:
            return None
        context = await self.memory.get_client_context(client_id)
        return context.get(key)

    async def learn(self, client_id: str, insight: dict):
        """Store a learning about a client."""
        if self.memory:
            await self.memory.store_learning(client_id, self.agent_id, insight)

    def get_stats(self) -> dict:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "executions": self._execution_count,
            "total_cost_usd": round(self._total_cost, 4),
        }
