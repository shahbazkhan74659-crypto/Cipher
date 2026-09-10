"""Cipher's terminal CLI shell.

Phase 2: a placeholder loop only — input in, echo out. No OpenRouter call yet
(that's Phase 3). Built async from the start so Phase 3 can add the real
async model call into this same loop without a rewrite.
"""

import asyncio
import logging

from cipher.logging_setup import configure_logging

logger = logging.getLogger(__name__)

EXIT_COMMANDS = {"exit", "quit"}


async def main() -> None:
    print("Cipher v0.1 — terminal shell (LLM not wired yet, Phase 3). Type 'exit' to quit.")
    logger.info("CLI session started")

    while True:
        try:
            user_input = await asyncio.to_thread(input, "You: ")
        except (EOFError, KeyboardInterrupt):
            print()
            break

        text = user_input.strip()
        if not text:
            continue

        logger.debug("Received input (%d chars)", len(text))

        if text.lower() in EXIT_COMMANDS:
            break

        print(f"Cipher (echo): {text}")

    print("Goodbye.")
    logger.info("CLI session ended")


def run() -> None:
    configure_logging()
    asyncio.run(main())


if __name__ == "__main__":
    run()
