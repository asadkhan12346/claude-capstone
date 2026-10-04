# Automated Documentation Sync Implementation Plan

**Status:** Draft; awaiting human approval before implementation  
**Basis:** Approved requirements, approved Option A architecture, and accepted design-review findings  
**Estimate note:** Estimates are engineering effort, excluding human approval wait time.

## Current Execution Status (2026-10-05)

| Category | Status |
| --- | --- |
| Tasks done | T-01: runtime/dependency policy and metadata; T-02: package and CLI bootstrap; T-03: repository scanner implementation; T-04: secret guard; T-05: Python API extraction; T-06: project/config extraction; T-07: fact model and resolver; T-08: README and API rendering; T-09: diff/approval and marker handling; T-10: safe backup writer; T-11: pipeline and reporting; T-12: end-to-end and integration coverage. |
| Tasks remaining | None. |
| Tasks now unblocked | None; implementation is complete and awaiting approval. |
| Blocked tasks | None. |
| Failing tests | None; the project pytest suite passes. |

**Latest full-suite result:** `.venv\Scripts\python.exe -m pytest -q` passed (20 tests), including the T-07 through T-12 checks. Editable installation succeeded, and the pipeline created README and API outputs for a representative project. The clean environment uses Python 3.13. The selected minimum, Python 3.11, is not installed locally, so execution on the minimum runtime remains unverified and should be covered in CI or when Python 3.11 is available.

## Dependency-Ordered Tasks

| ID | Title | Description | Files touched | Dependencies | Priority | Estimate | Requirement IDs | Copilot feature |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| T-01 | Resolve runtime and dependency policy | Record the confirmed Python range and minimum-only dependencies in requirements and project metadata; add metadata tests. | `docs/requirements.md`, `pyproject.toml`, `tests/test_project_metadata.py` | None | P0; Done | 0.5 day | NFR-02, NFR-03 | requirements-analyst agent + requirements prompt |
| T-02 | Bootstrap package and CLI | Add the installable package, `argparse` entry point, target path validation, `--yes` parsing, and help/usage behavior. | `pyproject.toml`, `src/doc_sync/__init__.py`, `src/doc_sync/__main__.py`, `src/doc_sync/cli.py`, `tests/test_cli.py` | T-01 | P1; Done | 0.5 day | FR-01, FR-07, NFR-04 | implementer agent + post-edit hook |
| T-03 | Implement repository scanner | Walk local Git repos/plain folders once; prune `.git`, tests, CI and excluded directories; reject out-of-root symlinks; enforce file-count and byte budgets. | `src/doc_sync/scanner.py`, `tests/test_scanner.py` | T-02 | P1; Done | 0.5 day | FR-01, FR-05, NFR-02, NFR-03 | implementer agent + post-edit hook |
| T-04 | Add Secret Guard | Exclude sensitive filenames before opening; screen permitted content before parsing; discard matches, fail closed on uncertain sanitization, and report location only. | `src/doc_sync/security.py`, `tests/test_security.py` | T-03 | P1; Done | 0.5-1 day | FR-05, FR-06, NFR-01 | implementer agent + post-edit hook |
| T-05 | Extract Python API facts | Use `ast`/`tokenize` without imports to list modules and public functions/classes, signatures, docstrings, literal `__all__`, and simple static relative re-exports. | `src/doc_sync/extractors/python_api.py`, `tests/test_python_api.py` | T-04 | P1; Done | 1 day | FR-03, FR-04, NFR-01 | implementer agent + post-edit hook |
| T-06 | Extract project/config facts | Parse TOML, JSON, YAML, `.env.example`, requirements, and existing README for dependencies, entry points, config names, overview/usage facts; skip malformed files independently. | `src/doc_sync/extractors/project_config.py`, `tests/test_project_config.py` | T-01, T-04 | P1; Done | 1 day | FR-01, FR-02, FR-04, FR-05 | implementer agent + post-edit hook |
| T-07 | Build fact model and resolver | Store sanitized values with source locations; merge evidence; represent missing fields as exact `Not Found`; retain non-sensitive conflicts. | `src/doc_sync/facts.py`, `tests/test_facts.py` | T-05, T-06 | P1; Done | 0.5 day | FR-04, FR-05, NFR-01, NFR-03 | implementer agent + post-edit hook |
| T-08 | Render Markdown documents | Render the root README and `docs/api.md` from facts; escape Markdown safely; render the exact no-Python README section and omit API output in that path. | `src/doc_sync/rendering.py`, `tests/test_rendering.py` | T-07 | P1; Done | 0.5-1 day | FR-02, FR-03, FR-04, FR-05 | implementer agent + verify prompt + post-edit hook |
| T-09 | Implement diff and marker handling | Produce a redacted diff every run; support approval and `--yes`; append a marker pair when absent; update only one valid pair; reject malformed/duplicate pairs; fingerprint targets and re-prompt on changes. | `src/doc_sync/approval.py`, `src/doc_sync/markers.py`, `tests/test_approval.py`, `tests/test_markers.py` | T-08 | P1; Done | 1 day | FR-06, NFR-03, NFR-04 | implementer agent + verify prompt + post-edit hook |
| T-10 | Implement safe backup writer | Revalidate fingerprints immediately before writing; refuse secret-bearing targets; retain only same-folder `<filename>.bak`; write via temporary file and atomic replacement. | `src/doc_sync/writer.py`, `tests/test_writer.py` | T-09 | P1; Done | 0.5-1 day | FR-06, NFR-01, NFR-03 | implementer agent + verify prompt + post-edit hook |
| T-11 | Connect pipeline and error reporting | Orchestrate scanner through writer; continue after per-file errors; emit sanitized warnings; route the no-Python path through README diff/approval/write and exit successfully. | `src/doc_sync/pipeline.py`, `src/doc_sync/reporting.py`, `tests/test_pipeline.py` | T-03, T-04, T-07, T-08, T-09, T-10 | P1; Done | 0.5-1 day | FR-01, FR-05, FR-07, NFR-01, NFR-03, NFR-04 | implementer agent + verify prompt + post-edit hook |
| T-12 | Add end-to-end and performance coverage | Exercise plain folders and Git repos, safe update behavior, failure paths, and a 1,000-file/100-MiB fixture within the active 60-second target. | `tests/integration/`, `tests/performance/` | T-11 | P1; Done | 1 day | FR-01 through FR-07, NFR-01 through NFR-04 | implementer agent + verify prompt + post-edit hook |

## Definition of Done

### T-01: Resolve runtime and dependency policy

- Human decision records the supported Python runtime range and PyYAML/`packaging` version constraints and update policy; update `docs/requirements.md` and metadata consistently.
- Tests/checks: metadata tests pass; clean Python 3.13 environment install and dependency resolution succeed. Python 3.11 execution was not verifiable locally because that interpreter is unavailable; run the same checks on 3.11 in CI or when available.

### T-02: Bootstrap package and CLI

- Package installs in the selected environment; command/module entry point displays help and validates required arguments.
- Tests: `--help`, valid local directory, missing path, non-directory path, and `--yes` parsing.

### T-03: Implement repository scanner

- Scanner supports Git and plain-folder targets, visits supported files once, prunes excluded directories, refuses out-of-root symlinks, and enforces all three scan limits with sanitized warnings.
- Tests: included/excluded files, nested `.git`, symlink escape, over-count, over-size, aggregate-size, unreadable path, and empty input.

### T-04: Add Secret Guard

- Excluded secret filenames are never opened; permitted inputs are screened before parsing; matched values never enter the fact model or emitted diagnostics; uncertain cases skip safely.
- Tests: synthetic token/password/API-key patterns, false positives, excluded-file open spy, sanitizer uncertainty, and assertions that raw and partially masked fixtures are absent from captured output.

### T-05: Extract Python API facts

- Python files are parsed statically only. Public-name rules match architecture; dynamic imports/exports are never executed and ambiguous items are represented as `Not Found`.
- Tests: modules, functions, classes, signatures, docstrings, literal `__all__`, simple relative re-exports, syntax errors, dynamic exports, and a module with a side effect proving it was not imported.

### T-06: Extract project/config facts

- Supported project/config files produce evidence-backed fields; unsupported directives and malformed files warn and skip without aborting other extraction.
- Tests: valid/malformed TOML and JSON, bounded safe YAML including alias/nesting limits, `.env.example` names only, requirements specifiers/directives, README facts, missing inputs, and continuation after one parser failure.

### T-07: Build fact model and resolver

- Facts contain sanitized value and provenance only; absent/unverifiable fields use exact `Not Found`; conflicts preserve both non-sensitive values and references.
- Tests: provenance retention, missing field, conflicting values, sensitive-value rejection, and no accidental fabricated defaults.

### T-08: Render Markdown documents

- README contains all required fields; API doc lists verified API facts; Markdown is escaped; no-Python targets produce the exact README notice and no API document.
- Tests: snapshot/content assertions for complete facts, missing facts, conflicts, special Markdown characters, and empty/no-Python output.

### T-09: Implement diff and marker handling

- Diff is always available, `--yes` skips only the interactive prompt, declined changes are not written, absent markers append safely, and malformed/duplicate markers fail closed.
- Tests: diff content, interactive approve/decline, `--yes`, append, replace inside markers, preserve outside content, unmatched/duplicate markers, and changed fingerprint requiring a fresh approval.

### T-10: Implement safe backup writer

- Secret-bearing targets are refused before diff/backup; approved targets get one latest `.bak`; writes are atomic and original content survives write failure.
- Tests: first backup, replacement of prior `.bak`, backup failure, atomic-replace failure, target race after approval, secret-bearing target produces no diff/backup, and output bytes match approved content.

### T-11: Connect pipeline and error reporting

- One bad file does not abort the run; warnings reveal paths and safe reasons only; no-Python path writes through the normal safety path and exits with a clear success message.
- Tests: mixed valid/malformed repository, invalid target, empty/no-Python run, declined diff, parser and writer failures, warning redaction, and no external/network calls.

### T-12: Add end-to-end and performance coverage

- End-to-end requirements are covered, with test results reproducible through pytest; performance target is measured and documented.
- Tests: complete pytest suite; representative 1,000-supported-file/100-MiB repository completes active processing under 60 seconds; security assertions cover Fact Model, output, diff, backup, warning, and log capture.

## Blocked Tasks

- **T-04 through T-12 are blocked** on T-03 completion, according to the dependency chain in the task table.
- Python 3.11 runtime execution remains a verification gap for T-01, not a blocker for T-02; add a Python 3.11 CI check before claiming the supported minimum has been exercised.

## Copilot Workflow and Approval Gate

- T-01's runtime and dependency decisions are resolved and recorded in `docs/requirements.md` and `pyproject.toml`.
- Use the implementer agent for one task at a time. The post-edit hook runs pytest and scans changed files after edits; use the verify prompt for documented acceptance checks.
- After T-12, obtain human approval before code review, use the code-reviewer agent and code-review prompt, then run verification and create `docs/test-report.md` with the verify prompt.
- T-06 is complete; proceed to T-07 only after the next human approval gate for the implementation sequence.