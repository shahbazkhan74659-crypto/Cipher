import pytest

from cipher.cli import SYSTEM_PROMPT, main
from cipher.llm_client import LLMClient, LLMClientError


class StubClient(LLMClient):
    """Test double: replies come from a canned queue (str reply or Exception)."""

    def __init__(self, replies):
        self.replies = list(replies)
        self.calls: list[list[dict[str, str]]] = []

    async def complete(self, messages):
        self.calls.append(list(messages))
        reply = self.replies.pop(0)
        if isinstance(reply, Exception):
            raise reply
        return reply


def queue_input(monkeypatch, inputs):
    it = iter(inputs)

    def fake_input(prompt=""):
        try:
            return next(it)
        except StopIteration:
            raise EOFError

    monkeypatch.setattr("builtins.input", fake_input)


def system_message():
    return {"role": "system", "content": SYSTEM_PROMPT}


async def test_blank_input_is_skipped_without_calling_client(monkeypatch):
    queue_input(monkeypatch, ["", "   ", "exit"])
    client = StubClient([])

    await main(client)

    assert client.calls == []


async def test_exit_command_ends_loop_without_calling_client(monkeypatch, capsys):
    queue_input(monkeypatch, ["exit"])
    client = StubClient([])

    await main(client)

    assert client.calls == []
    assert "Goodbye." in capsys.readouterr().out


async def test_quit_is_case_insensitive(monkeypatch):
    queue_input(monkeypatch, ["QUIT"])
    client = StubClient([])

    await main(client)

    assert client.calls == []


async def test_successful_turn_records_history_and_prints_reply(monkeypatch, capsys):
    queue_input(monkeypatch, ["hello", "exit"])
    client = StubClient(["hi there"])

    await main(client)

    assert client.calls == [[system_message(), {"role": "user", "content": "hello"}]]
    assert "Cipher: hi there" in capsys.readouterr().out


async def test_failed_turn_pops_history_and_does_not_corrupt_next_turn(monkeypatch, capsys):
    queue_input(monkeypatch, ["first", "second", "exit"])
    client = StubClient([LLMClientError("boom"), "second reply"])

    await main(client)

    out = capsys.readouterr().out
    assert "Cipher: [error] boom" in out
    assert "Cipher: second reply" in out

    # Second call's history must not contain the failed first turn.
    assert client.calls[1] == [system_message(), {"role": "user", "content": "second"}]


async def test_eof_input_ends_loop_cleanly(monkeypatch, capsys):
    queue_input(monkeypatch, [])  # first input() call raises EOFError immediately
    client = StubClient([])

    await main(client)

    assert client.calls == []
    assert "Goodbye." in capsys.readouterr().out


async def test_keyboard_interrupt_ends_loop_cleanly(monkeypatch, capsys):
    def fake_input(prompt=""):
        raise KeyboardInterrupt

    monkeypatch.setattr("builtins.input", fake_input)
    client = StubClient([])

    await main(client)

    assert client.calls == []
    assert "Goodbye." in capsys.readouterr().out
