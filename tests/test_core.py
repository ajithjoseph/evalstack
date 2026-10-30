# tests/test_core.py

import pytest

from evalstack.core import EvalResult, EvalRunner
from evalstack.scorer import ContainsScorer, ExactMatchScorer


class FakeModel:
    """Stands in for a provider: returns canned replies and records prompts."""

    def __init__(self, *replies):
        self.replies = list(replies)
        self.prompts = []

    def __call__(self, prompt):
        self.prompts.append(prompt)
        return self.replies.pop(0)


def test_eval_result_holds_fields():
    r = EvalResult(
        prompt="Capital of France?",
        response="Paris",
        expected="Paris",
        score=1.0,
        passed=True,
        metadata={"scorer": "exact"},
    )
    assert r.prompt == "Capital of France?"
    assert r.expected == "Paris"
    assert r.passed is True
    assert r.metadata == {"scorer": "exact"}


def test_runner_defaults():
    runner = EvalRunner(model="some-model")
    assert runner.model == "some-model"
    assert isinstance(runner.scorer, ContainsScorer)
    assert runner.provider == "anthropic"


def test_runner_has_no_threshold():
    # Pass/fail belongs to the scorer (D-016).
    assert not hasattr(EvalRunner(model="m"), "threshold")


def test_constructing_runner_makes_no_client():
    # Building the client is deferred to the first run, so no SDK is needed here.
    EvalRunner(model="m", provider="does-not-exist")


def test_run_passes():
    model = FakeModel("The capital of France is Paris.")
    result = EvalRunner(model="m", generate=model).run(
        "What is the capital of France?", expected="Paris")
    assert model.prompts == ["What is the capital of France?"]
    assert result.response == "The capital of France is Paris."
    assert result.score == 1.0
    assert result.passed is True
    assert result.metadata["reason"] == "Response contains 'Paris'"


def test_run_fails():
    result = EvalRunner(model="m", generate=FakeModel("Lyon")).run("q", "Paris")
    assert result.passed is False
    assert result.score == 0.0
    assert result.metadata["reason"] == "Response missing 'Paris'"


def test_run_uses_given_scorer():
    runner = EvalRunner(model="m", scorer=ExactMatchScorer(),
                        generate=FakeModel("The answer is Paris"))
    assert runner.run("q", "Paris").passed is False


def test_run_metadata():
    result = EvalRunner(model="m", generate=FakeModel("Paris")).run("q", "Paris")
    meta = result.metadata
    assert meta["model"] == "m"
    assert meta["provider"] == "custom"
    assert meta["scorer"] == "ContainsScorer"
    assert meta["latency_s"] >= 0


def test_run_raises_provider_errors_instead_of_scoring():
    def broken(prompt):
        raise ConnectionError("network down")

    with pytest.raises(ConnectionError):
        EvalRunner(model="m", generate=broken).run("q", "Paris")


def test_run_with_unknown_provider_raises():
    with pytest.raises(ValueError, match="Unknown provider"):
        EvalRunner(model="m", provider="nope").run("q", "Paris")


def test_batch_runs_in_order():
    model = FakeModel("Paris", "Berlin")
    results = EvalRunner(model="m", generate=model).batch([
        {"prompt": "France?", "expected": "Paris"},
        {"prompt": "Spain?", "expected": "Madrid"},
    ])
    assert model.prompts == ["France?", "Spain?"]
    assert [r.passed for r in results] == [True, False]


def test_batch_empty_list():
    assert EvalRunner(model="m", generate=FakeModel()).batch([]) == []


@pytest.mark.parametrize("bad", [
    {"prompt": "only a prompt"},
    {"expected": "only expected"},
    "not a dict",
])
def test_batch_checks_every_item_before_calling_the_model(bad):
    model = FakeModel("Paris")
    with pytest.raises(ValueError, match="Item 1"):
        EvalRunner(model="m", generate=model).batch(
            [{"prompt": "q", "expected": "Paris"}, bad])
    assert model.prompts == []
