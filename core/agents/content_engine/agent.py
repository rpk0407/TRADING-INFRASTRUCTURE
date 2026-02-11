"""
Content Engine Agent — AI-powered content creation at scale.

Generates:
- Blog posts & articles
- Product descriptions
- Email campaigns & sequences
- Social media content calendars
- Landing page copy
- Video scripts
- Ad copy (Google, Meta, LinkedIn)
- Press releases
"""

import json
from typing import Any, Optional

import structlog

from core.agents.base_agent import BaseAgent
from core.llm_router.router import LLMRouter
from core.orchestrator.memory_manager import MemoryManager

logger = structlog.get_logger(__name__)

CONTENT_SYSTEM_PROMPT = """You are an expert content strategist and copywriter.
You create compelling, conversion-optimized content that drives business results.
You understand SEO, brand voice, and audience psychology deeply.
Always output structured JSON when asked."""


class ContentEngineAgent(BaseAgent):
    def __init__(
        self,
        llm_router: Optional[LLMRouter] = None,
        memory: Optional[MemoryManager] = None,
    ):
        super().__init__(
            agent_id="content_engine",
            name="Content Engine",
            capabilities=[
                "blog_writing",
                "email_campaigns",
                "social_media_content",
                "product_descriptions",
                "ad_copy",
                "landing_page_copy",
                "video_scripts",
                "press_releases",
                "content_calendar",
                "brand_voice",
            ],
            cost_tier=1,
            llm_router=llm_router,
            memory=memory,
        )

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        self._execution_count += 1
        client_id = context["client_id"]
        params = context["workflow_params"]
        client_memory = context.get("client_memory", {})

        content_type = params.get("content_type", "full_strategy")
        logger.info(
            "content_engine.starting",
            client_id=client_id,
            content_type=content_type,
        )

        results = {}

        if content_type in ("full_strategy", "brand_voice"):
            results["brand_voice"] = await self._develop_brand_voice(
                params, client_memory
            )

        if content_type in ("full_strategy", "content_calendar"):
            results["content_calendar"] = await self._create_content_calendar(
                params, client_memory, results.get("brand_voice")
            )

        if content_type in ("full_strategy", "blog"):
            results["blog_posts"] = await self._generate_blog_posts(
                params, client_memory, results.get("brand_voice")
            )

        if content_type in ("full_strategy", "email"):
            results["email_sequences"] = await self._create_email_sequences(
                params, client_memory, results.get("brand_voice")
            )

        if content_type in ("full_strategy", "social"):
            results["social_content"] = await self._create_social_content(
                params, client_memory, results.get("brand_voice")
            )

        if content_type in ("full_strategy", "ads"):
            results["ad_copy"] = await self._generate_ad_copy(
                params, client_memory, results.get("brand_voice")
            )

        await self.learn(client_id, {
            "type": "content_generated",
            "content_types": list(results.keys()),
            "brand_voice_established": "brand_voice" in results,
        })

        return {
            "status": "success",
            "cost_usd": self._total_cost,
            "content": results,
            "pieces_generated": sum(
                len(v) if isinstance(v, list) else 1 for v in results.values()
            ),
        }

    async def _develop_brand_voice(self, params: dict, memory: dict) -> dict:
        """Develop a consistent brand voice guide."""
        prompt = f"""Create a comprehensive brand voice guide for this business:

Business: {params.get('business_name', '')}
Industry: {params.get('industry', '')}
Target Audience: {params.get('target_audience', '')}
Values: {params.get('values', [])}
Differentiators: {params.get('differentiators', [])}

Return JSON:
{{
    "tone": "description of overall tone",
    "personality_traits": ["trait1", "trait2", ...],
    "vocabulary": {{
        "use": ["words to use"],
        "avoid": ["words to avoid"]
    }},
    "writing_rules": ["rule1", "rule2", ...],
    "example_sentences": ["example1", "example2", ...],
    "tagline_options": ["tagline1", "tagline2", "tagline3"]
}}"""

        response = await self.think(
            prompt=prompt,
            task_type="content_draft",
            system_prompt=CONTENT_SYSTEM_PROMPT,
        )
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"tone": "professional and approachable", "raw": response}

    async def _create_content_calendar(
        self, params: dict, memory: dict, brand_voice: Optional[dict]
    ) -> list[dict]:
        """Generate a 30-day content calendar."""
        prompt = f"""Create a 30-day content calendar for:

Business: {params.get('business_name', '')}
Industry: {params.get('industry', '')}
Brand Voice: {json.dumps(brand_voice) if brand_voice else 'professional'}
Goals: {params.get('goals', ['brand awareness', 'lead generation'])}
Platforms: {params.get('platforms', ['blog', 'linkedin', 'twitter', 'instagram'])}

Return a JSON array of 30 daily content plans:
[{{
    "day": 1,
    "platform": "blog",
    "content_type": "article",
    "topic": "topic title",
    "headline": "compelling headline",
    "key_points": ["point1", "point2"],
    "cta": "call to action",
    "hashtags": ["#tag1", "#tag2"]
}}]"""

        response = await self.think(
            prompt=prompt,
            task_type="content_draft",
            system_prompt=CONTENT_SYSTEM_PROMPT,
            max_tokens=4096,
        )
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return [{"raw": response}]

    async def _generate_blog_posts(
        self, params: dict, memory: dict, brand_voice: Optional[dict]
    ) -> list[dict]:
        """Generate SEO-optimized blog post outlines and first drafts."""
        topics = params.get("blog_topics", [])
        if not topics:
            # Auto-generate topics
            topic_prompt = f"""Generate 5 high-value blog post topics for:
Business: {params.get('business_name', '')}
Industry: {params.get('industry', '')}
Target Audience: {params.get('target_audience', '')}

Return JSON array: ["topic1", "topic2", ...]"""
            resp = await self.think(prompt=topic_prompt, task_type="content_draft")
            try:
                topics = json.loads(resp)
            except json.JSONDecodeError:
                topics = ["Industry Trends", "How-To Guide", "Case Study"]

        # Research: scrape reference URLs if provided for deeper topic insights
        research_urls = params.get("research_urls", [])
        research_data = []
        if research_urls:
            fetched = await self.scraper.fetch_multiple(research_urls, extract_mode="text")
            for page in fetched:
                research_data.append({
                    "url": page.get("url"),
                    "title": page.get("title"),
                    "snippet": (page.get("text", "") or "")[:500],
                })

        posts = []
        for topic in topics[:3]:
            # Find topic-relevant research snippets
            topic_research = [r for r in research_data if topic.lower() in (r.get("title", "") or "").lower() or topic.lower() in (r.get("snippet", "") or "").lower()]
            prompt = f"""Write a comprehensive, SEO-optimized blog post about: {topic}

Business: {params.get('business_name', '')}
Brand Voice: {json.dumps(brand_voice) if brand_voice else 'professional'}
Target Length: 1500-2000 words
Research Data: {json.dumps(topic_research) if topic_research else json.dumps(research_data[:2]) if research_data else 'none available'}

Return JSON:
{{
    "title": "SEO-optimized title",
    "meta_description": "155 char meta description",
    "slug": "url-friendly-slug",
    "outline": ["section1", "section2", ...],
    "content": "Full article in markdown",
    "keywords": ["primary keyword", "secondary keywords"],
    "internal_links_suggested": ["topic1", "topic2"]
}}"""

            result = await self.think_with_reflection(
                prompt=prompt,
                task_description=f"Write a high-quality SEO blog post about: {topic}",
                task_type="content_final",
                system_prompt=CONTENT_SYSTEM_PROMPT,
                quality_threshold=75,
            )
            final_content = result.get("final_output", result.get("original_output", ""))
            try:
                posts.append(json.loads(final_content))
            except json.JSONDecodeError:
                posts.append({"title": topic, "content": final_content})

        return posts

    async def _create_email_sequences(
        self, params: dict, memory: dict, brand_voice: Optional[dict]
    ) -> list[dict]:
        """Generate email marketing sequences."""
        prompt = f"""Create a 5-email welcome/nurture sequence for:

Business: {params.get('business_name', '')}
Industry: {params.get('industry', '')}
Goal: {params.get('email_goal', 'convert leads to customers')}
Brand Voice: {json.dumps(brand_voice) if brand_voice else 'professional'}

Return JSON array:
[{{
    "email_number": 1,
    "subject_line": "compelling subject",
    "preview_text": "preview text",
    "body_html": "email body with HTML formatting",
    "cta_text": "button text",
    "cta_url_placeholder": "/link",
    "send_delay_days": 0
}}]"""

        response = await self.think(
            prompt=prompt,
            task_type="content_final",
            system_prompt=CONTENT_SYSTEM_PROMPT,
            max_tokens=4096,
        )
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return [{"raw": response}]

    async def _create_social_content(
        self, params: dict, memory: dict, brand_voice: Optional[dict]
    ) -> dict:
        """Generate social media content for multiple platforms."""
        prompt = f"""Create a week of social media content for:

Business: {params.get('business_name', '')}
Industry: {params.get('industry', '')}
Brand Voice: {json.dumps(brand_voice) if brand_voice else 'professional'}
Platforms: {params.get('platforms', ['linkedin', 'twitter', 'instagram'])}

Return JSON:
{{
    "linkedin": [
        {{"text": "post text", "hashtags": ["#tag"], "best_time": "Tuesday 10am"}}
    ],
    "twitter": [
        {{"text": "tweet text (under 280 chars)", "hashtags": ["#tag"]}}
    ],
    "instagram": [
        {{"caption": "caption text", "hashtags": ["#tag"], "image_description": "what image to create"}}
    ]
}}"""

        response = await self.think(
            prompt=prompt,
            task_type="content_draft",
            system_prompt=CONTENT_SYSTEM_PROMPT,
            max_tokens=4096,
        )
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"raw": response}

    async def _generate_ad_copy(
        self, params: dict, memory: dict, brand_voice: Optional[dict]
    ) -> dict:
        """Generate ad copy for multiple platforms."""
        prompt = f"""Create ad copy variations for:

Business: {params.get('business_name', '')}
Industry: {params.get('industry', '')}
Product/Service: {params.get('product', '')}
Target Audience: {params.get('target_audience', '')}
Budget Range: {params.get('ad_budget', 'moderate')}

Return JSON:
{{
    "google_ads": [
        {{
            "headline1": "30 chars max",
            "headline2": "30 chars max",
            "headline3": "30 chars max",
            "description1": "90 chars max",
            "description2": "90 chars max",
            "keywords": ["keyword1", "keyword2"]
        }}
    ],
    "meta_ads": [
        {{
            "primary_text": "ad text",
            "headline": "headline",
            "description": "link description",
            "cta": "Learn More|Sign Up|Shop Now"
        }}
    ],
    "linkedin_ads": [
        {{
            "intro_text": "ad text",
            "headline": "headline",
            "description": "description"
        }}
    ]
}}"""

        response = await self.think(
            prompt=prompt,
            task_type="content_final",
            system_prompt=CONTENT_SYSTEM_PROMPT,
            max_tokens=3072,
        )
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"raw": response}
