"""
Web Scraper Tool — Gives agents the ability to fetch and parse web content.

Used by:
- SEO Agent: competitor analysis, SERP analysis
- Marketing Agent: competitor campaigns, market research
- Content Engine: reference material gathering
- Growth Analytics: market data collection
"""

import asyncio
import re
from typing import Any, Optional
from urllib.parse import urljoin, urlparse

import structlog

logger = structlog.get_logger(__name__)


class WebScraper:
    """
    Async web scraper with rate limiting and content extraction.
    Designed for agent use — returns clean, structured data.
    """

    def __init__(self, max_concurrent: int = 5, delay_seconds: float = 1.0):
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._delay = delay_seconds
        self._cache: dict[str, dict] = {}

    async def fetch_page(self, url: str, extract_mode: str = "text") -> dict:
        """
        Fetch and parse a web page.

        Args:
            url: URL to fetch
            extract_mode: "text" | "links" | "metadata" | "full"

        Returns:
            {url, status, title, content, links, metadata, word_count}
        """
        if url in self._cache:
            return self._cache[url]

        async with self._semaphore:
            try:
                import httpx

                headers = {
                    "User-Agent": (
                        "Mozilla/5.0 (compatible; NexusBot/1.0; "
                        "+https://nexus-ai.com/bot)"
                    ),
                    "Accept": "text/html,application/xhtml+xml",
                    "Accept-Language": "en-US,en;q=0.9",
                }

                async with httpx.AsyncClient(
                    timeout=30.0,
                    follow_redirects=True,
                    max_redirects=5,
                ) as client:
                    resp = await client.get(url, headers=headers)

                result = {
                    "url": str(resp.url),
                    "status": resp.status_code,
                    "content_type": resp.headers.get("content-type", ""),
                }

                if resp.status_code != 200:
                    result["error"] = f"HTTP {resp.status_code}"
                    return result

                html = resp.text

                # Extract components based on mode
                result["title"] = self._extract_title(html)
                result["content"] = self._extract_text(html)
                result["word_count"] = len(result["content"].split())

                if extract_mode in ("links", "full"):
                    result["links"] = self._extract_links(html, str(resp.url))

                if extract_mode in ("metadata", "full"):
                    result["metadata"] = self._extract_metadata(html)

                self._cache[url] = result
                await asyncio.sleep(self._delay)

                logger.info(
                    "scraper.fetched",
                    url=url,
                    words=result["word_count"],
                )
                return result

            except Exception as e:
                logger.error("scraper.error", url=url, error=str(e))
                return {"url": url, "status": 0, "error": str(e)}

    async def fetch_multiple(
        self, urls: list[str], extract_mode: str = "text"
    ) -> list[dict]:
        """Fetch multiple URLs concurrently."""
        tasks = [self.fetch_page(url, extract_mode) for url in urls]
        return await asyncio.gather(*tasks)

    async def search_and_extract(
        self, query: str, num_results: int = 5
    ) -> list[dict]:
        """
        Simulate search by generating likely URLs from query terms.
        In production, integrate with SerpAPI or Google Custom Search.
        """
        # Return structured search intent for the agent to process
        return [{
            "query": query,
            "num_results": num_results,
            "note": "Connect SerpAPI key for live results",
            "suggested_sources": self._suggest_sources(query),
        }]

    def _extract_title(self, html: str) -> str:
        match = re.search(r"<title[^>]*>(.*?)</title>", html, re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else ""

    def _extract_text(self, html: str) -> str:
        """Extract readable text from HTML."""
        # Remove script and style elements
        text = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
        # Remove HTML tags
        text = re.sub(r"<[^>]+>", " ", text)
        # Clean whitespace
        text = re.sub(r"\s+", " ", text).strip()
        # Decode common entities
        text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
        text = text.replace("&quot;", '"').replace("&#39;", "'").replace("&nbsp;", " ")
        return text

    def _extract_links(self, html: str, base_url: str) -> list[dict]:
        """Extract all links with anchor text."""
        links = []
        for match in re.finditer(
            r'<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',
            html,
            re.DOTALL | re.IGNORECASE,
        ):
            href = match.group(1).strip()
            text = re.sub(r"<[^>]+>", "", match.group(2)).strip()
            if href.startswith(("http://", "https://")):
                full_url = href
            elif href.startswith("/"):
                full_url = urljoin(base_url, href)
            else:
                continue

            links.append({"url": full_url, "text": text[:200]})

        return links[:100]  # Cap at 100 links

    def _extract_metadata(self, html: str) -> dict:
        """Extract meta tags, OG data, schema markup."""
        meta = {}

        # Standard meta tags
        for match in re.finditer(
            r'<meta\s+(?:name|property)=["\']([^"\']+)["\']'
            r'\s+content=["\']([^"\']*)["\']',
            html,
            re.IGNORECASE,
        ):
            meta[match.group(1)] = match.group(2)

        # Also check reversed attribute order
        for match in re.finditer(
            r'<meta\s+content=["\']([^"\']*)["\']'
            r'\s+(?:name|property)=["\']([^"\']+)["\']',
            html,
            re.IGNORECASE,
        ):
            meta[match.group(2)] = match.group(1)

        # Canonical URL
        canonical = re.search(
            r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)["\']',
            html,
            re.IGNORECASE,
        )
        if canonical:
            meta["canonical"] = canonical.group(1)

        # H1 tags
        h1s = re.findall(r"<h1[^>]*>(.*?)</h1>", html, re.DOTALL | re.IGNORECASE)
        meta["h1_tags"] = [re.sub(r"<[^>]+>", "", h).strip() for h in h1s[:5]]

        return meta

    def _suggest_sources(self, query: str) -> list[str]:
        """Suggest research sources based on query topic."""
        topics = {
            "seo": ["moz.com", "ahrefs.com", "searchengineland.com"],
            "marketing": ["hubspot.com", "neilpatel.com", "marketingland.com"],
            "business": ["hbr.org", "forbes.com", "entrepreneur.com"],
            "design": ["dribbble.com", "behance.net", "awwwards.com"],
            "tech": ["techcrunch.com", "producthunt.com", "ycombinator.com"],
        }
        query_lower = query.lower()
        for topic, sources in topics.items():
            if topic in query_lower:
                return sources
        return ["google.com", "wikipedia.org"]

    def clear_cache(self):
        self._cache.clear()
