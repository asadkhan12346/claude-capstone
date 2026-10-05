# Agentic SDLC Project Instructions

## Pipeline
- Read `docs/CONTRACT.md` and run `python orchestrator.py status` before work.
- Work only when your phase is ACTIVE and only in files it owns.
- Submit with `python orchestrator.py submit <phase>` and stop for human approval.

## Requirements
- Ask the human about ambiguities; never assume answers.
- Record each answer with its source. Keep the pipeline story-agnostic.

## Scope
- Make minimal changes only to phase-owned files. Never create later-phase artifacts.
- Never edit `sdlc/`, `orchestrator.py`, `hooks/`, or `.github/hooks/` during a phase.

## Code quality
- Python 3.11+, standard library only, PEP 8, type hints on every function signature.
- No bare `except:` clauses, network calls in application code, or secrets.

## Testing
- Use `unittest` only. Run `python -m unittest discover -s tests -v` after code changes.
- Run `python -m compileall -q .` before implementation submission.

## Traceability
- Define FR-/NFR- IDs in requirements and cite them in later artifacts and tests.

## Human approval
- Agents never run `approve`, `reject`, or `reopen`.
- After submit, stop and print exactly: `Awaiting human approval. Run: python orchestrator.py approve <phase> --by <your-name>`.

## Git and auditability
- No force push, history rewrite, `--no-verify`, or push to main/master.
- Report only observed facts and real command output. Never claim an unrun check passed.
