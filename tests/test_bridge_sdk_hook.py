"""Guardrail: refuse silent env leaks if cursor-sdk drops the private hook."""

from __future__ import annotations

import importlib
import importlib.util

import pytest


@pytest.mark.skipif(
    importlib.util.find_spec("cursor_sdk") is None,
    reason="cursor-sdk not installed (optional [sdk] extra)",
)
def test_bridge_subprocess_env_hook_still_present():
    import cursor_sdk

    bridge = importlib.import_module(f"{cursor_sdk.__name__}._bridge")
    assert hasattr(bridge, "_bridge_subprocess_env"), (
        "cursor-sdk removed _bridge_subprocess_env; update "
        "hermes_cursor.runtime.bridge before bumping the pin"
    )
    client = getattr(cursor_sdk, "CursorClient", None) or getattr(cursor_sdk, "Client")
    assert hasattr(client, "launch_bridge")
