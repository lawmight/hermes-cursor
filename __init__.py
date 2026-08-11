"""Drop-in layout entry for ``~/.hermes/plugins/hermes-cursor/``.

Re-exports ``register(ctx)`` from the installable package when available,
otherwise registers a thin shim that imports from a sibling ``src/`` tree
(editable checkout).
"""

from __future__ import annotations

from pathlib import Path

_ROOT = Path(__file__).resolve().parent
_SRC = _ROOT / "src"


def register(ctx) -> None:
    """Hermes drop-in plugin entry point."""
    try:
        from hermes_cursor import register as _register
    except ImportError:
        import sys

        if str(_SRC) not in sys.path:
            sys.path.insert(0, str(_SRC))
        from hermes_cursor import register as _register  # type: ignore

    _register(ctx)
