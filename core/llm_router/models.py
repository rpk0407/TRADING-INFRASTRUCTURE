"""
LLM Router — Data models for the intelligent model routing system.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class LLMProvider(str, Enum):
    KIMI_LOCAL = "kimi_local"
    OLLAMA = "ollama"
    DEEPSEEK = "deepseek"
    GEMINI = "gemini"
    GROQ = "groq"
    ANTIGRAVITY = "antigravity"
    CLAUDE = "claude"


class TaskComplexity(str, Enum):
    TRIVIAL = "trivial"        # Classification, simple extraction
    SIMPLE = "simple"          # Content drafting, summarization
    MODERATE = "moderate"      # Code generation, analysis
    COMPLEX = "complex"        # Multi-step reasoning, planning
    EXPERT = "expert"          # Requires top-tier model capability


# Cost per 1K tokens (approximate)
PROVIDER_COSTS = {
    LLMProvider.KIMI_LOCAL: {"input": 0.0, "output": 0.0},         # FREE
    LLMProvider.OLLAMA: {"input": 0.0, "output": 0.0},             # FREE
    LLMProvider.DEEPSEEK: {"input": 0.0, "output": 0.0},           # FREE (local)
    LLMProvider.GEMINI: {"input": 0.0, "output": 0.0},             # FREE tier (15 RPM)
    LLMProvider.GROQ: {"input": 0.0, "output": 0.0},               # FREE tier (30 RPM)
    LLMProvider.ANTIGRAVITY: {"input": 0.0005, "output": 0.001},   # Near-zero
    LLMProvider.CLAUDE: {"input": 0.003, "output": 0.015},         # Paid fallback
}

# Capability ratings per provider (1-10)
PROVIDER_CAPABILITIES = {
    LLMProvider.KIMI_LOCAL: {
        "reasoning": 8, "coding": 8, "creative": 7,
        "analysis": 8, "planning": 7, "multilingual": 9,
    },
    LLMProvider.OLLAMA: {
        "reasoning": 6, "coding": 7, "creative": 6,
        "analysis": 6, "planning": 5, "multilingual": 5,
    },
    LLMProvider.DEEPSEEK: {
        "reasoning": 9, "coding": 9, "creative": 5,
        "analysis": 9, "planning": 8, "multilingual": 6,
    },
    LLMProvider.GEMINI: {
        "reasoning": 8, "coding": 7, "creative": 8,
        "analysis": 8, "planning": 8, "multilingual": 8,
    },
    LLMProvider.GROQ: {
        "reasoning": 8, "coding": 7, "creative": 7,
        "analysis": 7, "planning": 7, "multilingual": 7,
    },
    LLMProvider.ANTIGRAVITY: {
        "reasoning": 7, "coding": 7, "creative": 7,
        "analysis": 7, "planning": 7, "multilingual": 6,
    },
    LLMProvider.CLAUDE: {
        "reasoning": 10, "coding": 10, "creative": 9,
        "analysis": 10, "planning": 10, "multilingual": 8,
    },
}

# Map task types to required capability threshold
TASK_CAPABILITY_REQUIREMENTS = {
    "classification": {"reasoning": 4},
    "summarization": {"reasoning": 5, "analysis": 5},
    "content_draft": {"creative": 6},
    "content_final": {"creative": 8},
    "code_generation": {"coding": 7},
    "code_review": {"coding": 8, "reasoning": 7},
    "planning": {"planning": 7, "reasoning": 8},
    "analysis": {"analysis": 7, "reasoning": 7},
    "seo_optimization": {"analysis": 6, "creative": 6},
    "website_structure": {"coding": 7, "planning": 7},
    "growth_prediction": {"analysis": 8, "reasoning": 8},
    "customer_support": {"reasoning": 6, "creative": 5},
}


@dataclass
class LLMResponse:
    """Response from an LLM provider."""
    content: str
    provider: LLMProvider
    model: str
    tokens_in: int = 0
    tokens_out: int = 0
    cost_usd: float = 0.0
    latency_ms: float = 0.0
    cached: bool = False
    metadata: dict = field(default_factory=dict)

    @property
    def total_tokens(self) -> int:
        return self.tokens_in + self.tokens_out


@dataclass
class ProviderHealth:
    """Health status of an LLM provider."""
    provider: LLMProvider
    is_available: bool = False
    latency_ms: float = 0.0
    error_rate: float = 0.0
    last_checked: Optional[str] = None
    consecutive_failures: int = 0
