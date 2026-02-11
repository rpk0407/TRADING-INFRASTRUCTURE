"""
LLM Router — Data models for the intelligent model routing system.
4 Core Providers: Ollama, OpenCode, OpenGravity, Claude
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class LLMProvider(str, Enum):
    OLLAMA = "ollama"              # Local: general-purpose (Mixtral, Llama 3.1)
    OPENCODE = "opencode"          # Local: coding specialist (DeepSeek Coder, CodeLlama, Qwen2.5-Coder)
    OPENGRAVITY = "opengravity"    # Hybrid: agent coordination + local/cloud
    CLAUDE = "claude"              # Premium: Anthropic API (fallback)


class TaskComplexity(str, Enum):
    TRIVIAL = "trivial"        # Classification, simple extraction
    SIMPLE = "simple"          # Content drafting, summarization
    MODERATE = "moderate"      # Code generation, analysis
    COMPLEX = "complex"        # Multi-step reasoning, planning
    EXPERT = "expert"          # Requires top-tier model capability


# Cost per 1K tokens (approximate)
PROVIDER_COSTS = {
    LLMProvider.OLLAMA: {"input": 0.0, "output": 0.0},               # FREE (local)
    LLMProvider.OPENCODE: {"input": 0.0, "output": 0.0},             # FREE (local via Ollama)
    LLMProvider.OPENGRAVITY: {"input": 0.0005, "output": 0.001},     # Near-zero (hybrid)
    LLMProvider.CLAUDE: {"input": 0.003, "output": 0.015},           # Paid (premium fallback)
}

# Capability ratings per provider (1-10)
PROVIDER_CAPABILITIES = {
    LLMProvider.OLLAMA: {
        "reasoning": 7, "coding": 5, "creative": 7,
        "analysis": 7, "planning": 6, "multilingual": 6,
    },
    LLMProvider.OPENCODE: {
        "reasoning": 6, "coding": 9, "creative": 4,
        "analysis": 6, "planning": 5, "multilingual": 5,
    },
    LLMProvider.OPENGRAVITY: {
        "reasoning": 7, "coding": 7, "creative": 7,
        "analysis": 7, "planning": 8, "multilingual": 6,
    },
    LLMProvider.CLAUDE: {
        "reasoning": 10, "coding": 10, "creative": 9,
        "analysis": 10, "planning": 10, "multilingual": 8,
    },
}

# Map task types to required capability thresholds
# These thresholds steer routing: code_generation needs coding>=8 → OpenCode(9) or Claude(10)
TASK_CAPABILITY_REQUIREMENTS = {
    "classification": {"reasoning": 4},
    "summarization": {"reasoning": 5, "analysis": 5},
    "content_draft": {"creative": 6},
    "content_final": {"creative": 8},
    "code_generation": {"coding": 8},
    "code_review": {"coding": 8, "reasoning": 7},
    "code_completion": {"coding": 8},
    "code_debugging": {"coding": 8, "reasoning": 7},
    "planning": {"planning": 7, "reasoning": 8},
    "analysis": {"analysis": 7, "reasoning": 7},
    "seo_optimization": {"analysis": 6, "creative": 6},
    "website_structure": {"coding": 7, "planning": 7},
    "growth_prediction": {"analysis": 8, "reasoning": 8},
    "customer_support": {"reasoning": 6, "creative": 5},
    "agent_coordination": {"planning": 8},
    "multi_agent_task": {"planning": 8, "reasoning": 7},
    "general": {"reasoning": 5},
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
