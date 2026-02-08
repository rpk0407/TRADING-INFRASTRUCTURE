"""
Kimi K2.5 Local Client — Wraps the OpenAI-compatible API served by
vLLM, Ollama, or HuggingFace TGI for Kimi K2.5 local inference.

Kimi K2.5 by Moonshot AI strengths:
- Strong reasoning and math (close to GPT-4 level)
- Excellent coding capabilities
- 128K context window
- Vision capabilities (image understanding)
- Multilingual (especially strong in Chinese + English)
- Can be self-hosted for ZERO cost
"""

import httpx
from typing import Optional
from dataclasses import dataclass

from config.settings import settings


@dataclass
class KimiResponse:
    content: str
    tokens_in: int
    tokens_out: int
    model: str
    finish_reason: str


class KimiK2Client:
    """
    Client for locally-hosted Kimi K2.5.

    Supports three deployment modes:
    1. Ollama: ollama run kimi-k2.5 (easiest)
    2. vLLM: vllm serve moonshotai/Kimi-K2.5 (best throughput)
    3. HuggingFace TGI: text-generation-launcher (most flexible)

    All expose an OpenAI-compatible /v1/chat/completions endpoint.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 120.0,
    ):
        self.base_url = base_url or settings.kimi_local_url
        self.model = model or settings.kimi_model_name
        self.timeout = timeout

    async def chat(
        self,
        messages: list[dict],
        max_tokens: int = 4096,
        temperature: float = 0.7,
        top_p: float = 0.9,
        stop: Optional[list[str]] = None,
    ) -> KimiResponse:
        """Send a chat completion request."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "top_p": top_p,
                    "stop": stop,
                },
            )
            response.raise_for_status()
            data = response.json()

        choice = data["choices"][0]
        usage = data.get("usage", {})

        return KimiResponse(
            content=choice["message"]["content"],
            tokens_in=usage.get("prompt_tokens", 0),
            tokens_out=usage.get("completion_tokens", 0),
            model=data.get("model", self.model),
            finish_reason=choice.get("finish_reason", "stop"),
        )

    async def is_available(self) -> bool:
        """Check if Kimi K2.5 service is running."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.base_url}/models")
                return resp.status_code == 200
        except Exception:
            return False

    async def chat_with_vision(
        self,
        messages: list[dict],
        image_url: str,
        max_tokens: int = 2048,
    ) -> KimiResponse:
        """
        Chat with image input (Kimi K2.5 supports vision).
        Useful for: analyzing client logos, competitor screenshots, etc.
        """
        # Add image to the last user message
        enriched_messages = messages.copy()
        if enriched_messages and enriched_messages[-1]["role"] == "user":
            enriched_messages[-1] = {
                "role": "user",
                "content": [
                    {"type": "text", "text": enriched_messages[-1]["content"]},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            }

        return await self.chat(
            messages=enriched_messages,
            max_tokens=max_tokens,
        )
