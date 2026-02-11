"""
Quality Scoring & Self-Improving Feedback Loop

After every agent execution, this system:
1. Scores the output quality (0-100)
2. Identifies what model/params produced best results per task type
3. Automatically tunes routing preferences over time
4. Flags outputs that need human review
5. Builds a knowledge base of what works per client/industry

This is what makes NEXUS truly unique — it gets BETTER the more you use it.
"""

import json
from datetime import datetime, timezone
from typing import Any, Optional

import structlog

from core.llm_router.models import LLMProvider

logger = structlog.get_logger(__name__)


class QualityScorer:
    """
    Scores LLM output quality using heuristics and (optionally) a judge LLM.
    """

    # Minimum acceptable scores per task type
    QUALITY_THRESHOLDS = {
        "code_generation": 70,
        "content_final": 75,
        "planning": 65,
        "analysis": 70,
        "content_draft": 50,
        "classification": 80,
        "seo_optimization": 65,
        "website_structure": 70,
        "growth_prediction": 65,
        "customer_support": 60,
    }

    def score_output(
        self,
        output: str,
        task_type: str,
        expected_format: str = "json",
    ) -> dict:
        """
        Score an LLM output on multiple dimensions.
        Returns: {"total": 0-100, "dimensions": {...}, "issues": [...]}
        """
        scores = {}
        issues = []

        # Dimension 1: Completeness — did it produce substantial output?
        length = len(output.strip())
        if length < 50:
            scores["completeness"] = 10
            issues.append("Output too short")
        elif length < 200:
            scores["completeness"] = 40
        elif length < 1000:
            scores["completeness"] = 70
        else:
            scores["completeness"] = 90

        # Dimension 2: Format compliance — did it follow requested format?
        if expected_format == "json":
            try:
                parsed = json.loads(output)
                scores["format"] = 100
                # Check if JSON has substance
                if isinstance(parsed, dict) and len(parsed) < 2:
                    scores["format"] = 60
                    issues.append("JSON output has very few keys")
                elif isinstance(parsed, list) and len(parsed) < 1:
                    scores["format"] = 40
                    issues.append("JSON array is empty")
            except json.JSONDecodeError:
                # Check if it contains JSON somewhere
                if "{" in output and "}" in output:
                    scores["format"] = 30
                    issues.append("Contains JSON but not valid")
                else:
                    scores["format"] = 10
                    issues.append("Expected JSON but got plain text")
        else:
            scores["format"] = 80  # Non-JSON is harder to validate

        # Dimension 3: Relevance indicators
        task_keywords = {
            "code_generation": ["function", "class", "return", "import", "const", "def"],
            "content_draft": ["audience", "brand", "engagement", "content"],
            "planning": ["strategy", "timeline", "goal", "action", "phase"],
            "analysis": ["data", "trend", "metric", "insight", "growth"],
            "seo_optimization": ["keyword", "meta", "search", "ranking", "SEO"],
        }
        keywords = task_keywords.get(task_type, [])
        if keywords:
            found = sum(1 for kw in keywords if kw.lower() in output.lower())
            scores["relevance"] = min(100, (found / max(len(keywords), 1)) * 100)
        else:
            scores["relevance"] = 70  # Default assumption

        # Dimension 4: No obvious errors
        error_indicators = ["error", "sorry", "i cannot", "i can't", "as an ai"]
        has_errors = any(ind in output.lower()[:200] for ind in error_indicators)
        scores["no_errors"] = 30 if has_errors else 90
        if has_errors:
            issues.append("Output may contain refusal or error language")

        # Calculate weighted total
        weights = {
            "completeness": 0.25,
            "format": 0.30,
            "relevance": 0.25,
            "no_errors": 0.20,
        }
        total = sum(scores[d] * weights[d] for d in scores)

        return {
            "total": round(total),
            "dimensions": scores,
            "issues": issues,
            "passes_threshold": total >= self.QUALITY_THRESHOLDS.get(task_type, 60),
            "task_type": task_type,
        }


class FeedbackLoop:
    """
    Tracks performance of each provider per task type and auto-tunes routing.
    """

    def __init__(self):
        self._history: list[dict] = []
        self._provider_scores: dict[str, dict[str, list[float]]] = {}
        self._scorer = QualityScorer()

    def record(
        self,
        provider: LLMProvider,
        task_type: str,
        output: str,
        latency_ms: float,
        cost_usd: float,
    ):
        """Record an execution and its quality score."""
        score = self._scorer.score_output(output, task_type)

        record = {
            "provider": provider.value,
            "task_type": task_type,
            "quality_score": score["total"],
            "latency_ms": latency_ms,
            "cost_usd": cost_usd,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "issues": score["issues"],
        }
        self._history.append(record)

        # Track per-provider per-task scores
        key = provider.value
        self._provider_scores.setdefault(key, {})
        self._provider_scores[key].setdefault(task_type, [])
        self._provider_scores[key][task_type].append(score["total"])

        # Keep only last 100 scores per combo
        if len(self._provider_scores[key][task_type]) > 100:
            self._provider_scores[key][task_type] = (
                self._provider_scores[key][task_type][-100:]
            )

        if not score["passes_threshold"]:
            logger.warning(
                "feedback.low_quality",
                provider=provider.value,
                task_type=task_type,
                score=score["total"],
                issues=score["issues"],
            )

        return score

    def get_best_provider(self, task_type: str) -> Optional[str]:
        """Get the best-performing provider for a given task type."""
        best_provider = None
        best_avg = 0.0

        for provider, tasks in self._provider_scores.items():
            if task_type in tasks and len(tasks[task_type]) >= 3:
                avg = sum(tasks[task_type]) / len(tasks[task_type])
                if avg > best_avg:
                    best_avg = avg
                    best_provider = provider

        return best_provider

    def get_provider_report(self) -> dict:
        """Generate a performance report across all providers."""
        report = {}
        for provider, tasks in self._provider_scores.items():
            report[provider] = {}
            for task_type, scores in tasks.items():
                report[provider][task_type] = {
                    "avg_score": round(sum(scores) / len(scores), 1),
                    "min_score": min(scores),
                    "max_score": max(scores),
                    "samples": len(scores),
                }
        return report

    def get_stats(self) -> dict:
        return {
            "total_evaluations": len(self._history),
            "provider_report": self.get_provider_report(),
            "recent_issues": [
                h for h in self._history[-10:] if h.get("issues")
            ],
        }
