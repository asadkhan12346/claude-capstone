# Migration: GitHub Copilot → Claude Code

## Baseline (recorded before any change)

```
python -m compileall -q .   → exit 0  (no output)
python -m unittest discover -s tests -v  → Ran 78 tests in 0.870s  OK
```

---

## (a) File migration table

| Old path | New path | Method | Notes |
|---|---|---|---|
| `.github/copilot-instructions.md` | `CLAUDE.md` | `git mv` | Content rewritten (Section 5) |
| `.github/agents/requirements.agent.md` | `.claude/agents/requirements.md` | `git mv` | Content rewritten (Section 6) |
| `.github/agents/architecture.agent.md` | `.claude/agents/architecture.md` | `git mv` | Content rewritten (Section 6) |
| `.github/agents/design-review.agent.md` | `.claude/agents/design-review.md` | `git mv` | Content rewritten (Section 6) |
| `.github/agents/planning.agent.md` | `.claude/agents/planning.md` | `git mv` | Content rewritten (Section 6) |
| `.github/agents/implementation.agent.md` | `.claude/agents/implementation.md` | `git mv` | Content rewritten (Section 6) |
| `.github/agents/review.agent.md` | `.claude/agents/review.md` | `git mv` | Content rewritten (Section 6) |
| `.github/agents/verify.agent.md` | `.claude/agents/verify.md` | `git mv` | Content rewritten (Section 6) |
| `.github/agents/pr.agent.md` | `.claude/agents/pr.md` | `git mv` | Content rewritten (Section 6) |
| `.github/prompts/requirements.prompt.md` | `.claude/commands/requirements.md` | `git mv` | Content rewritten (Section 6) |
| `.github/prompts/architecture.prompt.md` | `.claude/commands/architecture.md` | `git mv` | Content rewritten (Section 6) |
| `.github/prompts/design-review.prompt.md` | `.claude/commands/design-review.md` | `git mv` | Content rewritten (Section 6) |
| `.github/prompts/planning.prompt.md` | `.claude/commands/planning.md` | `git mv` | Content rewritten (Section 6) |
| `.github/prompts/implementation.prompt.md` | `.claude/commands/implementation.md` | `git mv` | Content rewritten (Section 6) |
| `.github/prompts/review.prompt.md` | `.claude/commands/review.md` | `git mv` | Content rewritten (Section 6) |
| `.github/prompts/verify.prompt.md` | `.claude/commands/verify.md` | `git mv` | Content rewritten (Section 6) |
| `.github/prompts/pr.prompt.md` | `.claude/commands/pr.md` | `git mv` | Content rewritten (Section 6) |
| `.github/skills/requirements/SKILL.md` | `.claude/skills/requirements/SKILL.md` | `git mv` | Frontmatter updated (Section 6) |
| `.github/skills/verify/SKILL.md` | `.claude/skills/verify/SKILL.md` | `git mv` | Frontmatter updated (Section 6) |
| `.github/skills/pr/SKILL.md` | `.claude/skills/pr/SKILL.md` | `git mv` | Frontmatter updated (Section 6) |
| `hooks/guard.py` | `.claude/hooks/guard.py` | `git mv` | Payload parsing rewritten (Section 4) |
| `hooks/README.md` | `.claude/hooks/README.md` | `git mv` | Paths updated (Section 7) |
| `.github/hooks/hooks.json` | `.claude/settings.json` | New file (different schema) | hooks + permissions (Section 4) |

### Files that change in-place (not moved)

| File | What changes |
|---|---|
| `sdlc/phases.json` | `agent`/`prompt` paths → new locations; `protected` list → `.claude/hooks/`, `.claude/settings.json` |
| `docs/CONTRACT.md` | All path references updated; "Copilot" → "Claude Code" |
| `orchestrator.py` | Docstring and user-facing text only; zero logic change |
| `README.md` | Paths, "Copilot" → "Claude Code", `chat.useHooks` → `/hooks`/`/agents` instructions |
| `docs/RUNBOOK.md` | Paths, "Copilot" → "Claude Code", `chat.useHooks` → `/hooks` instructions |
| `tests/test_guard.py` | Import path (importlib); payload shapes; setUp directory names |
| `tests/test_config.py` | Agent/command paths; frontmatter field names; skill/hook registration checks |
| `tests/test_docs.py` | README.md and RUNBOOK.md link path to `hooks/README.md` → `.claude/hooks/README.md` |
| `tests/test_e2e_pipeline.py` | Directory list in setUp (`"hooks"`, `".github/hooks"` → `".claude/hooks"`) |
| `tools/audit_repo.py` | Import path (importlib); all `.github/` / `hooks/` paths → new locations |

---

## (b) Every line containing target strings (full inventory)

### "Copilot"

| File | Line | Content |
|---|---|---|
| `README.md` | 1 | `# Agentic SDLC with GitHub Copilot` |
| `README.md` | 3 | `...pipeline driven by GitHub Copilot custom agents.` |
| `README.md` | 101 | `...VS Code Copilot Chat with custom agents/prompts/skills/hooks enabled, and \`chat.useHooks\` enabled.` |
| `CHANGELOG.md` | 9 | `- Eight-phase, human-approved Copilot SDLC workflow...` |
| `tests/test_config.py` | 1 | `"""Structural checks for the phase manifest and Copilot configuration."""` |
| `docs/CONTRACT.md` | 5 | `Each phase has a narrowly scoped Copilot agent and prompt.` |
| `docs/RUNBOOK.md` | 3 | `...Copilot agents must stop after submitting a phase.` |
| `docs/RUNBOOK.md` | 10 | `Run \`python orchestrator.py next\`, then invoke \`/requirements\` in Copilot Chat.` |

### ".github/agents"

| File | Line | Content |
|---|---|---|
| `README.md` | 68 | `Each agent and prompt is under \`.github/agents/\` and \`.github/prompts/\`.` |
| `README.md` | 84 | `├── .github/agents/          # Eight phase agents` |
| `sdlc/phases.json` | 6,13,20,27,34,46,53,60 | `"agent": ".github/agents/<id>.agent.md"` (8 lines) |
| `docs/CONTRACT.md` | 13–20 | All 8 phase table rows reference `.github/agents/...` |
| `artifacts/verify.md` | 95 | `D .github/agents/architect.agent.md` (existing artifact — do not touch) |

### ".github/prompts"

| File | Line | Content |
|---|---|---|
| `README.md` | 68 | `Each agent and prompt is under \`.github/agents/\` and \`.github/prompts/\`.` |
| `README.md` | 86 | `├── .github/prompts/         # Eight slash commands` |
| `sdlc/phases.json` | 7,14,21,28,35,47,54,61 | `"prompt": ".github/prompts/<id>.prompt.md"` (8 lines) |
| `docs/CONTRACT.md` | 13–20 | All 8 phase table rows reference `.github/prompts/...` |

### ".github/skills"

| File | Line | Content |
|---|---|---|
| `README.md` | 87 | `├── .github/skills/          # Requirements, verification, PR methods` |

### ".github/hooks"

| File | Line | Content |
|---|---|---|
| `README.md` | 85 | `├── .github/hooks/           # VS Code hook registration` |
| `hooks/README.md` | 3 | `...registered as a VS Code \`PreToolUse\` hook in \`.github/hooks/hooks.json\`.` |
| `hooks/README.md` | 28 | `Agents must never edit \`.github/hooks/hooks.json\` or turn the hook off...` |
| `sdlc/phases.json` | 71 | `".github/hooks/"` (in protected array) |
| `docs/CONTRACT.md` | 34 | `...hooks/, and .github/hooks/.` |
| `tests/test_config.py` | 62 | `for protected in ("sdlc/", "orchestrator.py", "hooks/**", ".github/hooks/**"):` |
| `tests/test_e2e_pipeline.py` | 34 | `for directory in ("sdlc", "artifacts", "hooks", ".github/hooks"):` |
| `.github/copilot-instructions.md` | 14 | `Never edit \`sdlc/\`, \`orchestrator.py\`, \`hooks/\`, or \`.github/hooks/\` during a phase.` |
| All 8 `.github/agents/*.agent.md` | Forbidden section | `Never edit sdlc/, orchestrator.py, hooks/**, or .github/hooks/**` |
| All 8 `.github/prompts/*.prompt.md` | Scope section | `Never edit sdlc/, orchestrator.py, hooks/, .github/hooks/` |

### "vscode/"

| File | Line | Content |
|---|---|---|
| `.github/agents/requirements.agent.md` | 10 | `  - vscode/askQuestions` |
| `.github/agents/architecture.agent.md` | 10 | `  - vscode/askQuestions` |
| `.github/agents/design-review.agent.md` | 10 | `  - vscode/askQuestions` |
| `.github/agents/planning.agent.md` | 8 | `  - vscode/askQuestions` |
| `tests/test_config.py` | 74 | `self.assertIn("vscode/askQuestions", requirements)` |
| `tests/test_config.py` | 75 | `self.assertIn("vscode/askQuestions", architecture)` |

### "chat.useHooks"

| File | Line | Content |
|---|---|---|
| `README.md` | 101 | `...and \`chat.useHooks\` enabled.` |
| `hooks/README.md` | 3 | `Enable \`chat.useHooks\` in VS Code settings.` |
| `hooks/README.md` | 28 | `A human may disable the hook by changing VS Code's \`chat.useHooks\` setting.` |
| `docs/RUNBOOK.md` | 55 | `Expected: a denial naming R03 and exit code 2. Point: hooks must be enabled with VS Code \`chat.useHooks\`.` |

### "GHCP"

No matches anywhere in the repository.

---

## (c) What stays unchanged (do not touch)

| Path | Reason |
|---|---|
| `orchestrator.py` (logic) | No logic change; only docstring/user-facing text |
| `todo/__init__.py` | Phase 5 output; already complete |
| `todo/app.py` | Phase 5 output; already complete |
| `todo/cli.py` | Phase 5 output; already complete |
| `tests/test_todo.py` | Phase 5 tests; already passing |
| `tests/test_orchestrator.py` (logic) | Orchestrator logic unchanged |
| `artifacts/*.md` | Existing artifacts from prior run; leave as-is |
| `CHANGELOG.md` | Owned by pr phase; do not edit |
| `user_story.md` | Source document; unchanged |
| `sdlc/state.json` | Live state; never hand-edit |
| `sdlc/audit.log.jsonl` | Live audit log; never edit |
| `.editorconfig` | Config; no Copilot references |
| `.gitignore` | No Copilot references |
| `.codemie` | No Copilot references |
| `tests/test_orchestrator.py` | Orchestrator tests; no path changes needed |
| `.github/workflows/` | No workflows present; nothing to touch |
| All `.github/` files | Preserved until Section 9 approval; deleted only then |

---

## Explicit decisions (required by master prompt)

### Decision: `Bash(git push:*)` in deny list

**Chosen: OMIT `Bash(git push:*)` from the `deny` list. Rely on guard rule R04 instead.**

Rationale: Stage B of the pr phase must push a feature branch. R04 already blocks
`git push --force`, `git push -f`, `git push origin main`, and `git push origin master`
while allowing `git push --force-with-lease origin feature-branch` and plain feature
pushes. The `deny` list in settings.json uses a prefix-match against the literal command
string, which is too blunt—it would block every push including legitimate feature branch
pushes. R04 provides the needed granularity at the guard level.

The deny list retains:
```
"Bash(python orchestrator.py approve:*)",
"Bash(python orchestrator.py reject:*)",
"Bash(python orchestrator.py reopen:*)"
```

### Decision: Python import path for `.claude/hooks/guard.py`

Python identifiers cannot begin with a dot, so `import .claude.hooks.guard` is invalid.
Tests and `tools/audit_repo.py` will load the guard via `importlib.util.spec_from_file_location`
using the absolute path. The guard module is NOT exposed as a regular Python package.

### Decision: `guard.py main()` root path

Currently `main()` uses `Path(__file__).resolve().parents[1]` (one level up from `hooks/`).
After moving to `.claude/hooks/guard.py`, one extra level is needed:
`Path(__file__).resolve().parents[2]` (two levels up from `.claude/hooks/` = project root).

### Decision: frontmatter schema after migration

| File type | Required frontmatter fields |
|---|---|
| `.claude/agents/<id>.md` | `name: <id>`, `description: …`, `tools: …`, `model: inherit` |
| `.claude/commands/<id>.md` | `description: …` (and `argument-hint:` where useful) |
| `.claude/skills/<name>/SKILL.md` | `name: …`, `description: …` |

The current `test_config.py` checks for `name:` and `agent:` in prompt frontmatter—these
assertions will be removed in favour of checking `description:` in commands and
`name:`/`description:`/`tools:`/`model:` in agents.

### Decision: `vscode/askQuestions` tool replacement

The four agents that used `vscode/askQuestions` (requirements, architecture, design-review,
planning) will NOT list `AskUserQuestion` in their tools frontmatter. Per Section 3,
subagents cannot ask the human. The main-session slash command owns all clarifying
questions. Agents receive answers passed by the orchestrator session.

The updated `test_tools_are_scoped_to_roles` will verify:
- requirements and architecture agents do NOT contain `vscode/askQuestions`
- implementation and review agents contain `search/usages` equivalent (Grep/Glob tool reference)
- verify agent has testFailure equivalent (Bash with unittest)
- pr agent has changes equivalent (Bash with git diff)

---

## Summary of test changes

| Test file | Change scope |
|---|---|
| `test_config.py` | Agent path `.github/agents/` → `.claude/agents/`; command path; frontmatter fields; skill path; hook registration check (settings.json); protected-path assertions; vscode tool check removed |
| `test_docs.py` | Link-check path `hooks/README.md` → `.claude/hooks/README.md` |
| `test_e2e_pipeline.py` | setUp directory list; protected path strings |
| `test_guard.py` | Import via importlib; payload format (Bash/Write/Edit tool names); setUp mkdir paths |
| `tools/audit_repo.py` | Import via importlib; all `.github/`/`hooks/` path checks |

---

**STOP — awaiting your approval before making any file changes.**
