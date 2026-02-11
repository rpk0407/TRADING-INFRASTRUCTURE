"""
NEXUS AI — Main API Server
FastAPI application with REST + WebSocket endpoints.
"""

import asyncio
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import workflows, agents, clients, analytics, health, lifecycle
from api.websockets.events import router as ws_router
from core.orchestrator.nexus import NexusOrchestrator
from config.settings import settings

logger = structlog.get_logger(__name__)

# Global orchestrator instance
orchestrator: NexusOrchestrator | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and shutdown the orchestrator."""
    global orchestrator
    orchestrator = NexusOrchestrator()
    await orchestrator.initialize()
    app.state.orchestrator = orchestrator
    logger.info("api.server_started", port=settings.port)
    yield
    await orchestrator.shutdown()
    logger.info("api.server_stopped")


app = FastAPI(
    title="NEXUS AI — Agentic Workflow Platform",
    description=(
        "Complete AI agent orchestration for business automation. "
        "Websites, marketing, CRM, SEO, analytics — all automated."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure per environment in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REST Routes
app.include_router(health.router, tags=["Health"])
app.include_router(workflows.router, prefix="/api/v1/workflows", tags=["Workflows"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["Agents"])
app.include_router(clients.router, prefix="/api/v1/clients", tags=["Clients"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])
app.include_router(lifecycle.router, prefix="/api/v1/lifecycle", tags=["Lifecycle"])

# WebSocket
app.include_router(ws_router, prefix="/ws")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.server:app",
        host=settings.host,
        port=settings.port,
        workers=settings.workers,
        reload=settings.debug,
    )
