---
name: add-scorer
description: Checklist for adding a new scorer to evalstack/scorer.py, with tests, playground wiring and docs. Use when asked to add or change a scorer.
---

# Add a scorer

1. **Decide the contract first.** Write down, before coding:
   - what `value` means (binary 0/1 or graded 0.0-1.0),
   - when `passed` is True,
   - how inputs are normalised (match the built-ins, `.strip().lower()`, unless
     there is a reason not to, and record that reason in `DECISIONS.md`),
   - what happens with empty or whitespace-only `response` and `expected`
     (see D-013 for why an empty `expected` should not pass).
2. **Implement** in `evalstack/scorer.py`:
   - subclass `BaseScorer`, implement `score(self, response: str, expected: str) -> Score`,
   - one-line class docstring saying what scores 1.0,
   - always return a `Score`, `value` within 0.0-1.0, and a `reason` a human can act on,
   - no network calls or API keys in a non-LLM scorer.
3. **Test** in `tests/test_scorer.py`:
   - a pass case and a fail case,
   - a `parametrize` table for whitespace, case, empty strings and punctuation,
   - assert the exact `reason` text for at least one pass and one fail,
   - if graded, test the boundaries (0.0, 1.0 and the pass cut-off).
4. **Wire into the playground**: add it to `SCORERS` in `playground/server.py`
   and an `<option>` in `playground/index.html`. Add one case to
   `tests/test_playground.py`.
5. **Docs**: update the Real vs stubbed table in `CLAUDE.md`. Add a
   `DECISIONS.md` entry for any non-obvious choice.
6. Run the `verify-before-commit` checklist.
