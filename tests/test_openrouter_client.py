import httpx
import pytest

from cipher.config import Settings
from cipher.llm_client import LLMClientError
from cipher.openrouter_client import OpenRouterClient

MESSAGES = [{"role": "user", "content": "hi"}]


def make_client(handler, monkeypatch, fast_retries=True):
    if fast_retries:
        import cipher.openrouter_client as mod

        monkeypatch.setattr(mod, "RETRY_DELAY_SECONDS", 0)

    transport = httpx.MockTransport(handler)
    http_client = httpx.AsyncClient(transport=transport)
    settings = Settings(openrouter_api_key="test-key")
    return OpenRouterClient(http_client, settings), http_client


def success_response():
    return httpx.Response(
        200, json={"choices": [{"message": {"content": "hello there"}}]}
    )


async def test_successful_call_returns_content(monkeypatch):
    def handler(request):
        return success_response()

    client, http_client = make_client(handler, monkeypatch)
    async with http_client:
        result = await client.complete(MESSAGES)

    assert result == "hello there"


async def test_retryable_status_succeeds_on_later_attempt(monkeypatch):
    calls = []

    def handler(request):
        calls.append(request)
        if len(calls) == 1:
            return httpx.Response(503, json={"error": {"message": "overloaded"}})
        return success_response()

    client, http_client = make_client(handler, monkeypatch)
    async with http_client:
        result = await client.complete(MESSAGES)

    assert result == "hello there"
    assert len(calls) == 2


async def test_retryable_status_exhausts_attempts(monkeypatch):
    def handler(request):
        return httpx.Response(503, json={"error": {"message": "overloaded"}})

    client, http_client = make_client(handler, monkeypatch)
    async with http_client:
        with pytest.raises(LLMClientError, match=r"gave up after 3 attempts\)$"):
            await client.complete(MESSAGES)


async def test_non_retryable_status_fails_immediately(monkeypatch):
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(401, json={"error": {"message": "bad key"}})

    client, http_client = make_client(handler, monkeypatch)
    async with http_client:
        with pytest.raises(LLMClientError):
            await client.complete(MESSAGES)

    assert len(calls) == 1


async def test_embedded_error_with_retryable_code_retries(monkeypatch):
    calls = []

    def handler(request):
        calls.append(request)
        if len(calls) == 1:
            return httpx.Response(200, json={"error": {"code": 503, "message": "busy"}})
        return success_response()

    client, http_client = make_client(handler, monkeypatch)
    async with http_client:
        result = await client.complete(MESSAGES)

    assert result == "hello there"
    assert len(calls) == 2


async def test_embedded_error_with_non_retryable_code_fails_immediately(monkeypatch):
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(200, json={"error": {"code": 400, "message": "bad request"}})

    client, http_client = make_client(handler, monkeypatch)
    async with http_client:
        with pytest.raises(LLMClientError, match="bad request"):
            await client.complete(MESSAGES)

    assert len(calls) == 1


async def test_non_json_response_raises_llm_client_error(monkeypatch):
    def handler(request):
        return httpx.Response(200, text="not json")

    client, http_client = make_client(handler, monkeypatch)
    async with http_client:
        with pytest.raises(LLMClientError, match="non-JSON"):
            await client.complete(MESSAGES)


async def test_unexpected_response_shape_raises_llm_client_error(monkeypatch):
    def handler(request):
        return httpx.Response(200, json={"choices": [{}]})

    client, http_client = make_client(handler, monkeypatch)
    async with http_client:
        with pytest.raises(LLMClientError, match="unexpected response shape"):
            await client.complete(MESSAGES)


async def test_timeout_is_retried_and_eventually_fails(monkeypatch):
    def handler(request):
        raise httpx.ReadTimeout("timed out", request=request)

    client, http_client = make_client(handler, monkeypatch)
    async with http_client:
        with pytest.raises(LLMClientError, match=r"gave up after 3 attempts\)$"):
            await client.complete(MESSAGES)


async def test_connection_error_is_retried_and_eventually_fails(monkeypatch):
    def handler(request):
        raise httpx.ConnectError("connection refused", request=request)

    client, http_client = make_client(handler, monkeypatch)
    async with http_client:
        with pytest.raises(LLMClientError, match=r"gave up after 3 attempts\)$"):
            await client.complete(MESSAGES)


async def test_timeout_then_success_retries_through(monkeypatch):
    calls = []

    def handler(request):
        calls.append(request)
        if len(calls) == 1:
            raise httpx.ReadTimeout("timed out", request=request)
        return success_response()

    client, http_client = make_client(handler, monkeypatch)
    async with http_client:
        result = await client.complete(MESSAGES)

    assert result == "hello there"
    assert len(calls) == 2


async def test_describe_status_error_rate_limit_message():
    request = httpx.Request("POST", "https://openrouter.ai/api/v1/chat/completions")
    response = httpx.Response(429, json={"error": {"message": "slow down"}}, request=request)
    error = httpx.HTTPStatusError("429", request=request, response=response)

    from cipher.openrouter_client import OpenRouterClient

    description = OpenRouterClient._describe_status_error(error)

    assert "Rate limited" in description
    assert "slow down" in description


async def test_describe_status_error_generic_message_without_body():
    request = httpx.Request("POST", "https://openrouter.ai/api/v1/chat/completions")
    response = httpx.Response(500, text="not json", request=request)
    error = httpx.HTTPStatusError("500", request=request, response=response)

    from cipher.openrouter_client import OpenRouterClient

    description = OpenRouterClient._describe_status_error(error)

    assert description == "OpenRouter request failed (HTTP 500)."
