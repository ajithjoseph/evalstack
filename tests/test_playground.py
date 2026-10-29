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


def test_llm_judge_reports_not_implemented():
    status, body = server.score_request(
        {"scorer": "llm_judge", "response": "a", "expected": "b"})
    assert status == 200
    assert body["not_implemented"] is True
    assert "LLMJudgeScorer" in body["reason"]


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
