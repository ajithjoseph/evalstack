# Decisions

A running record of design decisions. Each entry: context, options, what was
chosen and why, and when to revisit. Add new entries at the bottom; don't
rewrite old ones. If a decision is reversed, add a new entry that supersedes it.

Entries D-001 to D-006 and D-008/D-009 describe choices already visible in the
code before this file existed. The reasoning for those is inferred from the code,
not from the author, so the author should correct anything that's wrong.

---

## D-001: Scorers are pluggable classes behind one abstract method

- **Context:** Different evals need different scoring (exact, contains, LLM judge, later RAG/faithfulness).
- **Options:** (a) plain functions, (b) an abstract base class, (c) a Protocol.
- **Chosen:** (b) `BaseScorer(ABC)` with one method `score(response: str, expected: str) -> Score`.
- **Why:** Gives a single contract, lets scorers hold config (e.g. a judge model) in `__init__`, and fails fast at instantiation if `score` is missing.
- **Revisit when:** a scorer needs more than `(response, expected)`, e.g. the prompt, retrieved context or a full agent trace. That signature change will touch every scorer.

## D-002: `Score` is a plain dataclass (value, passed, reason)

- **Context:** Scorers need a uniform result.
- **Options:** dataclass, pydantic model, tuple/dict.
- **Chosen:** `@dataclass Score(value: float, passed: bool, reason: str)`, value meant to be 0.0-1.0.
- **Why:** Zero dependencies, cheap, readable. Note that the 0.0-1.0 range is only a comment, not enforced.
- **Revisit when:** results need serialisation/validation (logging, dashboard). Pydantic is already a dependency (D-005).

## D-003: Built-in string scorers normalise with `.strip().lower()`

- **Context:** LLM output often differs from the reference only by case or surrounding whitespace.
- **Options:** no normalisation, strip+lower, aggressive (punctuation, inner whitespace, Unicode casefold).
- **Chosen:** strip+lower on both sides, nothing else.
- **Why:** Simple and predictable. Consequences pinned in tests: `"Paris."` does not exact-match `"Paris"`, inner double spaces don't match, `"STRASSE"` vs `"straße"` doesn't match (`lower`, not `casefold`), and `ContainsScorer` matches plain substrings (`"Parisian"` contains `"Paris"`).
- **Revisit when:** real eval sets show false fails on punctuation or Unicode. Consider making normalisation a constructor option rather than changing the default.

## D-004: Unbuilt features exist as stubs that raise `NotImplementedError`

- **Context:** Building in public; the API shape is published before it works.
- **Options:** leave classes out until ready, or ship stubs.
- **Chosen:** stubs (`LLMJudgeScorer.score`, `EvalRunner.run`, `EvalRunner.batch`) that raise with a "ships in ..." message.
- **Why:** Shows the intended API and fails loudly instead of returning a fake score.
- **Revisit when:** each feature ships. Tests in `tests/test_core.py` and `tests/test_scorer.py` pin the stub behaviour and must be replaced with real tests at that point. The stub messages were made consistent (all say v0.1) on 2026-10-30.

## D-005: `anthropic`, `openai`, `pydantic` are hard runtime dependencies

- **Context:** The roadmap needs LLM calls; both major SDKs are listed.
- **Options:** hard deps, optional extras (`evalstack[anthropic]`), or no SDK (raw HTTP).
- **Chosen:** hard deps in `[project].dependencies`.
- **Why:** Simplest for users once the LLM features land.
- **Revisit:** soon. Nothing imports these today, so every install pulls two large SDKs for no benefit. Moving them to extras before v0.1 avoids a breaking change later.

## D-006: Build with setuptools, flat layout, package listed explicitly

- **Context:** The original `build-backend = "setuptools.backends.legacy:build"` doesn't exist; `pip install -e .` failed with `BackendUnavailable: Cannot import 'setuptools.backends.legacy'`.
- **Options:** `setuptools.build_meta`, switch to hatchling, or poetry.
- **Chosen (2026-10-29):** `setuptools.build_meta`, plus `[tool.setuptools] packages = ["evalstack"]`.
- **Why:** Smallest fix that keeps setuptools. The explicit package list stops setuptools auto-discovery from picking up `playground/` or `tests/` as packages.
- **Revisit when:** moving to a `src/` layout or adding package data.

## D-007: `ContainsScorer` passes when `expected` is empty or whitespace-only (superseded by D-013)

- **Context:** `"" in s` is True for every string, and `expected` is stripped first, so `expected="   "` passes any response, including an empty one. Found while writing edge-case tests.
- **Options:** (a) keep, (b) fail with a reason like "Expected value is empty", (c) raise `ValueError`.
- **Chosen (for now):** (a), pinned by `test_contains_empty_expected_always_passes` so nobody changes it by accident.
- **Why:** Changing scorer semantics is the author's call, not a test-writing task's. But (a) is a silent false pass, which is the worst failure for an eval tool. Leaning (b).
- **Revisit:** before v0.1. When changed, update the test and this entry.

## D-008: `EvalRunner` has a `threshold` (default 0.8) separate from `Score.passed` (open)

- **Context:** Scorers already decide `passed`; the runner also takes `threshold=0.8` but doesn't use it yet.
- **Options:** runner overrides pass/fail with `score.value >= threshold`; scorer stays the only judge; or scorers take their own threshold.
- **Chosen:** not decided. Both exist today.
- **Revisit:** when implementing `EvalRunner.run`. Two sources of truth for pass/fail will confuse users. For binary scorers a threshold of 0.8 is meaningless.

## D-009: Python 3.10+

- **Context:** Code uses built-in generics (`list[dict]`).
- **Chosen:** `requires-python = ">=3.10"`.
- **Revisit when:** 3.10 reaches end of life (Oct 2026), which is about now. Bumping to 3.11 is cheap at this size.

## D-010: Scorer playground is stdlib-only and lives outside the package

- **Context:** Wanted a local page to try scorers by hand, with no API keys.
- **Options:** Streamlit/Gradio, Flask/FastAPI, or stdlib `http.server` + one static HTML file.
- **Chosen (2026-10-29):** stdlib `http.server` in `playground/server.py` with `playground/index.html`, bound to `127.0.0.1`, not shipped in the wheel.
- **Why:** No new dependencies, starts instantly, nothing to keep patched. It's a dev tool, so it shouldn't add weight to `pip install evalstack`. `LLMJudgeScorer` is listed and shows its `NotImplementedError` message rather than being hidden.
- **Revisit when:** it needs batch runs, history or charts. That's when a real framework, or the planned dashboard, earns its keep.

## D-011: Dev dependencies live in a `[dev]` extra; `requirements.txt` left as is

- **Context:** There was no dev dependency group in `pyproject.toml`; `requirements.txt` mixes runtime and dev deps.
- **Chosen (2026-10-29):** `[project.optional-dependencies] dev = ["pytest>=7.0.0", "ruff>=0.1.0"]`. Install with `pip install -e ".[dev]"`. Did not add `black` or `pytest-asyncio` from `requirements.txt` since nothing uses them yet.
- **Why:** One install command, and `pyproject.toml` becomes the source of truth.
- **Revisit:** delete or regenerate `requirements.txt` once the author confirms nothing depends on it.

## D-012: Tests pin current behaviour, quirks included

- **Context:** Adding edge-case tests to an early codebase with some questionable behaviour (D-007, D-003).
- **Options:** test the behaviour we wish we had (failing tests / xfail), or pin what the code does now.
- **Chosen (2026-10-29):** pin current behaviour, with a comment and a pointer here where it's questionable.
- **Why:** The suite stays green and any behaviour change becomes a deliberate, visible diff.
- **Revisit:** per quirk, as each one is decided.

## D-013: `ContainsScorer` fails when `expected` is empty or whitespace-only

- **Context:** Supersedes D-007. An empty `expected` matched every response, a silent false pass.
- **Options:** (a) keep, (b) fail with a reason, (c) raise `ValueError`.
- **Chosen (2026-10-29):** (b). Returns `Score(0.0, False, "Expected value is empty; nothing to check for")`.
- **Why:** A false pass is the worst failure for an eval tool. Failing (rather than raising) keeps a batch run going while still surfacing the bad test case in the results, and matches how scorers report every other problem: through `reason`.
- **Not changed:** `ExactMatchScorer` with both sides empty still passes, since empty equals empty is a correct exact match.
- **Revisit when:** `EvalRunner.batch` exists. If bad test data should stop a run, validate the dataset up front rather than raising inside the scorer.

## D-014: CI runs ruff and pytest on Python 3.10-3.13, with ruff pinned exactly

- **Context:** There was no CI, so nothing checked a PR except whoever ran the tests locally.
- **Options:** GitHub Actions with a version matrix, a single version, or pre-commit hooks only.
- **Chosen (2026-10-30):** `.github/workflows/ci.yml` on pull requests and pushes to `main`. It installs `.[dev]`, then runs `ruff check .` and `pytest -q` on Python 3.10, 3.11, 3.12 and 3.13. `fail-fast: false` so one version failing still shows the others. Read-only token permissions.
- **Why:** The suite runs in well under a second, so a 4-version matrix costs nothing and covers every version `requires-python` allows. ruff is pinned to `==0.17.3` because its default rule set grows between releases (0.17 flags `UP045` and `PIE790`), and an unpinned ruff would turn CI red with no code change. The 3 pre-existing findings were fixed so lint can be a real gate.
- **Revisit when:** bumping ruff (do it on purpose, fix new findings in the same PR), dropping a Python version, or when tests need API keys (keep those out of the default job).

## D-015: `requirements.txt` defers to `pyproject.toml`

- **Context:** Supersedes the "revisit" in D-011. `requirements.txt` listed its own runtime and dev dependencies, which had already drifted (`black`, `pytest-asyncio`, `httpx` were listed there but used nowhere).
- **Options:** delete it, keep both in sync by hand, or make it a one-line pointer.
- **Chosen (2026-10-30):** a one-line pointer, `-e .[dev]`.
- **Why:** One source of truth, while `pip install -r requirements.txt` keeps working for anyone used to it. `httpx` still gets installed as a dependency of `anthropic` and `openai`.
- **Revisit when:** nobody uses `requirements.txt` any more; then delete it.
