# Automated Documentation Sync Requirements

**Status:** Draft, awaiting human approval  
**Basis:** User story and clarified answers provided by the user

## Overview

As a developer, I want documentation to be automatically generated and synced from my repository's code and config so that docs never go stale.

The tool documents verifiable facts from local Python projects. It generates Markdown only and preserves hand-written content while requiring approval before modifying existing documentation.

## Scope

### In Scope

- Local Git repositories or plain folders containing Python projects.
- Manual, on-demand command-line invocation.
- Inspection of Python source files, `requirements.txt`, `pyproject.toml`, `.env.example`, YAML and JSON configuration, and the existing root `README.md`.
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
- An empty repository produces a short Markdown document stating that the repository is empty and does not invent project or API details.

### FR-06: Protect existing documentation during updates

Never silently overwrite existing documentation. Show a proposed diff and require approval before writing, unless the user explicitly supplies `--yes`. Keep a backup of each original file. Update only content between `<!-- doc-sync:start -->` and `<!-- doc-sync:end -->` markers, preserving hand-written content outside them.

**Acceptance criteria**
- Without `--yes`, an existing document is not changed until the user approves the proposed diff.
- With `--yes`, the update is explicitly authorized.
- A backup of the original document exists before it is modified.
- Content outside the marker pair remains unchanged.

### FR-07: Run locally on demand

Provide manual command-line execution for local targets without authentication, GitHub API access, or external services.

**Acceptance criteria**
- The user can invoke a documentation run manually from the command line.
- The version 1 workflow makes no external service calls and requires no authentication.
- No scheduled or background run is required.

## Non-Functional Requirements

### NFR-01: Security and privacy

- Process repository content locally; do not send it to external services.
- Skip `.env`, `*.key`, `*.pem`, and credential files.
- Never read, print, or write secret values to generated documents, diffs, warnings, or logs. Redact content that looks like a token or password before it can appear in output.
- If a token is supplied through an environment variable, never print or write it to any output or log.

### NFR-02: Performance

- Support repositories containing up to approximately 1,000 files.
- Complete a run in under 60 seconds for a repository of that size.

### NFR-03: Reliability

- A failure in one input file must not crash the whole run.
- Missing and malformed inputs must be reported as specified in FR-05.
- Preserve original files through backups and marker-bounded updates as specified in FR-06.

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

- Which document or documents should state that the repository is empty: `Not Found`.
- What should happen if the documentation markers are absent, duplicated, or malformed: `Not Found`.
- What are the backup naming, location, and retention policies: `Not Found`.
- Should a diff still be displayed when `--yes` is supplied: `Not Found`.