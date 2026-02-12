"""
Reflection Engine — Self-critique and iterative improvement for agent outputs.

This is what makes NEXUS agents truly intelligent:
1. Generate initial output
2. Self-critique: identify weaknesses
3. Improve: fix the issues
4. Verify: confirm improvement
5. Repeat until quality threshold met or max iterations reached

Used by ALL agents for high-stakes outputs.
"""

import json
from typing import Any, Optional

import structlog

logger = structlog.get_logger(__name__)


class ReflectionEngine:
    """
    Implements reflection/self-critique patterns for agent outputs.
    Uses a secondary LLM call to evaluate and improve outputs.
    """

    MAX_ITERATIONS = 3
    DEFAULT_QUALITY_THRESHOLD = 75

    def __init__(self, llm_router):
        self._router = llm_router

    async def reflect_and_improve(
        self,
        original_output: str,
        task_description: str,
        task_type: str = "general",
        quality_threshold: int = None,
        max_iterations: int = None,
    ) -> dict:
        """
        Iteratively improve an output through self-reflection.

        Returns:
            {
                "final_output": str,
                "iterations": int,
                "improvements": [str],
                "quality_scores": [int],
                "converged": bool,
            }
        """
        threshold = quality_threshold or self.DEFAULT_QUALITY_THRESHOLD
        max_iter = max_iterations or self.MAX_ITERATIONS

        current = original_output
        improvements = []
        quality_scores = []

        for i in range(max_iter):
            # Step 1: Critique
            critique = await self._critique(current, task_description, task_type)
            quality_scores.append(critique["score"])

            logger.info(
                "reflection.iteration",
                iteration=i + 1,
                score=critique["score"],
                issues=len(critique["issues"]),
            )

            # If quality is good enough, stop
            if critique["score"] >= threshold:
                break

            # Step 2: Improve based on critique
            improved = await self._improve(
                current, critique, task_description, task_type
            )
            improvements.append(critique["summary"])
            # Stop if improvement produced same output (avoid infinite loop)
            if improved == current:
                break
            current = improved

        return {
            "final_output": current,
            "original_output": original_output,
            "iterations": len(quality_scores),
            "improvements": improvements,
            "quality_scores": quality_scores,
            "converged": quality_scores[-1] >= threshold if quality_scores else False,
        }

    async def _critique(
        self, output: str, task_description: str, task_type: str
    ) -> dict:
        """Have the LLM critique its own output."""
        critique_prompt = f"""You are a quality reviewer. Analyze the following output
and provide a structured critique.

TASK DESCRIPTION: {task_description}

OUTPUT TO REVIEW:
{output[:3000]}

Respond with ONLY valid JSON:
{{
    "score": <0-100 quality score>,
    "issues": [
        {{"category": "<completeness|accuracy|format|relevance|creativity>", "description": "<issue>", "severity": "<low|medium|high>"}}
    ],
    "strengths": ["<what's good>"],
    "summary": "<1-sentence summary of main issue>"
}}"""

        response = await self._router.generate(
            prompt=critique_prompt,
            task_type="analysis",
            max_tokens=1024,
            temperature=0.3,
        )

        try:
            critique = json.loads(response.content)
            return critique
        except json.JSONDecodeError:
            # Fallback: extract score heuristically
            return {
                "score": 50,
                "issues": [{"category": "format", "description": "Could not parse critique", "severity": "medium"}],
                "strengths": [],
                "summary": "Critique parsing failed, assuming medium quality",
            }

    async def _improve(
        self, output: str, critique: dict, task_description: str, task_type: str
    ) -> str:
        """Improve the output based on critique feedback."""
        issues_text = "\n".join(
            f"- [{i['severity'].upper()}] {i['category']}: {i['description']}"
            for i in critique.get("issues", [])
        )

        improve_prompt = f"""You previously generated output for the following task,
and a reviewer found issues. Fix ALL issues while keeping what's good.

ORIGINAL TASK: {task_description}

CURRENT OUTPUT:
{output[:3000]}

REVIEWER CRITIQUE (score: {critique.get('score', '?')}/100):
{issues_text}

STRENGTHS TO KEEP:
{chr(10).join('- ' + s for s in critique.get('strengths', []))}

Generate an IMPROVED version that addresses all issues.
Output ONLY the improved content, no explanations."""

        response = await self._router.generate(
            prompt=improve_prompt,
            task_type=task_type,
            max_tokens=4096,
            temperature=0.5,
        )

        return response.content

    async def verify_output(
        self, output: str, requirements: list[str]
    ) -> dict:
        """Verify output meets specific requirements."""
        checks = []
        for req in requirements:
            check_prompt = f"""Does the following output satisfy this requirement?
Requirement: {req}

Output (first 2000 chars):
{output[:2000]}

Respond with ONLY valid JSON:
{{"met": true/false, "confidence": 0.0-1.0, "evidence": "<quote or explanation>"}}"""

            response = await self._router.generate(
                prompt=check_prompt,
                task_type="classification",
                max_tokens=256,
                temperature=0.1,
            )

            try:
                result = json.loads(response.content)
                result["requirement"] = req
            except json.JSONDecodeError:
                result = {
                    "requirement": req,
                    "met": False,
                    "confidence": 0.0,
                    "evidence": "Could not verify",
                }
            checks.append(result)

        met_count = sum(1 for c in checks if c.get("met"))
        return {
            "all_met": met_count == len(requirements),
            "met_count": met_count,
            "total_requirements": len(requirements),
            "checks": checks,
            "overall_confidence": (
                sum(c.get("confidence", 0) for c in checks) / max(len(checks), 1)
            ),
        }


class ChainOfThought:
    """
    Implements chain-of-thought reasoning for complex tasks.
    Breaks down problems into steps and solves incrementally.
    """

    def __init__(self, llm_router):
        self._router = llm_router

    async def reason(
        self,
        problem: str,
        context: str = "",
        task_type: str = "analysis",
    ) -> dict:
        """
        Apply chain-of-thought reasoning to a complex problem.

        Returns structured reasoning with intermediate steps.
        """
        cot_prompt = f"""Solve the following problem step by step.
For each step, explain your reasoning clearly.

CONTEXT:
{context[:2000]}

PROBLEM:
{problem}

Respond with ONLY valid JSON:
{{
    "steps": [
        {{"step": 1, "action": "<what you're doing>", "reasoning": "<why>", "result": "<outcome>"}}
    ],
    "final_answer": "<your conclusion>",
    "confidence": 0.0-1.0,
    "assumptions": ["<any assumptions made>"]
}}"""

        response = await self._router.generate(
            prompt=cot_prompt,
            task_type=task_type,
            max_tokens=4096,
            temperature=0.3,
        )

        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {
                "steps": [{"step": 1, "action": "direct_response", "reasoning": "CoT parsing failed", "result": response.content[:2000]}],
                "final_answer": response.content[:2000],
                "confidence": 0.5,
                "assumptions": [],
            }

    async def plan_and_execute(
        self,
        goal: str,
        available_actions: list[str],
        constraints: list[str] = None,
    ) -> dict:
        """
        Create an action plan for achieving a goal.
        """
        constraints_text = "\n".join(f"- {c}" for c in (constraints or []))
        actions_text = "\n".join(f"- {a}" for a in available_actions)

        plan_prompt = f"""Create a detailed action plan to achieve the following goal.

GOAL: {goal}

AVAILABLE ACTIONS:
{actions_text}

CONSTRAINTS:
{constraints_text or "None"}

Respond with ONLY valid JSON:
{{
    "plan_name": "<descriptive name>",
    "steps": [
        {{
            "order": 1,
            "action": "<action from available list>",
            "details": "<specifics>",
            "dependencies": [<step numbers this depends on>],
            "estimated_impact": "low|medium|high"
        }}
    ],
    "expected_outcome": "<what success looks like>",
    "risk_factors": ["<potential issues>"]
}}"""

        response = await self._router.generate(
            prompt=plan_prompt,
            task_type="planning",
            max_tokens=2048,
            temperature=0.4,
        )

        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {
                "plan_name": "fallback_plan",
                "steps": [{"order": 1, "action": available_actions[0] if available_actions else "manual", "details": goal, "dependencies": [], "estimated_impact": "medium"}],
                "expected_outcome": goal,
                "risk_factors": ["Plan generation failed, using simplified fallback"],
            }
