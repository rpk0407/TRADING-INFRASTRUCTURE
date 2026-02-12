"""
Agent API — View and manage the agent fleet.
"""

from fastapi import APIRouter, Request, HTTPException

router = APIRouter()


@router.get("/")
async def list_agents(request: Request):
    """List all available agents and their capabilities."""
    orchestrator = request.app.state.orchestrator
    agents = orchestrator.list_agents()
    return {
        "agents": agents,
        "total": len(agents),
    }


@router.get("/{agent_id}")
async def get_agent(request: Request, agent_id: str):
    """Get detailed info about a specific agent."""
    orchestrator = request.app.state.orchestrator
    if agent_id not in orchestrator._agents:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

    agent = orchestrator._agents[agent_id]
    return {
        "agent_id": agent.agent_id,
        "name": agent.name,
        "capabilities": agent.capabilities,
        "cost_tier": agent.cost_tier,
        "stats": agent.get_stats(),
    }


@router.get("/{agent_id}/stats")
async def get_agent_stats(request: Request, agent_id: str):
    """Get execution statistics for an agent."""
    orchestrator = request.app.state.orchestrator
    if agent_id not in orchestrator._agents:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

    return orchestrator._agents[agent_id].get_stats()
