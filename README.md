# hermes-cursor

Standalone **Hermes Agent** community plugin for **Cursor** agents (local + cloud) via the official `cursor-sdk`.

| Layer | Owner |
| --- | --- |
| Inner agent loop / tools / sandbox | **Cursor** (`cursor-sdk`) |
| Sessions, memory, gateway, cron | **Hermes** |
| This plugin | Auth readiness, `hermes cursor` CLI, `cursor-cloud` skill |

**Honest MVP:** CLI + skill only. This package does **not** register
`model.provider=cursor` (no `ProviderProfile` / core `cursor_agent` api_mode).
See [CARVE_PLAN.md](./CARVE_PLAN.md) and upstream
[#70140](https://github.com/NousResearch/hermes-agent/issues/70140).

Repo: https://github.com/lawmight/hermes-cursor  
Author: **lawmight / Tom Coustols** (community plugin — not Nous Research).

## Install

### Option A — drop into `~/.hermes/plugins`

```bash
git clone https://github.com/lawmight/hermes-cursor.git
cd hermes-cursor

mkdir -p ~/.hermes/plugins
# Prefer a symlink so updates are a git pull away:
ln -sfn "$(pwd)" ~/.hermes/plugins/hermes-cursor

# Drop-in import path needs the package importable. Easiest:
python3 -m pip install -e '.[sdk]'

# If your Hermes build gates plugins:
hermes plugins list
hermes plugins enable hermes-cursor
```

The drop-in root contains `plugin.yaml` + `__init__.py` with `register(ctx)`.
That root shim also puts `src/` on `sys.path` for editable-less experiments,
but `pip install -e .` is the reliable path.

### Option B — pip only (entry point)

```bash
python3 -m pip install -e '.[sdk]'   # from a clone
# or eventually: pip install hermes-cursor[sdk]
```

Entry point (already in `pyproject.toml`):

```toml
[project.entry-points."hermes_agent.plugins"]
hermes-cursor = "hermes_cursor:register"
```

### Auth

```bash
# Cursor Dashboard → Integrations / API Keys
# Prefer $HERMES_HOME/.env so the gateway picks it up:
echo 'CURSOR_API_KEY=crsr_...' >> "${HERMES_HOME:-$HOME/.hermes}/.env"
```

REST verbs need only the key (no SDK wheel):

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

Inside a Hermes session, load the bundled skill (name may be namespaced by
your Hermes build):

```text
skill_view("cursor-cloud")
# or: skill_view("hermes-cursor:cursor-cloud")
```

## Dependencies

| Package | Role |
| --- | --- |
| *(none hard)* | REST `me` / `models` via stdlib |
| `cursor-sdk==1.0.27` (extra `[sdk]`) | Agent verbs — **lazy-imported** |

**Bridge env note:** local SDK launches still go through a private
`cursor_sdk._bridge._bridge_subprocess_env` hook (confirmed present on
1.0.27). This plugin monkey-patches that hook to strip Hermes secrets from
the bridge subprocess env, and hard-fails if the hook disappears. There is
still no public `env=` override — re-check on every pin bump
(`tests/test_bridge_sdk_hook.py`).

## Layout

```text
.
  plugin.yaml / __init__.py     # ~/.hermes/plugins/hermes-cursor drop-in
  pyproject.toml                # pip + hermes_agent.plugins entry point
  CARVE_PLAN.md
  src/hermes_cursor/
    __init__.py                 # register(ctx) → CLI + skill
    cli/commands.py             # hermes cursor verbs
    runtime/                    # bridge / projector / sdk_session
    skills/cursor-cloud/SKILL.md
  docs/user-guide.md
  inventory/                    # reference copies from legacy fork tip (not imported)
  tests/
```

## Non-goals (for now)

- In-tree PR to `NousResearch/hermes-agent`
- Claiming Cursor replaces `xai` / `xai-oauth` wallets
- Full `model.provider=cursor` without an upstream external-harness seam

## License

MIT
