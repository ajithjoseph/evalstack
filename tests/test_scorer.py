# tests/test_scorer.py

from evalstack.scorer import ExactMatchScorer, ContainsScorer


def test_exact_match_passes():
    scorer = ExactMatchScorer()
    result = scorer.score("Paris", "Paris")
    assert result.passed is True
    assert result.value == 1.0


def test_exact_match_fails():
    scorer = ExactMatchScorer()
    result = scorer.score("London", "Paris")
    assert result.passed is False
    assert result.value == 0.0


def test_contains_scorer_passes():
    scorer = ContainsScorer()
    result = scorer.score(
        "The capital of France is Paris.",
        "Paris"
    )
    assert result.passed is True


def test_contains_scorer_fails():
    scorer = ContainsScorer()
    result = scorer.score(
        "The capital of France is Lyon.",
        "Paris"
    )
    assert result.passed is False
