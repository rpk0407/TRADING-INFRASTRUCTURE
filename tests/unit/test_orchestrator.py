"""Tests for the NEXUS Orchestrator."""

import pytest
from core.orchestrator.agent_graph import AgentGraph, AgentNode
from core.orchestrator.task_queue import TaskQueue, Task, TaskPriority
from core.orchestrator.memory_manager import MemoryManager


class TestAgentGraph:
    def test_add_node(self):
        graph = AgentGraph()
        node = AgentNode(
            agent_id="test_agent",
            agent_name="Test Agent",
            capabilities=["testing"],
            cost_tier=1,
        )
        graph.add_node(node)
        assert graph.get_node("test_agent") is not None

    def test_execution_stages_no_deps(self):
        graph = AgentGraph()
        for i in range(3):
            graph.add_node(AgentNode(
                agent_id=f"agent_{i}",
                agent_name=f"Agent {i}",
            ))

        stages = graph.get_execution_stages(["agent_0", "agent_1", "agent_2"])
        # All agents can run in parallel (no dependencies)
        assert len(stages) == 1
        assert len(stages[0]) == 3

    def test_execution_stages_with_deps(self):
        graph = AgentGraph()
        graph.add_node(AgentNode(agent_id="a", agent_name="A"))
        graph.add_node(AgentNode(agent_id="b", agent_name="B"))
        graph.add_node(AgentNode(agent_id="c", agent_name="C"))
        graph.add_dependency("a", "b")  # A must finish before B
        graph.add_dependency("b", "c")  # B must finish before C

        stages = graph.get_execution_stages(["a", "b", "c"])
        assert len(stages) == 3
        assert stages[0] == ["a"]
        assert stages[1] == ["b"]
        assert stages[2] == ["c"]

    def test_cycle_detection(self):
        graph = AgentGraph()
        graph.add_node(AgentNode(agent_id="a", agent_name="A"))
        graph.add_node(AgentNode(agent_id="b", agent_name="B"))
        graph.add_dependency("a", "b")

        with pytest.raises(ValueError, match="cycle"):
            graph.add_dependency("b", "a")

    def test_find_agents_for_task(self):
        graph = AgentGraph()
        graph.add_node(AgentNode(
            agent_id="cheap",
            agent_name="Cheap",
            capabilities=["coding", "analysis"],
            cost_tier=1,
        ))
        graph.add_node(AgentNode(
            agent_id="expensive",
            agent_name="Expensive",
            capabilities=["coding", "analysis", "vision"],
            cost_tier=3,
        ))

        agents = graph.find_agents_for_task(["coding"])
        assert "cheap" in agents
        assert "expensive" not in agents  # Prefers cheaper


class TestTaskQueue:
    @pytest.mark.asyncio
    async def test_priority_ordering(self):
        queue = TaskQueue()
        await queue.enqueue(Task(priority=TaskPriority.LOW, task_id="low"))
        await queue.enqueue(Task(priority=TaskPriority.CRITICAL, task_id="critical"))
        await queue.enqueue(Task(priority=TaskPriority.NORMAL, task_id="normal"))

        first = await queue.dequeue()
        assert first.task_id == "critical"

    @pytest.mark.asyncio
    async def test_complete_and_fail(self):
        queue = TaskQueue()
        await queue.enqueue(Task(priority=TaskPriority.NORMAL, task_id="t1"))

        task = await queue.dequeue()
        queue.complete("t1", result={"done": True})

        completed = queue.get_task("t1")
        assert completed.status == "completed"

    @pytest.mark.asyncio
    async def test_retry_on_failure(self):
        queue = TaskQueue()
        await queue.enqueue(
            Task(priority=TaskPriority.NORMAL, task_id="t1", max_retries=3)
        )

        queue.fail("t1", error="temporary error")
        task = queue.get_task("t1")
        assert task.retry_count == 1
        assert task.status == "queued"  # Should be re-queued

    def test_stats(self):
        queue = TaskQueue()
        stats = queue.get_stats()
        assert stats["total"] == 0
        assert stats["queued"] == 0


class TestMemoryManager:
    @pytest.mark.asyncio
    async def test_client_profile(self):
        memory = MemoryManager()
        await memory.initialize()

        await memory.update_client_profile("client1", {
            "business_name": "TestCo",
            "industry": "tech",
        })

        context = await memory.get_client_context("client1")
        assert context["profile"]["business_name"] == "TestCo"

    @pytest.mark.asyncio
    async def test_store_workflow_result(self):
        memory = MemoryManager()
        await memory.initialize()

        await memory.store_workflow_result("client1", {
            "workflow_id": "wf_123",
            "status": "completed",
        })

        history = await memory.get_client_workflows("client1")
        assert len(history) == 1
        assert history[0]["workflow_id"] == "wf_123"

    @pytest.mark.asyncio
    async def test_store_learning(self):
        memory = MemoryManager()
        await memory.initialize()

        await memory.store_learning("client1", "seo_agent", {
            "insight": "Client prefers minimal design",
        })

        learnings = await memory.get_agent_learnings("client1", "seo_agent")
        assert len(learnings) == 1

    @pytest.mark.asyncio
    async def test_workflow_context(self):
        memory = MemoryManager()
        memory.set_workflow_context("wf_1", "step", "building")
        ctx = memory.get_workflow_context("wf_1")
        assert ctx["step"] == "building"
        memory.clear_workflow_context("wf_1")
        assert memory.get_workflow_context("wf_1") == {}
