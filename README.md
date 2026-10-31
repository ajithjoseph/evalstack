# EvalStack

> LLM apps are easy to build and hard to trust.
> EvalStack gives you the eval infrastructure to know the difference.

Open source evaluation and observability framework for production 
multi-agent AI systems.

## Why this exists

Most teams ship an LLM app, manually test a few prompts, and call
it done. Then it fails silently in production.

**What works today:**

- An eval loop for single LLM calls: send a prompt, score the reply, get
  pass/fail with a reason, one case or a batch
- Exact-match, contains and LLM-judge scorers
- Anthropic and OpenAI built in, or any function that takes a prompt and
  returns text, so there's no vendor lock-in

**Where it's going** (see the roadmap below): multi-agent workflow eval,
hallucination and faithfulness scoring, RAG retrieval scoring, MCP
integration and a production dashboard.

## Status

Early: v0.0.1, pre-alpha. Building in public since July 2026.
Follow the build log on [LinkedIn](https://www.linkedin.com/in/theajithjoseph/).

## Quick start

EvalStack isn't on PyPI yet, so install it from a clone (Python 3.11+):

```bash
git clone https://github.com/ajithjoseph/evalstack
cd evalstack
pip install -e ".[anthropic]"
```

```python
from evalstack.core import EvalRunner
from evalstack.scorer import LLMJudgeScorer

runner = EvalRunner(model="claude-opus-5-5")
result = runner.run("What is the capital of France?", expected="Paris")
print(result.passed, result.metadata["reason"])

# Grade meaning instead of matching text:
judge = LLMJudgeScorer(model="claude-opus-5-5")
runner = EvalRunner(model="claude-opus-5-5", scorer=judge)
```

Use `provider="openai"` (with `pip install -e ".[openai]"`) for OpenAI models,
or pass `generate=` any function that takes a prompt and returns text.

## Learn more

- **Basics guide:** scores, scorers, the runner, the judge and providers, in
  [`site/basics.html`](site/basics.html). It will be at evalstack.dev once the
  site is live.
- **Playground:** try scorers in your browser with no API key:
  `python playground/server.py`. See [`playground/README.md`](playground/README.md).
- **Design decisions:** [`DECISIONS.md`](DECISIONS.md).

## Roadmap

- [x] Core eval loop (single LLM call)
- [ ] Multi-agent workflow eval
- [ ] RAG retrieval quality scoring
- [ ] MCP server integration
- [ ] Production dashboard

## Contributing

PRs welcome. See [`CLAUDE.md`](CLAUDE.md) for how to build, test and run the
project. Every PR runs lint and tests on Python 3.11 to 3.13.

## Security

Please report vulnerabilities privately. See [`SECURITY.md`](SECURITY.md).
