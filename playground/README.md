# Scorer playground

A tiny local web page for trying EvalStack scorers by hand. Type a response and
an expected value, pick a scorer, and see the score, pass/fail and reason.

Standard library only. No API keys, no network calls, binds to `127.0.0.1`.

## Run it

From the repo root, with the project installed (`pip install -e ".[dev]"`):

```bash
python playground/server.py
```

Then open http://127.0.0.1:8765. Use `--port` to pick another port.

`LLMJudgeScorer` is listed but is still a stub, so it shows "NOT IMPLEMENTED"
with the stub's message instead of a score.

## API

- `GET /api/scorers` returns the scorer names.
- `POST /api/score` with `{"scorer": "contains", "response": "...", "expected": "..."}`
  returns `{"scorer", "value", "passed", "reason"}`.
