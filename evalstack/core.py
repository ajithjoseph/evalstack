# evalstack/core.py
"""
Core evaluation loop for EvalStack.
Handles single LLM call evaluation with scoring and logging.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class EvalResult:
    """Result of a single evaluation run."""
    prompt: str
    response: str
    expected: Optional[str]
    score: float
    passed: bool
    metadata: dict


class EvalRunner:
    """
    Core evaluation loop for single LLM calls.
    
    Usage:
        runner = EvalRunner(model="claude-sonnet-4-6")
        result = runner.run(
            prompt="What is the capital of France?",
            expected="Paris"
        )
    """

    def __init__(self, model: str, threshold: float = 0.8):
        self.model = model
        self.threshold = threshold

    def run(self, prompt: str, expected: Optional[str] = None) -> EvalResult:
        """
        Run a single eval against a model.
        Returns EvalResult with score and pass/fail.
        
        Note: LLM integration shipping in v0.1 (July 2026)
        """
        raise NotImplementedError(
            "LLM integration shipping in v0.1. "
            "Star the repo to follow progress."
        )

    def batch(self, prompts: list[dict]) -> list[EvalResult]:
        """Run multiple evals in sequence."""
        raise NotImplementedError("Batch eval shipping in v0.1.")
