"""Thin wrapper around the OpenAI chat API.

Why a wrapper? The rest of the project (agent loop, tests) only sees plain
dicts and one error type. Retries, timeouts, and API details stay here.
"""

import time

import openai

from startscore.config import Config


class LLMError(Exception):
    """Raised when the LLM call fails and cannot be recovered."""


_RETRYABLE = (
    openai.APIConnectionError, 
    openai.RateLimitError, 
    openai.InternalServerError, 
)


def make_client(config: Config) -> openai.OpenAI:
    return openai.OpenAI(api_key=config.api_key, timeout=config.timeout, max_retries=0)


def call_llm(
    messages: list[dict],
    config: Config,
    tools: list[dict] | None = None,
    client=None,
    max_retries: int = 3,
    backoff_seconds: float = 1.0,
) -> dict:
    """Send messages (and optional tool schemas) to the model.

    Returns a plain dict:
        {"content": str | None, "tool_calls": [{"id", "name", "arguments"}]}
    ``arguments`` is the raw JSON string from the model. It is NOT trusted yet:
    week 13 will parse and validate it before running any tool.

    Raises LLMError if all attempts fail or the error is not temporary.
    """
    if not messages:
        raise LLMError("messages must not be empty.")

    client = client or make_client(config)
    kwargs = {"model": config.model, "messages": messages}
    if tools:
        kwargs["tools"] = tools

    last_error: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:
            response = client.chat.completions.create(**kwargs)
            return _to_dict(response)
        except _RETRYABLE as error:
            last_error = error
            if attempt < max_retries:
                time.sleep(backoff_seconds * 2 ** (attempt - 1))  
        except openai.AuthenticationError as error:
            raise LLMError("Authentication failed. Check LLM_API_KEY.") from error
        except openai.APIStatusError as error:
            raise LLMError(f"The API rejected the request ({error.status_code}).") from error

    raise LLMError(
        f"LLM request failed after {max_retries} attempts: {type(last_error).__name__}."
    ) from last_error


def _to_dict(response) -> dict:
    if not response.choices:
        raise LLMError("The API returned no choices.")
    message = response.choices[0].message
    tool_calls = [
        {"id": call.id, "name": call.function.name, "arguments": call.function.arguments}
        for call in (message.tool_calls or [])
    ]
    return {"content": message.content, "tool_calls": tool_calls}