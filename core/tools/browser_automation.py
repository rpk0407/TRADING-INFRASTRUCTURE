"""
Browser Automation Tool — Headless browser control for agents.

Used by:
- Website Builder: screenshot generated sites, test responsiveness
- SEO Agent: check rendered content, Core Web Vitals
- Support Agent: test chatbot flows, simulate user journeys
- Marketing Agent: capture competitor pages, A/B test screenshots
"""

import asyncio
import os
import tempfile
from typing import Any, Optional

import structlog

logger = structlog.get_logger(__name__)


class BrowserAutomation:
    """
    Headless browser automation using Playwright (when available)
    or falling back to HTTP-based rendering.

    Designed for agent tasks — screenshots, DOM inspection, form testing.
    """

    def __init__(self, screenshots_dir: Optional[str] = None):
        self._screenshots_dir = screenshots_dir or tempfile.mkdtemp(prefix="nexus_screenshots_")
        os.makedirs(self._screenshots_dir, exist_ok=True)
        self._browser = None
        self._playwright_available = False

    async def initialize(self):
        """Try to initialize Playwright browser."""
        try:
            from playwright.async_api import async_playwright
            self._pw = await async_playwright().start()
            self._browser = await self._pw.chromium.launch(headless=True)
            self._playwright_available = True
            logger.info("browser.initialized", engine="playwright")
        except ImportError:
            self._playwright_available = False
            logger.info("browser.fallback", engine="httpx", reason="playwright not installed")

    async def screenshot(
        self,
        url: str,
        viewport: dict = None,
        full_page: bool = True,
    ) -> dict:
        """
        Take a screenshot of a URL.

        Returns:
            {url, screenshot_path, viewport, timestamp}
        """
        viewport = viewport or {"width": 1920, "height": 1080}

        if self._playwright_available:
            return await self._screenshot_playwright(url, viewport, full_page)
        else:
            return await self._screenshot_fallback(url)

    async def _screenshot_playwright(
        self, url: str, viewport: dict, full_page: bool
    ) -> dict:
        """Take screenshot using Playwright."""
        page = await self._browser.new_page(viewport_size=viewport)
        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)

            filename = f"screenshot_{hash(url) % 100000}.png"
            filepath = os.path.join(self._screenshots_dir, filename)

            await page.screenshot(path=filepath, full_page=full_page)

            return {
                "url": url,
                "screenshot_path": filepath,
                "viewport": viewport,
                "full_page": full_page,
                "success": True,
            }
        except Exception as e:
            return {"url": url, "success": False, "error": str(e)}
        finally:
            await page.close()

    async def _screenshot_fallback(self, url: str) -> dict:
        """Fallback: return page info without actual screenshot."""
        import httpx
        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                resp = await client.get(url)
                return {
                    "url": url,
                    "success": True,
                    "screenshot_path": None,
                    "note": "Install playwright for actual screenshots",
                    "status_code": resp.status_code,
                    "content_length": len(resp.text),
                }
        except Exception as e:
            return {"url": url, "success": False, "error": str(e)}

    async def get_page_metrics(self, url: str) -> dict:
        """
        Get page performance metrics (Core Web Vitals proxy).
        """
        if not self._playwright_available:
            return {"url": url, "note": "Install playwright for metrics"}

        page = await self._browser.new_page()
        try:
            # Navigate and measure timing
            start_event = asyncio.Event()
            metrics = {"url": url}

            response = await page.goto(url, wait_until="networkidle", timeout=30000)
            metrics["status_code"] = response.status if response else 0

            # Get performance timing
            timing = await page.evaluate("""() => {
                const perf = performance.getEntriesByType('navigation')[0];
                return {
                    dns_ms: perf ? perf.domainLookupEnd - perf.domainLookupStart : 0,
                    connect_ms: perf ? perf.connectEnd - perf.connectStart : 0,
                    ttfb_ms: perf ? perf.responseStart - perf.requestStart : 0,
                    dom_complete_ms: perf ? perf.domComplete - perf.responseEnd : 0,
                    load_ms: perf ? perf.loadEventEnd - perf.loadEventStart : 0,
                    total_ms: perf ? perf.loadEventEnd - perf.startTime : 0,
                };
            }""")
            metrics["timing"] = timing

            # Get page stats
            stats = await page.evaluate("""() => {
                return {
                    title: document.title,
                    meta_description: document.querySelector('meta[name=description]')?.content || '',
                    h1_count: document.querySelectorAll('h1').length,
                    img_count: document.querySelectorAll('img').length,
                    link_count: document.querySelectorAll('a').length,
                    script_count: document.querySelectorAll('script').length,
                    css_count: document.querySelectorAll('link[rel=stylesheet]').length,
                    viewport_meta: !!document.querySelector('meta[name=viewport]'),
                    has_favicon: !!document.querySelector('link[rel*=icon]'),
                };
            }""")
            metrics["page_stats"] = stats
            metrics["success"] = True

            return metrics

        except Exception as e:
            return {"url": url, "success": False, "error": str(e)}
        finally:
            await page.close()

    async def test_responsive(
        self, url: str
    ) -> dict:
        """Test a page at multiple viewport sizes."""
        viewports = {
            "mobile": {"width": 375, "height": 812},
            "tablet": {"width": 768, "height": 1024},
            "desktop": {"width": 1920, "height": 1080},
        }

        results = {}
        for device, vp in viewports.items():
            result = await self.screenshot(url, viewport=vp)
            results[device] = result

        return {
            "url": url,
            "responsive_test": results,
            "all_passed": all(r.get("success") for r in results.values()),
        }

    async def extract_structured_data(self, url: str) -> dict:
        """Extract structured data (JSON-LD, microdata) from a page."""
        if not self._playwright_available:
            # Fallback to HTTP
            import httpx
            try:
                async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                    resp = await client.get(url)
                    html = resp.text
            except Exception as e:
                return {"url": url, "error": str(e)}
        else:
            page = await self._browser.new_page()
            try:
                await page.goto(url, wait_until="networkidle", timeout=30000)
                html = await page.content()
            finally:
                await page.close()

        # Extract JSON-LD
        import re
        import json
        json_ld = []
        for match in re.finditer(
            r'<script\s+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
            html,
            re.DOTALL | re.IGNORECASE,
        ):
            try:
                json_ld.append(json.loads(match.group(1)))
            except json.JSONDecodeError:
                pass

        return {
            "url": url,
            "json_ld": json_ld,
            "has_structured_data": len(json_ld) > 0,
        }

    async def shutdown(self):
        """Clean up browser resources."""
        if self._browser:
            await self._browser.close()
        if hasattr(self, "_pw"):
            await self._pw.stop()
