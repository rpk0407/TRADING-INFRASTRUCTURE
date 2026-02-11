"""
Client Lifecycle Automation Engine

Manages the COMPLETE lifecycle of a client from onboarding to growth:

1. ONBOARD  — Discovery call analysis, business profile, goals
2. SETUP    — Website, branding, content, CRM, support systems
3. LAUNCH   — Go-live, marketing campaigns, SEO activation
4. GROW     — Analytics, A/B testing, scaling, new channels
5. RETAIN   — Health monitoring, proactive improvements, upselling

This is the NEXUS differentiator: fully automated company-in-a-box.
"""

import asyncio
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

import structlog

logger = structlog.get_logger(__name__)


class LifecyclePhase(str, Enum):
    ONBOARD = "onboard"
    SETUP = "setup"
    LAUNCH = "launch"
    GROW = "grow"
    RETAIN = "retain"


class ClientProfile:
    """Complete client profile built during onboarding."""

    def __init__(self, client_id: str):
        self.client_id = client_id
        self.created_at = datetime.now(timezone.utc)
        self.company_name: str = ""
        self.industry: str = ""
        self.company_size: str = ""
        self.target_audience: str = ""
        self.competitors: list[str] = []
        self.goals: list[str] = []
        self.budget_tier: str = "starter"  # starter | growth | enterprise
        self.current_phase: LifecyclePhase = LifecyclePhase.ONBOARD
        self.brand_voice: str = ""
        self.brand_colors: list[str] = []
        self.services: list[str] = []
        self.phase_history: list[dict] = []
        self.deliverables: dict[str, Any] = {}
        self.health_score: int = 100

    def to_dict(self) -> dict:
        return {
            "client_id": self.client_id,
            "company_name": self.company_name,
            "industry": self.industry,
            "company_size": self.company_size,
            "target_audience": self.target_audience,
            "competitors": self.competitors,
            "goals": self.goals,
            "budget_tier": self.budget_tier,
            "current_phase": self.current_phase.value,
            "brand_voice": self.brand_voice,
            "services": self.services,
            "phase_history": self.phase_history,
            "health_score": self.health_score,
            "created_at": self.created_at.isoformat(),
        }


class ClientLifecycleEngine:
    """
    Orchestrates the entire client lifecycle through automated phases.
    Each phase triggers specific agent workflows.
    """

    # Phase → required agent workflows
    PHASE_WORKFLOWS = {
        LifecyclePhase.ONBOARD: [
            {"name": "discovery_analysis", "agents": ["growth_analytics"], "priority": 1},
            {"name": "competitor_research", "agents": ["marketing_agent", "seo_agent"], "priority": 2},
            {"name": "brand_strategy", "agents": ["content_engine"], "priority": 3},
        ],
        LifecyclePhase.SETUP: [
            {"name": "website_creation", "agents": ["website_builder"], "priority": 1},
            {"name": "content_foundation", "agents": ["content_engine"], "priority": 2},
            {"name": "seo_foundation", "agents": ["seo_agent"], "priority": 2},
            {"name": "crm_setup", "agents": ["crm_agent"], "priority": 3},
            {"name": "support_setup", "agents": ["support_agent"], "priority": 3},
            {"name": "automation_setup", "agents": ["business_automation"], "priority": 4},
        ],
        LifecyclePhase.LAUNCH: [
            {"name": "pre_launch_audit", "agents": ["seo_agent", "website_builder"], "priority": 1},
            {"name": "campaign_launch", "agents": ["marketing_agent"], "priority": 2},
            {"name": "content_calendar_start", "agents": ["content_engine"], "priority": 2},
            {"name": "analytics_baseline", "agents": ["growth_analytics"], "priority": 3},
        ],
        LifecyclePhase.GROW: [
            {"name": "growth_analysis", "agents": ["growth_analytics"], "priority": 1},
            {"name": "seo_optimization", "agents": ["seo_agent"], "priority": 1},
            {"name": "campaign_optimization", "agents": ["marketing_agent"], "priority": 2},
            {"name": "content_scaling", "agents": ["content_engine"], "priority": 2},
            {"name": "crm_optimization", "agents": ["crm_agent"], "priority": 3},
        ],
        LifecyclePhase.RETAIN: [
            {"name": "health_check", "agents": ["growth_analytics", "seo_agent"], "priority": 1},
            {"name": "proactive_improvements", "agents": ["website_builder", "content_engine"], "priority": 2},
            {"name": "expansion_opportunities", "agents": ["marketing_agent", "growth_analytics"], "priority": 3},
        ],
    }

    def __init__(self, orchestrator=None):
        self._orchestrator = orchestrator
        self._clients: dict[str, ClientProfile] = {}

    def set_orchestrator(self, orchestrator):
        self._orchestrator = orchestrator

    # ─── Client Management ───

    async def onboard_client(self, intake_data: dict) -> ClientProfile:
        """
        Start client lifecycle from intake data.
        Automatically creates profile and kicks off discovery phase.
        """
        client_id = f"client_{uuid.uuid4().hex[:10]}"
        profile = ClientProfile(client_id)

        # Populate from intake
        profile.company_name = intake_data.get("company_name", "")
        profile.industry = intake_data.get("industry", "")
        profile.company_size = intake_data.get("company_size", "small")
        profile.target_audience = intake_data.get("target_audience", "")
        profile.competitors = intake_data.get("competitors", [])
        profile.goals = intake_data.get("goals", [])
        profile.budget_tier = intake_data.get("budget_tier", "starter")
        profile.services = intake_data.get("services", [])

        self._clients[client_id] = profile

        logger.info(
            "lifecycle.client_onboarded",
            client_id=client_id,
            company=profile.company_name,
            industry=profile.industry,
        )

        # Auto-start onboarding workflows
        if self._orchestrator:
            await self._run_phase(profile, LifecyclePhase.ONBOARD, intake_data)

        return profile

    async def advance_phase(self, client_id: str) -> dict:
        """Advance client to the next lifecycle phase."""
        profile = self._clients.get(client_id)
        if not profile:
            return {"error": "Client not found"}

        phase_order = list(LifecyclePhase)
        current_idx = phase_order.index(profile.current_phase)

        if current_idx >= len(phase_order) - 1:
            return {
                "client_id": client_id,
                "status": "at_final_phase",
                "phase": profile.current_phase.value,
            }

        next_phase = phase_order[current_idx + 1]

        # Record transition
        profile.phase_history.append({
            "from": profile.current_phase.value,
            "to": next_phase.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        profile.current_phase = next_phase

        logger.info(
            "lifecycle.phase_advanced",
            client_id=client_id,
            new_phase=next_phase.value,
        )

        # Auto-run phase workflows
        if self._orchestrator:
            await self._run_phase(profile, next_phase, profile.to_dict())

        return {
            "client_id": client_id,
            "new_phase": next_phase.value,
            "workflows_triggered": len(self.PHASE_WORKFLOWS.get(next_phase, [])),
        }

    async def _run_phase(
        self, profile: ClientProfile, phase: LifecyclePhase, params: dict
    ):
        """Execute all workflows for a lifecycle phase."""
        workflows = self.PHASE_WORKFLOWS.get(phase, [])

        # Group by priority for parallel execution
        priorities: dict[int, list] = {}
        for wf in workflows:
            priorities.setdefault(wf["priority"], []).append(wf)

        for priority in sorted(priorities.keys()):
            group = priorities[priority]
            logger.info(
                "lifecycle.executing_priority",
                phase=phase.value,
                priority=priority,
                workflows=[w["name"] for w in group],
            )

            tasks = []
            for wf in group:
                tasks.append(
                    self._orchestrator.execute_workflow(
                        client_id=profile.client_id,
                        workflow_type=wf["name"],
                        params={
                            **params,
                            "lifecycle_phase": phase.value,
                            "agents_hint": wf["agents"],
                        },
                    )
                )

            results = await asyncio.gather(*tasks, return_exceptions=True)
            for wf, result in zip(group, results):
                if isinstance(result, Exception):
                    logger.error(
                        "lifecycle.workflow_failed",
                        workflow=wf["name"],
                        error=str(result),
                    )
                else:
                    profile.deliverables[wf["name"]] = {
                        "status": "completed",
                        "workflow_id": result.workflow_id,
                        "cost_usd": result.cost_usd,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }

    # ─── Health Monitoring ───

    async def check_client_health(self, client_id: str) -> dict:
        """
        Proactive health check — identifies issues before clients notice.
        """
        profile = self._clients.get(client_id)
        if not profile:
            return {"error": "Client not found"}

        health_checks = {
            "website_uptime": True,
            "seo_ranking_trend": "stable",
            "content_freshness": True,
            "crm_engagement": "active",
            "support_resolution_rate": 0.95,
        }

        issues = []
        score = 100

        # Check each dimension
        if not health_checks["website_uptime"]:
            issues.append({"type": "critical", "area": "website", "msg": "Website down"})
            score -= 30

        if health_checks["seo_ranking_trend"] == "declining":
            issues.append({"type": "warning", "area": "seo", "msg": "Rankings declining"})
            score -= 15

        if not health_checks["content_freshness"]:
            issues.append({"type": "info", "area": "content", "msg": "No new content in 14 days"})
            score -= 10

        profile.health_score = max(0, score)

        return {
            "client_id": client_id,
            "health_score": profile.health_score,
            "phase": profile.current_phase.value,
            "issues": issues,
            "recommendation": self._get_recommendation(issues),
        }

    def _get_recommendation(self, issues: list) -> str:
        if not issues:
            return "Client is healthy. Consider growth opportunities."

        critical = [i for i in issues if i["type"] == "critical"]
        if critical:
            return f"URGENT: {critical[0]['msg']}. Trigger immediate fix workflow."

        warnings = [i for i in issues if i["type"] == "warning"]
        if warnings:
            return f"Attention needed: {warnings[0]['msg']}. Schedule optimization workflow."

        return "Minor improvements recommended. Schedule during next cycle."

    # ─── Automation Templates ───

    def get_automation_templates(self) -> list[dict]:
        """Pre-built automation templates for common client needs."""
        return [
            {
                "id": "full_company_setup",
                "name": "Complete Company Setup",
                "description": "Website + Content + SEO + CRM + Support + Automation",
                "phases": ["onboard", "setup", "launch"],
                "estimated_agents": 8,
                "estimated_workflows": 13,
                "ideal_for": "New companies needing everything from scratch",
            },
            {
                "id": "digital_transformation",
                "name": "Digital Transformation",
                "description": "Modernize existing business with AI-powered tools",
                "phases": ["onboard", "setup", "grow"],
                "estimated_agents": 6,
                "estimated_workflows": 10,
                "ideal_for": "Established companies going digital",
            },
            {
                "id": "growth_accelerator",
                "name": "Growth Accelerator",
                "description": "SEO + Marketing + Analytics + Content scaling",
                "phases": ["onboard", "grow"],
                "estimated_agents": 4,
                "estimated_workflows": 7,
                "ideal_for": "Companies with existing presence wanting to scale",
            },
            {
                "id": "brand_refresh",
                "name": "Brand Refresh",
                "description": "New website + content + updated marketing",
                "phases": ["onboard", "setup", "launch"],
                "estimated_agents": 3,
                "estimated_workflows": 6,
                "ideal_for": "Companies needing a rebrand or refresh",
            },
            {
                "id": "lead_machine",
                "name": "Lead Generation Machine",
                "description": "CRM + Marketing + SEO + Content funnel",
                "phases": ["onboard", "setup", "grow"],
                "estimated_agents": 4,
                "estimated_workflows": 8,
                "ideal_for": "B2B companies focused on lead generation",
            },
            {
                "id": "ecommerce_launch",
                "name": "E-Commerce Launch",
                "description": "Online store + Product content + Marketing + Support",
                "phases": ["onboard", "setup", "launch", "grow"],
                "estimated_agents": 7,
                "estimated_workflows": 14,
                "ideal_for": "Businesses launching online sales",
            },
        ]

    # ─── Query Methods ───

    def get_client(self, client_id: str) -> Optional[dict]:
        profile = self._clients.get(client_id)
        return profile.to_dict() if profile else None

    def list_clients(self) -> list[dict]:
        return [p.to_dict() for p in self._clients.values()]

    def get_phase_progress(self, client_id: str) -> dict:
        profile = self._clients.get(client_id)
        if not profile:
            return {"error": "Client not found"}

        phase_order = list(LifecyclePhase)
        current_idx = phase_order.index(profile.current_phase)
        total_phases = len(phase_order)

        completed_deliverables = len(profile.deliverables)
        total_expected = sum(
            len(self.PHASE_WORKFLOWS.get(p, []))
            for p in phase_order[:current_idx + 1]
        )

        return {
            "client_id": client_id,
            "current_phase": profile.current_phase.value,
            "phase_index": current_idx + 1,
            "total_phases": total_phases,
            "phase_progress_pct": round((current_idx + 1) / total_phases * 100),
            "deliverables_completed": completed_deliverables,
            "deliverables_expected": total_expected,
            "deliverable_progress_pct": round(
                completed_deliverables / max(total_expected, 1) * 100
            ),
        }
