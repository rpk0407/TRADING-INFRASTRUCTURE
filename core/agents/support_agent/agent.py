"""
Support Agent — Customer support automation and knowledge base creation.

Capabilities:
- FAQ generation from business context
- Support ticket routing logic
- Chatbot conversation flows
- Knowledge base articles
- Escalation procedures
- Response templates
- CSAT optimization
"""

import json
from typing import Any, Optional

import structlog

from core.agents.base_agent import BaseAgent
from core.llm_router.router import LLMRouter
from core.orchestrator.memory_manager import MemoryManager

logger = structlog.get_logger(__name__)

SUPPORT_SYSTEM_PROMPT = """You are a customer support operations expert.
You design support systems that delight customers while minimizing costs.
You create comprehensive knowledge bases, efficient routing, and empathetic
response frameworks. Output structured JSON."""


class SupportAgent(BaseAgent):
    def __init__(
        self,
        llm_router: Optional[LLMRouter] = None,
        memory: Optional[MemoryManager] = None,
    ):
        super().__init__(
            agent_id="support_agent",
            name="Support Automator",
            capabilities=[
                "faq_generation",
                "ticket_routing",
                "chatbot_flows",
                "knowledge_base",
                "escalation_procedures",
                "response_templates",
                "csat_optimization",
            ],
            cost_tier=1,
            llm_router=llm_router,
            memory=memory,
        )

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        self._execution_count += 1
        client_id = context["client_id"]
        params = context["workflow_params"]

        logger.info("support_agent.starting", client_id=client_id)

        results = {}

        # Generate FAQ
        results["faq"] = await self._generate_faq(params)

        # Create chatbot flows
        results["chatbot_flows"] = await self._design_chatbot_flows(params)

        # Browser-test chatbot if a live chatbot URL is provided
        chatbot_url = params.get("chatbot_url")
        if chatbot_url:
            try:
                screenshot = await self.browser.screenshot(chatbot_url)
                metrics = await self.browser.get_page_metrics(chatbot_url)
                results["chatbot_live_test"] = {
                    "url": chatbot_url,
                    "screenshot": screenshot,
                    "performance": metrics,
                    "status": "tested",
                }
                logger.info("support_agent.chatbot_tested", url=chatbot_url)
            except Exception as e:
                logger.warning("support_agent.chatbot_test_failed", url=chatbot_url, error=str(e))
                results["chatbot_live_test"] = {"url": chatbot_url, "status": "failed", "error": str(e)}

        # Response templates
        results["templates"] = await self._create_response_templates(params)

        # Ticket routing rules
        results["routing_rules"] = await self._design_routing(params)

        # Escalation procedures
        results["escalation"] = await self._create_escalation_procedures(params)

        # Knowledge base structure
        results["knowledge_base"] = await self._design_knowledge_base(params)

        await self.learn(client_id, {
            "type": "support_system_designed",
            "faq_count": len(results.get("faq", [])),
            "flows_count": len(results.get("chatbot_flows", [])),
        })

        return {
            "status": "success",
            "cost_usd": self._total_cost,
            "support": results,
        }

    async def _generate_faq(self, params: dict) -> list[dict]:
        prompt = f"""Generate a comprehensive FAQ for:

Business: {params.get('business_name', '')}
Industry: {params.get('industry', '')}
Products/Services: {params.get('products', [])}
Common Issues: {params.get('common_issues', [])}

Return JSON array of 15-20 FAQs organized by category:
[{{
    "category": "General|Pricing|Product|Support|Shipping|Returns",
    "question": "common question",
    "answer": "helpful answer",
    "keywords": ["search keywords"],
    "priority": "high|medium|low",
    "auto_resolvable": true
}}]"""

        response = await self.think(
            prompt=prompt,
            task_type="content_draft",
            system_prompt=SUPPORT_SYSTEM_PROMPT,
            max_tokens=4096,
        )
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return [{"raw": response}]

    async def _design_chatbot_flows(self, params: dict) -> list[dict]:
        prompt = f"""Design chatbot conversation flows for:

Business: {params.get('business_name', '')}
Industry: {params.get('industry', '')}

Create flows for: greeting, product inquiry, support issue, pricing, booking/ordering

Return JSON array:
[{{
    "flow_name": "name",
    "trigger": "what starts this flow",
    "nodes": [
        {{
            "id": "node_1",
            "type": "message|question|condition|action|handoff",
            "content": "what the bot says/does",
            "options": ["option1", "option2"],
            "next": {{"option1": "node_2", "option2": "node_3"}}
        }}
    ],
    "fallback": "what to do if bot can't handle it",
    "resolution_rate_target": "80%"
}}]"""

        response = await self.think(
            prompt=prompt,
            task_type="planning",
            system_prompt=SUPPORT_SYSTEM_PROMPT,
            max_tokens=4096,
        )
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return [{"raw": response}]

    async def _create_response_templates(self, params: dict) -> list[dict]:
        prompt = f"""Create customer support response templates for:

Business: {params.get('business_name', '')}

Categories: greeting, issue acknowledgment, resolution, follow-up,
refund, complaint, positive feedback, escalation

Return JSON array:
[{{
    "name": "template name",
    "category": "category",
    "subject": "email subject if applicable",
    "body": "template text with {{placeholders}}",
    "tone": "empathetic|professional|friendly",
    "use_case": "when to use this template",
    "variables": ["customer_name", "issue_type"]
}}]"""

        response = await self.think(
            prompt=prompt,
            task_type="content_draft",
            system_prompt=SUPPORT_SYSTEM_PROMPT,
            max_tokens=3072,
        )
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return [{"raw": response}]

    async def _design_routing(self, params: dict) -> dict:
        prompt = f"""Design ticket routing rules for:

Business: {params.get('business_name', '')}
Team Size: {params.get('support_team_size', 'small')}

Return JSON:
{{
    "categories": [
        {{
            "name": "category",
            "keywords": ["keyword1", "keyword2"],
            "priority": "urgent|high|normal|low",
            "assigned_to": "team/person",
            "sla_hours": 4,
            "auto_response": true
        }}
    ],
    "priority_rules": [
        {{"condition": "if X", "priority": "urgent", "action": "do Y"}}
    ],
    "business_hours": {{"timezone": "UTC", "hours": "9am-6pm", "days": "Mon-Fri"}},
    "after_hours_handling": "auto-response with expected reply time"
}}"""

        response = await self.think(
            prompt=prompt,
            task_type="planning",
            system_prompt=SUPPORT_SYSTEM_PROMPT,
        )
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"raw": response}

    async def _create_escalation_procedures(self, params: dict) -> dict:
        prompt = f"""Create escalation procedures for:

Business: {params.get('business_name', '')}

Return JSON:
{{
    "escalation_levels": [
        {{
            "level": 1,
            "name": "Frontline Support",
            "handles": ["basic questions", "known issues"],
            "escalation_triggers": ["unresolved after 2 responses", "customer angry"],
            "sla": "4 hours"
        }}
    ],
    "emergency_procedures": {{
        "outage": "steps to take",
        "security_breach": "steps to take",
        "pr_crisis": "steps to take"
    }},
    "customer_sentiment_triggers": {{
        "angry": "immediate escalation to L2",
        "threatening": "escalate to manager + legal"
    }}
}}"""

        response = await self.think(
            prompt=prompt,
            task_type="planning",
            system_prompt=SUPPORT_SYSTEM_PROMPT,
        )
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"raw": response}

    async def _design_knowledge_base(self, params: dict) -> dict:
        prompt = f"""Design a knowledge base structure for:

Business: {params.get('business_name', '')}
Industry: {params.get('industry', '')}

Return JSON:
{{
    "categories": [
        {{
            "name": "category name",
            "subcategories": ["sub1", "sub2"],
            "article_count_target": 10,
            "priority_articles": ["article title 1", "article title 2"]
        }}
    ],
    "search_optimization": {{
        "synonyms": {{"payment": ["billing", "charge", "invoice"]}},
        "suggested_searches": ["common search 1", "common search 2"]
    }},
    "content_guidelines": {{
        "format": "step-by-step with screenshots",
        "tone": "friendly and clear",
        "max_length": "500 words per article",
        "required_sections": ["overview", "steps", "troubleshooting"]
    }},
    "maintenance_schedule": "review all articles quarterly"
}}"""

        response = await self.think(
            prompt=prompt,
            task_type="planning",
            system_prompt=SUPPORT_SYSTEM_PROMPT,
        )
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"raw": response}
