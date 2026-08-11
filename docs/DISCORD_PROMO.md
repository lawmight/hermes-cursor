# Discord promo draft — `#plugins-skills-and-skins`

Tone: short, honest about roles, no overclaim. Surface when live smoke (at least Phase A+B) is green.

---

**hermes-cursor** — standalone community plugin (not in-tree)

Drive Cursor agents from Hermes without patching NousResearch/hermes-agent.

- `hermes cursor me|models|repos|launch|list|status|follow|send|…`
- Bundled `cursor-cloud` skill (`skill_view("hermes-cursor:cursor-cloud")`)
- Auth: `CURSOR_API_KEY` in `$HERMES_HOME/.env`
- SDK: optional `cursor-sdk==1.0.27` (lazy); REST catalog works without it

**Roles (important):** Cursor owns the inner agent loop / tools. Hermes keeps sessions, memory, gateway, cron. This is **not** `model.provider=cursor` — matches the upstream standalone-plugin guidance (#70140).

Install:

```bash
git clone https://github.com/lawmight/hermes-cursor
cd hermes-cursor
pip install -e '.[sdk]'
mkdir -p ~/.hermes/plugins && ln -sfn "$(pwd)" ~/.hermes/plugins/hermes-cursor
hermes plugins enable hermes-cursor
```

Repo: https://github.com/lawmight/hermes-cursor

Feedback / breakage welcome here. PRs to the standalone repo only — please don't open Cursor provider PRs against hermes-agent core.

---

Shorter alt (if the channel prefers one-liners):

> **hermes-cursor** — `hermes cursor` CLI + skill for Cursor cloud/local agents via official SDK. Standalone plugin (`~/.hermes/plugins` / pip). Not an in-tree provider. https://github.com/lawmight/hermes-cursor
