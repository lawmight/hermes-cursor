# hermes-cursor

Standalone **Hermes Agent** community plugin for **Cursor cloud agents**.

| Layer | Owner |
| --- | --- |
| Inner agent loop / tools / sandbox | **Cursor** (`cursor-sdk` local or cloud) |
| Sessions, memory, gateway, cron | **Hermes** |
| This plugin | Auth readiness, `hermes cursor` CLI, `cursor-cloud` skill |

**Honest MVP:** CLI + skill. This package does **not** register
`model.provider=cursor` (no `ProviderProfile` / core `cursor_agent` api_mode).
See [CARVE_PLAN.md](./CARVE_PLAN.md) and upstream
[#70140](https://github.com/NousResearch/hermes-agent/issues/70140).

Author: **lawmight / Tom Coustols** (fork community plugin — not Nous Research).

## Install

### Option A — drop-in directory

```bash
# symlink or copy this repo into Hermes plugins
ln -s "$(pwd)" ~/.hermes/plugins/hermes-cursor

# or: cp -a . ~/.hermes/plugins/hermes-cursor
hermes plugins enable hermes-cursor
```

Requires `plugin.yaml` + `__init__.py` with `register(ctx)` at the plugin root
(both are present in this repo). For the drop-in path without a pip install,
either `pip install -e .` once so `hermes_cursor` imports resolve, or keep the
`src/` tree next to the root `__init__.py` (it adds `src/` to `sys.path`).

### Option B — pip editable (entry point)

```bash
pip install -e .
# with SDK for launch/list/follow/… verbs:
pip install -e '.[sdk]'
```

Entry point:

```toml
[project.entry-points."hermes_agent.plugins"]
hermes-cursor = "hermes_cursor:register"
```

Then enable if your Hermes version gates plugins:

```bash
hermes plugins list
hermes plugins enable hermes-cursor
```

### Auth

```bash
# Cursor Dashboard → Integrations → API Keys
export CURSOR_API_KEY=...
# or put it in $HERMES_HOME/.env (preferred)
```

Verify (REST only — no SDK required):

```bash
hermes cursor me
hermes cursor models
```

## Usage

```bash
hermes cursor launch "Add logging to auth middleware" \
  --repo https://github.com/org/repo --ref main --pr

hermes cursor list
hermes cursor status bc-...
hermes cursor follow bc-...
hermes cursor send bc-... "Also add unit tests" --follow
```

Inside a Hermes session, load the skill:

```text
skill_view("hermes-cursor:cursor-cloud")
```

(Exact namespace may follow Hermes' plugin skill naming; bare
`skill_view("cursor-cloud")` works when registered without collision.)

## Dependencies

| Package | Role |
| --- | --- |
| *(none hard)* | REST `me` / `models` via stdlib |
| `cursor-sdk==1.0.27` (extra `[sdk]`) | Agent verbs — **lazy-imported** |

## Layout

```text
hermes-cursor-plugin/
  plugin.yaml / __init__.py     # ~/.hermes/plugins/hermes-cursor drop-in
  pyproject.toml                # pip + hermes_agent.plugins entry point
  CARVE_PLAN.md
  src/hermes_cursor/
    __init__.py                 # register(ctx)
    cli/commands.py             # hermes cursor verbs
    runtime/                    # bridge / projector / sdk_session (future)
    skills/cursor-cloud/SKILL.md
  docs/user-guide.md
  tests/
```

## Non-goals (for now)

- In-tree PR to `NousResearch/hermes-agent`
- Claiming Cursor replaces `xai` / wallet providers
- Full `model.provider=cursor` without an upstream external-harness seam

## License

MIT
