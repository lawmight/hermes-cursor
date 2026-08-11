# Hermes ↔ Cursor standalone plugin — carve plan

Date: 2026-08-12  
Source tip: `lawmight/hermes-agent` @ `cursor/bc-3845be2f-3cfa-4910-87cf-4fbcbc00fb27-6a3f` (`f81b880d3`)  
Policy: **no** in-tree PR to `NousResearch/hermes-agent` with `plugins/model-providers/cursor/`.  
Upstream design lock: [#70140](https://github.com/NousResearch/hermes-agent/issues/70140) (needs-decision; recommended shape = standalone CLI+skill / gated delegate).  
Port assessment: [fork PR #13](https://github.com/lawmight/hermes-agent/pull/13) / `docs/plans/cursor-provider-main-port.md`.  
Draft in-tree provider (do not rebase): [fork PR #1](https://github.com/lawmight/hermes-agent/pull/1) (~6.2k LOC).

## Proposed repo name

**`lawmight/hermes-cursor`** (pip: `hermes-cursor`, Discord promo name: "Hermes Cursor plugin")

Alternates if taken / naming conflict with ACP: `hermes-cursor-models`, `hermes-cursor-sdk`.

Install targets:
1. Drop-in: `~/.hermes/plugins/hermes-cursor/` (or symlink)
2. Pip entry point: `[project.entry-points."hermes_agent.plugins"] hermes-cursor = "hermes_cursor:register"`

## Honest packaging (roles)

| Layer | Owner |
|---|---|
| Inner agent loop / tools / sandbox | **Cursor** (`cursor-sdk` local or cloud) |
| Sessions, memory, gateway, cron, messaging | **Hermes** |
| This plugin | Auth readiness, `hermes cursor` CLI, skill, optional gated `ctx.register_tool` delegate, config under plugin `config.yaml` / Hermes `.env` (`CURSOR_API_KEY`) |

**Do not claim** first-class `model.provider=cursor` until Hermes exposes a vendor-neutral external-harness hook. Current public `ProviderProfile.api_mode` values are only `chat_completions | codex_responses | anthropic_messages | bedrock_converse`. Legacy PR #1 invented `cursor_agent` via core patches — that violates upstream third-party policy and is the reason prior Cursor PRs closed on placement.

MVP = **Footprint Ladder rungs 2–4** (#70140 Phase 1): CLI + skill (+ optional gated tool). Full provider shape stays in `runtime/` as a *future* module, not the advertised install path.

## File split

### KEEP → package (adapt imports / pin SDK 1.x)

| Legacy path | New path | Notes |
|---|---|---|
| `hermes_cli/cursor_cli.py` | `hermes_cursor/cli/commands.py` | Business logic; wire via `ctx.register_cli_command` |
| `hermes_cli/subcommands/cursor.py` | fold into CLI setup_fn | Drop `_BUILTIN_SUBCOMMANDS` edits |
| `optional-skills/.../cursor-cloud/SKILL.md` | `hermes_cursor/skills/cursor-cloud/SKILL.md` | Teach `hermes cursor` via terminal |
| `agent/transports/cursor_event_projector.py` | `hermes_cursor/runtime/event_projector.py` | Still useful for streaming CLI / future harness |
| `agent/transports/cursor_sdk_session.py` | `hermes_cursor/runtime/sdk_session.py` | Upgrade to cursor-sdk **1.0.27**; retest create/resume/cancel |
| `agent/transports/cursor_bridge.py` | `hermes_cursor/runtime/bridge.py` | **High risk**: private `_bridge_subprocess_env` patch; replace or gate on 1.x |
| `agent/transports/cursor_hermes_tools.py` | `hermes_cursor/runtime/hermes_tools.py` | **Defer for MVP** — #70140 recommends Cursor owns tools inside SDK run |
| `plugins/model-providers/cursor/{__init__,plugin.yaml}` | `hermes_cursor/provider/` (**deferred / experimental**) | Catalog fetch helpers reusable; do not register as default provider without core seam |
| `website/docs/.../cursor-agent-runtime.md` | `docs/user-guide.md` | Rewrite for plugin install + billing honesty |
| Cursor-specific tests (session/projector/CLI/skill) | `tests/` | Port assertions; drop core-wiring tests |

### DROP (core patches / obsolete)

- Edits to `agent/agent_init.py`, `conversation_loop.py`, `run_agent.py`, `agent_runtime_helpers.py`
- `agent/cursor_runtime.py` as Hermes full-turn forwarder (unless a generic hook lands)
- Picker/setup patches in `hermes_cli/models.py`, `model_setup_flows.py`, `providers.py`
- Direct registration in `hermes_cli/main.py`
- Gateway `message_type` patch
- `tools/lazy_deps.py` `provider.cursor` pin inside Hermes (plugin owns its own dep)
- Bundled `plugins/model-providers/cursor/` intended for upstream merge
- Reuse of #40876 OAuth (`api2.cursor.sh` tokens ≠ `api.cursor.com` / SDK keys)

### ADAPT / rewrite

- `plugin.yaml`: `kind` as general plugin (CLI+tools), not in-tree model-provider claim for MVP
- Config: plugin-owned `config.yaml` (`runtime: local|cloud`, mode, timeouts) — no new behavioral `HERMES_*` knobs
- Auth: `CURSOR_API_KEY` in `$HERMES_HOME/.env` only
- Model allowlist v1 (per #70140): first-party `grok-4.5`, `composer-2.5` (+ fast via `model.params`); live `Cursor.models.list()` as discovery, not unbounded Other Models

## SDK upgrade

| Item | Value |
|---|---|
| Legacy pin | `cursor-sdk==0.1.9` |
| Target pin | `cursor-sdk==1.0.27` (PyPI latest 2026-08-06; shared version with `@cursor/sdk` since 1.0.24) |
| Public surface | `Agent.create` / `resume`, `LocalAgentOptions` / `CloudAgentOptions`, `Cursor.models.list`, `get_usage` — broadly compatible |
| Highest risk | Private bridge env sanitization — **still present on 1.0.27** (retested 2026-08-12); no public `env=` yet; keep hard-fail if hook vanishes |
| Auth | Dashboard / service-account `CURSOR_API_KEY` only (OAuth from #40876 cannot unlock SDK) |

## Phased delivery

1. **Scaffold + carve plan** (this doc) — done locally under `/workspace/hermes-cursor-plugin`
2. **MVP package**: `register()` → CLI + skill; REST-only verbs without SDK; lazy SDK import for launch/follow
3. **SDK 1.x cutover** on session/CLI paths; kill or replace private bridge patch
4. **Publish**: create `lawmight/hermes-cursor`, pip metadata, Discord `#plugins-skills-and-skins` promo copy
5. **Optional later**: experimental provider module *only if* #70140 decides ProviderProfile is OK *or* a tiny generic external-runtime seam lands upstream (separate issue, not bundled Cursor code)

## Blockers

1. **`gh` auth on Hermes Cursor box** — not logged in (device flow hit HTTP 429). Need Tom to authorize `gh` (or `GH_TOKEN`) before creating/pushing `lawmight/hermes-cursor`.
2. **Cloud Agent** — useful to implement MVP against connected GitHub once the empty repo exists; can also implement entirely on this box then push.
3. **#70140 still `needs-decision`** — MVP CLI+skill matches recommended option A; full `model.provider` waits on maintainer call.
4. **Live `CURSOR_API_KEY` smoke** — needed before claiming SDK 1.x green (billable).
5. **No generic external-harness plugin hook on Hermes main** — blocks honest full-provider without core PR (which we will not open for Cursor-specific code).

## Non-goals

- In-tree PR to NousResearch/hermes-agent
- Rebase/merge of fork PR #1 onto main
- Claiming Cursor replaces `xai` / `xai-oauth` wallets
- Community OpenAI-compat proxies
