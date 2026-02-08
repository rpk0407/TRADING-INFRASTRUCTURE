"""
Analytics API — Platform-wide analytics and LLM usage stats.
"""

from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/llm-usage")
async def get_llm_usage(request: Request):
    """Get LLM router usage statistics."""
    orchestrator = request.app.state.orchestrator
    return orchestrator.llm_router.get_stats()


@router.get("/platform-stats")
async def get_platform_stats(request: Request):
    """Get overall platform statistics."""
    orchestrator = request.app.state.orchestrator

    return {
        "active_workflows": len(orchestrator.active_workflows),
        "registered_agents": len(orchestrator._agents),
        "task_queue": orchestrator.task_queue.get_stats(),
        "llm_router": orchestrator.llm_router.get_stats(),
        "agents": {
            aid: agent.get_stats()
            for aid, agent in orchestrator._agents.items()
        },
    }


@router.get("/cost-breakdown")
async def get_cost_breakdown(request: Request):
    """Get cost breakdown across all LLM providers."""
    orchestrator = request.app.state.orchestrator
    llm_stats = orchestrator.llm_router.get_stats()

    # Aggregate workflow costs
    workflow_costs = {}
    for wf_id, wf in orchestrator.active_workflows.items():
        workflow_costs[wf_id] = {
            "client_id": wf.client_id,
            "type": wf.workflow_type,
            "cost_usd": wf.cost_usd,
            "status": wf.status.value,
        }

    return {
        "llm_costs": llm_stats,
        "workflow_costs": workflow_costs,
        "total_platform_cost": sum(
            wf.cost_usd for wf in orchestrator.active_workflows.values()
        ),
    }
