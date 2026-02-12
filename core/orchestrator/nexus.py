"""
NEXUS Orchestrator — The Brain
Coordinates all agents through a DAG-based execution graph.
Routes tasks intelligently, manages state, and ensures fault tolerance.
"""

import asyncio
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Optional
from enum import Enum

import structlog

from core.orchestrator.agent_graph import AgentGraph, AgentNode
from core.orchestrator.task_queue import TaskQueue, Task, TaskPriority
from core.orchestrator.memory_manager import MemoryManager
from core.orchestrator.feedback_loop import FeedbackLoop, QualityScorer
from core.lifecycle.client_engine import ClientLifecycleEngine
from core.llm_router.router import LLMRouter
from config.settings import settings

logger = structlog.get_logger(__name__)


class WorkflowStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Workflow:
    """Represents a complete client workflow execution."""

    def __init__(
        self,
        workflow_id: str,
        client_id: str,
        workflow_type: str,
        params: dict[str, Any],
    ):
        self.workflow_id = workflow_id
        self.client_id = client_id
        self.workflow_type = workflow_type
        self.params = params
        self.status = WorkflowStatus.PENDING
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = self.created_at
        self.results: dict[str, Any] = {}
        self.errors: list[dict] = []
        self.agent_executions: list[dict] = []
        self.cost_usd: float = 0.0

    def to_dict(self) -> dict:
        return {
            "workflow_id": self.workflow_id,
            "client_id": self.client_id,
            "workflow_type": self.workflow_type,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "results": self.results,
            "errors": self.errors,
            "cost_usd": self.cost_usd,
            "agent_count": len(self.agent_executions),
        }


class NexusOrchestrator:
    """
    Central orchestrator that coordinates all NEXUS agents.

    Key capabilities:
    - DAG-based agent execution (parallel where possible, sequential where needed)
    - Intelligent LLM routing (cheapest model that can do the job)
    - Persistent memory per client
    - Fault tolerance with automatic retries and fallbacks
    - Real-time progress streaming via WebSocket
    - Cost tracking per workflow
    """

    MAX_COMPLETED_WORKFLOWS = 200

    def __init__(self):
        self.agent_graph = AgentGraph()
        self.task_queue = TaskQueue()
        self.memory = MemoryManager()
        self.llm_router = LLMRouter()
        self.feedback_loop = FeedbackLoop()
        self.lifecycle_engine = ClientLifecycleEngine(orchestrator=self)
        self.active_workflows: dict[str, Workflow] = {}
        self._agents: dict[str, Any] = {}
        self._running = False
        self._semaphore = asyncio.Semaphore(settings.agent_max_concurrent)

    async def initialize(self):
        """Boot up all subsystems."""
        logger.info("nexus.initializing", env=settings.env.value)
        await self.memory.initialize()
        await self.llm_router.initialize()
        await self._register_default_agents()
        self._running = True
        logger.info(
            "nexus.ready",
            agents=list(self._agents.keys()),
            llm_strategy=settings.llm_router_strategy.value,
        )

    async def shutdown(self):
        """Graceful shutdown."""
        logger.info("nexus.shutting_down")
        self._running = False
        await self.memory.flush()
        await self.llm_router.shutdown()

    async def _register_default_agents(self):
        """Register all available agents into the system."""
        from core.agents.website_builder.agent import WebsiteBuilderAgent
        from core.agents.content_engine.agent import ContentEngineAgent
        from core.agents.marketing_agent.agent import MarketingAgent
        from core.agents.crm_agent.agent import CRMAgent
        from core.agents.seo_agent.agent import SEOAgent
        from core.agents.growth_analytics.agent import GrowthAnalyticsAgent
        from core.agents.support_agent.agent import SupportAgent
        from core.agents.business_automation.agent import BusinessAutomationAgent

        agent_classes = [
            WebsiteBuilderAgent,
            ContentEngineAgent,
            MarketingAgent,
            CRMAgent,
            SEOAgent,
            GrowthAnalyticsAgent,
            SupportAgent,
            BusinessAutomationAgent,
        ]

        for agent_cls in agent_classes:
            agent = agent_cls(llm_router=self.llm_router, memory=self.memory)
            self._agents[agent.agent_id] = agent
            self.agent_graph.add_node(
                AgentNode(
                    agent_id=agent.agent_id,
                    agent_name=agent.name,
                    capabilities=agent.capabilities,
                    cost_tier=agent.cost_tier,
                )
            )
            logger.info("nexus.agent_registered", agent=agent.name)

    # ─── Workflow Execution ───

    async def execute_workflow(
        self,
        client_id: str,
        workflow_type: str,
        params: dict[str, Any],
    ) -> Workflow:
        """
        Execute a complete workflow for a client.
        Automatically determines which agents to invoke and in what order.
        """
        workflow_id = f"wf_{uuid.uuid4().hex[:12]}"
        workflow = Workflow(workflow_id, client_id, workflow_type, params)
        self.active_workflows[workflow_id] = workflow

        logger.info(
            "nexus.workflow_started",
            workflow_id=workflow_id,
            client_id=client_id,
            type=workflow_type,
        )

        try:
            workflow.status = WorkflowStatus.RUNNING
            execution_plan = await self._plan_workflow(workflow)
            await self._execute_plan(workflow, execution_plan)
            workflow.status = WorkflowStatus.COMPLETED
        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            workflow.errors.append({
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            logger.error("nexus.workflow_failed", workflow_id=workflow_id, error=str(e))
            raise
        finally:
            workflow.updated_at = datetime.now(timezone.utc)
            await self.memory.store_workflow_result(client_id, workflow.to_dict())

        logger.info(
            "nexus.workflow_completed",
            workflow_id=workflow_id,
            cost=workflow.cost_usd,
            agents_used=len(workflow.agent_executions),
        )

        # Cleanup old completed workflows to prevent memory leak
        self._cleanup_old_workflows()

        return workflow

    def _cleanup_old_workflows(self):
        """Remove old completed/failed workflows to bound memory."""
        finished = [
            wid for wid, w in self.active_workflows.items()
            if w.status in (WorkflowStatus.COMPLETED, WorkflowStatus.FAILED)
        ]
        if len(finished) > self.MAX_COMPLETED_WORKFLOWS:
            for wid in finished[:len(finished) - self.MAX_COMPLETED_WORKFLOWS]:
                del self.active_workflows[wid]

    async def _plan_workflow(self, workflow: Workflow) -> list[list[str]]:
        """
        Use LLM to determine optimal agent execution plan.
        Returns a list of execution stages (each stage runs in parallel).
        """
        client_context = await self.memory.get_client_context(workflow.client_id)
        available_agents = {
            aid: {
                "name": a.name,
                "capabilities": a.capabilities,
                "cost_tier": a.cost_tier,
            }
            for aid, a in self._agents.items()
        }

        planning_prompt = f"""You are the NEXUS workflow planner. Given a client request,
determine which agents to use and in what order.

CLIENT CONTEXT:
{client_context}

AVAILABLE AGENTS:
{available_agents}

WORKFLOW REQUEST:
Type: {workflow.workflow_type}
Parameters: {workflow.params}

Return a JSON array of execution stages. Each stage is an array of agent IDs
that can run in parallel. Stages execute sequentially.

Example: [["website_builder"], ["seo_agent", "content_engine"], ["growth_analytics"]]

Think carefully about dependencies:
- Website must be built before SEO can optimize it
- Content should be ready before marketing campaigns
- Analytics can run after data-producing agents finish

Return ONLY the JSON array, no other text."""

        response = await self.llm_router.generate(
            prompt=planning_prompt,
            task_type="planning",
            max_tokens=1024,
        )

        try:
            plan = json.loads(response.content)
            logger.info("nexus.plan_created", stages=len(plan), plan=plan)
            return plan
        except (json.JSONDecodeError, KeyError):
            # Fallback: run the most relevant single agent
            default_agent = self._get_default_agent(workflow.workflow_type)
            return [[default_agent]]

    async def _execute_plan(
        self, workflow: Workflow, plan: list[list[str]]
    ):
        """Execute the planned agent stages."""
        for stage_idx, stage_agents in enumerate(plan):
            logger.info(
                "nexus.stage_started",
                workflow_id=workflow.workflow_id,
                stage=stage_idx,
                agents=stage_agents,
            )

            # Run all agents in this stage concurrently
            tasks = []
            for agent_id in stage_agents:
                if agent_id in self._agents:
                    tasks.append(
                        self._execute_agent(workflow, agent_id, stage_idx)
                    )

            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                for result in results:
                    if isinstance(result, Exception):
                        workflow.errors.append({
                            "stage": stage_idx,
                            "error": str(result),
                        })

    async def _execute_agent(
        self, workflow: Workflow, agent_id: str, stage: int
    ) -> dict:
        """Execute a single agent within the workflow context."""
        async with self._semaphore:
            agent = self._agents[agent_id]
            start_time = datetime.now(timezone.utc)

            logger.info(
                "nexus.agent_executing",
                workflow_id=workflow.workflow_id,
                agent=agent.name,
                stage=stage,
            )

            try:
                # Provide agent with workflow context + previous stage results
                context = {
                    "client_id": workflow.client_id,
                    "workflow_params": workflow.params,
                    "previous_results": workflow.results,
                    "client_memory": await self.memory.get_client_context(
                        workflow.client_id
                    ),
                }

                result = await asyncio.wait_for(
                    agent.execute(context),
                    timeout=settings.agent_timeout_seconds,
                )

                duration_ms = (
                    datetime.now(timezone.utc) - start_time
                ).total_seconds() * 1000

                # Store result for downstream agents
                workflow.results[agent_id] = result
                workflow.cost_usd += result.get("cost_usd", 0.0)

                # ─── Feedback Loop: Score & Record ───
                output_str = str(result.get("output", result))
                task_type = result.get("task_type", "general")
                provider_used = result.get("provider", None)
                if provider_used:
                    from core.llm_router.models import LLMProvider
                    try:
                        provider_enum = LLMProvider(provider_used)
                    except ValueError:
                        provider_enum = None
                    if provider_enum:
                        quality = self.feedback_loop.record(
                            provider=provider_enum,
                            task_type=task_type,
                            output=output_str,
                            latency_ms=duration_ms,
                            cost_usd=result.get("cost_usd", 0.0),
                        )
                        result["quality_score"] = quality["total"]
                        result["quality_issues"] = quality["issues"]

                        # Auto-tune: if feedback loop has enough data, hint router
                        best = self.feedback_loop.get_best_provider(task_type)
                        if best:
                            self.llm_router.set_preference(task_type, best)

                execution_record = {
                    "agent_id": agent_id,
                    "agent_name": agent.name,
                    "stage": stage,
                    "duration_ms": duration_ms,
                    "cost_usd": result.get("cost_usd", 0.0),
                    "quality_score": result.get("quality_score"),
                    "status": "completed",
                }
                workflow.agent_executions.append(execution_record)

                logger.info(
                    "nexus.agent_completed",
                    agent=agent.name,
                    duration_ms=duration_ms,
                    quality=result.get("quality_score"),
                )
                return result

            except asyncio.TimeoutError:
                logger.error("nexus.agent_timeout", agent=agent.name)
                raise
            except Exception as e:
                logger.error(
                    "nexus.agent_error", agent=agent.name, error=str(e)
                )
                raise

    def _get_default_agent(self, workflow_type: str) -> str:
        """Map workflow types to default agents."""
        mapping = {
            "website": "website_builder",
            "content": "content_engine",
            "marketing": "marketing_agent",
            "crm": "crm_agent",
            "seo": "seo_agent",
            "analytics": "growth_analytics",
            "support": "support_agent",
            "automation": "business_automation",
            "full_setup": "website_builder",
        }
        return mapping.get(workflow_type, "website_builder")

    # ─── Query Methods ───

    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        return self.active_workflows.get(workflow_id)

    def list_agents(self) -> list[dict]:
        return [
            {
                "agent_id": aid,
                "name": a.name,
                "capabilities": a.capabilities,
                "cost_tier": a.cost_tier,
                "status": "ready",
            }
            for aid, a in self._agents.items()
        ]

    async def get_client_dashboard(self, client_id: str) -> dict:
        """Get complete client overview."""
        history = await self.memory.get_client_workflows(client_id)
        context = await self.memory.get_client_context(client_id)
        total_cost = sum(w.get("cost_usd", 0) for w in history)

        return {
            "client_id": client_id,
            "total_workflows": len(history),
            "total_cost_usd": total_cost,
            "context": context,
            "recent_workflows": history[-10:],
            "available_agents": self.list_agents(),
            "feedback_stats": self.feedback_loop.get_stats(),
        }

    def get_system_health(self) -> dict:
        """Complete system health including feedback loop."""
        return {
            "llm_router": self.llm_router.get_stats(),
            "feedback_loop": self.feedback_loop.get_stats(),
            "active_workflows": len(self.active_workflows),
            "registered_agents": len(self._agents),
            "running": self._running,
        }
