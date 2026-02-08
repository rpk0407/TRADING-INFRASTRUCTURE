"""
SEO Agent — Search Engine Optimization automation.

Capabilities:
- Technical SEO audits
- Keyword research & clustering
- Content optimization
- Link building strategies
- Local SEO
- Schema markup generation
- Competitor SEO analysis
- Performance tracking setup
"""

import json
from typing import Any, Optional

import structlog

from core.agents.base_agent import BaseAgent
from core.llm_router.router import LLMRouter
from core.orchestrator.memory_manager import MemoryManager

logger = structlog.get_logger(__name__)

SEO_SYSTEM_PROMPT = """You are an expert SEO strategist with deep knowledge of
Google's algorithms, technical SEO, content optimization, and link building.
You create actionable, data-driven SEO strategies. Output structured JSON."""


class SEOAgent(BaseAgent):
    def __init__(
        self,
        llm_router: Optional[LLMRouter] = None,
        memory: Optional[MemoryManager] = None,
    ):
        super().__init__(
            agent_id="seo_agent",
            name="SEO Optimizer",
            capabilities=[
                "technical_seo_audit",
                "keyword_research",
                "content_optimization",
                "link_building",
                "local_seo",
                "schema_markup",
                "competitor_seo",
                "seo_reporting",
            ],
            cost_tier=1,
            llm_router=llm_router,
            memory=memory,
        )

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        self._execution_count += 1
        client_id = context["client_id"]
        params = context["workflow_params"]
        previous = context.get("previous_results", {})

        logger.info("seo_agent.starting", client_id=client_id)

        results = {}

        # Keyword research
        results["keywords"] = await self._keyword_research(params)

        # Technical SEO checklist
        results["technical_audit"] = await self._technical_audit(params, previous)

        # On-page optimization
        results["on_page"] = await self._on_page_optimization(
            params, results["keywords"]
        )

        # Schema markup
        results["schema_markup"] = await self._generate_schema(params)

        # Link building strategy
        results["link_building"] = await self._link_building_strategy(params)

        # Local SEO (if applicable)
        if params.get("has_physical_location", False):
            results["local_seo"] = await self._local_seo_strategy(params)

        await self.learn(client_id, {
            "type": "seo_strategy_created",
            "keywords_found": len(results.get("keywords", [])),
        })

        return {
            "status": "success",
            "cost_usd": self._total_cost,
            "seo": results,
        }

    async def _keyword_research(self, params: dict) -> list[dict]:
        prompt = f"""Perform comprehensive keyword research for:

Business: {params.get('business_name', '')}
Industry: {params.get('industry', '')}
Products/Services: {params.get('products', [])}
Location: {params.get('location', 'global')}
Current website: {params.get('website_url', 'new site')}

Return JSON array of 20+ keyword opportunities:
[{{
    "keyword": "keyword phrase",
    "search_volume_estimate": "high|medium|low",
    "competition": "high|medium|low",
    "intent": "informational|commercial|transactional|navigational",
    "difficulty_estimate": "1-10",
    "relevance_score": "1-10",
    "recommended_page": "which page to target",
    "content_type": "blog|landing|product|category",
    "priority": "primary|secondary|long-tail"
}}]"""

        response = await self.think(
            prompt=prompt,
            task_type="seo_optimization",
            system_prompt=SEO_SYSTEM_PROMPT,
            max_tokens=4096,
        )
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return [{"raw": response}]

    async def _technical_audit(self, params: dict, previous: dict) -> dict:
        website_data = previous.get("website_builder", {})

        prompt = f"""Create a technical SEO audit checklist and recommendations for:

Business: {params.get('business_name', '')}
Website Info: {json.dumps(website_data) if isinstance(website_data, dict) else 'new website'}
Tech Stack: {params.get('tech_stack', 'Next.js')}

Return JSON:
{{
    "critical_issues": [
        {{"issue": "description", "impact": "high", "fix": "how to fix"}}
    ],
    "recommendations": [
        {{"area": "speed|mobile|crawlability|indexing|security",
         "recommendation": "what to do",
         "priority": "high|medium|low",
         "implementation": "how to implement"}}
    ],
    "meta_tags_template": {{
        "title_format": "Page Title | Brand - Keyword",
        "description_format": "template with {{variables}}",
        "og_tags": ["required og tags"]
    }},
    "robots_txt": "recommended robots.txt content",
    "sitemap_structure": ["url patterns to include"],
    "page_speed_checklist": ["optimization1", "optimization2"],
    "core_web_vitals_targets": {{
        "LCP": "< 2.5s",
        "FID": "< 100ms",
        "CLS": "< 0.1"
    }}
}}"""

        response = await self.think(
            prompt=prompt,
            task_type="seo_optimization",
            system_prompt=SEO_SYSTEM_PROMPT,
            max_tokens=3072,
        )
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"raw": response}

    async def _on_page_optimization(self, params: dict, keywords: list) -> list[dict]:
        prompt = f"""Create on-page SEO optimization plan for each main page:

Business: {params.get('business_name', '')}
Target Keywords: {json.dumps(keywords[:10]) if isinstance(keywords, list) else keywords}
Pages: {params.get('pages', ['home', 'about', 'services', 'contact'])}

Return JSON array:
[{{
    "page": "page name",
    "primary_keyword": "main keyword",
    "secondary_keywords": ["kw1", "kw2"],
    "title_tag": "optimized title",
    "meta_description": "optimized description (155 chars)",
    "h1": "main heading",
    "h2_suggestions": ["subheading1", "subheading2"],
    "content_outline": ["section1", "section2"],
    "internal_links": ["link to page X"],
    "image_alt_suggestions": ["alt text 1"],
    "word_count_target": 1500
}}]"""

        response = await self.think(
            prompt=prompt,
            task_type="seo_optimization",
            system_prompt=SEO_SYSTEM_PROMPT,
            max_tokens=4096,
        )
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return [{"raw": response}]

    async def _generate_schema(self, params: dict) -> dict:
        prompt = f"""Generate JSON-LD schema markup for:

Business: {params.get('business_name', '')}
Type: {params.get('business_type', 'LocalBusiness')}
Industry: {params.get('industry', '')}
Address: {params.get('address', '')}
Phone: {params.get('phone', '')}

Return JSON with multiple schema types:
{{
    "organization": {{"@context": "...", "@type": "Organization", ...}},
    "local_business": {{"@context": "...", "@type": "LocalBusiness", ...}},
    "website": {{"@context": "...", "@type": "WebSite", ...}},
    "breadcrumb": {{"@context": "...", "@type": "BreadcrumbList", ...}},
    "faq": {{"@context": "...", "@type": "FAQPage", ...}}
}}"""

        response = await self.think(
            prompt=prompt,
            task_type="code_generation",
            system_prompt=SEO_SYSTEM_PROMPT,
        )
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"raw": response}

    async def _link_building_strategy(self, params: dict) -> dict:
        prompt = f"""Create a link building strategy for:

Business: {params.get('business_name', '')}
Industry: {params.get('industry', '')}
Budget: {params.get('seo_budget', 'moderate')}

Return JSON:
{{
    "strategies": [
        {{
            "method": "guest posting|broken link|resource page|PR|partnerships",
            "description": "how to execute",
            "expected_links_per_month": 5,
            "effort": "high|medium|low",
            "quality": "high|medium",
            "timeline": "ongoing|one-time"
        }}
    ],
    "target_domains": ["types of sites to target"],
    "content_for_links": ["content ideas that attract links"],
    "outreach_templates": ["template description"],
    "monthly_targets": {{"links": 10, "referring_domains": 5}}
}}"""

        response = await self.think(
            prompt=prompt,
            task_type="planning",
            system_prompt=SEO_SYSTEM_PROMPT,
        )
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"raw": response}

    async def _local_seo_strategy(self, params: dict) -> dict:
        prompt = f"""Create a local SEO strategy for:

Business: {params.get('business_name', '')}
Location: {params.get('location', '')}
Industry: {params.get('industry', '')}

Return JSON:
{{
    "google_business_profile": {{
        "optimization_checklist": ["item1", "item2"],
        "categories": ["primary", "secondary"],
        "posts_strategy": "how often and what to post"
    }},
    "local_citations": ["directory1", "directory2"],
    "review_strategy": {{
        "platforms": ["google", "yelp"],
        "response_templates": {{"positive": "template", "negative": "template"}},
        "generation_tactics": ["tactic1"]
    }},
    "local_content": ["content type for local relevance"],
    "map_pack_optimization": ["tip1", "tip2"]
}}"""

        response = await self.think(
            prompt=prompt,
            task_type="seo_optimization",
            system_prompt=SEO_SYSTEM_PROMPT,
        )
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"raw": response}
