"""
Workflow API — Create, monitor, and manage AI agent workflows.
"""

from typing import Any, Optional

from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

router = APIRouter()


class WorkflowRequest(BaseModel):
    """Request to create a new workflow."""
    client_id: str = Field(..., description="Client identifier")
    workflow_type: str = Field(
        ...,
        description="Type of workflow",
        examples=[
            "full_setup",
            "website",
            "content",
            "marketing",
            "seo",
            "crm",
            "analytics",
            "support",
            "automation",
        ],
    )
    params: dict[str, Any] = Field(
        default_factory=dict,
        description="Workflow parameters",
        examples=[{
            "business_name": "TechCorp",
            "industry": "SaaS",
            "description": "B2B project management tool",
            "target_audience": "Small to mid-size teams",
            "goals": ["increase signups", "reduce churn"],
        }],
    )


class WorkflowResponse(BaseModel):
    workflow_id: str
    status: str
    message: str


@router.post("/", response_model=WorkflowResponse)
async def create_workflow(
    request: Request,
    workflow: WorkflowRequest,
    background_tasks: BackgroundTasks,
):
    """
    Create and execute a new AI agent workflow.

    The workflow will automatically:
    1. Analyze the client's needs
    2. Select optimal agents
    3. Execute in parallel where possible
    4. Return comprehensive results
    """
    orchestrator = request.app.state.orchestrator

    # Start workflow in background
    async def run_workflow():
        await orchestrator.execute_workflow(
            client_id=workflow.client_id,
            workflow_type=workflow.workflow_type,
            params=workflow.params,
        )

    background_tasks.add_task(run_workflow)

    return WorkflowResponse(
        workflow_id=f"wf_pending_{workflow.client_id}",
        status="accepted",
        message=(
            f"Workflow '{workflow.workflow_type}' queued for client "
            f"'{workflow.client_id}'. Check /workflows/{{id}} for status."
        ),
    )


@router.get("/{workflow_id}")
async def get_workflow(request: Request, workflow_id: str):
    """Get workflow status and results."""
    orchestrator = request.app.state.orchestrator
    workflow = orchestrator.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow.to_dict()


@router.get("/")
async def list_workflows(request: Request, client_id: Optional[str] = None):
    """List all active workflows, optionally filtered by client."""
    orchestrator = request.app.state.orchestrator
    workflows = orchestrator.active_workflows.values()

    if client_id:
        workflows = [w for w in workflows if w.client_id == client_id]

    return {
        "total": len(list(workflows)),
        "workflows": [w.to_dict() for w in workflows],
    }


# ─── Pre-built Workflow Templates ───

WORKFLOW_TEMPLATES = {
    "full_business_setup": {
        "name": "Complete Business Setup",
        "description": "Website + Content + Marketing + CRM + SEO + Analytics",
        "workflow_type": "full_setup",
        "agents_involved": [
            "website_builder", "content_engine", "marketing_agent",
            "crm_agent", "seo_agent", "growth_analytics",
            "support_agent", "business_automation",
        ],
        "estimated_time": "15-30 minutes",
        "required_params": ["business_name", "industry", "description"],
    },
    "website_launch": {
        "name": "Website Launch Package",
        "description": "Build + SEO optimize + Deploy a complete website",
        "workflow_type": "website",
        "agents_involved": ["website_builder", "seo_agent", "content_engine"],
        "estimated_time": "10-15 minutes",
        "required_params": ["business_name", "industry", "description"],
    },
    "growth_package": {
        "name": "Growth Acceleration",
        "description": "Analytics + Marketing + CRM optimization",
        "workflow_type": "growth",
        "agents_involved": [
            "growth_analytics", "marketing_agent", "crm_agent",
        ],
        "estimated_time": "10-20 minutes",
        "required_params": ["business_name", "industry", "current_revenue"],
    },
    "content_blitz": {
        "name": "Content Marketing Blitz",
        "description": "Full content strategy + calendar + initial assets",
        "workflow_type": "content",
        "agents_involved": ["content_engine", "seo_agent", "marketing_agent"],
        "estimated_time": "10-15 minutes",
        "required_params": ["business_name", "industry", "target_audience"],
    },
    "operations_overhaul": {
        "name": "Operations Automation",
        "description": "Process audit + Workflow automation + Integration plan",
        "workflow_type": "automation",
        "agents_involved": [
            "business_automation", "support_agent", "crm_agent",
        ],
        "estimated_time": "10-15 minutes",
        "required_params": ["business_name", "industry", "pain_points"],
    },
}


@router.get("/templates/all")
async def get_workflow_templates():
    """Get all available pre-built workflow templates."""
    return {
        "templates": WORKFLOW_TEMPLATES,
        "total": len(WORKFLOW_TEMPLATES),
    }
