"""Smoke tests for plugin registration surface (no network, no SDK)."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"


def test_plugin_yaml_parses_at_repo_root():
    data = yaml.safe_load((ROOT / "plugin.yaml").read_text())
    assert data["name"] == "hermes-cursor"
    assert data["author"].startswith("lawmight")
    assert "CURSOR_API_KEY" in str(data.get("requires_env"))


def test_plugin_yaml_parses_in_package():
    data = yaml.safe_load((SRC / "hermes_cursor" / "plugin.yaml").read_text())
    assert data["name"] == "hermes-cursor"
    assert "Nous Research" not in data.get("author", "")


def test_register_callable_importable():
    from hermes_cursor import register

    assert callable(register)


def test_register_wires_cli_and_skill():
    from hermes_cursor import register

    recorded: dict = {"cli": [], "skills": []}

    class FakeCtx:
        def register_cli_command(self, name, help, setup_fn, handler_fn=None, description=""):
            recorded["cli"].append(
                {
                    "name": name,
                    "help": help,
                    "setup_fn": setup_fn,
                    "handler_fn": handler_fn,
                    "description": description,
                }
            )

        def register_skill(self, name, path):
            recorded["skills"].append((name, Path(path)))

    register(FakeCtx())

    assert len(recorded["cli"]) == 1
    assert recorded["cli"][0]["name"] == "cursor"
    assert callable(recorded["cli"][0]["setup_fn"])
    assert callable(recorded["cli"][0]["handler_fn"])
    assert any(name == "cursor-cloud" for name, _ in recorded["skills"])
    skill_path = next(p for name, p in recorded["skills"] if name == "cursor-cloud")
    assert skill_path.name == "SKILL.md"
    assert skill_path.exists()


def test_setup_parser_builds_subcommands():
    import argparse

    from hermes_cursor.cli.commands import setup_parser

    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    cursor = sub.add_parser("cursor")
    setup_parser(cursor)

    args = parser.parse_args(["cursor", "me"])
    assert args.cursor_action == "me"

    args = parser.parse_args(["cursor", "launch", "do thing", "--repo", "https://example.com/r"])
    assert args.cursor_action == "launch"
    assert args.prompt == "do thing"
    assert args.repo == "https://example.com/r"


def test_skill_frontmatter_honest_about_roles():
    text = (SRC / "hermes_cursor" / "skills" / "cursor-cloud" / "SKILL.md").read_text()
    assert "model.provider=cursor" in text
    assert "does **not** provide" in text or "does **not**" in text
    assert "Nous Research" not in text.split("---", 2)[1]


def test_pyproject_pins_sdk_extra_and_entry_point():
    text = (ROOT / "pyproject.toml").read_text()
    assert 'cursor-sdk==1.0.27' in text
    assert 'hermes_agent.plugins' in text
    assert 'hermes-cursor = "hermes_cursor:register"' in text
