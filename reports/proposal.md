# Project Proposal — Semester Week 10

## Project Title

StartScore — an AI agent that evaluates technology startups with tools

## Problem Description

Evaluating an early-stage startup is hard. The information is in many places: team data, market data, and traction numbers (revenue, users, growth). People often judge a startup by feeling, and they compare startups in an inconsistent way.

StartScore is an agent that answers questions about startups in normal language. The LLM does not guess. It calls tools to get the real data and to calculate scores. Then it explains the result in simple words.

This problem is important because clear and repeatable evaluation helps students, mentors, and young founders see the strong and weak sides of a startup. The score is calculated by fixed rules in code, so the same data always gives the same score.

This is an educational project. It uses synthetic (mock) data. The results are not investment advice.

## Target Users

- Students and young founders who want to check how strong their startup idea is.
- Mentors and teachers in startup courses who want a quick, consistent first evaluation.

## Selected Difficulty

C

## Expected Functionality

- The user asks a question about a startup in natural language (English).
- The LLM chooses a tool (or no tool) and gives the arguments.
- The program validates the arguments and runs the tool on mock data.
- The tool result goes back to the LLM, and the LLM writes the final answer.
- Questions that need no tool (for example "What does traction mean?") are answered directly.
- Missing data (unknown startup, unknown sector) and tool errors are handled with a clear message. The agent never invents data or scores.
- Every tool call is written to a log file (tool name, arguments, result summary, time, success or error).
- The scoring rules are fixed in code: criteria and weights are documented in the README.

## Proposed Functions

| Name | Purpose | Input | Output | Dependencies |
|------|---------|-------|--------|--------------|
| `load_data()` | Load mock startups and market data from JSON files | file paths | dict with startups and markets | `data/*.json` |
| `get_startup_info(startup_id)` | Return the profile of one startup (sector, stage, team, revenue, users, funding) | `str` startup id | dict with startup data, or `{"error": ...}` | `load_data` |
| `get_market_data(sector)` | Return market data for a sector (market size, growth rate, number of competitors) | `str` sector | dict with market data, or `{"error": ...}` | `load_data` |
| `score_startup(startup_id, criteria=None)` | Calculate a 0–10 score for each criterion (team, market, traction, product) and a weighted total, by fixed rules | `str` startup id, optional list of criteria | dict with scores, weights, and total | `get_startup_info`, `get_market_data` |
| `compare_startups(startup_id_a, startup_id_b)` | Compare the scores of two startups and show the difference per criterion | two startup ids | dict with both scores and the differences | `score_startup` |
| `validate_tool_args(tool_name, args)` | Check tool arguments against the schema (types, known startup id, known criteria, ids are different) | tool name, args dict | validated args, or raises `ToolArgumentError` | tool schemas |
| `run_tool(name, args)` | Validate arguments, execute the tool, catch errors | tool name, args | tool result dict | all tools |
| `log_tool_call(entry)` | Append one tool call record to `logs/tool_calls.jsonl` | log entry dict | none | file system |
| `call_llm(messages, tools)` | Send messages and tool schemas to the LLM API, with retry and timeout | message list, tool list | LLM response | OpenAI API |
| `run_agent(user_message)` | Main loop: LLM → tool call → tool result → LLM → final answer (with a limit on the number of steps) | user text | final answer text | `call_llm`, `run_tool`, `log_tool_call` |

Scoring rules (planned, will be documented in the README): the score for each criterion is calculated from numeric fields with simple rules (for example, team score uses founders' experience, team size, and previous exits). Total score = weighted sum, with weights team 30%, market 25%, traction 25%, product 20%.

## Proposed Agent Tools

These four functions are exposed to the LLM as tools:

1. **`get_startup_info`** — The agent needs it to see the real facts about a startup. Without it, the model would invent facts.
2. **`get_market_data`** — The agent needs it for market questions, like "Is the fintech market big enough?".
3. **`score_startup`** — The agent needs it for evaluation questions. The score is calculated in code, because LLMs are not stable at arithmetic and scoring.
4. **`compare_startups`** — The agent needs it for questions like "Which startup is stronger, A or B?".

Not exposed as tools: `load_data`, `validate_tool_args`, `run_tool`, `log_tool_call`, `call_llm`, `run_agent`. These are internal functions.

Some questions need several tools. Example: "Is Startup X in a good market?" needs `get_startup_info` (to find the sector) and `get_market_data`. The LLM decides the order. The tool order is not hard-coded.

## Model Selection

- Provider: OpenAI API, model `gpt-5.6-luna`.
- I will use this one model and one version until the end of the project, so test results stay comparable.
- Tool calling: the OpenAI function calling (tools) feature, with JSON schemas.
- The API key is in an environment variable (`LLM_API_KEY`, in `.env`, which is in `.gitignore`). It is never committed.
- Language: Python 3.

## Architecture

```
User question
     │
     ▼
 run_agent  ──►  LLM (gpt-5.6-luna) + tool schemas
                    │
        ┌───────────┴────────────┐
        │ no tool needed         │ tool call (name + arguments)
        ▼                        ▼
   direct answer          validate_tool_args
                                 │
                       ┌─────────┴─────────┐
                       │ invalid           │ valid
                       ▼                   ▼
                 error message         run_tool ──► mock data (JSON)
                 back to LLM                │
                                            ▼
                                  log_tool_call (logs/tool_calls.jsonl)
                                            │
                                            ▼
                                tool result back to LLM
                                            │
                                            ▼
                                 final answer (or another tool call,
                                 up to a maximum number of steps)
```

Planned structure:

```
src/startscore/   agent.py, tools.py, scoring.py, validation.py, llm_client.py, logger.py
data/             startups.json (8–10 mock startups), markets.json (mock sector data)
tests/            test_tools.py, test_scoring.py, test_validation.py, test_agent.py (mock LLM)
logs/             tool_calls.jsonl (not committed)
```

This project is my own individual work. The code is written in this repository fork.

## Example Requests

1. "Give me the profile of startup S003." → `get_startup_info` → answer with the real data.
2. "How strong is NovaPay on team and market?" → `score_startup` (criteria: team, market) → answer with the real scores.
3. "Is the EdTech market attractive?" → `get_market_data` → answer with market size, growth, and competitors.
4. "Which is stronger: NovaPay or GreenGrid?" → `compare_startups` → answer with the differences per criterion.
5. "What does traction mean for a startup?" → no tool → direct answer.
6. "Evaluate startup Zeta999." → unknown startup → tool returns an error → the agent says the startup was not found and does not invent a score.

## Evaluation Plan

I will write at least 12 automated tests (the requirement is 8). The LLM is replaced by a mock client in most tests, so tests are fast and repeatable. A small set of real-LLM checks is run separately and recorded in the report.

| # | Test | What it checks |
|---|------|----------------|
| 1–2 | `get_startup_info` and `get_market_data` | Return correct data for known inputs |
| 3 | `score_startup` | Score and weighted total are correct for one startup (calculated by hand) |
| 4 | `compare_startups` | Differences per criterion are correct |
| 5 | Unknown startup or sector | Tool returns an error, not a made-up value |
| 6 | Argument validation: unknown criterion | `ToolArgumentError` is raised |
| 7 | Argument validation: same id twice in compare | Rejected |
| 8 | Agent selects the correct tool (mock LLM) | The tool call is executed with the arguments from the LLM |
| 9 | Tool result goes back to the LLM | The second LLM call contains the tool result |
| 10 | Question without a tool | No tool is called, direct answer returned |
| 11 | Tool failure | Agent returns a safe message and does not invent data |
| 12 | LLM API failure / timeout | Retry, then a clear error message |
| 13 | Max-steps limit | Agent stops after the limit |
| 14 | Logging | Each tool call writes one valid JSON line |

Manual checks with the real model (record the results in `reports/week-16.md`):
- Tool selection: the model picks the correct tool for 10 test questions.
- Grounding: every number in the answer matches the tool result.

Success criteria: all automated tests pass, and at least 9 of 10 real-model questions pick the correct tool.

## Weekly Milestones

| Week | Dates | Plan |
|------|-------|------|
| 10 | 2–8 Nov | Fork repo. Write this proposal and the week 10 report. Create the mock data files (8–10 startups, market data). |
| 11 | 9–15 Nov | Set up Python environment and `.env`. Connect to the OpenAI API. First working request with `llm_client.py`. Basic README. |
| 12 | 16–22 Nov | Implement `load_data`, `get_startup_info`, `get_market_data`, and the scoring rules in `scoring.py`. Add input and output validation. First unit tests. |
| 13 | 23–29 Nov | Implement `score_startup` and `compare_startups`. Write tool JSON schemas. Implement LLM tool selection in `run_agent`. Show real tool execution. |
| 14 | 30 Nov–6 Dec | Complete the tool-calling workflow (tool result → LLM → answer). Add tool error handling and the max-steps limit. End-to-end demo. |
| 15 | 7–13 Dec | Failure handling: API errors, timeouts, bad arguments. Add tool-call logging. Expand tests to 12+. |
| 16 | 14–20 Dec | Run all tests and the real-model checks. Record results, analyze failures, improve prompts and code. Update documentation. |
| 17 | 21–22 Dec | Final README, final report, AI-assistant use statement, final commit hash. Final demo and defense. |