"""Tests for config and the LLM client. No real API calls: a fake client is used."""

from types import SimpleNamespace

import openai
import pytest

try:  
    import httpx
except ImportError:  
    import httpx2 as httpx

from startscore import cli
from startscore.config import Config, ConfigError, load_config
from startscore.llm_client import LLMError, call_llm

CONFIG = Config(api_key="test-key", model="test-model", timeout=5.0)
REQUEST = httpx.Request("POST", "https://api.openai.com/v1/chat/completions")


def fake_response(content="Hello", tool_calls=None):
    message = SimpleNamespace(content=content, tool_calls=tool_calls)
    return SimpleNamespace(choices=[SimpleNamespace(message=message)])


class FakeClient:
    """Plays a list of results: an Exception is raised, anything else is returned."""

    def __init__(self, results):
        self.results = list(results)
        self.calls = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        result = self.results.pop(0)
        if isinstance(result, Exception):
            raise result
        return result


def status_error(cls, code):
    return cls("error", response=httpx.Response(code, request=REQUEST), body=None)




def test_call_llm_returns_text_answer():
    client = FakeClient([fake_response("Traction means early proof of demand.")])
    reply = call_llm([{"role": "user", "content": "hi"}], CONFIG, client=client)
    assert reply == {"content": "Traction means early proof of demand.", "tool_calls": []}
    assert client.calls[0]["model"] == "test-model"
    assert "tools" not in client.calls[0]


def test_call_llm_returns_tool_calls_as_plain_dicts():
    call = SimpleNamespace(
        id="call_1",
        function=SimpleNamespace(name="get_startup_info", arguments='{"startup_id": "S001"}'),
    )
    client = FakeClient([fake_response(content=None, tool_calls=[call])])
    tools = [{"type": "function", "function": {"name": "get_startup_info"}}]
    reply = call_llm([{"role": "user", "content": "x"}], CONFIG, tools=tools, client=client)
    assert reply["tool_calls"] == [
        {"id": "call_1", "name": "get_startup_info", "arguments": '{"startup_id": "S001"}'}
    ]
    assert client.calls[0]["tools"] == tools


def test_call_llm_retries_temporary_error_then_succeeds():
    client = FakeClient(
        [openai.APIConnectionError(request=REQUEST), fake_response("OK after retry")]
    )
    reply = call_llm([{"role": "user", "content": "hi"}], CONFIG, client=client, backoff_seconds=0)
    assert reply["content"] == "OK after retry"
    assert len(client.calls) == 2


def test_call_llm_gives_up_after_max_retries():
    errors = [status_error(openai.RateLimitError, 429) for _ in range(3)]
    client = FakeClient(errors)
    with pytest.raises(LLMError, match="after 3 attempts"):
        call_llm([{"role": "user", "content": "hi"}], CONFIG, client=client, backoff_seconds=0)
    assert len(client.calls) == 3


def test_call_llm_does_not_retry_authentication_error():
    client = FakeClient([status_error(openai.AuthenticationError, 401)])
    with pytest.raises(LLMError, match="Authentication"):
        call_llm([{"role": "user", "content": "hi"}], CONFIG, client=client, backoff_seconds=0)
    assert len(client.calls) == 1


def test_call_llm_rejects_empty_messages():
    with pytest.raises(LLMError, match="must not be empty"):
        call_llm([], CONFIG, client=FakeClient([]))



@pytest.fixture
def clean_env(monkeypatch):
    monkeypatch.setattr("startscore.config.load_dotenv", lambda *args, **kwargs: None)
    for name in ("LLM_API_KEY", "LLM_MODEL", "LLM_TIMEOUT"):
        monkeypatch.delenv(name, raising=False)
    return monkeypatch


def test_load_config_requires_api_key(clean_env):
    with pytest.raises(ConfigError, match="LLM_API_KEY"):
        load_config()


def test_load_config_uses_defaults(clean_env):
    clean_env.setenv("LLM_API_KEY", "abc")
    config = load_config()
    assert (config.api_key, config.model, config.timeout) == ("abc", "gpt-5.6-luna", 30.0)


def test_load_config_rejects_bad_timeout(clean_env):
    clean_env.setenv("LLM_API_KEY", "abc")
    clean_env.setenv("LLM_TIMEOUT", "soon")
    with pytest.raises(ConfigError, match="LLM_TIMEOUT"):
        load_config()




def test_cli_prints_error_without_api_key(clean_env, capsys):
    assert cli.main(["What is traction?"]) == 1
    assert "LLM_API_KEY" in capsys.readouterr().err


def test_cli_needs_a_question(capsys):
    assert cli.main([]) == 2
    assert "Usage" in capsys.readouterr().err