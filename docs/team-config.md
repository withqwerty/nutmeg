# Team and user config

Nutmeg reads two config files. For every setting, the stricter of the two applies.

| File | Where | Who changes it |
|---|---|---|
| Team config | `.nutmeg/team.json` in the team's repository | The team, through normal code review |
| User config | `~/.config/nutmeg/user.json` (or `$XDG_CONFIG_HOME/nutmeg/user.json`, or the path in `$NUTMEG_USER_CONFIG`) | The user, through `/nutmeg` setup or `nutmeg config set` |

`nutmeg config show` prints the settings in force and why. When either file changes during a session, the
next gate asks again and writes a `gate_settings_changed` receipt.

## Autonomy levels

Each stage (plan, run, publish) has a level. A lower level is stricter.

| Level | Name | What happens |
|---|---|---|
| L1 | Suggest | Nutmeg shows the card (`nutmeg gate`) and the user runs the code. |
| L2 | Draft | Nutmeg asks before each run and each publish. |
| L3 | Execute with checkpoints | As L2. With `run_then_review`, a run goes ahead and its card waits in the review queue (`nutmeg queue`). Publishing always asks. |

Persona defaults: `fanalyst` L3, `club` L2, `company` L2.

## Team keys (`.nutmeg/team.json`)

| Key | Type | Default | Meaning |
|---|---|---|---|
| `max_autonomy` | object | none | The highest level allowed per stage, for example `{"plan": "L2", "run": "L2", "publish": "L2"}`. A user level above it drops to it. |
| `allow_run_then_review` | boolean | `true` | `false` means every run asks, whatever the user sets. |
| `persona_default` | string | `club` | The persona for users who have not chosen one. |
| `approved_services` | list of hosts | `[]` | Services the team has approved. The run card labels each detected or declared host "approved by team" or "not on the team list". Nutmeg never blocks a step because of this. |
| `approved_ai_providers` | list of strings | `[]` | The AI providers the club has sanctioned, for reference on cards and in bundles. |
| `licences` | object | `{}` | A licence note per provider, for example `{"opta": "Internal use only; no redistribution"}`. Bundles show the note when they include raw data. |
| `data_in_git` | `yes`, `no` or `ask` | `ask` | Whether new projects commit data, run outputs and figure snapshots. `ask` makes `nutmeg new` ask per project. A user may keep data out when the team says `yes`, never the reverse. |
| `signoff` | object | `{"required": false}` | `{"required": true}` means a headline claim counts as verified only after a teammate who is not its author runs `nutmeg signoff`. Until then `nutmeg check` reports it and publishing refuses. |

Example:

```json
{
  "max_autonomy": {"plan": "L2", "run": "L2", "publish": "L2"},
  "allow_run_then_review": false,
  "persona_default": "club",
  "approved_services": ["statsbomb.com", "api.wyscout.com"],
  "approved_ai_providers": ["Anthropic (Claude for Work)"],
  "licences": {"opta": "Club licence: internal use only; no redistribution"},
  "data_in_git": "no",
  "signoff": {"required": true}
}
```

## User keys (`user.json`)

| Key | Type | Meaning |
|---|---|---|
| `persona` | `fanalyst`, `club` or `company` | Sets the default levels. |
| `autonomy_plan`, `autonomy_run`, `autonomy_publish` | `L1`, `L2` or `L3` | Per-stage levels; the team's `max_autonomy` still applies. |
| `run_then_review` | boolean | Let runs at L3 go ahead and queue their cards for review. |
| `name` | string | The name on sign-offs, contests and notes (default: `git config user.name`). |

Set them with, for example:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/core/nutmeg.py" config set --persona fanalyst --autonomy-run L3 --run-then-review yes
```

## Sign-off

- Mark a headline claim with `nutmeg claim add --headline ...`.
- A teammate checks it (`nutmeg why <claim>`) and runs `nutmeg signoff <claim> --note "<what I checked>"`.
- Changing a claim's statement, value or evidence returns it to draft and clears the sign-off.
