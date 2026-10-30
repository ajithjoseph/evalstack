# evalstack/core.py
"""
Core evaluation loop for EvalStack.
Sends a prompt to a model, scores the reply and returns an EvalResult.
"""

import time
from dataclasses import dataclass

from evalstack.providers import Generate, make_generate
from evalstack.scorer import BaseScorer, ContainsScorer


@dataclass
class EvalResult:
    """Result of a single evaluation run."""
    prompt: str
    response: str
    expected: str
    score: float
    passed: bool
    metadata: dict


class EvalRunner:
    """
    Core evaluation loop for single LLM calls.

    Usage:
        runner = EvalRunner(model="claude-opus-5-5")
        result = runner.run(
            prompt="What is the capital of France?",
            expected="Paris"
        )

    The scorer decides pass/fail (DECISIONS.md D-016). It defaults to
    ContainsScorer, since model replies are usually full sentences. Pass
    `generate` (any prompt -> text function) to use another provider or a
    fake in tests; otherwise the client is built on the first call.
    """

    def __init__(
        self,
        model: str,
        scorer: BaseScorer | None = None,
        provider: str = "anthropic",
        generate: Generate | None = None,
    ):
        self.model = model
        self.scorer = scorer or ContainsScorer()
        self.provider = provider if generate is None else "custom"
        self._generate = generate

    def run(self, prompt: str, expected: str) -> EvalResult:
        """
        Run a single eval against the model.
        Provider errors and refusals are raised, never scored.
        """
        if self._generate is None:
            self._generate = make_generate(self.provider, self.model)
        start = time.perf_counter()
        response = self._generate(prompt)
        latency = time.perf_counter() - start
        score = self.scorer.score(response, expected)
        return EvalResult(
            prompt=prompt,
            response=response,
            expected=expected,
            score=score.value,
            passed=score.passed,
            metadata={
                "model": self.model,
                "provider": self.provider,
                "scorer": type(self.scorer).__name__,
                "reason": score.reason,
                "latency_s": round(latency, 3),
            },
        )

    def batch(self, prompts: list[dict]) -> list[EvalResult]:
        """
        Run multiple evals in sequence. Each item needs "prompt" and
        "expected" keys; all items are checked before any model call.
        """
        for i, case in enumerate(prompts):
            if not isinstance(case, dict) or not {"prompt", "expected"} <= case.keys():
                raise ValueError(f"Item {i} needs 'prompt' and 'expected' keys")
        return [self.run(case["prompt"], case["expected"]) for case in prompts]
