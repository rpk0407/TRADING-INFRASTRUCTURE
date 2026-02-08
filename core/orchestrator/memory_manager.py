"""
Memory Manager — Persistent context and learning for each client.
This is what makes NEXUS unique: agents LEARN from each client interaction.
"""

import json
from datetime import datetime, timezone
from typing import Any, Optional

import structlog

from config.settings import settings

logger = structlog.get_logger(__name__)


class MemoryManager:
    """
    Manages persistent memory across all client interactions.

    Three memory layers:
    1. Short-term: Current workflow context (in-memory)
    2. Medium-term: Client session history (Redis)
    3. Long-term: Full client profile + learnings (Database)

    This allows agents to:
    - Remember client preferences and brand guidelines
    - Learn from past workflow outcomes
    - Improve recommendations over time
    - Maintain context across sessions
    """

    def __init__(self):
        self._short_term: dict[str, dict] = {}
        self._client_profiles: dict[str, dict] = {}
        self._workflow_history: dict[str, list[dict]] = {}
        self._redis = None

    async def initialize(self):
        """Connect to storage backends."""
        logger.info("memory.initializing", backend=settings.agent_memory_backend)

        if settings.agent_memory_backend == "redis":
            try:
                import redis.asyncio as aioredis
                self._redis = aioredis.from_url(
                    settings.redis_url, decode_responses=True
                )
                await self._redis.ping()
                logger.info("memory.redis_connected")
            except Exception as e:
                logger.warning(
                    "memory.redis_unavailable, falling back to in-memory",
                    error=str(e),
                )
                self._redis = None

    async def flush(self):
        """Persist all in-memory state."""
        if self._redis:
            for client_id, profile in self._client_profiles.items():
                await self._redis.set(
                    f"nexus:client:{client_id}:profile",
                    json.dumps(profile),
                )
            for client_id, history in self._workflow_history.items():
                await self._redis.set(
                    f"nexus:client:{client_id}:workflows",
                    json.dumps(history[-100:]),  # Keep last 100
                )

    # ─── Client Context ───

    async def get_client_context(self, client_id: str) -> dict:
        """Get full client context for agent consumption."""
        profile = await self._get_client_profile(client_id)
        recent_workflows = await self.get_client_workflows(client_id)

        return {
            "profile": profile,
            "recent_workflows": recent_workflows[-5:],
            "preferences": profile.get("preferences", {}),
            "brand": profile.get("brand", {}),
            "industry": profile.get("industry", ""),
            "goals": profile.get("goals", []),
            "learnings": profile.get("learnings", []),
        }

    async def update_client_profile(
        self, client_id: str, updates: dict[str, Any]
    ):
        """Update client profile with new information."""
        profile = await self._get_client_profile(client_id)
        profile.update(updates)
        profile["updated_at"] = datetime.now(timezone.utc).isoformat()
        self._client_profiles[client_id] = profile

        if self._redis:
            await self._redis.set(
                f"nexus:client:{client_id}:profile",
                json.dumps(profile),
            )

        logger.debug("memory.profile_updated", client_id=client_id)

    async def store_workflow_result(self, client_id: str, result: dict):
        """Store completed workflow for learning."""
        history = self._workflow_history.setdefault(client_id, [])
        result["stored_at"] = datetime.now(timezone.utc).isoformat()
        history.append(result)

        if self._redis:
            await self._redis.rpush(
                f"nexus:client:{client_id}:workflows",
                json.dumps(result),
            )

    async def get_client_workflows(self, client_id: str) -> list[dict]:
        """Get client's workflow history."""
        if client_id in self._workflow_history:
            return self._workflow_history[client_id]

        if self._redis:
            data = await self._redis.lrange(
                f"nexus:client:{client_id}:workflows", 0, -1
            )
            if data:
                history = [json.loads(d) for d in data]
                self._workflow_history[client_id] = history
                return history

        return []

    # ─── Agent Learning ───

    async def store_learning(
        self, client_id: str, agent_id: str, learning: dict
    ):
        """Store an insight learned by an agent about a client."""
        profile = await self._get_client_profile(client_id)
        learnings = profile.setdefault("learnings", [])
        learnings.append({
            "agent_id": agent_id,
            "insight": learning,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        # Keep only most recent 50 learnings
        profile["learnings"] = learnings[-50:]
        self._client_profiles[client_id] = profile

    async def get_agent_learnings(
        self, client_id: str, agent_id: str
    ) -> list[dict]:
        """Get learnings specific to an agent for a client."""
        profile = await self._get_client_profile(client_id)
        return [
            l for l in profile.get("learnings", [])
            if l.get("agent_id") == agent_id
        ]

    # ─── Short-term Context ───

    def set_workflow_context(self, workflow_id: str, key: str, value: Any):
        """Store temporary workflow context."""
        ctx = self._short_term.setdefault(workflow_id, {})
        ctx[key] = value

    def get_workflow_context(self, workflow_id: str) -> dict:
        """Get temporary workflow context."""
        return self._short_term.get(workflow_id, {})

    def clear_workflow_context(self, workflow_id: str):
        """Clean up after workflow completion."""
        self._short_term.pop(workflow_id, None)

    # ─── Internal ───

    async def _get_client_profile(self, client_id: str) -> dict:
        if client_id in self._client_profiles:
            return self._client_profiles[client_id]

        if self._redis:
            data = await self._redis.get(f"nexus:client:{client_id}:profile")
            if data:
                profile = json.loads(data)
                self._client_profiles[client_id] = profile
                return profile

        # New client
        profile = {
            "client_id": client_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "preferences": {},
            "brand": {},
            "industry": "",
            "goals": [],
            "learnings": [],
        }
        self._client_profiles[client_id] = profile
        return profile
