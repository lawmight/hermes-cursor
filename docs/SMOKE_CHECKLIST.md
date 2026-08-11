# Live CURSOR_API_KEY smoke checklist

Use a **real** Cursor user or service-account API key from
[Cursor Dashboard → Integrations / API Keys](https://cursor.com/dashboard?tab=integrations).
Prefer a throwaway key for the first pass. Cloud `launch` is billable.

## Prep

- [ ] Hermes installed and working (`hermes --version`)
- [ ] Clone `https://github.com/lawmight/hermes-cursor`
- [ ] `python3 -m pip install -e '.[sdk]'` (pins `cursor-sdk==1.0.27`)
- [ ] `mkdir -p ~/.hermes/plugins && ln -sfn "$(pwd)" ~/.hermes/plugins/hermes-cursor`
- [ ] `hermes plugins enable hermes-cursor` (plugins are opt-in)
- [ ] `CURSOR_API_KEY` in `$HERMES_HOME/.env` (or export for the shell)
- [ ] Optional debug: `HERMES_PLUGINS_DEBUG=1 hermes plugins list` → see `hermes-cursor` + CLI command `cursor`

## Phase A — REST only (no agent loop)

- [ ] `hermes cursor me` → prints account / key name (map `userEmail` / `apiKeyName` fields)
- [ ] `hermes cursor models` → non-empty catalog (accepts API `items` or `models` shape)
- [ ] Confirm **no** `cursor-sdk` wheel was required for A (stdlib urllib path)

## Phase B — SDK cloud verbs

- [ ] `hermes cursor repos` → connected SCM repos (or clear empty)
- [ ] `hermes cursor list` → agents list (may be empty)
- [ ] `hermes cursor launch "Reply with exactly CURSOR_SMOKE_OK and stop" --repo <connected-repo-url> --ref main`
  - `--model` defaults to `default` (account default); override with `--model <id>` if needed
  - Capture `bc-…` id
  - Prefer a tiny public/private repo Tom owns; avoid production
- [ ] `hermes cursor status bc-…` → progresses / finishes (pass `runtime=cloud` internally if needed)
- [ ] `hermes cursor follow bc-…` → shows assistant text (falls back to `wait().result` if stream is status-only); look for `CURSOR_SMOKE_OK`
- [ ] `hermes cursor send bc-… "Confirm still CURSOR_SMOKE_OK" --follow`
- [ ] `hermes cursor artifacts bc-…` → lists or empty (OK)
- [ ] `hermes cursor cancel bc-…` on a deliberately long launch (optional interrupt path)
- [ ] Cleanup: `hermes cursor archive bc-…` (or `delete` if you want it gone)

## Phase C — skill path

- [ ] In a Hermes session: `skill_view("hermes-cursor:cursor-cloud")` loads
- [ ] Ask Hermes to run `hermes cursor me` via terminal → same success as Phase A

## Phase D — bridge / secret hygiene (local runtime)

Only if testing **local** SDK agents (`runtime: local`):

- [ ] Launch a local agent with Hermes env containing dummy secrets
  (`HERMES_DUMMY=secret`, `OPENAI_API_KEY=sk-test`, etc.)
- [ ] Confirm bridge subprocess env does **not** contain those keys
  (plugin patches `_bridge_subprocess_env`; guardrail test:
  `pytest tests/test_bridge_sdk_hook.py`)
- [ ] If the private hook is missing on a newer pin → launch must **hard-fail**,
  never silently inherit `os.environ`

## Pass / fail

| Gate | Pass criteria |
| --- | --- |
| A | `me` + `models` green |
| B | one launch → follow shows smoke string; status/list work |
| C | skill loads; CLI reachable from session |
| D | no Hermes secret leakage; hook absence fails closed |

**Do not** claim `model.provider=cursor` in README or docs after smoke.
Report results + any API field mismatches back through Chief of Staff.
