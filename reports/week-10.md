# Semester Week 10 Progress Report

## Completed Work

Forked the instructor repository ardakshalkar/css4007-ai-agents-final to my account.
Read the README, the C-level requirements (C.md), the calendar, and the grading rules.
Chose level C and the project idea: StartScore, an agent that evaluates technology startups with tools on mock data.
Compared several project ideas and chose this one because it needs real tools (data lookup and scoring) and is easy to test.
Wrote the project proposal in reports/proposal.md: problem, users, functions, four agent tools, model, architecture, example requests, evaluation plan, and milestones for weeks 10–17.

## Important Commits

Commit hash: 78592be8d076ed651eed733b9af2109a04ea4fea
Description: Add StartScore proposal and week 10 report
Link: https://github.com/bisembaevaaigerim/css4007-ai-agents-final/commit/78592be8d076ed651eed733b9af2109a04ea4fea

## Current Functionality

The application code is not started yet. This week was planning. The repository has the completed proposal and the first report.

## Problems Encountered

It was not clear how to make the evaluation "real" and not just an opinion of the LLM.
I had to decide how to make tool selection real and not hard-coded.
I had to decide how to make the agent safe, so it does not invent scores for startups that do not exist.

## Solutions

The scores are calculated in Python by fixed rules (criteria and weights), and the LLM only explains the result.
The LLM chooses the tool through the function calling API, and there is no keyword matching in my code.
Tools return an explicit error for unknown startups, and the agent must tell the user that the data is missing.
I planned four tools (get_startup_info, get_market_data, score_startup, compare_startups). The requirement is two, so this gives a safety margin.

## What I Learned

How tool calling works: the program sends tool schemas to the model, the model returns a tool name and arguments, the program runs the tool and the result goes back to the model for the final answer.
Why tool arguments must be validated before execution, because the model can send wrong ids or unknown criteria.
Why a mock LLM client helps with tests: tests become fast, free, and repeatable.
The rules for the weekly work: 2–4 meaningful commits each week, and weekly reports must match the real repository activity.

## Next Week

Set up the Python environment, .env and .env.example.
Connect to the OpenAI API and make the first working LLM request.
Write the first basic documentation in the README.
Commit working code.
