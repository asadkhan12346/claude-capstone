# Automated Documentation Sync Architecture

**Status:** Updated after design review; awaiting human approval before planning  
**Requirements:** [docs/requirements.md](requirements.md)  
**Selected approach:** Option A, a simple modular static-analysis pipeline

## Architecture Overview

The tool is a local command-line application organized as a linear pipeline:

`Scanner -> Extractors -> Fact Model -> Renderer -> Diff/Approval -> Writer`

The CLI validates the selected local repository or folder and coordinates the pipeline. Source code is parsed statically; repository modules are never imported or executed. A shared pre-parser Secret Guard sanitizes eligible content before extractors can retain facts. Extracted facts retain source provenance so missing values can be marked `Not Found` and disagreements can be reported as `Conflicts`. The writer updates only approved generated sections in the root `README.md` and `docs/api.md`, backing up each original to a same-folder `<filename>.bak` before writing.

## Component Diagram

```mermaid
flowchart LR
    User --> CLI["CLI and input validation"]
    CLI --> Scanner["Scanner and pre-open exclusions"]
    Scanner --> Extractors["Pre-parser Secret Guard and static extractors"]
    Scanner -->|no Python files| Empty["Empty-repository README section"]
    Empty --> Renderer
    Extractors --> Facts["Fact Model and conflict resolver"]
    Facts --> Renderer["Markdown renderer"]
    Renderer --> Approval["Diff and approval gate"]
    Approval -->|approved or --yes| Writer["Backup and atomic writer"]
    Approval -->|declined| Reporter["Redacted reporter"]
    Scanner -. warnings .-> Reporter
    Extractors -. warnings .-> Reporter
    Writer -. write errors .-> Reporter
```

## Data Flow

```mermaid
sequenceDiagram
    actor User
    participant CLI
    participant Scanner
    participant Extractors
    participant Facts as Fact Model
    participant Renderer
    participant Gate as Diff/Approval
    participant Writer

    User->>CLI: Local path and optional --yes
    CLI->>Scanner: Validated repository root
    Scanner->>Scanner: Prune .git/excluded directories; enforce scan budgets
    alt No Python files
        Scanner->>Renderer: Empty-repository README section only
        Renderer->>Gate: README change
        Gate-->>User: Redacted diff
        alt --yes supplied
            Gate->>Writer: Authorized README change
        else interactive approval
            User->>Gate: Approve or decline
            Gate->>Writer: README change only when approved
        end
        Writer->>Writer: Revalidate target, back up, atomically write
        Writer-->>CLI: Success
        CLI-->>User: Clear non-error message; no API document generated
    else Python files found
        Scanner->>Extractors: Eligible content through Secret Guard
        Extractors->>Facts: Sanitized facts with file and line provenance
        Facts->>Facts: Resolve missing fields and conflicts
        Facts->>Renderer: Resolved documentation facts
        Renderer->>Gate: Proposed README and API changes
        Gate-->>User: Redacted diff
        alt --yes supplied
            Gate->>Writer: Authorized changes
        else interactive approval
            User->>Gate: Approve or decline
            Gate->>Writer: Changes only when approved
        end
        Writer->>Writer: Revalidate targets, back up, atomically replace files
        Writer-->>User: Completion status and sanitized warnings
    end
```

## Components and Requirement Mapping

| Component | Responsibilities | Requirement IDs |
| --- | --- | --- |
| CLI and input validation | Accept a local path and optional `--yes`; reject invalid paths and non-local inputs; start one on-demand run. | FR-01, FR-07, NFR-04 |
| Scanner | Prune `.git`, tests, CI, excluded directories, and out-of-root symlinks before descent; enumerate supported inputs once; skip `.env`, `*.key`, `*.pem`, and case-insensitive `credentials*` filenames. Enforce a 1,000-file, 5 MiB-per-file, and 100 MiB aggregate scan budget. | FR-01, FR-05, NFR-01, NFR-02, NFR-03 |
| Extractors and Secret Guard | Before parsing, replace matched secret values in an ephemeral sanitized buffer while preserving syntax; if safe sanitization is not possible, skip that file. Parse Python source statically and config safely; extract README facts, API signatures/docstrings, dependencies, entry points, and config variable names. | FR-01, FR-02, FR-03, FR-05, NFR-01 |
| Fact Model and conflict resolver | Store only sanitized facts with source path and line provenance; never retain matched secret values. Merge evidence; produce `Not Found` for unverifiable fields and `Conflicts` notes for contradictory non-sensitive facts. | FR-04, FR-05, NFR-01, NFR-03 |
| Markdown renderer | Render README and API-reference sections from resolved facts; for no-Python inputs, render only the required empty-repository README section and no API document. | FR-02, FR-03, FR-04, FR-05 |
| Diff/Approval gate | Screen existing targets before diff/backup; always show a redacted proposed diff; obtain interactive approval unless `--yes` was supplied; revalidate target fingerprints before writing and regenerate the diff if a target changed. | FR-06, FR-07, NFR-01, NFR-04 |
| Backup and atomic writer | After approval and fingerprint revalidation, copy the original to `<filename>.bak` in the same folder, replacing any older backup; update only the generated marker region or append a new marked section when markers are absent; write through a temporary file and replace atomically. | FR-06, NFR-03 |
| Redacted reporter | Report skipped/malformed files and write failures without including file contents, token values, or passwords. | FR-05, NFR-01, NFR-03, NFR-04 |

## Technology Choices

| Area | Choice | Justification |
| --- | --- | --- |
| Runtime and CLI | Python 3.11+ with standard-library `argparse` and `pathlib`. | Meets the repository's Python rule, supports local paths, and avoids a CLI framework dependency for a small manual tool. |
| Python API extraction | Standard-library `ast` and `tokenize`; never import or execute target modules. | Retrieves modules, signatures, and docstrings without executing untrusted code. A literal `__all__` defines exports when present; otherwise non-underscore top-level functions and classes are public. Include only simple statically resolvable relative re-exports. Dynamic or ambiguous exports are not executed and are reported as `Not Found`. |
| TOML and JSON | `tomllib` and `json` from the standard library. | Native parsers are sufficient for the specified formats and need no additional dependencies. |
| YAML and requirements | `PyYAML` with a bounded `SafeLoader`, and `packaging.requirements.Requirement`. | Safe YAML parsing avoids arbitrary object construction; alias, nesting, and input-size limits bound resource use. `packaging` validates standard dependency specifiers. Unsupported requirements-file directives are warned about rather than guessed. |
| Fact representation | Small typed records containing field, value, source path, and line. | Keeps provenance available for conflicts, review, and `Not Found` decisions without retaining the whole repository. |
| Markdown generation | Project-owned templates and deterministic escaping; standard-library `difflib` for unified diffs. | Keeps output format and marker behavior explicit, reviewable, and independent of an external service. |
| Safe writes | Standard-library `shutil.copy2`, `tempfile`, and `os.replace`. | Keeps the latest same-folder `<filename>.bak` and atomically replaces a target after approval. |
| Tests | `pytest`. | Matches the repository-wide testing rule; tests verify parsing, redaction, conflicts, approval, and marker preservation. Tests are not used as documentation inputs. |

## Error Handling

- Validate the input root before scanning. Invalid or inaccessible roots produce a concise error and no output changes.
- Handle read, decoding, and parse failures per file. Emit a sanitized warning, skip that file, mark dependent facts `Not Found`, and continue scanning.
- When sources disagree, preserve both non-sensitive values and their provenance in a `Conflicts` note. Redact sensitive values in the note.
- If the folder contains no Python files, route a short README section through the same diff/approval/writer path, skip API generation, then print a clear non-error message and exit successfully.
- If the user declines a diff, leave targets and backups unchanged. If backup or atomic replacement fails, preserve the original and report the failure without exposing content.
- If a target has no markers, append a new `<!-- doc-sync:start -->` / `<!-- doc-sync:end -->` section without changing existing content. Update only content inside one valid marker pair.
- If markers are unmatched, duplicated, or malformed, refuse to modify that target and continue with any independent output that can be safely updated.
- Before a write, copy the original to `<filename>.bak` in the same folder. Replace the previous `.bak` so only the latest backup remains.
- Capture a content fingerprint when constructing each diff. After approval and immediately before replacement, compare the current target to that fingerprint; if it changed, do not write and require a fresh diff and approval.
- Prune `.git` and excluded directories before traversal. Enforce scan budgets; over-budget files are skipped with sanitized warnings and affected fields become `Not Found`.

## Security Approach

- All processing is local. The application has no network client, hosting-platform integration, authentication flow, or GitHub API call.
- Apply filename exclusions before opening files: `.env`, `*.key`, `*.pem`, and case-insensitive filenames beginning with `credentials`. Do not read token environment variables.
- Parse Python statically; never import or execute target code. Parse YAML with `safe_load`.
- Run one shared Secret Guard at extractor ingress, before format parsers or the Fact Model receive content. It detects token, password, and API-key patterns, removes matched values in an ephemeral sanitized buffer, and preserves syntax only when safe. If sanitization is uncertain, skip the file, mark affected fields `Not Found`, and report only its path and line.
- Never store matched secret values or partially masked secret values in the Fact Model, generated documents, diffs, backups, warnings, or logs. Affected configuration values are omitted or represented as `Not Found`; ordinary original document content is preserved in backups only when the output preflight finds no secret-like value.
- Screen existing output files before producing a diff or backup. If a secret-like value is found, refuse to update that target and report only its path, so the value is not copied into a backup or diff.
- Sensitive files excluded by name are never opened. Secret-pattern screening of other permitted files is local and transient; token environment variables are never read.

## Testability

| Test level | Scenarios | Requirement coverage |
| --- | --- | --- |
| Unit | Static signatures/docstrings, literal `__all__`, simple relative re-exports, config parsing, `Not Found`, conflicts, malformed files, and per-file warning behavior. | FR-02, FR-03, FR-04, FR-05 |
| Security | Synthetic secret-like values; assert raw and partially masked values never appear in the Fact Model, outputs, diffs, backups, warnings, or logs. Assert excluded filenames are not opened and uncertain sanitization skips the file. | FR-06, NFR-01 |
| Writer | Marker append/update, malformed-marker refusal, diff decline, `--yes`, latest `.bak`, atomic-write failure preservation, secret-bearing target refusal, and changed-target fingerprint detection. | FR-06, NFR-03, NFR-04 |
| Integration | Plain folder and Git repo inputs; `.git` pruning; empty/no-Python path; mixed valid/malformed sources; conflict report; no external calls. | FR-01, FR-05, FR-07 |
| Performance | Representative repository with up to 1,000 eligible files and no more than the aggregate byte budget; measure active processing, excluding human approval wait, and require completion under 60 seconds. | NFR-02, NFR-03 |

## Dependency Risk

The Low-severity dependency-version and update-policy finding is deferred. `PyYAML` and `packaging` remain the selected dependencies; pinning, license review, and update policy must be addressed during implementation planning.

## Future Extensions

The extractor interface can later support plugins for additional source or configuration formats. Version 1 uses only the built-in Python and config extractors; plugin discovery is not part of this design.

## Final Decisions

- Generated sections use `<!-- doc-sync:start -->` and `<!-- doc-sync:end -->`. If neither marker exists, append a new marked section and preserve all existing content. If markers are unmatched, duplicated, or malformed, refuse to update that target.
- Before each write, copy the original file to `<filename>.bak` in the same folder. Replace any previous `.bak`; keep only the latest backup.
- If no Python files are found, send `Repository is empty or contains no supported files` through the README diff/approval/writer path, skip API generation, print a clear non-error message, and exit successfully.
- Skip `.env`, `*.key`, `*.pem`, and case-insensitive `credentials*` files by filename. Discard values matching token, password, or API-key patterns before they enter the Fact Model. Never write matching or partially redacted values to outputs or logs.
- Always show a redacted diff. `--yes` skips the interactive approval prompt, not the diff.
- If an existing output contains a secret-like value, refuse to produce its diff, backup, or update; report only the file path.
- Enforce scan budgets of 1,000 supported files, 5 MiB per file, and 100 MiB aggregate; warn and mark affected facts `Not Found` when a limit is exceeded.
- Revalidate output fingerprints after approval; if a target changed after its diff was prepared, regenerate the diff and obtain approval again.

## Changes After Review

- Synchronized `docs/requirements.md` with the approved marker, backup, empty-repository, and secret-screening decisions.
- Added a pre-parser Secret Guard and fail-closed handling when secret screening or sanitization is uncertain.
- Routed empty-repository output through diff approval and writing; added `.git` pruning, symlink boundaries, and scan budgets.
- Added target-fingerprint revalidation, static public API rules, and focused security, writer, integration, and performance tests.
- Deferred the Low-severity dependency version and update-policy finding.