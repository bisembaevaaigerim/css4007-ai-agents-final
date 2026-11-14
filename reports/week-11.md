# Semester Week 11 Progress Report

## Completed Work

- Set up the Python project: `requirements.txt`, `pytest.ini`, `.env.example` (the real `.env` is in `.gitignore`).
- Wrote `config.py`: reads the API key, model name and timeout from environment variables, and gives a clear error if the key is missing or the timeout is wrong.
- Wrote `llm_client.py` with `call_llm()`: it sends messages (and later tool schemas) to the model, retries temporary errors, and returns a plain dict with the text and the tool calls.
- Wrote `cli.py`: the first working request. The user types a question, the model answers.
- Wrote 11 automated tests with a fake client (no real API calls).
- Wrote basic documentation in `STARTSCORE.md`: setup, run, test, code map  and design decisions.

## Important Commits

- Commit hash: 2e45ed6
- Description: Set up Python project and configuration
- Link: https://github.com/bisembaevaaigerim/css4007-ai-agents-final/commit/2e45ed6

- Commit hash: 71455e7
- Description: Add LLM client with retries and a command line request
- Link: https://github.com/bisembaevaaigerim/css4007-ai-agents-final/commit/71455e7

- Commit hash: 18434fc
- Description: Add tests for the LLM client and project documentation
- Link: https://github.com/bisembaevaaigerim/css4007-ai-agents-final/commit/18434fc

## Current Functionality

The application can answer a plain question with the real model:

```
python -m startscore.cli "What does traction mean for a startup?"
```

Tools, scoring, and the agent loop are not implemented yet. The 11 tests pass with a fake client.

## Problems Encountered

- Which errors should be retried? Retrying a wrong API key only wastes time.
- How to test API code without a real key, network, or cost.
- The `openai` package uses a different HTTP library (`httpx` or `httpx2`) in different versions, and my first test file failed to import.

## Solutions

- Only temporary errors are retried (network, rate limit 429, server 5xx). Authentication errors and bad requests (4xx) stop at once with a clear `LLMError`.
- `call_llm()` accepts a `client` argument, so tests pass a fake client that returns prepared answers or raises prepared errors.
- The test file imports whichever HTTP library is installed.

## What I Learned

- A chat request is a list of messages with roles (system, user, assistant), and the model returns one assistant message.
- Retry with exponential backoff (1s, 2s, 4s) is a standard way to handle temporary API errors.
- Why secrets stay in environment variables and `.env`, and why the repository has only `.env.example`.
- The model returns tool call arguments as a JSON string. This string must be parsed and validated before any tool runs. I will do this in week 13.

## Next Week

- Create the mock data files (`data/startups.json`, `data/markets.json`).
- Implement `load_data`, `get_startup_info`, and `get_market_data`.
- Implement the scoring rules in `scoring.py` and write unit tests for them.
- Add validation of inputs and outputs.