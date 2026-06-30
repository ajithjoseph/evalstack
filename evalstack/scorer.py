# evalstack/scorer.py
"""
Scoring strategies for EvalStack.
Pluggable scorers for different eval types.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Score:
    value: float      # 0.0 to 1.0
    passed: bool
    reason: str


class BaseScorer(ABC):
    """Abstract base class for all scorers."""

    @abstractmethod
    def score(self, response: str, expected: str) -> Score:
        """Score a response against expected output."""
        pass


class ExactMatchScorer(BaseScorer):
    """Scores 1.0 if response exactly matches expected."""

    def score(self, response: str, expected: str) -> Score:
        match = response.strip().lower() == expected.strip().lower()
        return Score(
            value=1.0 if match else 0.0,
            passed=match,
            reason="Exact match" if match else "No exact match"
        )


class ContainsScorer(BaseScorer):
    """Scores 1.0 if expected string is contained in response."""

    def score(self, response: str, expected: str) -> Score:
        contains = expected.strip().lower() in response.strip().lower()
        return Score(
            value=1.0 if contains else 0.0,
            passed=contains,
            reason=f"Response contains '{expected}'" if contains
                   else f"Response missing '{expected}'"
        )


class LLMJudgeScorer(BaseScorer):
    """
    Uses an LLM to judge response quality.
    Coming in v0.1 — requires API integration.
    """

    def score(self, response: str, expected: str) -> Score:
        raise NotImplementedError(
            "LLMJudgeScorer ships in v0.0.1. "
            "Use ExactMatchScorer or ContainsScorer for now."
        )
