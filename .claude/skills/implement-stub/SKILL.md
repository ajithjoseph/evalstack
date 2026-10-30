---
name: implement-stub
description: Checklist for replacing a NotImplementedError stub with a real implementation, especially anything that calls a model. Use when asked to build a stubbed or roadmap feature.
---

# Implement a stub

1. **Read `DECISIONS.md` first**, especially D-016 (the scorer owns pass/fail),
   D-017 (the `generate` interface) and D-018 (SDKs are optional extras).
2. **Pick the model id from current provider docs**, not from the docstring
   example. Keep it configurable. Never hard-code a key.
3. **Keep unit tests offline.** They must not call a real API. Take a
   `generate` function (or an SDK client) so tests can pass a fake. Gate any
   live test behind an env var and skip it when credentials are missing.
4. **Replace the stub tests.** Any test that checks for `NotImplementedError`
   must be removed or rewritten in the same change, not left failing.
5. **Errors**: decide and test what happens on API errors, timeouts and
   malformed model output. Never turn an error into a passing score.
6. **Playground**: anything wired into the playground must still work with no
   SDK or key installed (show a clear message instead of crashing).
7. **Docs**: update What's real and Known issues in `CLAUDE.md`, the README
   roadmap if a box is now done, and add a `DECISIONS.md` entry.
8. Run the `verify-before-commit` checklist.
