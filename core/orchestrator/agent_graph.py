"""
Agent Graph — DAG-based agent dependency and routing system.
Determines optimal execution order and parallelization.
"""

from dataclasses import dataclass, field
from typing import Optional
import networkx as nx
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class AgentNode:
    """Represents an agent in the execution graph."""
    agent_id: str
    agent_name: str
    capabilities: list[str] = field(default_factory=list)
    cost_tier: int = 1  # 1=free/local, 2=cheap, 3=moderate, 4=expensive
    dependencies: list[str] = field(default_factory=list)
    max_concurrent: int = 1
    timeout_seconds: int = 300

    def __hash__(self):
        return hash(self.agent_id)


class AgentGraph:
    """
    Manages the directed acyclic graph of agent dependencies.
    Enables parallel execution of independent agents while
    respecting dependency ordering.
    """

    def __init__(self):
        self.graph = nx.DiGraph()
        self._nodes: dict[str, AgentNode] = {}

    def add_node(self, node: AgentNode):
        """Register an agent node."""
        self._nodes[node.agent_id] = node
        self.graph.add_node(node.agent_id, data=node)

    def add_dependency(self, from_agent: str, to_agent: str):
        """Declare that from_agent must complete before to_agent starts."""
        if from_agent in self._nodes and to_agent in self._nodes:
            self.graph.add_edge(from_agent, to_agent)
            if not nx.is_directed_acyclic_graph(self.graph):
                self.graph.remove_edge(from_agent, to_agent)
                raise ValueError(
                    f"Adding dependency {from_agent} -> {to_agent} "
                    f"would create a cycle"
                )

    def get_execution_stages(
        self, required_agents: list[str]
    ) -> list[list[str]]:
        """
        Compute execution stages from the graph.
        Each stage contains agents that can run in parallel.
        Stages execute sequentially.
        """
        subgraph = self.graph.subgraph(
            [a for a in required_agents if a in self.graph]
        )

        if not subgraph.nodes:
            return [required_agents]

        stages = []
        remaining = set(required_agents)
        completed = set()

        while remaining:
            # Find agents whose dependencies are all completed
            ready = []
            for agent_id in remaining:
                deps = set(self.graph.predecessors(agent_id)) & set(required_agents)
                if deps.issubset(completed):
                    ready.append(agent_id)

            if not ready:
                # No agents ready — break cycle by forcing one
                ready = [next(iter(remaining))]

            stages.append(ready)
            completed.update(ready)
            remaining -= set(ready)

        return stages

    def get_agent_capabilities(self) -> dict[str, list[str]]:
        """Map all capabilities to their providing agents."""
        cap_map: dict[str, list[str]] = {}
        for agent_id, node in self._nodes.items():
            for cap in node.capabilities:
                cap_map.setdefault(cap, []).append(agent_id)
        return cap_map

    def find_agents_for_task(self, task_capabilities: list[str]) -> list[str]:
        """Find the minimum set of agents that cover all required capabilities."""
        cap_map = self.get_agent_capabilities()
        selected = set()
        for cap in task_capabilities:
            if cap in cap_map:
                # Prefer cheapest agent that has this capability
                candidates = cap_map[cap]
                cheapest = min(
                    candidates, key=lambda a: self._nodes[a].cost_tier
                )
                selected.add(cheapest)
        return list(selected)

    def get_node(self, agent_id: str) -> Optional[AgentNode]:
        return self._nodes.get(agent_id)

    def visualize(self) -> str:
        """ASCII visualization of the agent graph."""
        lines = ["Agent Dependency Graph:", "=" * 40]
        for node_id in nx.topological_sort(self.graph):
            node = self._nodes[node_id]
            deps = list(self.graph.predecessors(node_id))
            dep_str = f" <- [{', '.join(deps)}]" if deps else ""
            lines.append(
                f"  [{node.cost_tier}] {node.agent_name} ({node.agent_id}){dep_str}"
            )
        return "\n".join(lines)
