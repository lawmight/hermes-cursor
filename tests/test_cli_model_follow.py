"""Unit tests for launch model default + follow text recovery."""

from __future__ import annotations

from contextlib import contextmanager
from types import SimpleNamespace

from hermes_cursor.cli import commands as cli


class _FakeRun:
    def __init__(self, *, messages=None, result="", status="finished"):
        self._messages = list(messages or [])
        self.result = result
        self.status = status

    def messages(self):
        yield from self._messages

    def wait(self):
        return SimpleNamespace(status=self.status, result=self.result)

    def supports(self, op: str) -> bool:
        return op == "stream"


def test_stream_run_falls_back_to_terminal_result(capsys):
    run = _FakeRun(
        messages=[SimpleNamespace(type="status", status="RUNNING")],
        result="CURSOR_SMOKE_OK",
        status="finished",
    )
    status = cli._stream_run(run)
    out = capsys.readouterr().out
    assert status == "finished"
    assert "CURSOR_SMOKE_OK" in out
    assert "[status] RUNNING" in out


def test_stream_run_keeps_live_assistant_text(capsys):
    assistant = SimpleNamespace(
        type="assistant",
        message=SimpleNamespace(
            content=[SimpleNamespace(type="text", text="hello from stream")]
        ),
    )
    run = _FakeRun(messages=[assistant], result="should-not-duplicate")
    cli._stream_run(run)
    out = capsys.readouterr().out
    assert "hello from stream" in out
    assert "should-not-duplicate" not in out


def test_pick_latest_run_by_created_at():
    older = SimpleNamespace(id="run-1", created_at="2026-01-01T00:00:00Z")
    newer = SimpleNamespace(id="run-2", created_at="2026-08-12T00:00:00Z")
    assert cli._pick_latest_run([older, newer]).id == "run-2"
    assert cli._pick_latest_run([newer, older]).id == "run-2"


def test_launch_defaults_model_to_default(monkeypatch):
    captured: dict = {}

    class Agent:
        agent_id = "bc-test"

        def send(self, prompt):
            return _FakeRun(result="ok")

    class Agents:
        def create(self, **kwargs):
            captured.update(kwargs)
            return Agent()

    class Client:
        def __init__(self):
            self.agents = Agents()

        def close(self):
            return None

    @contextmanager
    def fake_open(_sdk):
        yield Client()

    monkeypatch.setattr(cli, "_require_api_key", lambda: "crsr_test")
    monkeypatch.setattr(cli, "_get_sdk", lambda: object())
    monkeypatch.setattr(cli, "_open_client", fake_open)

    args = SimpleNamespace(
        prompt="hi",
        repo="https://github.com/lawmight/hermes-cursor",
        ref="main",
        model="",
        name="",
        pr=False,
        branch_current=False,
        pool="",
        env_var=[],
        follow=False,
    )
    assert cli.cmd_launch(args) == 0
    assert captured["model"] == "default"
