---
name: verify-before-commit
description: Checks to run before every commit in evalstack (install, tests, lint, playground smoke test, diff review). Use before committing or opening a PR.
---

# Verify before commit

Run from the repo root inside the venv (`source .venv/bin/activate`).

1. **Install still works**
   ```bash
   pip install -e ".[dev]"
   ```
2. **Tests pass**
   ```bash
   pytest -q
   ```
   All green. No skip or xfail added to get there.
3. **Lint**
   ```bash
   ruff check .
   ```
   Must be clean. CI runs the same check and fails on any finding.
4. **Playground smoke test** (only if `evalstack/` or `playground/` changed)
   ```bash
   python playground/server.py --port 8765
   ```
   In another shell:
   ```bash
   curl -s -X POST http://127.0.0.1:8765/api/score -d '{"scorer":"contains","response":"Paris!","expected":"paris"}'
   ```
   Expect `"passed": true`. Stop the server with Ctrl+C.
5. **Review the diff**
   ```bash
   git status && git diff
   ```
   - no secrets, API keys, `.venv/` or `__pycache__/`,
   - no stray debug prints,
   - no test calls a real model API,
   - stubs still raise `NotImplementedError` unless this change implements them.
6. **Docs in sync**: `CLAUDE.md` (What's real, Known issues) and
   `DECISIONS.md` reflect the change.
7. **Commit message** uses a conventional prefix (`feat:`, `fix:`, `test:`,
   `docs:`, `chore:`) and says why, not just what.
