# tests/test_playground.py

import importlib.util
from pathlib import Path

_path = Path(__file__).resolve().parent.parent / "playground" / "server.py"
_spec = importlib.util.spec_from_file_location("playground_server", _path)
server = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(server)


def test_scores_exact_match():
    status, body = server.score_request(
        {"scorer": "exact_match", "response": " Paris ", "expected": "paris"})
    assert status == 200
    assert body == {"scorer": "exact_match", "value": 1.0,
                    "passed": True, "reason": "Exact match"}


def test_scores_contains_fail():
    status, body = server.score_request(
        {"scorer": "contains", "response": "Lyon", "expected": "Paris"})
    assert status == 200
    assert body["passed"] is False
    assert body["value"] == 0.0


def test_contains_empty_expected_fails():
    status, body = server.score_request(
        {"scorer": "contains", "response": "anything", "expected": "  "})
    assert status == 200
    assert body["passed"] is False
    assert "empty" in body["reason"]


def use_judge(monkeypatch, generate):
    monkeypatch.setitem(server.SCORERS, "llm_judge",
                        lambda: server.LLMJudgeScorer(model="m", generate=generate))


def test_llm_judge_scores(monkeypatch):
    use_judge(monkeypatch, lambda p: '{"score": 0.8, "reason": "Close"}')
    status, body = server.score_request(
        {"scorer": "llm_judge", "response": "a", "expected": "b"})
    assert status == 200
    assert body == {"scorer": "llm_judge", "value": 0.8,
                    "passed": True, "reason": "Close"}


def test_llm_judge_without_sdk_is_unavailable(monkeypatch):
    def no_sdk(prompt):
        raise ImportError("pip install 'evalstack[anthropic]'")

    use_judge(monkeypatch, no_sdk)
    status, body = server.score_request(
        {"scorer": "llm_judge", "response": "a", "expected": "b"})
    assert status == 200
    assert body["unavailable"] is True
    assert "evalstack[anthropic]" in body["reason"]


def test_llm_judge_api_error_is_an_error_not_a_score(monkeypatch):
    def broken(prompt):
        raise ConnectionError("network down")

    use_judge(monkeypatch, broken)
    status, body = server.score_request(
        {"scorer": "llm_judge", "response": "a", "expected": "b"})
    assert status == 502
    assert body == {"error": "ConnectionError: network down"}


def test_default_judge_model(monkeypatch):
    monkeypatch.delenv("EVALSTACK_JUDGE_MODEL", raising=False)
    assert server.SCORERS["llm_judge"]().model == "claude-opus-5-5"
    monkeypatch.setenv("EVALSTACK_JUDGE_MODEL", "claude-haiku-5-5")
    assert server.SCORERS["llm_judge"]().model == "claude-haiku-5-5"


def test_unknown_scorer_rejected():
    status, body = server.score_request({"scorer": "nope"})
    assert status == 400
    assert "Unknown scorer" in body["error"]


def test_non_string_inputs_rejected():
    status, _ = server.score_request(
        {"scorer": "contains", "response": 1, "expected": None})
    assert status == 400


def test_missing_fields_default_to_empty_strings():
    status, body = server.score_request({"scorer": "exact_match"})
    assert status == 200
    assert body["passed"] is True
