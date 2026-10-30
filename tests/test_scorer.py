# tests/test_scorer.py

import pytest

from evalstack.scorer import (
    BaseScorer,
    ContainsScorer,
    ExactMatchScorer,
    LLMJudgeScorer,
    Score,
)


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


# --- Score / BaseScorer ---

def test_score_holds_fields():
    s = Score(value=0.5, passed=False, reason="half")
    assert (s.value, s.passed, s.reason) == (0.5, False, "half")


def test_base_scorer_is_abstract():
    with pytest.raises(TypeError):
        BaseScorer()


def test_subclass_without_score_cannot_be_instantiated():
    class Incomplete(BaseScorer):
        pass

    with pytest.raises(TypeError):
        Incomplete()


# --- ExactMatchScorer edge cases ---

@pytest.mark.parametrize("response, expected", [
    ("  Paris  ", "Paris"),        # leading/trailing spaces
    ("Paris\n", "Paris"),           # trailing newline
    ("\tParis", "Paris"),           # leading tab
    ("Paris", "  Paris\n"),         # whitespace on the expected side
    ("PARIS", "paris"),             # case
    ("pArIs", "PaRiS"),
    ("", ""),                       # both empty
    ("   ", ""),                    # whitespace-only vs empty
])
def test_exact_match_ignores_outer_whitespace_and_case(response, expected):
    result = ExactMatchScorer().score(response, expected)
    assert result == Score(value=1.0, passed=True, reason="Exact match")


@pytest.mark.parametrize("response, expected", [
    ("Paris France", "Paris  France"),  # inner whitespace is not normalised
    ("Paris.", "Paris"),                # punctuation counts
    ("", "Paris"),                      # empty response
    ("Paris", ""),                      # empty expected
    ("The answer is Paris", "Paris"),   # substring is not an exact match
])
def test_exact_match_fails_on(response, expected):
    result = ExactMatchScorer().score(response, expected)
    assert result == Score(value=0.0, passed=False, reason="No exact match")


def test_exact_match_uses_lower_not_casefold():
    # Current behaviour: str.lower(), so German sharp s does not fold to "ss".
    assert ExactMatchScorer().score("STRASSE", "straße").passed is False


# --- ContainsScorer edge cases ---

@pytest.mark.parametrize("response, expected", [
    ("The capital is PARIS.", "paris"),     # case
    ("The capital is paris.", "  Paris  "),  # whitespace on expected is stripped
    ("Paris", "Paris"),                     # equal strings
    ("Parisian food", "Paris"),             # plain substring, no word boundaries
])
def test_contains_passes_on(response, expected):
    result = ContainsScorer().score(response, expected)
    assert result.passed is True
    assert result.value == 1.0


@pytest.mark.parametrize("response, expected", [
    ("", "Paris"),                          # empty response
    ("Par is", "Paris"),                    # split by whitespace
    ("The capital is Paris", "Paris, France"),
])
def test_contains_fails_on(response, expected):
    result = ContainsScorer().score(response, expected)
    assert result.passed is False
    assert result.value == 0.0


@pytest.mark.parametrize("response", ["anything at all", "", "   "])
@pytest.mark.parametrize("expected", ["", "   ", "\n\t"])
def test_contains_empty_expected_fails(response, expected):
    # An empty expected would match every response, so it fails (D-013).
    result = ContainsScorer().score(response, expected)
    assert result == Score(
        value=0.0,
        passed=False,
        reason="Expected value is empty; nothing to check for",
    )


def test_contains_reason_quotes_original_expected():
    # The reason uses expected as given, not the stripped/lowercased form.
    passed = ContainsScorer().score("paris", " Paris ")
    failed = ContainsScorer().score("lyon", " Paris ")
    assert passed.reason == "Response contains ' Paris '"
    assert failed.reason == "Response missing ' Paris '"


# --- LLMJudgeScorer ---

def judge_with(reply):
    prompts = []

    def generate(prompt):
        prompts.append(prompt)
        return reply

    return LLMJudgeScorer(model="m", generate=generate), prompts


def test_llm_judge_is_a_base_scorer():
    assert isinstance(LLMJudgeScorer(model="m"), BaseScorer)


def test_llm_judge_passes_on_high_score():
    judge, prompts = judge_with('{"score": 0.9, "reason": "Same answer"}')
    result = judge.score("It is Paris.", "Paris")
    assert result == Score(value=0.9, passed=True, reason="Same answer")
    assert "<reference>\nParis\n</reference>" in prompts[0]
    assert "<response>\nIt is Paris.\n</response>" in prompts[0]


def test_llm_judge_fails_below_threshold():
    judge, _ = judge_with('{"score": 0.2, "reason": "Different city"}')
    assert judge.score("Lyon", "Paris") == Score(0.2, False, "Different city")


@pytest.mark.parametrize("value, passed", [(0.69, False), (0.7, True), (0.0, False), (1, True)])
def test_llm_judge_threshold_boundary(value, passed):
    judge, _ = judge_with(f'{{"score": {value}, "reason": "r"}}')
    assert judge.score("x", "y").passed is passed


def test_llm_judge_custom_threshold():
    judge = LLMJudgeScorer(model="m", pass_threshold=0.95,
                           generate=lambda p: '{"score": 0.9, "reason": "r"}')
    assert judge.score("x", "y").passed is False


@pytest.mark.parametrize("threshold", [-0.1, 1.1])
def test_llm_judge_rejects_bad_threshold(threshold):
    with pytest.raises(ValueError, match="pass_threshold"):
        LLMJudgeScorer(model="m", pass_threshold=threshold)


def test_llm_judge_finds_json_inside_extra_text():
    judge, _ = judge_with('Here you go:\n```json\n{"score": 1.0, "reason": "ok"}\n```')
    assert judge.score("x", "y").value == 1.0


def test_llm_judge_missing_reason_gets_default():
    judge, _ = judge_with('{"score": 1.0}')
    assert judge.score("x", "y").reason == "No reason given"


@pytest.mark.parametrize("reply, message", [
    ("I think it is fine", "no JSON object"),
    ("{not json}", "not valid JSON"),
    ('{"reason": "no score"}', "no numeric score"),
    ('{"score": "high"}', "no numeric score"),
    ('{"score": true}', "no numeric score"),
    ('{"score": 7, "reason": "out of ten"}', "outside 0.0-1.0"),
    ('{"score": -0.5}', "outside 0.0-1.0"),
])
def test_llm_judge_raises_on_bad_reply(reply, message):
    # A malformed judgement is an error, never a score.
    judge, _ = judge_with(reply)
    with pytest.raises(ValueError, match=message):
        judge.score("x", "y")


@pytest.mark.parametrize("expected", ["", "   "])
def test_llm_judge_empty_expected_fails_without_calling_model(expected):
    judge, prompts = judge_with('{"score": 1.0}')
    result = judge.score("anything", expected)
    assert result == Score(0.0, False, "Expected value is empty; nothing to check for")
    assert prompts == []


def test_llm_judge_braces_in_text_do_not_break_prompt():
    judge, prompts = judge_with('{"score": 1.0, "reason": "ok"}')
    judge.score('{"score": 1.0}', "a {placeholder}")
    assert "a {placeholder}" in prompts[0]
