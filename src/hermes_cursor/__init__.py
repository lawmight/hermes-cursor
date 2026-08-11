"""hermes-cursor — standalone Hermes plugin for Cursor cloud agents.

MVP footprint (Hermes issue #70140 option A): CLI + skill.
Does **not** register a ProviderProfile / ``model.provider=cursor``.
"""

from __future__ import annotations

from pathlib import Path

__version__ = "0.1.0"

_PACKAGE_DIR = Path(__file__).resolve().parent
_SKILLS_DIR = _PACKAGE_DIR / "skills"


def register(ctx) -> None:
    """Hermes plugin entry point (pip ``hermes_agent.plugins``)."""
    from hermes_cursor.cli.commands import cursor_command, setup_parser

    ctx.register_cli_command(
        name="cursor",
        help="Manage Cursor cloud agents and the Cursor model catalog",
        description=(
            "Drive Cursor cloud agents and inspect the model catalog via the "
            "official cursor-sdk. Requires CURSOR_API_KEY. This plugin does "
            "not provide model.provider=cursor — Cursor owns the inner agent "
            "loop; use hermes cursor / the cursor-cloud skill to delegate."
        ),
        setup_fn=setup_parser,
        handler_fn=cursor_command,
    )

    if _SKILLS_DIR.is_dir():
        for child in sorted(_SKILLS_DIR.iterdir()):
            skill_md = child / "SKILL.md"
            if child.is_dir() and skill_md.exists():
                try:
                    ctx.register_skill(child.name, skill_md)
                except Exception:
                    # Older Hermes builds may lack register_skill — CLI still works.
                    pass


__all__ = ["register", "__version__"]
