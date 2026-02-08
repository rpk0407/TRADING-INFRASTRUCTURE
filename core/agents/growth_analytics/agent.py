"""
Growth Analytics Agent — Business intelligence and growth prediction.

This is the agent that shows clients their FUTURE — why they'll keep coming back.

Capabilities:
- Revenue forecasting (Prophet time series)
- Churn prediction
- Market opportunity sizing
- Customer lifetime value modeling
- Cohort analysis frameworks
- Growth experiment design
- Unit economics modeling
- Competitive benchmarking
"""

import json
from typing import Any, Optional

import structlog

from core.agents.base_agent import BaseAgent
from core.llm_router.router import LLMRouter
from core.orchestrator.memory_manager import MemoryManager

logger = structlog.get_logger(__name__)

ANALYTICS_SYSTEM_PROMPT = """You are a senior growth analyst and data scientist.
You build predictive models, identify growth levers, and create actionable
business intelligence. You think in terms of unit economics, cohorts, and
compounding growth. Output structured JSON with real numbers."""


class GrowthAnalyticsAgent(BaseAgent):
    def __init__(
        self,
        llm_router: Optional[LLMRouter] = None,
        memory: Optional[MemoryManager] = None,
    ):
        super().__init__(
            agent_id="growth_analytics",
            name="Growth Analytics",
            capabilities=[
                "revenue_forecasting",
                "churn_prediction",
                "market_sizing",
                "ltv_modeling",
                "cohort_analysis",
                "growth_experiments",
                "unit_economics",
                "competitive_benchmarking",
                "kpi_dashboards",
            ],
            cost_tier=2,
            llm_router=llm_router,
            memory=memory,
        )

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        self._execution_count += 1
        client_id = context["client_id"]
        params = context["workflow_params"]
        previous = context.get("previous_results", {})

        logger.info("growth_analytics.starting", client_id=client_id)

        results = {}

        # Market opportunity
        results["market_analysis"] = await self._analyze_market(params)

        # Unit economics model
        results["unit_economics"] = await self._model_unit_economics(params)

        # Growth forecast
        results["growth_forecast"] = await self._forecast_growth(
            params, results["unit_economics"]
        )

        # Growth experiment framework
        results["experiments"] = await self._design_experiments(params, previous)

        # KPI dashboard design
        results["dashboard"] = await self._design_dashboard(params)

        # Actionable growth playbook
        results["growth_playbook"] = await self._create_growth_playbook(
            params, results
        )

        await self.learn(client_id, {
            "type": "growth_analysis_completed",
            "market_size": results.get("market_analysis", {}).get(
                "total_addressable_market"
            ),
            "forecast_months": 12,
        })

        return {
            "status": "success",
            "cost_usd": self._total_cost,
            "analytics": results,
        }

    async def _analyze_market(self, params: dict) -> dict:
        prompt = f"""Analyze the market opportunity for:

Business: {params.get('business_name', '')}
Industry: {params.get('industry', '')}
Products/Services: {params.get('products', [])}
Location: {params.get('location', 'global')}
Current Revenue: {params.get('current_revenue', 'startup')}

Return JSON:
{{
    "total_addressable_market": "$X billion",
    "serviceable_addressable_market": "$X million",
    "serviceable_obtainable_market": "$X million",
    "market_growth_rate": "X% CAGR",
    "market_trends": [
        {{"trend": "description", "impact": "positive|negative", "timeline": "near|mid|long"}}
    ],
    "market_segments": [
        {{"segment": "name", "size": "$X", "growth": "X%", "fit": "high|medium|low"}}
    ],
    "competitive_landscape": {{
        "concentration": "fragmented|moderate|concentrated",
        "barriers_to_entry": "low|medium|high",
        "key_success_factors": ["factor1", "factor2"]
    }},
    "positioning_recommendation": "where to position in the market"
}}"""

        response = await self.think(
            prompt=prompt,
            task_type="growth_prediction",
            system_prompt=ANALYTICS_SYSTEM_PROMPT,
            max_tokens=3072,
        )
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"raw": response}

    async def _model_unit_economics(self, params: dict) -> dict:
        prompt = f"""Build a unit economics model for:

Business: {params.get('business_name', '')}
Business Model: {params.get('business_model', 'subscription/service')}
Average Price: {params.get('avg_price', 'estimate for industry')}
Industry: {params.get('industry', '')}

Return JSON:
{{
    "metrics": {{
        "average_revenue_per_user": "$X/month",
        "customer_acquisition_cost": "$X",
        "lifetime_value": "$X",
        "ltv_cac_ratio": "X:1",
        "gross_margin": "X%",
        "payback_period_months": X,
        "monthly_churn_rate": "X%",
        "average_customer_lifetime_months": X
    }},
    "benchmarks": {{
        "industry_avg_ltv_cac": "X:1",
        "industry_avg_churn": "X%",
        "industry_avg_margin": "X%"
    }},
    "improvement_levers": [
        {{
            "lever": "description",
            "current_estimate": "X",
            "target": "Y",
            "revenue_impact": "+$X/month",
            "difficulty": "easy|medium|hard"
        }}
    ],
    "break_even_analysis": {{
        "customers_needed": X,
        "monthly_revenue_target": "$X",
        "timeline_estimate": "X months"
    }}
}}"""

        response = await self.think(
            prompt=prompt,
            task_type="growth_prediction",
            system_prompt=ANALYTICS_SYSTEM_PROMPT,
            max_tokens=3072,
        )
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"raw": response}

    async def _forecast_growth(self, params: dict, unit_economics: dict) -> dict:
        prompt = f"""Create a 12-month growth forecast for:

Business: {params.get('business_name', '')}
Current State: {params.get('current_state', 'early stage')}
Current Customers: {params.get('current_customers', 0)}
Current MRR: {params.get('current_mrr', '$0')}
Unit Economics: {json.dumps(unit_economics) if isinstance(unit_economics, dict) else unit_economics}
Growth Strategy: {params.get('growth_strategy', 'organic + paid')}

Return JSON with THREE scenarios:
{{
    "conservative": {{
        "monthly_projections": [
            {{"month": 1, "new_customers": X, "churned": X, "total_customers": X,
             "mrr": "$X", "spend": "$X", "net_revenue": "$X"}}
        ],
        "year_end": {{"customers": X, "arr": "$X", "total_spend": "$X", "roi": "X%"}}
    }},
    "moderate": {{
        "monthly_projections": [...],
        "year_end": {{...}}
    }},
    "aggressive": {{
        "monthly_projections": [...],
        "year_end": {{...}}
    }},
    "key_assumptions": ["assumption1", "assumption2"],
    "biggest_risks": ["risk1", "risk2"],
    "growth_milestones": [
        {{"milestone": "first 100 customers", "estimated_month": 3}},
        {{"milestone": "$10K MRR", "estimated_month": 6}}
    ]
}}"""

        response = await self.think(
            prompt=prompt,
            task_type="growth_prediction",
            system_prompt=ANALYTICS_SYSTEM_PROMPT,
            max_tokens=4096,
        )
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"raw": response}

    async def _design_experiments(self, params: dict, previous: dict) -> list[dict]:
        prompt = f"""Design 5 growth experiments prioritized by ICE score:

Business: {params.get('business_name', '')}
Industry: {params.get('industry', '')}
Current channels: {params.get('channels', ['organic', 'paid'])}
Previous results: {json.dumps({k: v.get('status') for k, v in previous.items()}) if previous else 'none'}

Return JSON array sorted by priority:
[{{
    "experiment_name": "name",
    "hypothesis": "If we X, then Y because Z",
    "metric": "primary metric to measure",
    "ice_score": {{
        "impact": 8,
        "confidence": 6,
        "ease": 7,
        "total": 21
    }},
    "implementation": {{
        "steps": ["step1", "step2"],
        "duration": "2 weeks",
        "resources_needed": ["resource1"],
        "estimated_cost": "$X"
    }},
    "success_criteria": "specific measurable outcome",
    "minimum_sample_size": X,
    "expected_lift": "X% improvement in metric"
}}]"""

        response = await self.think(
            prompt=prompt,
            task_type="planning",
            system_prompt=ANALYTICS_SYSTEM_PROMPT,
            max_tokens=4096,
        )
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return [{"raw": response}]

    async def _design_dashboard(self, params: dict) -> dict:
        prompt = f"""Design a KPI dashboard for:

Business: {params.get('business_name', '')}
Business Model: {params.get('business_model', 'subscription')}

Return JSON:
{{
    "dashboard_sections": [
        {{
            "name": "Revenue & Growth",
            "metrics": [
                {{
                    "name": "MRR",
                    "type": "currency",
                    "visualization": "line_chart",
                    "refresh": "daily",
                    "alert_threshold": "< target"
                }}
            ]
        }}
    ],
    "executive_summary_metrics": ["metric1", "metric2", "metric3", "metric4"],
    "data_sources": ["source1", "source2"],
    "refresh_schedule": "real-time for critical, daily for others",
    "access_levels": {{
        "executive": ["all"],
        "manager": ["team metrics"],
        "team": ["individual metrics"]
    }}
}}"""

        response = await self.think(
            prompt=prompt,
            task_type="planning",
            system_prompt=ANALYTICS_SYSTEM_PROMPT,
        )
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"raw": response}

    async def _create_growth_playbook(self, params: dict, analysis: dict) -> dict:
        market = analysis.get("market_analysis", {})
        economics = analysis.get("unit_economics", {})
        forecast = analysis.get("growth_forecast", {})

        prompt = f"""Create an actionable growth playbook based on this analysis:

Business: {params.get('business_name', '')}
Market Opportunity: {json.dumps(market)[:500] if isinstance(market, dict) else 'see above'}
Unit Economics: {json.dumps(economics)[:500] if isinstance(economics, dict) else 'see above'}
Forecast: {json.dumps(forecast)[:500] if isinstance(forecast, dict) else 'see above'}

Return JSON:
{{
    "executive_summary": "2-3 sentence summary of the growth opportunity",
    "immediate_actions": [
        {{"action": "description", "expected_impact": "X%", "timeline": "this week"}}
    ],
    "30_day_plan": [
        {{"week": 1, "focus": "area", "actions": ["action1"], "target": "metric target"}}
    ],
    "90_day_goals": ["goal1", "goal2", "goal3"],
    "scaling_triggers": [
        {{"trigger": "when X happens", "action": "do Y", "rationale": "because Z"}}
    ],
    "resource_requirements": {{
        "people": ["role1", "role2"],
        "tools": ["tool1", "tool2"],
        "budget": "$X/month"
    }},
    "north_star_metric": "the ONE metric to focus on",
    "confidence_level": "high|medium|low",
    "biggest_opportunity": "description of the #1 growth opportunity"
}}"""

        response = await self.think(
            prompt=prompt,
            task_type="planning",
            system_prompt=ANALYTICS_SYSTEM_PROMPT,
            max_tokens=3072,
        )
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"raw": response}
