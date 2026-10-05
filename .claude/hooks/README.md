# PreToolUse Guard

`.claude/hooks/guard.py` is a fail-closed PreToolUse hook registered in `.claude/settings.json`. Claude Code invokes it before every `Bash`, `Write`, `Edit`, `MultiEdit`, and `NotebookEdit` tool call.

Run `/hooks` in Claude Code to confirm the PreToolUse hook is loaded.

## Rules

| ID | Description | What it blocks |
|---|---|---|
| R01 | Recursive deletion of a dangerous target | `rm -rf /`, `rm -rf .`, `rm -rf ~`, etc. |
| R02 | Filesystem destruction or unsafe permissions | `mkfs`, `dd of=/dev/sd*`, `chmod -R 777` |
| R03 | Destructive Git history or working-tree operation | `git reset --hard`, `git clean -f`, `git restore .`, `git checkout .`, `filter-branch` |
| R04 | Force push or push to a protected branch | `git push --force`, `git push -f`, `git push origin main` |
| R05 | Verification or shell safety bypass | `--no-verify`, `curl | sh`, `base64 -d | sh`, `eval | sh` |
| R06 | Agent attempted a human-only approval action | `python orchestrator.py approve/reject/reopen` |
| R07 | Write to a protected pipeline file | Writes to `sdlc/`, `orchestrator.py`, `.claude/hooks/`, `.claude/settings.json` |
| R08 | Write outside the ACTIVE phase ownership | Writes to another phase's owned files |

## Exit behavior

- **Exit 0**: operation allowed (no output).
- **Exit 2**: operation blocked; the denial message is printed to stderr.
- **Fail closed**: any exception or malformed input blocks the call with a FAIL-CLOSED message.

## Limitations

- Shell parsing is necessarily incomplete; a determined user can construct payloads that evade the regex-based rules.
- Approval is bypassable by a user who edits `sdlc/state.json` directly; the hook cannot prevent filesystem access.
- The hook is not active during `python orchestrator.py approve/reject/reopen` because those run in a plain terminal, not through Claude Code tools.
- A human may unload the hook by editing `.claude/settings.json`. Agents must never edit `.claude/hooks/guard.py` or `.claude/settings.json` to bypass a denial.

## Registration

The hook is wired in `.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash|Write|Edit|MultiEdit|NotebookEdit",
        "hooks": [
          {"type": "command",
           "command": "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/guard.py\"",
           "timeout": 15}
        ]
      }
    ]
  }
}
```

Run `/hooks` in Claude Code to confirm the hook is active. Run `/agents` to confirm the 8 agents appear.
