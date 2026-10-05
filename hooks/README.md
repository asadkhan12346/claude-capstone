# SDLC Guard

The guard is registered as a VS Code `PreToolUse` hook in `.github/hooks/hooks.json`. Enable `chat.useHooks` in VS Code settings. It reads one JSON payload from stdin, prints nothing for an allowed operation, and emits a structured denial to stdout/stderr with exit code 2 when blocked. Malformed input fails closed.

| Rule | Blocks | Safe alternative |
|---|---|---|
| R01 | Recursive deletion of root, home, repository, `.git`, `.`/`..`, or bare wildcard | Target one disposable path |
| R02 | Filesystem formatting, `dd` to a device, writes to `/dev/sd*`, or recursive mode 777 | Use a targeted reversible operation |
| R03 | Hard reset, forced clean, destructive checkout/restore, deleting main/master, history filtering, or rebasing onto main/master | Inspect changes and use a narrow reversible operation |
| R04 | Force push, `+refspec`, or push to main/master | Push a feature branch without force |
| R05 | Hook/verification bypasses and common piped-shell execution | Use reviewed commands and normal hooks |
| R06 | Agent invocation of approve/reject/reopen | A human uses an interactive terminal |
| R07 | Writes to protected pipeline files/directories | Write only an active phase-owned file |
| R08 | Writes to files owned by a phase other than ACTIVE | Check orchestrator status and write only active outputs |

## Manual check

From the repository root, run:

```powershell
'{"tool_name":"run_in_terminal","tool_input":{"command":"git reset --hard"}}' | python hooks/guard.py
```

Expected: JSON denial includes `[R03]`; exit code is 2. A benign `git status` payload should be allowed with no output and exit code 0.

## Disable hook

A human may disable the hook by changing VS Code's `chat.useHooks` setting. Agents must never edit `.github/hooks/hooks.json` or turn the hook off to bypass a denial.
