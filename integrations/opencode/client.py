"""
OpenCode Client — Coding-specialized inference via Ollama.

Routes coding tasks to purpose-built models:
- deepseek-coder-v2  → code generation & debugging
- codellama          → fill-in-the-middle completion
- qwen2.5-coder      → code review & explanation

All models run locally through Ollama, cost = $0.
"""

import httpx
from typing import Optional
from dataclasses import dataclass, field

from config.settings import settings


@dataclass
class OpenCodeResponse:
    """Structured response from any OpenCode operation."""
    content: str
    language: str
    tokens_in: int
    tokens_out: int
    model: str


class OpenCodeClient:
    """
    Client for coding-specialized local models running on Ollama.

    Uses three dedicated models optimized for different coding tasks:
    1. Primary (deepseek-coder-v2) — generation, debugging, refactoring
    2. Completion (codellama) — fill-in-the-middle code completion
    3. Review (qwen2.5-coder) — code review, explanation
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        primary_model: Optional[str] = None,
        completion_model: Optional[str] = None,
        review_model: Optional[str] = None,
        timeout: float = 180.0,
    ):
        self.base_url = (base_url or settings.ollama_url).rstrip("/")
        self.primary_model = primary_model or settings.opencode_primary_model
        self.completion_model = completion_model or settings.opencode_completion_model
        self.review_model = review_model or settings.opencode_review_model
        self.timeout = timeout

    # ── Internal helpers ─────────────────────────────────────────

    async def _generate(
        self,
        prompt: str,
        model: str,
        system: Optional[str] = None,
        temperature: float = 0.2,
    ) -> dict:
        """Send a generation request to Ollama and return the raw JSON."""
        payload: dict = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature},
        }
        if system:
            payload["system"] = system

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json=payload,
            )
            response.raise_for_status()
            return response.json()

    def _build_response(
        self, data: dict, language: str, model: str
    ) -> OpenCodeResponse:
        """Convert raw Ollama response into an OpenCodeResponse."""
        return OpenCodeResponse(
            content=data.get("response", ""),
            language=language,
            tokens_in=data.get("prompt_eval_count", 0),
            tokens_out=data.get("eval_count", 0),
            model=model,
        )

    # ── Public API ───────────────────────────────────────────────

    async def generate_code(
        self,
        prompt: str,
        language: str,
        model: Optional[str] = None,
    ) -> OpenCodeResponse:
        """
        Generate code from a natural-language prompt.

        Uses the primary model (deepseek-coder-v2) by default.
        """
        target_model = model or self.primary_model
        system = (
            f"You are an expert {language} programmer. "
            "Generate clean, well-documented, production-ready code. "
            "Return ONLY the code with no surrounding explanation unless asked."
        )
        data = await self._generate(prompt, target_model, system=system)
        return self._build_response(data, language, target_model)

    async def complete_code(
        self,
        prefix: str,
        suffix: str,
        language: str,
    ) -> OpenCodeResponse:
        """
        Fill-in-the-middle code completion.

        Uses codellama's FIM (fill-in-middle) capability by default.
        The prompt is formatted with <PRE>, <SUF>, <MID> tokens for FIM.
        """
        fim_prompt = f"<PRE> {prefix} <SUF>{suffix} <MID>"
        system = (
            f"You are a {language} code completion engine. "
            "Complete the code between the prefix and suffix. "
            "Return ONLY the code that fills the gap."
        )
        data = await self._generate(
            fim_prompt,
            self.completion_model,
            system=system,
            temperature=0.1,
        )
        return self._build_response(data, language, self.completion_model)

    async def review_code(
        self,
        code: str,
        language: str,
    ) -> OpenCodeResponse:
        """
        Review code for bugs, security issues, and improvements.

        Uses the review model (qwen2.5-coder) by default.
        """
        prompt = (
            f"Review the following {language} code. "
            "Identify bugs, security issues, performance problems, and style issues. "
            "Provide specific, actionable suggestions.\n\n"
            f"```{language}\n{code}\n```"
        )
        system = (
            "You are a senior code reviewer. Be thorough but concise. "
            "Focus on correctness, security, and maintainability."
        )
        data = await self._generate(prompt, self.review_model, system=system)
        return self._build_response(data, language, self.review_model)

    async def explain_code(
        self,
        code: str,
        language: str,
    ) -> OpenCodeResponse:
        """
        Explain what a piece of code does in plain English.

        Uses the review model for its strong comprehension.
        """
        prompt = (
            f"Explain the following {language} code clearly and concisely. "
            "Describe what it does, how it works, and any notable patterns.\n\n"
            f"```{language}\n{code}\n```"
        )
        system = (
            "You are a patient, expert programming teacher. "
            "Explain code in clear, accessible language."
        )
        data = await self._generate(prompt, self.review_model, system=system)
        return self._build_response(data, language, self.review_model)

    async def debug_code(
        self,
        code: str,
        error: str,
        language: str,
    ) -> OpenCodeResponse:
        """
        Diagnose and fix code given an error message.

        Uses the primary model (deepseek-coder-v2) for its strong reasoning.
        """
        prompt = (
            f"The following {language} code produces an error. "
            "Diagnose the root cause and provide the corrected code.\n\n"
            f"**Code:**\n```{language}\n{code}\n```\n\n"
            f"**Error:**\n```\n{error}\n```"
        )
        system = (
            "You are an expert debugger. First explain the root cause briefly, "
            "then provide the complete corrected code."
        )
        data = await self._generate(prompt, self.primary_model, system=system)
        return self._build_response(data, language, self.primary_model)

    async def refactor_code(
        self,
        code: str,
        language: str,
        instructions: str,
    ) -> OpenCodeResponse:
        """
        Refactor code according to specific instructions.

        Uses the primary model (deepseek-coder-v2) for generation quality.
        """
        prompt = (
            f"Refactor the following {language} code according to these instructions: "
            f"{instructions}\n\n"
            f"```{language}\n{code}\n```\n\n"
            "Return the complete refactored code."
        )
        system = (
            "You are a senior software engineer specializing in refactoring. "
            "Produce clean, idiomatic, well-structured code."
        )
        data = await self._generate(prompt, self.primary_model, system=system)
        return self._build_response(data, language, self.primary_model)

    # ── Utility ──────────────────────────────────────────────────

    async def is_available(self) -> bool:
        """Check if Ollama is running and accessible."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                return resp.status_code == 200
        except Exception:
            return False

    async def list_models(self) -> list[str]:
        """
        List coding models currently available in Ollama.

        Returns only models that match the configured coding model names.
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                resp.raise_for_status()
                data = resp.json()

            all_models = [m["name"] for m in data.get("models", [])]

            # Filter to known coding model families
            coding_prefixes = (
                "deepseek-coder",
                "codellama",
                "qwen2.5-coder",
                "starcoder",
                "codegemma",
                "code",
            )
            return [
                m for m in all_models
                if any(m.startswith(prefix) for prefix in coding_prefixes)
            ]
        except Exception:
            return []
