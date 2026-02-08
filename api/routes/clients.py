"""
Client API — Manage client profiles, history, and dashboards.
"""

from typing import Any

from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()


class ClientProfileUpdate(BaseModel):
    business_name: str | None = None
    industry: str | None = None
    description: str | None = None
    target_audience: str | None = None
    brand: dict[str, Any] | None = None
    goals: list[str] | None = None
    preferences: dict[str, Any] | None = None


@router.get("/{client_id}/dashboard")
async def get_client_dashboard(request: Request, client_id: str):
    """Get complete client dashboard data."""
    orchestrator = request.app.state.orchestrator
    return await orchestrator.get_client_dashboard(client_id)


@router.put("/{client_id}/profile")
async def update_client_profile(
    request: Request,
    client_id: str,
    profile: ClientProfileUpdate,
):
    """Update client profile information."""
    orchestrator = request.app.state.orchestrator
    updates = {k: v for k, v in profile.model_dump().items() if v is not None}
    await orchestrator.memory.update_client_profile(client_id, updates)
    return {"status": "updated", "client_id": client_id, "fields": list(updates.keys())}


@router.get("/{client_id}/workflows")
async def get_client_workflows(request: Request, client_id: str):
    """Get client's workflow history."""
    orchestrator = request.app.state.orchestrator
    workflows = await orchestrator.memory.get_client_workflows(client_id)
    return {
        "client_id": client_id,
        "total_workflows": len(workflows),
        "workflows": workflows,
    }


@router.get("/{client_id}/learnings")
async def get_client_learnings(request: Request, client_id: str):
    """Get all agent learnings about this client."""
    orchestrator = request.app.state.orchestrator
    context = await orchestrator.memory.get_client_context(client_id)
    return {
        "client_id": client_id,
        "learnings": context.get("learnings", []),
    }
