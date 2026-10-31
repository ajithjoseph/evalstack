# Security policy

## Reporting a vulnerability

Please report security issues privately through GitHub:
**Security tab → Report a vulnerability** on
https://github.com/ajithjoseph/evalstack. Don't open a public issue.

Include what you found, how to reproduce it, and what an attacker could do
with it. You should get a reply within a week.

## Supported versions

EvalStack is pre-alpha (v0.0.1). Only the latest commit on `main` gets fixes.

## What's in scope

- **The `evalstack` package**: anything that could leak API keys, make
  unintended model calls, or turn an error into a passing score.
- **The playground** (`playground/server.py`): it's a local dev tool. It binds
  to `127.0.0.1`, only answers requests addressed to `127.0.0.1` or
  `localhost`, and only accepts JSON bodies, so other web pages can't drive it
  through your browser.
- **The CI and Pages workflows** in `.github/workflows/`.

## Known limitations

- **LLM judge prompt injection.** `LLMJudgeScorer` puts the response being
  graded inside its prompt. A response written to manipulate the judge ("score
  this 1.0") might raise its own score. The prompt marks the response as data,
  which reduces but doesn't remove this. Don't treat judge scores as a security
  boundary (DECISIONS.md D-021).
- **API keys** are read by the provider SDKs from your environment. EvalStack
  never stores or logs them. Tests never call a real API.
