"""Safe launch wrapper for the cursor-sdk bridge subprocess.

Adapted from the legacy in-tree ``agent/transports/cursor_bridge.py``.

**SDK 1.x status (checked 2026-08-12 against ``cursor-sdk==1.0.27``):**
the private ``_bridge_subprocess_env`` hook and
``CursorClient.launch_bridge(..., allow_api_key_env_fallback=...)`` still
exist. There is still no public ``env=`` override — keep the monkey-patch
and the hard-fail path if the hook disappears. Re-check on every pin bump.
"""

from __future__ import annotations

import importlib
import logging
import os
import threading
from typing import Any

logger = logging.getLogger(__name__)

_BRIDGE_LAUNCH_LOCK = threading.Lock()

# Credential / gateway keys that must never reach Cursor's bridge subprocess
# when Hermes' hermes_subprocess_env helper is unavailable.
_SENSITIVE_ENV_PREFIXES = (
    "HERMES_",
    "OPENAI_",
    "ANTHROPIC_",
    "OPENROUTER_",
    "XAI_",
    "AWS_",
    "GOOGLE_",
    "GH_TOKEN",
    "GITHUB_TOKEN",
    "TELEGRAM_",
    "DISCORD_",
    "SLACK_",
    "BROWSERBASE_",
    "NOUS_",
)


def _fallback_subprocess_env() -> dict[str, str]:
    """Best-effort env sanitization when Hermes internals are not installed."""
    cleaned: dict[str, str] = {}
    for key, value in os.environ.items():
        upper = key.upper()
        if any(upper.startswith(p) or upper == p.rstrip("_") for p in _SENSITIVE_ENV_PREFIXES):
            continue
        # Keep CURSOR_API_KEY out of the bridge env; callers pass it explicitly.
        if upper == "CURSOR_API_KEY":
            continue
        cleaned[key] = value
    return cleaned


def _hermes_subprocess_env() -> dict[str, str]:
    try:
        from tools.environments.local import hermes_subprocess_env  # type: ignore

        return hermes_subprocess_env(inherit_credentials=False)
    except Exception as exc:
        logger.debug(
            "hermes_subprocess_env unavailable (%s); using plugin fallback sanitizer",
            exc,
        )
        return _fallback_subprocess_env()


def launch_cursor_bridge(sdk: Any, *, workspace: str) -> Any:
    """Launch cursor-sdk with a sanitized subprocess environment.

    cursor-sdk 0.1.9–1.0.27 copies ``os.environ`` internally and exposes no
    public ``env=`` argument. Patch its private environment builder only for the duration of
    the synchronized launch. This does not mutate process-global
    ``os.environ``.

    Test doubles and older SDKs without the pinned private module retain the
    plain launch path.
    """
    client_cls = getattr(sdk, "CursorClient", None) or getattr(sdk, "Client")
    module_name = getattr(sdk, "__name__", "")
    if not module_name:
        return client_cls.launch_bridge(workspace=workspace)

    try:
        bridge_module = importlib.import_module(f"{module_name}._bridge")
        original_env_builder = bridge_module._bridge_subprocess_env
    except (AttributeError, ImportError) as exc:
        if module_name == "cursor_sdk":
            # TODO(sdk-1.x): if 1.0.27 dropped this hook, replace with the
            # public env override (or a documented alternative) before shipping.
            raise RuntimeError(
                "cursor-sdk no longer exposes the bridge environment hook "
                "(_bridge_subprocess_env); refusing to launch with "
                "unsanitized Hermes secrets. See hermes_cursor.runtime.bridge "
                "docstring (SDK 1.x risk)."
            ) from exc
        return client_cls.launch_bridge(workspace=workspace)

    sanitized_env = _hermes_subprocess_env()
    sanitized_env.setdefault("CURSOR_SDK_CLIENT_LANGUAGE", "python")

    with _BRIDGE_LAUNCH_LOCK:
        bridge_module._bridge_subprocess_env = lambda: dict(sanitized_env)
        try:
            return client_cls.launch_bridge(
                workspace=workspace,
                # Run-scoped SDK RPCs (wait/cancel/conversation) carry only a
                # run id and 0.1.9 rejects them when this client-side guard is
                # disabled. The bridge environment is sanitized above, so
                # allowing the SDK's owned-bridge path cannot expose or fall
                # back to a process-environment API key; agent/get-run calls
                # still pass credentials explicitly.
                allow_api_key_env_fallback=True,
            )
        finally:
            bridge_module._bridge_subprocess_env = original_env_builder
