# tests/test_providers.py

import sys
from types import SimpleNamespace

import pytest

from evalstack.providers import (
    RefusalError,
    anthropic_generate,
    make_generate,
    openai_generate,
)


class FakeAnthropic:
    """Records requests and returns a canned Messages API response."""

    def __init__(self, text="Paris", stop_reason="end_turn"):
        self.calls = []
        reply = SimpleNamespace(
            stop_reason=stop_reason,
            content=[SimpleNamespace(type="thinking", thinking=""),
                     SimpleNamespace(type="text", text=text)],
        )

        def create(**kwargs):
            self.calls.append(kwargs)
            return reply

        self.messages = SimpleNamespace(create=create)
        self.beta = SimpleNamespace(messages=SimpleNamespace(create=create))


class FakeOpenAI:
    def __init__(self, content="Paris", refusal=None):
        self.calls = []
        message = SimpleNamespace(content=content, refusal=refusal)

        def create(**kwargs):
            self.calls.append(kwargs)
            return SimpleNamespace(choices=[SimpleNamespace(message=message)])

        self.chat = SimpleNamespace(completions=SimpleNamespace(create=create))


def test_anthropic_returns_text_blocks_only():
    client = FakeAnthropic("Paris")
    assert anthropic_generate("claude-haiku-4-5", client=client)("q") == "Paris"
    assert client.calls == [{
        "model": "claude-haiku-4-5",
        "max_tokens": 16000,
        "messages": [{"role": "user", "content": "q"}],
    }]


@pytest.mark.parametrize("model", ["claude-opus-5-5", "claude-fable-5-1",
                                   "claude-opus-5", "claude-sonnet-5-5"])
def test_anthropic_opts_into_refusal_fallback_where_supported(model):
    client = FakeAnthropic()
    anthropic_generate(model, client=client)("q")
    call = client.calls[0]
    assert call["fallbacks"] == "default"
    assert call["betas"] == ["server-side-fallback-2026-07-01"]


def test_anthropic_refusal_raises():
    client = FakeAnthropic(stop_reason="refusal")
    with pytest.raises(RefusalError):
        anthropic_generate("claude-opus-5-5", client=client)("q")


def test_openai_returns_message_content():
    client = FakeOpenAI("Paris")
    assert openai_generate("gpt-x", client=client)("q") == "Paris"
    assert client.calls == [{"model": "gpt-x",
                             "messages": [{"role": "user", "content": "q"}]}]


def test_openai_empty_content_is_empty_string():
    assert openai_generate("gpt-x", client=FakeOpenAI(None))("q") == ""


def test_openai_refusal_raises():
    with pytest.raises(RefusalError, match="not allowed"):
        openai_generate("gpt-x", client=FakeOpenAI(None, refusal="not allowed"))("q")


@pytest.mark.parametrize("provider, factory, extra", [
    ("anthropic", anthropic_generate, "evalstack[anthropic]"),
    ("openai", openai_generate, "evalstack[openai]"),
])
def test_missing_sdk_names_the_extra(monkeypatch, provider, factory, extra):
    monkeypatch.setitem(sys.modules, provider, None)  # makes the import fail
    with pytest.raises(ImportError, match=extra.replace("[", r"\[").replace("]", r"\]")):
        factory("m")


def test_make_generate_unknown_provider():
    with pytest.raises(ValueError, match="Unknown provider 'nope'"):
        make_generate("nope", "m")
