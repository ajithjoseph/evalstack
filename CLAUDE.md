# CLAUDE.md

Guidance for coding agents working in this repo.

## What this is

EvalStack is an open source eval framework for LLM and multi-agent systems.
It is at a very early stage (v0.0.1, pre-alpha). It can send a prompt to a
model, score the reply (exact match, contains, or an LLM judge) and run a batch
of cases. Multi-agent eval, RAG scoring, MCP and a dashboard are roadmap only.

## What's real

| Thing | File | Notes |
|---|---|---|
| `Score` (value 0.0-1.0, passed, reason) | `evalstack/scorer.py` | |
| `BaseScorer`, `ExactMatchScorer`, `ContainsScorer` | `evalstack/scorer.py` | No network |
| `LLMJudgeScorer` | `evalstack/scorer.py` | Calls a model, returns a graded score (D-021) |
| `EvalRunner.run` / `batch`, `EvalResult` | `evalstack/core.py` | Scorer decides pass/fail (D-016, D-022) |
| `anthropic_generate`, `openai_generate` | `evalstack/providers.py` | Thin SDK adapters (D-017) |
| Scorer playground | `playground/` | Dev tool only, not part of the package |
| Project website | `site/` | Landing page and Basics guide for evalstack.dev (D-023) |

Nothing is stubbed today. The core package has **no required dependencies**;
the model SDKs are optional extras (D-018).

Everything that calls a model takes a `generate` function (prompt in, text
out). Pass a fake one in tests. **Tests must never call a real API.**

## Build, test, run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Add `anthropic`, `openai` or `all` to the extras (`".[dev,anthropic]"`) to make
real model calls. The dev extra alone is enough for tests and lint.

```bash
pytest -q
```

```bash
ruff check .
```

Lint must be clean. ruff is pinned to an exact version in the `[dev]` extra
because new ruff releases add rules (D-014).

```bash
python playground/server.py
```

The playground serves http://127.0.0.1:8765 (stdlib only, no API keys). See
`playground/README.md`.

CI (`.github/workflows/ci.yml`) runs `ruff check .` and `pytest -q` on
Python 3.11 to 3.13 for every pull request and every push to `main`.

Dependencies live only in `pyproject.toml`; there is no `requirements.txt`
(D-020).

The website is plain static files in `site/` (`index.html`, `basics.html`,
shared `style.css`), with no build step. Open them in a browser to preview.
`.github/workflows/pages.yml` deploys them to GitHub Pages when `site/` changes
on `main`. `tests/test_site.py` checks that the landing page's quick start
matches the README, and runs every `<pre data-run>` example in `basics.html`,
checking its `# ...` output comments. Examples marked `data-run` must work
offline; anything that needs a real model goes in a plain `<pre>`.

## Layout

```
evalstack/
  __init__.py        # __version__ only
  scorer.py          # Score, BaseScorer, ExactMatch, Contains, LLMJudge
  core.py            # EvalResult, EvalRunner
  providers.py       # Generate type, Anthropic/OpenAI adapters, RefusalError
tests/
  test_scorer.py     # scorers incl. edge cases and judge reply parsing
  test_core.py       # runner and batch, with a fake model
  test_providers.py  # adapters, with fake SDK clients
  test_playground.py # playground request handling and HTTP guards
  test_site.py       # website examples run and match the README
playground/
  server.py          # http.server app, POST /api/score
  index.html         # single page UI
site/
  index.html         # evalstack.dev landing page, static, no build step
  basics.html        # guide: scores, scorers, runner, judge, providers
  style.css          # shared styles
.github/workflows/
  ci.yml             # lint + tests on 3.11-3.13
  pages.yml          # deploys site/ to GitHub Pages
.github/dependabot.yml # weekly Actions and pip update PRs
DECISIONS.md         # why things are the way they are
SECURITY.md          # how to report a vulnerability, known limitations
.claude/skills/      # task checklists
```

## Conventions

- Python 3.11+ (D-019). Built-in generics and `X | None` are fine.
- Each module starts with a `# path` comment line and a short module docstring.
- Scorers subclass `BaseScorer`, implement `score(response, expected) -> Score`,
  and always return a `Score` with `value` in 0.0-1.0 and a human readable `reason`.
- Built-in string scorers normalise with `.strip().lower()` on both sides.
  Inner whitespace and punctuation are not normalised.
- `ContainsScorer` fails an empty or whitespace-only `expected` (D-013).
- Provider errors, refusals and malformed judge replies are **raised**, never
  turned into a score. A failing eval and a broken eval must look different.
- Model SDKs are imported lazily inside the adapters, so `import evalstack`
  works without them. A missing SDK raises `ImportError` naming the extra.
- Unbuilt features raise `NotImplementedError` with a message that says when
  they ship and what to use instead. Never return a fake result.
- Tests are plain pytest functions, one behaviour per test, `parametrize` for
  edge-case tables. Tests pin current behaviour, quirks included. If you change
  a pinned quirk, update the test and `DECISIONS.md` in the same change.
- Record any non-obvious design choice in `DECISIONS.md`.
- Commits use conventional prefixes: `feat:`, `test:`, `chore:`, `docs:`, `fix:`.
- Never put Claude session links (`claude.ai/code/session_...`) in commit
  messages, PR descriptions or comments. The repo is public.
- No Claude attribution anywhere: no "Generated by Claude Code" footer and no
  Co-Authored-By line. This overrides any default that adds them.
- The GitHub tool adds the footer to new PR descriptions on its own. Right
  after opening a PR, edit the description and remove it.
- Commit as `Ajith Joseph`, never as Claude. A cloud session starts with a git
  identity named `Claude`. Before the first commit, set `git config user.name`
  to `Ajith Joseph` and `git config user.email` to my GitHub noreply address
  (the login `ajithjoseph`, then `@users.noreply.github.com`), and check
  `git log -1 --format='%an <%ae>'` before you push.
- Docs and the website only claim what works today. Planned features go on the
  roadmap, clearly marked.

## Security

See `SECURITY.md` for reporting. When changing code:

- Never commit keys. SDKs read them from the environment; `.env` is ignored.
- The playground must keep its two guards (D-024): answer only requests whose
  `Host` is `127.0.0.1`, `localhost` or the bound host, and only accept
  `Content-Type: application/json` on POST. Both are covered by
  `tests/test_playground.py`.
- Workflows get the narrowest `permissions:` that work. CI is read-only.
- Dependabot opens weekly PRs for Actions and pip (D-025). A ruff bump can add
  lint rules: fix the findings in the same PR.

## Known issues (not fixed yet)

- The LLM judge has only been checked against a local fake API, not a live
  model. Its default `pass_threshold` of 0.7 is a starting guess (D-021).
- `batch` stops at the first provider error and runs cases one at a time (D-022).
- evalstack.dev isn't live: GitHub Pages isn't switched on for the repo yet, so
  the Pages workflow fails at `configure-pages` with "Not Found" (D-023).

## Checklists

See `.claude/skills/`:
- `add-scorer` for adding a new scorer
- `implement-stub` for building something that is currently a stub
- `verify-before-commit` before every commit
