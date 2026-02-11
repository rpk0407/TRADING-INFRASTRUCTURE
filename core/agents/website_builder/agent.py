"""
Website Builder Agent — Generates complete, deployable websites from business descriptions.

Capabilities:
- Full website generation (React, Next.js, static HTML/CSS)
- Component-based architecture
- Responsive design with modern aesthetics
- SEO-ready structure
- CMS integration
- One-click deployment (Vercel, Netlify, Cloudflare Pages)
"""

import json
import os
from typing import Any, Optional
from pathlib import Path

import structlog

from core.agents.base_agent import BaseAgent
from core.llm_router.router import LLMRouter
from core.orchestrator.memory_manager import MemoryManager
from config.settings import settings

logger = structlog.get_logger(__name__)

WEBSITE_SYSTEM_PROMPT = """You are an expert website architect and developer.
You create modern, responsive, high-converting websites.
Your designs are clean, professional, and optimized for performance and SEO.
You output structured JSON with all website components."""


class WebsiteBuilderAgent(BaseAgent):
    def __init__(
        self,
        llm_router: Optional[LLMRouter] = None,
        memory: Optional[MemoryManager] = None,
    ):
        super().__init__(
            agent_id="website_builder",
            name="Website Builder",
            capabilities=[
                "website_generation",
                "landing_page",
                "ecommerce_site",
                "portfolio_site",
                "corporate_site",
                "blog_setup",
                "responsive_design",
                "deployment",
            ],
            cost_tier=1,
            llm_router=llm_router,
            memory=memory,
        )

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """Generate a complete website from client parameters."""
        self._execution_count += 1
        client_id = context["client_id"]
        params = context["workflow_params"]
        client_memory = context.get("client_memory", {})

        logger.info("website_builder.starting", client_id=client_id)

        # Step 1: Analyze requirements
        site_plan = await self._plan_website(params, client_memory)

        # Step 2: Generate site structure
        structure = await self._generate_structure(site_plan)

        # Step 3: Generate pages
        pages = await self._generate_pages(site_plan, structure)

        # Step 4: Generate styles
        styles = await self._generate_styles(site_plan)

        # Step 5: Generate components
        components = await self._generate_components(site_plan)

        # Step 6: Write files to output directory
        output_path = await self._write_website(
            client_id, structure, pages, styles, components
        )

        # Step 6b: Validate generated code for syntax errors
        validation = await self._validate_generated_code(pages, components)

        # Step 7: Learn from this generation
        await self.learn(client_id, {
            "type": "website_generated",
            "site_type": site_plan.get("site_type"),
            "pages": len(pages),
            "style_preference": site_plan.get("style"),
        })

        return {
            "status": "success",
            "cost_usd": self._total_cost,
            "output_path": str(output_path),
            "site_plan": site_plan,
            "pages_generated": len(pages),
            "components_generated": len(components),
            "validation": validation,
            "deployment_ready": validation.get("all_valid", False),
        }

    async def _plan_website(self, params: dict, memory: dict) -> dict:
        """Analyze client needs and create a detailed website plan."""
        brand = memory.get("brand", {})
        industry = memory.get("industry", "")

        prompt = f"""Analyze this client's website requirements and create a detailed plan.

CLIENT INFO:
Business Name: {params.get('business_name', 'Unknown')}
Industry: {params.get('industry', industry)}
Description: {params.get('description', '')}
Target Audience: {params.get('target_audience', '')}
Goals: {params.get('goals', [])}
Brand Colors: {brand.get('colors', params.get('colors', ''))}
Style Preference: {params.get('style', 'modern professional')}
Features Requested: {params.get('features', [])}

Return a JSON object with:
{{
    "site_type": "corporate|ecommerce|portfolio|blog|landing|saas",
    "pages": ["home", "about", "services", ...],
    "style": {{
        "primary_color": "#hex",
        "secondary_color": "#hex",
        "accent_color": "#hex",
        "font_heading": "font name",
        "font_body": "font name",
        "layout": "modern|classic|minimal|bold"
    }},
    "components": ["hero", "features", "testimonials", "cta", ...],
    "seo_keywords": ["keyword1", "keyword2", ...],
    "tech_stack": "nextjs|react|static",
    "features": ["contact_form", "blog", "analytics", ...]
}}

Return ONLY valid JSON."""

        response = await self.think(
            prompt=prompt,
            task_type="website_structure",
            system_prompt=WEBSITE_SYSTEM_PROMPT,
            max_tokens=2048,
        )

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "site_type": "corporate",
                "pages": ["home", "about", "services", "contact"],
                "style": {
                    "primary_color": "#2563eb",
                    "secondary_color": "#1e40af",
                    "accent_color": "#f59e0b",
                    "font_heading": "Inter",
                    "font_body": "Inter",
                    "layout": "modern",
                },
                "components": ["hero", "features", "testimonials", "cta", "footer"],
                "tech_stack": "nextjs",
                "features": ["contact_form", "analytics"],
            }

    async def _generate_structure(self, plan: dict) -> dict:
        """Generate the file/folder structure for the website."""
        tech = plan.get("tech_stack", "nextjs")

        if tech == "nextjs":
            return {
                "type": "nextjs",
                "files": {
                    "package.json": True,
                    "next.config.js": True,
                    "tailwind.config.js": True,
                    "tsconfig.json": True,
                    "app/layout.tsx": True,
                    "app/page.tsx": True,
                    "app/globals.css": True,
                },
                "pages": {f"app/{p}/page.tsx": True for p in plan.get("pages", []) if p != "home"},
                "components": {f"components/{c}.tsx": True for c in plan.get("components", [])},
            }
        else:
            return {
                "type": "static",
                "files": {
                    "index.html": True,
                    "styles/main.css": True,
                    "scripts/main.js": True,
                },
                "pages": {f"{p}.html": True for p in plan.get("pages", []) if p != "home"},
            }

    async def _generate_pages(self, plan: dict, structure: dict) -> dict[str, str]:
        """Generate code for each page."""
        pages = {}

        for page_name in plan.get("pages", ["home"]):
            prompt = f"""Generate a complete, production-ready page component for a {plan.get('site_type')} website.

PAGE: {page_name}
SITE PLAN: {json.dumps(plan, indent=2)}

Requirements:
- Use {'Next.js 14 App Router with TypeScript and Tailwind CSS' if structure['type'] == 'nextjs' else 'semantic HTML5 with modern CSS'}
- Make it responsive (mobile-first)
- Include proper heading hierarchy for SEO
- Use the brand colors: {plan.get('style', {})}
- Make it visually stunning and conversion-optimized
- Include realistic placeholder content relevant to the industry

Return ONLY the code, no markdown fences."""

            code = await self.think_code(
                prompt=prompt,
                system_prompt=WEBSITE_SYSTEM_PROMPT,
                max_tokens=4096,
                temperature=0.6,
            )
            pages[page_name] = code

        return pages

    async def _generate_styles(self, plan: dict) -> str:
        """Generate the global stylesheet."""
        style = plan.get("style", {})
        prompt = f"""Generate a complete Tailwind CSS configuration and global styles for:

Style Config: {json.dumps(style)}
Site Type: {plan.get('site_type')}
Layout: {style.get('layout', 'modern')}

Include:
- Custom color palette based on brand colors
- Typography scale
- Animation utilities
- Dark mode support
- Custom component classes

Return the CSS code only, no markdown fences."""

        return await self.think(
            prompt=prompt,
            task_type="code_generation",
            system_prompt=WEBSITE_SYSTEM_PROMPT,
            max_tokens=2048,
        )

    async def _generate_components(self, plan: dict) -> dict[str, str]:
        """Generate reusable UI components."""
        components = {}

        for comp_name in plan.get("components", []):
            prompt = f"""Generate a reusable React/Next.js component: {comp_name}

Site Type: {plan.get('site_type')}
Style: {json.dumps(plan.get('style', {}))}

Requirements:
- TypeScript with proper interfaces
- Tailwind CSS for styling
- Accessible (ARIA attributes)
- Responsive
- Animated with smooth transitions
- Include realistic placeholder content

Return ONLY the TypeScript/React code, no markdown."""

            code = await self.think_code(
                prompt=prompt,
                system_prompt=WEBSITE_SYSTEM_PROMPT,
                max_tokens=2048,
                temperature=0.6,
            )
            components[comp_name] = code

        return components

    async def _write_website(
        self,
        client_id: str,
        structure: dict,
        pages: dict[str, str],
        styles: str,
        components: dict[str, str],
    ) -> Path:
        """Write all generated files to the output directory."""
        output_dir = Path(settings.website_output_dir) / client_id
        output_dir.mkdir(parents=True, exist_ok=True)

        # Write pages
        for page_name, code in pages.items():
            if structure["type"] == "nextjs":
                if page_name == "home":
                    file_path = output_dir / "app" / "page.tsx"
                else:
                    file_path = output_dir / "app" / page_name / "page.tsx"
            else:
                file_name = "index.html" if page_name == "home" else f"{page_name}.html"
                file_path = output_dir / file_name

            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(code)

        # Write styles
        styles_path = output_dir / ("app/globals.css" if structure["type"] == "nextjs" else "styles/main.css")
        styles_path.parent.mkdir(parents=True, exist_ok=True)
        styles_path.write_text(styles)

        # Write components
        for comp_name, code in components.items():
            comp_path = output_dir / "components" / f"{comp_name}.tsx"
            comp_path.parent.mkdir(parents=True, exist_ok=True)
            comp_path.write_text(code)

        # Write package.json for Next.js
        if structure["type"] == "nextjs":
            pkg = {
                "name": f"nexus-site-{client_id}",
                "version": "1.0.0",
                "private": True,
                "scripts": {
                    "dev": "next dev",
                    "build": "next build",
                    "start": "next start",
                },
                "dependencies": {
                    "next": "^14.2.0",
                    "react": "^18.3.0",
                    "react-dom": "^18.3.0",
                },
                "devDependencies": {
                    "@types/node": "^22.0.0",
                    "@types/react": "^18.3.0",
                    "autoprefixer": "^10.4.0",
                    "postcss": "^8.4.0",
                    "tailwindcss": "^3.4.0",
                    "typescript": "^5.6.0",
                },
            }
            (output_dir / "package.json").write_text(json.dumps(pkg, indent=2))

        logger.info(
            "website_builder.files_written",
            output_dir=str(output_dir),
            pages=len(pages),
            components=len(components),
        )
        return output_dir

    async def _validate_generated_code(
        self, pages: dict[str, str], components: dict[str, str]
    ) -> dict:
        """Validate generated JS/TS code for syntax errors using the code executor."""
        validation_results = {"pages": {}, "components": {}, "all_valid": True}

        all_files = {**{f"page:{k}": v for k, v in pages.items()},
                     **{f"component:{k}": v for k, v in components.items()}}

        for label, code in all_files.items():
            # Use the executor to run a quick syntax check via Node.js
            check_script = (
                "const code = " + json.dumps(code) + ";\n"
                "try {\n"
                "  new Function(code);\n"
                "  console.log(JSON.stringify({valid: true}));\n"
                "} catch(e) {\n"
                "  console.log(JSON.stringify({valid: false, error: e.message}));\n"
                "}"
            )
            result = await self.executor.execute(check_script, language="javascript")
            category, name = label.split(":", 1)
            bucket = "pages" if category == "page" else "components"
            try:
                parsed = json.loads(result.get("stdout", "{}"))
                validation_results[bucket][name] = parsed
                if not parsed.get("valid", False):
                    validation_results["all_valid"] = False
            except json.JSONDecodeError:
                validation_results[bucket][name] = {
                    "valid": False,
                    "error": result.get("stderr", "unknown error"),
                }
                validation_results["all_valid"] = False

        logger.info(
            "website_builder.validation_complete",
            all_valid=validation_results["all_valid"],
        )
        return validation_results
