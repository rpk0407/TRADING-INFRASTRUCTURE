"""
Deployment Manager — Deploy generated websites to hosting platforms.

Supports:
- Vercel (default, best for Next.js)
- Netlify
- Cloudflare Pages
- Custom servers via SSH
"""

import asyncio
import subprocess
from pathlib import Path
from typing import Optional

import structlog

from config.settings import settings

logger = structlog.get_logger(__name__)


class DeploymentManager:
    """Handles automated deployment of generated websites."""

    async def deploy(
        self,
        site_path: Path,
        provider: Optional[str] = None,
        project_name: Optional[str] = None,
    ) -> dict:
        """
        Deploy a generated website to a hosting provider.

        Returns:
            {"url": "https://...", "provider": "vercel", "status": "deployed"}
        """
        provider = provider or settings.website_deploy_provider

        if provider == "vercel":
            return await self._deploy_vercel(site_path, project_name)
        elif provider == "netlify":
            return await self._deploy_netlify(site_path, project_name)
        elif provider == "cloudflare":
            return await self._deploy_cloudflare(site_path, project_name)
        else:
            return {"status": "ready", "path": str(site_path), "provider": "local"}

    async def _deploy_vercel(self, site_path: Path, name: Optional[str]) -> dict:
        """Deploy to Vercel using CLI."""
        if not settings.vercel_token:
            return {
                "status": "skipped",
                "reason": "VERCEL_TOKEN not configured",
                "path": str(site_path),
            }

        cmd = ["vercel", "--yes", "--prod", "--token", settings.vercel_token]
        if name:
            cmd.extend(["--name", name])

        try:
            result = subprocess.run(
                cmd,
                cwd=str(site_path),
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode == 0:
                url = result.stdout.strip().split("\n")[-1]
                logger.info("deployment.vercel_success", url=url)
                return {"status": "deployed", "url": url, "provider": "vercel"}
            else:
                logger.error("deployment.vercel_failed", error=result.stderr)
                return {"status": "failed", "error": result.stderr, "provider": "vercel"}

        except subprocess.TimeoutExpired:
            return {"status": "timeout", "provider": "vercel"}

    async def _deploy_netlify(self, site_path: Path, name: Optional[str]) -> dict:
        """Deploy to Netlify using CLI."""
        if not settings.netlify_token:
            return {"status": "skipped", "reason": "NETLIFY_TOKEN not configured"}

        cmd = [
            "netlify", "deploy", "--prod", "--dir", str(site_path),
            "--auth", settings.netlify_token,
        ]
        if name:
            cmd.extend(["--site", name])

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=300
            )
            if result.returncode == 0:
                return {"status": "deployed", "provider": "netlify", "output": result.stdout}
            return {"status": "failed", "error": result.stderr, "provider": "netlify"}
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "provider": "netlify"}

    async def _deploy_cloudflare(self, site_path: Path, name: Optional[str]) -> dict:
        """Deploy to Cloudflare Pages."""
        return {
            "status": "ready",
            "provider": "cloudflare",
            "instructions": (
                f"Run: npx wrangler pages deploy {site_path} "
                f"--project-name {name or 'nexus-site'}"
            ),
        }
