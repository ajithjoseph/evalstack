---
name: implement-stub
description: Checklist for replacing a NotImplementedError stub (LLMJudgeScorer, EvalRunner.run, EvalRunner.batch) with a real implementation. Use when asked to build the eval loop or the LLM judge.
---

# Implement a stub

1. **Read `DECISIONS.md` first**, especially D-004 (stubs), D-005 (LLM SDK
   dependencies) and D-008 (threshold vs `Score.passed`). Settle D-008 before
   building `EvalRunner.run`, and record the outcome.
2. **Pick the model id from current provider docs**, not from the docstring
   example. Keep it configurable. Never hard-code a key.
3. **Keep unit tests offline.** They must not call a real API. Inject the
   client (or a callable) so tests can pass a fake. Gate any live test behind
   an env var and skip it when the key is missing.
4. **Replace the stub tests.** The `NotImplementedError` tests in
   `tests/test_core.py` and `tests/test_scorer.py` must be removed or rewritten
   in the same change, not left failing.
5. **Errors**: decide and test what happens on API errors, timeouts and
   malformed model output. Never turn an error into a passing score.
6. **Playground**: if the stub was `LLMJudgeScorer`, the playground must still
   work with no API key (show a clear message instead of crashing).
7. **Docs**: update Real vs stubbed and Known issues in `CLAUDE.md`, the README
   roadmap if a box is now done, and add a `DECISIONS.md` entry.
8. Run the `verify-before-commit` checklist.
