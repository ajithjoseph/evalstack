# CLAUDE.md

Guidance for coding agents working in this repo.

## What this is

EvalStack is an open source eval framework for LLM and multi-agent systems.
It is at a very early stage (v0.0.1, pre-alpha). Today the only working code is
two string scorers. The eval loop and the LLM judge are stubs.

## Real vs stubbed

| Thing | File | Status |
|---|---|---|
| `Score` dataclass (value 0.0-1.0, passed, reason) | `evalstack/scorer.py` | Real |
| `BaseScorer` abstract base | `evalstack/scorer.py` | Real |
| `ExactMatchScorer` | `evalstack/scorer.py` | Real |
| `ContainsScorer` | `evalstack/scorer.py` | Real |
| `LLMJudgeScorer.score` | `evalstack/scorer.py` | Stub, raises `NotImplementedError` |
| `EvalResult` dataclass | `evalstack/core.py` | Real (data only) |
| `EvalRunner.__init__` | `evalstack/core.py` | Real (stores `model`, `threshold`) |
| `EvalRunner.run` / `batch` | `evalstack/core.py` | Stub, raises `NotImplementedError` |
| Scorer playground | `playground/` | Real, dev tool only, not part of the package |

`anthropic`, `openai` and `pydantic` are declared runtime dependencies but
nothing imports them yet.

## Build, test, run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

```bash
pytest -q
```

```bash
ruff check .
```

```bash
python playground/server.py
```

The playground serves http://127.0.0.1:8765 (stdlib only, no API keys). See
`playground/README.md`.

## Layout

```
evalstack/
  __init__.py        # __version__ only
  scorer.py          # Score, BaseScorer, ExactMatch, Contains, LLMJudge (stub)
  core.py            # EvalResult, EvalRunner (stub)
tests/
  test_scorer.py     # scorer behaviour incl. edge cases
  test_core.py       # EvalResult, EvalRunner stub behaviour
  test_playground.py # playground request handling
playground/
  server.py          # http.server app, POST /api/score
  index.html         # single page UI
DECISIONS.md         # why things are the way they are
.claude/skills/      # task checklists
```

## Conventions

- Python 3.10+. Built-in generics (`list[dict]`) are fine.
- Each module starts with a `# path` comment line and a short module docstring.
- Scorers subclass `BaseScorer`, implement `score(response, expected) -> Score`,
  and always return a `Score` with `value` in 0.0-1.0 and a human readable `reason`.
- Built-in string scorers normalise with `.strip().lower()` on both sides.
  Inner whitespace and punctuation are not normalised.
- `ContainsScorer` fails an empty or whitespace-only `expected` (D-013).
- Unbuilt features raise `NotImplementedError` with a message that says when
  they ship and what to use instead. Never return a fake result.
- Tests are plain pytest functions, one behaviour per test, `parametrize` for
  edge-case tables. Tests pin current behaviour, quirks included. If you change
  a pinned quirk, update the test and `DECISIONS.md` in the same change.
- Record any non-obvious design choice in `DECISIONS.md`.
- Commits use conventional prefixes: `feat:`, `test:`, `chore:`, `docs:`, `fix:`.

## Known issues (not fixed yet)

- `LLMJudgeScorer` error says it "ships in v0.0.1", but the package is already
  0.0.1 and its own docstring says v0.1.
- `EvalRunner.run` docstring says v0.1 ships "July 2026", which has passed.
- `EvalRunner.threshold` is stored but unused, and overlaps with `Score.passed`
  (D-008).
- `ruff check .` reports 3 pre-existing findings in `evalstack/`
  (`UP045` twice in `core.py`, `PIE790` in `scorer.py`). New code should add none.
- `requirements.txt` duplicates `pyproject.toml`. `pyproject.toml` is the
  source of truth (D-011).

## Checklists

See `.claude/skills/`:
- `add-scorer` for adding a new scorer
- `implement-stub` for replacing a `NotImplementedError` stub
- `verify-before-commit` before every commit
