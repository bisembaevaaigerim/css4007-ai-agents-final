"""First working request: ask the model one question from the command line.

Usage:
    python -m startscore.cli "What does traction mean for a startup?"

Tools are not connected yet (planned for week 13).
"""

import sys

from startscore.config import ConfigError, load_config
from startscore.llm_client import LLMError, call_llm

SYSTEM_PROMPT = (
    "You are StartScore, an assistant that explains how technology startups are "
    "evaluated. This is an educational project, not investment advice. "
    "If you do not know something, say so. Do not invent facts or numbers."
)


def ask(question: str) -> str:
    config = load_config()
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]
    reply = call_llm(messages, config)
    return reply["content"] or "(The model returned an empty answer.)"


def main(argv: list[str]) -> int:
    question = " ".join(argv).strip()
    if not question:
        print('Usage: python -m startscore.cli "your question"', file=sys.stderr)
        return 2
    try:
        print(ask(question))
    except (ConfigError, LLMError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))