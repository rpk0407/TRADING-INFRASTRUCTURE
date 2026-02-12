"""
Lifecycle API — Client onboarding, phase management, health monitoring.
"""

from typing import Any

from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()


class ClientIntake(BaseModel):
    company_name: str
    industry: str
    company_size: str = "small"
    target_audience: str = ""
    competitors: list[str] = Field(default_factory=list)
    goals: list[str] = Field(default_factory=list)
    budget_tier: str = "starter"
    services: list[str] = Field(default_factory=list)


@router.post("/onboard")
async def onboard_client(request: Request, intake: ClientIntake):
    """Onboard a new client — starts the full lifecycle automation."""
    orchestrator = request.app.state.orchestrator
    profile = await orchestrator.lifecycle_engine.onboard_client(intake.model_dump())
    return {
        "status": "onboarded",
        "client": profile.to_dict(),
        "next_steps": "Discovery and competitor research workflows started automatically.",
    }


@router.post("/{client_id}/advance")
async def advance_phase(request: Request, client_id: str):
    """Advance client to the next lifecycle phase."""
    orchestrator = request.app.state.orchestrator
    result = await orchestrator.lifecycle_engine.advance_phase(client_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.get("/{client_id}/health")
async def client_health(request: Request, client_id: str):
    """Get client health score and recommendations."""
    orchestrator = request.app.state.orchestrator
    result = await orchestrator.lifecycle_engine.check_client_health(client_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.get("/{client_id}/progress")
async def client_progress(request: Request, client_id: str):
    """Get client phase progress."""
    orchestrator = request.app.state.orchestrator
    result = orchestrator.lifecycle_engine.get_phase_progress(client_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.get("/{client_id}/profile")
async def get_client_profile(request: Request, client_id: str):
    """Get full client lifecycle profile."""
    orchestrator = request.app.state.orchestrator
    profile = orchestrator.lifecycle_engine.get_client(client_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Client not found")
    return profile.to_dict() if hasattr(profile, "to_dict") else profile


@router.get("/")
async def list_lifecycle_clients(request: Request):
    """List all clients in the lifecycle system."""
    orchestrator = request.app.state.orchestrator
    return {
        "clients": orchestrator.lifecycle_engine.list_clients(),
        "total": len(orchestrator.lifecycle_engine._clients),
    }


@router.get("/templates")
async def get_templates(request: Request):
    """Get available automation templates."""
    orchestrator = request.app.state.orchestrator
    return {
        "templates": orchestrator.lifecycle_engine.get_automation_templates(),
    }


@router.get("/system/health")
async def system_health(request: Request):
    """Get complete system health including feedback loop stats."""
    orchestrator = request.app.state.orchestrator
    return orchestrator.get_system_health()
