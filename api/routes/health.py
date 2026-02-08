"""Health check endpoints."""

from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "nexus-ai"}


@router.get("/health/detailed")
async def detailed_health(request: Request):
    orchestrator = request.app.state.orchestrator
    llm_stats = orchestrator.llm_router.get_stats()
    task_stats = orchestrator.task_queue.get_stats()

    return {
        "status": "healthy",
        "service": "nexus-ai",
        "agents": len(orchestrator._agents),
        "active_workflows": len(orchestrator.active_workflows),
        "llm": llm_stats,
        "tasks": task_stats,
    }
