"""Model-agnostic LLM client interface (ARCHITECTURE.md #4).

Swapping the LLM provider should mean writing a new LLMClient
implementation, not touching the CLI or any other caller.
"""

import abc


class LLMClientError(Exception):
    """The one error shape callers need to handle, regardless of provider."""


class LLMClient(abc.ABC):
    @abc.abstractmethod
    async def complete(self, messages: list[dict[str, str]]) -> str:
        """Send messages to the model and return its reply text.

        Raises LLMClientError on any failure (network, rate limit, malformed
        response) — callers never need to know the provider-specific error type.
        """
