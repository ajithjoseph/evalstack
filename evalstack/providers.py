# evalstack/providers.py
"""
Model adapters for EvalStack.

Everything that calls a model takes a `Generate`: a plain function from a
prompt string to the model's text reply. That keeps the eval loop provider
neutral and lets tests pass a fake. The adapters below build a Generate for
the Anthropic and OpenAI SDKs, which are optional extras (DECISIONS.md D-017).
"""

from collections.abc import Callable
from typing import Any

Generate = Callable[[str], str]

# Models that accept server-side refusal fallbacks (`fallbacks: "default"`).
_FALLBACK_MODELS = {
    "claude-fable-5-1",
    "claude-opus-5-5",
    "claude-opus-5",
    "claude-sonnet-5-5",
}
_FALLBACK_BETA = "server-side-fallback-2026-07-01"


class RefusalError(RuntimeError):
    """The model declined to answer, so there is no response to score."""


def anthropic_generate(model: str, max_tokens: int = 16000,
                       client: Any = None) -> Generate:
    """Build a Generate that calls the Anthropic Messages API."""
    if client is None:
        try:
            import anthropic
        except ImportError:
            raise ImportError(
                "The Anthropic provider needs the anthropic SDK: "
                "pip install 'evalstack[anthropic]'"
            ) from None
        client = anthropic.Anthropic()

    def generate(prompt: str) -> str:
        request = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        if model in _FALLBACK_MODELS:
            # On a safety decline, let the API retry on its recommended model.
            message = client.beta.messages.create(
                betas=[_FALLBACK_BETA], fallbacks="default", **request
            )
        else:
            message = client.messages.create(**request)
        if message.stop_reason == "refusal":
            raise RefusalError(f"{model} declined the prompt")
        return "".join(b.text for b in message.content if b.type == "text")

    return generate


def openai_generate(model: str, client: Any = None) -> Generate:
    """Build a Generate that calls the OpenAI Chat Completions API."""
    if client is None:
        try:
            import openai
        except ImportError:
            raise ImportError(
                "The OpenAI provider needs the openai SDK: "
                "pip install 'evalstack[openai]'"
            ) from None
        client = openai.OpenAI()

    def generate(prompt: str) -> str:
        completion = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
        message = completion.choices[0].message
        if getattr(message, "refusal", None):
            raise RefusalError(f"{model} declined the prompt: {message.refusal}")
        return message.content or ""

    return generate


PROVIDERS = {
    "anthropic": anthropic_generate,
    "openai": openai_generate,
}


def make_generate(provider: str, model: str) -> Generate:
    """Build a Generate for a named provider."""
    if provider not in PROVIDERS:
        raise ValueError(
            f"Unknown provider {provider!r}; use one of {sorted(PROVIDERS)} "
            "or pass your own generate function"
        )
    return PROVIDERS[provider](model)
