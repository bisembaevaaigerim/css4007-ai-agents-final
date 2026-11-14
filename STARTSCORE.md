# StartScore

An LLM agent that evaluates technology startups with tools. Educational project for CSS 4007 (level C). It uses mock data only. The results are not investment advice.

**Status (week 11):** the LLM client works and can answer a plain question. Tools, scoring and the agent loop are planned for weeks 12–14. See `reports/proposal.md` for the full plan.

## Setup

Requires Python 3.10 or newer.

```
python -m venv .venv
.venv\Scripts\activate          # Windows PowerShell
# source .venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
copy .env.example .env          # macOS / Linux: cp .env.example .env
```

Open `.env` and put your API key in `LLM_API_KEY`. The `.env` file is in `.gitignore`: never commit it.

| Variable | Meaning | Default |
|----------|---------|---------|
| `LLM_API_KEY` | OpenAI API key (required) | none |
| `LLM_MODEL` | Model name | `gpt-5.6-luna` |
| `LLM_TIMEOUT` | Seconds to wait for one API call | `30` |

## Run

Set `PYTHONPATH` to `src` (or run from the repository root with the command below):

```
# Windows PowerShell
$env:PYTHONPATH = "src"
python -m startscore.cli "What does traction mean for a startup?"

# macOS / Linux
PYTHONPATH=src python -m startscore.cli "What does traction mean for a startup?"
```

## Test

```
python -m pytest
```

The tests use a fake client, so they do not call the API and do not need a key.

## Code map

| File | Purpose |
|------|---------|
| `src/startscore/config.py` | Reads settings from environment variables; fails early if the key is missing |
| `src/startscore/llm_client.py` | `call_llm()`: sends messages to the model, retries temporary errors (network, rate limit, server 5xx), raises `LLMError` for the rest, returns a plain dict |
| `src/startscore/cli.py` | First working request from the command line |
| `tests/test_llm_client.py` | Tests for config, retries, error handling, and the command line |

## Design decisions

- **One wrapper for the API.** The rest of the code sees only a plain dict and one error type (`LLMError`). This makes tests easy: a fake client replaces the real one.
- **Own retry loop** (`max_retries=0` in the SDK). Retries are visible in the code and testable. Temporary errors (network, 429, 5xx) are retried with waiting 1s, 2s, 4s. Authentication errors and bad requests are not retried, because trying again cannot fix them.
- **Tool call arguments stay a raw string.** The model can send wrong or unsafe arguments, so week 13 will parse and validate them before any tool runs.