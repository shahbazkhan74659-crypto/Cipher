"""Cipher's terminal CLI shell.

Phase 4: a running conversation history (with a system prompt) is threaded
through each call, so the model has memory of prior turns within a session.
History is in-memory only — lost on exit (persistence is v0.5, MEMORY.md).
"""

import asyncio
import logging
import sys

import httpx

from cipher.config import ConfigError, load_settings
from cipher.llm_client import LLMClient, LLMClientError
from cipher.logging_setup import configure_logging
from cipher.openrouter_client import OpenRouterClient

logger = logging.getLogger(__name__)

EXIT_COMMANDS = {"exit", "quit"}
SYSTEM_PROMPT = "You are Cipher, a helpful personal AI assistant."


async def main(client: LLMClient) -> None:
    print("Cipher v0.1 — terminal shell. Type 'exit' to quit.")
    logger.info("CLI session started")

    history: list[dict[str, str]] = [{"role": "system", "content": SYSTEM_PROMPT}]

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

        history.append({"role": "user", "content": text})

        try:
            reply = await client.complete(history)
        except LLMClientError as e:
            print(f"Cipher: [error] {e}")
            logger.error("LLM call failed: %s", e)
            history.pop()  # drop the unanswered turn, keep history clean
            continue

        history.append({"role": "assistant", "content": reply})
        print(f"Cipher: {reply}")

    print("Goodbye.")
    logger.info("CLI session ended")


def run() -> None:
    configure_logging()

    try:
        settings = load_settings()
    except ConfigError as e:
        print(f"Cipher: [config error] {e}", file=sys.stderr)
        sys.exit(1)

    async def _run() -> None:
        async with httpx.AsyncClient(timeout=60.0) as http_client:
            client = OpenRouterClient(http_client, settings)
            await main(client)

    asyncio.run(_run())


if __name__ == "__main__":
    run()
