# Hermes Cursor plugin — user guide

Short install + honesty about roles. Full carve history lives in
[`CARVE_PLAN.md`](../CARVE_PLAN.md).

## Roles

| Layer | Owner |
| --- | --- |
| Inner agent loop, coding tools, sandbox | **Cursor** |
| Sessions, memory, gateway, cron, messaging | **Hermes** |
| This plugin | `CURSOR_API_KEY` readiness, `hermes cursor` CLI, `cursor-cloud` skill |

This plugin is **not** a first-class chat model provider. Upstream Hermes
`ProviderProfile.api_mode` values today are
`chat_completions | codex_responses | anthropic_messages | bedrock_converse`.
Legacy fork work that invented `cursor_agent` via core patches is intentionally
**not** shipped here.

Billing: Cursor cloud / SDK usage is billed on your Cursor subscription /
dashboard. Hermes sessions around the CLI stay on whatever provider you
already use for chat.

## Install

### Drop-in

```bash
ln -s /path/to/hermes-cursor-plugin ~/.hermes/plugins/hermes-cursor
hermes plugins enable hermes-cursor
```

### Pip

```bash
pip install -e '/path/to/hermes-cursor-plugin[sdk]'
hermes plugins enable hermes-cursor   # if required by your Hermes version
```

### Auth

1. Create a key at [Cursor Dashboard → Integrations](https://cursor.com/dashboard?tab=integrations).
2. Put `CURSOR_API_KEY=...` in `$HERMES_HOME/.env` (or the process environment).
3. Run `hermes cursor me`.

OAuth tokens from Cursor IDE login paths are **not** interchangeable with
SDK / Cloud Agents API keys.

## CLI cheat sheet

```bash
hermes cursor me
hermes cursor models
hermes cursor repos
hermes cursor launch "<task>" --repo <url> [--ref <ref>] [--pr] [--follow]
hermes cursor list [--archived]
hermes cursor status <bc-id>
hermes cursor follow <bc-id>
hermes cursor send <bc-id> "<prompt>" [--follow]
hermes cursor cancel <bc-id>
hermes cursor artifacts <bc-id> [--download DIR]
hermes cursor archive|unarchive <bc-id>
hermes cursor delete <bc-id> --yes
```

`me` / `models` are REST-only (no SDK). Other verbs need
`pip install 'hermes-cursor[sdk]'` (`cursor-sdk==1.0.27`).

## Skill

Bundled as `skills/cursor-cloud/SKILL.md`. After the plugin loads:

```text
skill_view("hermes-cursor:cursor-cloud")
```

Teach the agent to drive `hermes cursor` via the `terminal` tool — zero
extra tool-schema footprint.

## SDK 1.x note

The optional runtime bridge under `hermes_cursor.runtime.bridge` still
documents a private `_bridge_subprocess_env` patch carried from cursor-sdk
0.1.9. Before relying on local-bridge launches against 1.0.27, retest or
replace that path (see TODOs in the module and CARVE_PLAN.md).

## What this is not

- `hermes model` → Cursor as primary chat
- Replacing Hermes tools with Cursor tools inside the Hermes turn loop
- An in-tree Nous Research bundled plugin
