# tests/test_core.py

import pytest

from evalstack.core import EvalResult, EvalRunner


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


def test_eval_result_expected_can_be_none():
    r = EvalResult(prompt="p", response="r", expected=None,
                   score=0.0, passed=False, metadata={})
    assert r.expected is None


def test_runner_stores_model_and_default_threshold():
    runner = EvalRunner(model="some-model")
    assert runner.model == "some-model"
    assert runner.threshold == 0.8


def test_runner_custom_threshold():
    assert EvalRunner(model="m", threshold=0.5).threshold == 0.5


def test_runner_run_not_implemented():
    with pytest.raises(NotImplementedError, match="v0.1"):
        EvalRunner(model="m").run("What is the capital of France?", expected="Paris")


def test_runner_run_without_expected_not_implemented():
    with pytest.raises(NotImplementedError):
        EvalRunner(model="m").run("prompt")


def test_runner_batch_not_implemented():
    with pytest.raises(NotImplementedError, match="v0.1"):
        EvalRunner(model="m").batch([{"prompt": "p", "expected": "e"}])


def test_runner_batch_empty_list_still_not_implemented():
    with pytest.raises(NotImplementedError):
        EvalRunner(model="m").batch([])
