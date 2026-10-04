# Automated Documentation Sync Requirements

**Status:** Approved by user; baseline synchronized after design review  
**Basis:** User story and clarified answers provided by the user

## Overview

As a developer, I want documentation to be automatically generated and synced from my repository's code and config so that docs never go stale.

The tool documents verifiable facts from local Python projects. It generates Markdown only and preserves hand-written content while requiring approval before modifying existing documentation.

## Scope

### In Scope

- Local Git repositories or plain folders containing Python projects.
- Manual, on-demand command-line invocation.
- Inspection of Python source files, `requirements.txt`, `pyproject.toml`, `.env.example`, YAML and JSON configuration, and the existing root `README.md`.
- Prune `.git`, tests, and CI directories before descent; do not follow symlinks outside the selected root.
- Bound scanning to 1,000 supported files, 5 MiB per file, and 100 MiB aggregate input. Skip over-budget inputs with a warning and mark affected fields `Not Found`.
- Generation or update of the root `README.md` and `docs/api.md`.
- Documentation based only on verifiable repository facts.

### Out of Scope

- Languages other than Python.
- Hosted-repository platform support, GitHub API access, and authentication.
- Commit history, CI files, and tests as documentation sources.
- Scheduling or background runs.
- Sending repository content to external services.

## Functional Requirements

### FR-01: Inspect supported local Python projects

Accept a local Git repository or plain folder containing a Python project. Inspect Python source, `requirements.txt`, `pyproject.toml`, `.env.example`, YAML/JSON configuration files, and the existing root README. Do not use commit history, CI files, or tests as sources.

**Acceptance criteria**
- A local Git checkout and a plain Python-project folder can each be selected as input.
- Facts are gathered from the listed source and configuration files when present.
- Non-Python languages, commit history, CI files, and tests are not used to generate documentation.
- Missing source files do not prevent processing of other available inputs.

### FR-02: Generate or update the project README

Generate or update the repository-root `README.md` in Markdown with project name, description, dependencies, entry points, configuration variables, installation, and usage.

**Acceptance criteria**
- The README contains each requested field.
- Each value is supported by an inspected repository file; an unverifiable value is written as the exact text `Not Found`.
- The output is Markdown and is written to the repository root.

### FR-03: Generate the API reference

Generate or update `docs/api.md` in Markdown with the project's modules and its public functions and classes, including verified signatures and docstrings.

**Acceptance criteria**
- The API reference lists modules and public functions/classes discoverable in Python source files.
- Each listed signature and docstring matches verifiable source; missing information is `Not Found` rather than inferred.
- The output is written to `docs/api.md` in Markdown.

### FR-04: Ground facts and represent uncertainty

Use only facts verified from repository files. Represent missing information and conflicts explicitly.

**Acceptance criteria**
- No undocumented assumptions or invented values appear in generated content.
- A field that cannot be verified contains exactly `Not Found`.
- Contradictory verified values are both recorded in a `Conflicts` note.

### FR-05: Handle malformed, missing, and empty inputs

Continue the documentation run when an individual file is missing or malformed, and handle empty repositories without crashing.

**Acceptance criteria**
- A missing file results in `Not Found` for affected fields, while processing continues.
- A malformed file is skipped, produces a warning, results in `Not Found` for affected fields, and does not abort the run.
- Warnings do not expose sensitive content.
- If the selected folder contains no Python files, the root README receives a marked section stating exactly `Repository is empty or contains no supported files`; API generation is skipped, a clear non-error message is printed, and the run exits successfully.

### FR-06: Protect existing documentation during updates

Never silently overwrite existing documentation. Always show a proposed diff. Require approval before writing unless the user explicitly supplies `--yes`, which skips the prompt but not the diff. Before writing, copy the original to `<filename>.bak` in the same folder, replacing any previous backup so only the latest remains. Update only content between `<!-- doc-sync:start -->` and `<!-- doc-sync:end -->` markers. If neither marker exists, append a new marked section without changing existing content; if markers are unmatched, duplicated, or malformed, refuse that target. Fingerprint targets when generating diffs and revalidate after approval. If a target changes, regenerate the diff and require approval again. If an existing target contains a secret-like value, do not diff, back up, or update it; report only its path.

**Acceptance criteria**
- Without `--yes`, an existing document is not changed until the user approves the proposed diff.
- With `--yes`, the update is explicitly authorized, but the diff is still shown.
- A backup of the original document exists as `<filename>.bak` in the same folder before it is modified; only the latest backup is retained.
- Content outside a valid marker pair remains unchanged. If markers are absent, the generated section is appended; if markers are malformed or duplicated, that target is not modified.
- If the target changes after diff generation, no write occurs until a fresh diff is shown and approved.
- A target containing a secret-like value is not diffed, backed up, or modified.

### FR-07: Run locally on demand

Provide manual command-line execution for local targets without authentication, GitHub API access, or external services.

**Acceptance criteria**
- The user can invoke a documentation run manually from the command line.
- The version 1 workflow makes no external service calls and requires no authentication.
- No scheduled or background run is required.

## Non-Functional Requirements

### NFR-01: Security and privacy

- Process repository content locally; do not send it to external services.
- Never open `.env`, `*.key`, `*.pem`, or case-insensitive `credentials*` files.
- A local pre-parser Secret Guard screens permitted input for token, password, and API-key patterns. It discards matches before parsers or the Fact Model receive the value; if safe sanitization is uncertain, the file is skipped and affected fields are `Not Found`.
- Never retain matched values or write raw or partially masked values to generated documents, diffs, backups, warnings, or logs. If an existing output contains a secret-like value, refuse to update it and report only its path.
- If a token is supplied through an environment variable, never print or write it to any output or log.

### NFR-02: Performance

- Support repositories containing up to approximately 1,000 supported files and 100 MiB of aggregate input, with no supported input file larger than 5 MiB.
- Complete active processing in under 60 seconds at that limit; time waiting for human diff approval is excluded.

### NFR-03: Reliability

- A failure in one input file must not crash the whole run.
- Missing and malformed inputs must be reported as specified in FR-05.
- Preserve original files through backups and marker-bounded updates as specified in FR-06.
- Do not write a target whose content changed after its approval diff was generated; regenerate the diff and request approval again.

### NFR-04: Usability

- The tool is manually invoked from the command line.
- Proposed changes are reviewable as a diff and require approval by default; `--yes` provides explicit non-interactive authorization.
- Warnings identify issues without exposing sensitive values.

## Assumptions and Constraints

- Target repositories are Python projects; the tool does not document other languages in version 1.
- The tool is for local Git repositories or plain folders; hosting-platform integration and authentication are not part of version 1.
- The source inputs are limited to Python files, `requirements.txt`, `pyproject.toml`, `.env.example`, YAML/JSON configuration files, and the existing root README. Commit history, CI files, and tests are excluded.
- Generated outputs are the root `README.md` and `docs/api.md`; both are Markdown.
- Project implementation follows the repository rule to use Python 3.11+ and pytest. Whether the tool's supported runtime is exactly Python 3.11+ is `Not Found`.
- No exact CLI command name or invocation syntax has been specified beyond the `--yes` flag.

## Open Questions

- Exact CLI command name and invocation syntax, other than the `--yes` flag: `Not Found`.
- Exact supported Python runtime versions for the tool itself: `Not Found`.
- Supported/pinned versions and update policy for PyYAML and `packaging`: `Not Found` (deferred to implementation planning).