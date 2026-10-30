# EvalStack

> LLM apps are easy to build and hard to trust.
> EvalStack gives you the eval infrastructure to know the difference.

Open source evaluation and observability framework for production 
multi-agent AI systems.

## Why this exists

Most teams ship an LLM app, manually test a few prompts, and call 
it done. Then it fails silently in production. EvalStack gives you:

- A structured eval loop for single and multi-agent workflows
- Hallucination and faithfulness scoring out of the box
- Production observability without vendor lock-in
- MCP compatible from day one

## Status

Early. Building in public starting July 2026. 
Follow the build log → [LinkedIn](https://www.linkedin.com/in/theajithjoseph/) | [EvalStack](https://evalstack.dev)

## Quick start

```bash
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

## Roadmap

- [x] Core eval loop (single LLM call)
- [ ] Multi-agent workflow eval
- [ ] RAG retrieval quality scoring
- [ ] MCP server integration
- [ ] Production dashboard

## Contributing

PRs welcome. See `CLAUDE.md` for how to build, test and run the project, and
`DECISIONS.md` for why things are the way they are.
