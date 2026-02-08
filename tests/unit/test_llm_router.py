"""Tests for the LLM Router."""

import pytest
from core.llm_router.models import (
    LLMProvider,
    LLMResponse,
    TaskComplexity,
    PROVIDER_COSTS,
    PROVIDER_CAPABILITIES,
    TASK_CAPABILITY_REQUIREMENTS,
)


class TestLLMModels:
    def test_provider_costs_defined(self):
        for provider in LLMProvider:
            assert provider in PROVIDER_COSTS
            assert "input" in PROVIDER_COSTS[provider]
            assert "output" in PROVIDER_COSTS[provider]

    def test_local_models_are_free(self):
        assert PROVIDER_COSTS[LLMProvider.KIMI_LOCAL]["input"] == 0.0
        assert PROVIDER_COSTS[LLMProvider.KIMI_LOCAL]["output"] == 0.0
        assert PROVIDER_COSTS[LLMProvider.OLLAMA]["input"] == 0.0
        assert PROVIDER_COSTS[LLMProvider.OLLAMA]["output"] == 0.0

    def test_provider_capabilities_defined(self):
        for provider in LLMProvider:
            assert provider in PROVIDER_CAPABILITIES
            caps = PROVIDER_CAPABILITIES[provider]
            assert "reasoning" in caps
            assert "coding" in caps

    def test_claude_is_highest_rated(self):
        claude_caps = PROVIDER_CAPABILITIES[LLMProvider.CLAUDE]
        for provider in [LLMProvider.KIMI_LOCAL, LLMProvider.OLLAMA]:
            other_caps = PROVIDER_CAPABILITIES[provider]
            assert sum(claude_caps.values()) >= sum(other_caps.values())

    def test_llm_response(self):
        resp = LLMResponse(
            content="test",
            provider=LLMProvider.KIMI_LOCAL,
            model="kimi-k2.5",
            tokens_in=100,
            tokens_out=50,
        )
        assert resp.total_tokens == 150
        assert resp.cost_usd == 0.0

    def test_task_requirements_valid(self):
        for task_type, reqs in TASK_CAPABILITY_REQUIREMENTS.items():
            for cap, min_score in reqs.items():
                assert cap in PROVIDER_CAPABILITIES[LLMProvider.CLAUDE]
                assert 1 <= min_score <= 10
