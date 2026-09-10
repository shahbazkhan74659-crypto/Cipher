"""OpenRouter implementation of LLMClient (LLM.md: primary provider for v0.1).

Single request/response only — no streaming (Phase 4/5). Retries a bounded
number of times, only for signals that are clearly transient (rate limit,
provider-reported overload/5xx, request timeouts, network errors). This is
NOT auto-fallback across models or providers (LLM.md: "fallbacks are manual,
not routed") — it's retrying the one configured model a couple of times
before surfacing a real failure.
"""

import asyncio
import logging

import httpx

from cipher.config import Settings
from cipher.llm_client import LLMClient, LLMClientError

logger = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MAX_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 2.0
RETRYABLE_STATUSES = {429, 500, 502, 503, 504}


class _RetryableError(Exception):
    """Internal signal: this attempt failed in a way that looks transient."""


class OpenRouterClient(LLMClient):
    def __init__(self, http_client: httpx.AsyncClient, settings: Settings) -> None:
        self._http = http_client
        self._settings = settings

    async def complete(self, messages: list[dict[str, str]]) -> str:
        last_error: Exception | None = None

        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                return await self._complete_once(messages)
            except _RetryableError as e:
                last_error = e
                if attempt < MAX_ATTEMPTS:
                    logger.warning(
                        "Retryable OpenRouter error (attempt %d/%d), retrying in %.0fs: %s",
                        attempt, MAX_ATTEMPTS, RETRY_DELAY_SECONDS, e,
                    )
                    await asyncio.sleep(RETRY_DELAY_SECONDS)

        raise LLMClientError(f"{last_error} (gave up after {MAX_ATTEMPTS} attempts)")

    async def _complete_once(self, messages: list[dict[str, str]]) -> str:
        try:
            response = await self._http.post(
                OPENROUTER_URL,
                headers={"Authorization": f"Bearer {self._settings.openrouter_api_key}"},
                json={"model": self._settings.model, "messages": messages},
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            description = self._describe_status_error(e)
            if e.response.status_code in RETRYABLE_STATUSES:
                raise _RetryableError(description) from e
            raise LLMClientError(description) from e
        except httpx.TimeoutException as e:
            raise _RetryableError("Request to OpenRouter timed out.") from e
        except httpx.RequestError as e:
            raise _RetryableError(f"Network problem reaching OpenRouter: {e}") from e

        try:
            data = response.json()
        except ValueError as e:
            logger.error("Non-JSON OpenRouter response: %s", response.text)
            raise LLMClientError("OpenRouter returned a non-JSON response.") from e

        if "error" in data:
            err = data["error"]
            message = f"OpenRouter/provider error: {err.get('message', 'Unknown upstream error.')}"
            if err.get("code") in RETRYABLE_STATUSES:
                raise _RetryableError(message)
            raise LLMClientError(message)

        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as e:
            logger.error("Unexpected OpenRouter response shape: %s", response.text)
            raise LLMClientError("OpenRouter returned an unexpected response shape.") from e

    @staticmethod
    def _describe_status_error(e: httpx.HTTPStatusError) -> str:
        status = e.response.status_code
        detail = None
        try:
            detail = e.response.json().get("error", {}).get("message")
        except (ValueError, AttributeError):
            pass

        if status == 429:
            base = "Rate limited by OpenRouter's free tier — try again shortly."
        else:
            base = f"OpenRouter request failed (HTTP {status})."

        return f"{base} {detail}" if detail else base
