"""
Base Agent — Foundation class for all NEXUS agents.
Every agent inherits this and implements execute().
"""

import asyncio
import json
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
    - Has access to tools: web scraper, code executor, reflection, browser
    - Can spawn sub-tasks and coordinate with other agents
    - Tracks its own execution cost
    - Supports reflection/self-improvement on outputs
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

        # Tools — lazy-initialized when first used
        self._scraper = None
        self._executor = None
        self._reflection = None
        self._chain_of_thought = None
        self._browser = None

    # ─── Tool Accessors (lazy init) ───

    @property
    def scraper(self):
        if self._scraper is None:
            from core.tools.web_scraper import WebScraper
            self._scraper = WebScraper()
        return self._scraper

    @property
    def executor(self):
        if self._executor is None:
            from core.tools.code_executor import CodeExecutor
            self._executor = CodeExecutor()
        return self._executor

    @property
    def reflection(self):
        if self._reflection is None:
            from core.tools.reflection_engine import ReflectionEngine
            self._reflection = ReflectionEngine(self.llm_router)
        return self._reflection

    @property
    def chain_of_thought(self):
        if self._chain_of_thought is None:
            from core.tools.reflection_engine import ChainOfThought
            self._chain_of_thought = ChainOfThought(self.llm_router)
        return self._chain_of_thought

    @property
    def browser(self):
        if self._browser is None:
            from core.tools.browser_automation import BrowserAutomation
            self._browser = BrowserAutomation()
        return self._browser

    # ─── Core Methods ───

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
        force_provider: Optional[str] = None,
    ) -> str:
        """Use the LLM router to generate a response."""
        if not self.llm_router:
            raise RuntimeError(f"Agent {self.name} has no LLM router")

        from core.llm_router.models import LLMProvider
        fp = LLMProvider(force_provider) if force_provider else None

        response = await self.llm_router.generate(
            prompt=prompt,
            task_type=task_type,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            force_provider=fp,
        )
        self._total_cost += response.cost_usd
        return response.content

    async def think_code(self, prompt: str, **kwargs) -> str:
        """Generate code — forces routing to OpenCode provider."""
        return await self.think(prompt, task_type="code_generation", force_provider="opencode", **kwargs)

    async def think_with_reflection(
        self,
        prompt: str,
        task_description: str,
        task_type: str = "general",
        system_prompt: Optional[str] = None,
        quality_threshold: int = 75,
    ) -> dict:
        """Generate output with automatic self-improvement via reflection."""
        # First pass
        initial = await self.think(
            prompt=prompt,
            task_type=task_type,
            system_prompt=system_prompt,
            max_tokens=4096,
        )

        # Reflect and improve
        result = await self.reflection.reflect_and_improve(
            original_output=initial,
            task_description=task_description,
            task_type=task_type,
            quality_threshold=quality_threshold,
        )

        logger.info(
            "agent.reflected",
            agent=self.name,
            iterations=result["iterations"],
            scores=result["quality_scores"],
            converged=result["converged"],
        )
        return result

    async def reason_step_by_step(
        self,
        problem: str,
        context: str = "",
        task_type: str = "analysis",
    ) -> dict:
        """Use chain-of-thought reasoning for complex problems."""
        return await self.chain_of_thought.reason(
            problem=problem,
            context=context,
            task_type=task_type,
        )

    async def scrape_url(self, url: str, mode: str = "text") -> dict:
        """Fetch and parse a web page."""
        return await self.scraper.fetch_page(url, extract_mode=mode)

    async def run_code(
        self, code: str, language: str = "python"
    ) -> dict:
        """Execute code in a sandboxed environment."""
        return await self.executor.execute(code, language=language)

    # ─── Memory Methods ───

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
