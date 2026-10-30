# Scorer playground

A tiny local web page for trying EvalStack scorers by hand. Type a response and
an expected value, pick a scorer, and see the score, pass/fail and reason.

Standard library only, binds to `127.0.0.1`. The string scorers need no API
keys and make no network calls.

## Run it

From the repo root, with the project installed (`pip install -e ".[dev]"`):

```bash
python playground/server.py
```

Then open http://127.0.0.1:8765. Use `--port` to pick another port.

`LLMJudgeScorer` calls a real model, so it costs money per click. It needs the
Anthropic SDK and credentials (`ANTHROPIC_API_KEY`, or an `ant auth login`
profile):

```bash
pip install -e ".[dev,anthropic]"
```

It uses `claude-opus-5-5` unless `EVALSTACK_JUDGE_MODEL` is set. Without the
SDK it shows "UNAVAILABLE" with install instructions; API errors show as an
error message, never as a score.

## API

- `GET /api/scorers` returns the scorer names.
- `POST /api/score` with `{"scorer": "contains", "response": "...", "expected": "..."}`
  returns `{"scorer", "value", "passed", "reason"}`.
