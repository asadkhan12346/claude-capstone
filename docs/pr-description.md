# Pull Request Description

## Summary

`doc-sync` is an on-demand tool that scans local Python code and configuration to generate or update a project README and API reference. It helps keep documentation from going stale by grounding generated content in verifiable source facts and writing the exact text `Not Found` for fields that cannot be verified.

## Changes Made

The following files are added compared with the repository's first commit (`abac602`):

### Agent definitions

- `.github/agents/architect.agent.md` — Defines the architecture authoring role and its output constraints.
- `.github/agents/code-reviewer.agent.md` — Defines the review role, review criteria, and findings artifact.
- `.github/agents/design-reviewer.agent.md` — Defines the design-risk review role and findings artifact.
- `.github/agents/implementer.agent.md` — Defines task-scoped implementation, testing, and approval rules.
- `.github/agents/planner.agent.md` — Defines how approved design work becomes a dependency-ordered plan.
- `.github/agents/pr-author.agent.md` — Defines PR-description and changelog responsibilities and constraints.
- `.github/agents/requirements-analyst.agent.md` — Defines requirements elicitation and acceptance-criteria responsibilities.
- `.github/agents/sdlc-orchestrator.agent.md` — Coordinates the staged workflow and its approval gates.

### Hooks

- `.github/hooks/post-edit-checks.json` — Registers the post-edit validation command.
- `.github/hooks/post_edit_checks.py` — Runs pytest and scans changed files for likely hardcoded secrets, blocking unsafe results.

### Prompts

- `.github/prompts/architecture.prompt.md` — Guides creation of the architecture document.
- `.github/prompts/code-review.prompt.md` — Guides requirements-based code review.
- `.github/prompts/design-review.prompt.md` — Guides design-risk review.
- `.github/prompts/impl-plan.prompt.md` — Guides dependency-ordered implementation planning.
- `.github/prompts/pr.prompt.md` — Guides preparation of PR materials.
- `.github/prompts/requirements.prompt.md` — Guides requirements and acceptance-criteria elicitation.
- `.github/prompts/sdlc-run.prompt.md` — Guides staged SDLC orchestration and approval checks.
- `.github/prompts/verify.prompt.md` — Guides execution and documentation of verification.

### Skill

- `.github/skills/doc-sync/SKILL.md` — Defines the evidence-grounded workflow for syncing repository documentation.

### Project and SDLC documentation

- `CHANGELOG.md` — Records the project changes and verification result.
- `docs/architecture.md` — Documents the approved pipeline architecture and component boundaries.
- `docs/code-review.md` — Records review criteria, findings, fixes, and review status.
- `docs/design-review.md` — Records design risks and accepted mitigations.
- `docs/impl-plan.md` — Tracks dependency-ordered implementation tasks and completion status.
- `docs/pr-description.md` — Provides this PR summary, inventory, evidence, and reviewer checklist.
- `docs/requirements.md` — Defines product scope, functional requirements, and acceptance criteria.
- `docs/sdlc-state.md` — Tracks SDLC stages and approval dates.
- `docs/test-report.md` — Records test, coverage, fixture, and content-quality verification.
- `pyproject.toml` — Defines package metadata, supported Python version, dependencies, and CLI entry point.


### Source modules

- `src/doc_sync/__init__.py` — Marks the `doc_sync` package and exposes its package metadata.
- `src/doc_sync/__main__.py` — Enables module-based CLI invocation.
- `src/doc_sync/approval.py` — Builds proposed diffs and approval fingerprints.
- `src/doc_sync/cli.py` — Parses CLI options, validates targets, and invokes documentation generation.
- `src/doc_sync/extractors/__init__.py` — Defines the extractor package.
- `src/doc_sync/extractors/project_config.py` — Extracts project, dependency, entry-point, configuration, and README facts.
- `src/doc_sync/extractors/python_api.py` — Extracts public Python API facts statically from syntax trees.
- `src/doc_sync/facts.py` — Stores evidence-backed facts and resolves missing or conflicting values.
- `src/doc_sync/markers.py` — Adds or replaces generated content inside documentation markers.
- `src/doc_sync/pipeline.py` — Orchestrates scanning, extraction, rendering, approval, and safe writes.
- `src/doc_sync/rendering.py` — Renders README and API Markdown, including `Not Found` values.
- `src/doc_sync/reporting.py` — Formats sanitized run warnings and status messages.
- `src/doc_sync/scanner.py` — Scans supported files with exclusions, symlink checks, and resource limits.
- `src/doc_sync/security.py` — Detects secret paths and values and sanitizes permitted input.
- `src/doc_sync/writer.py` — Creates backups and atomically writes approved, screened documentation.

### Fixture repositories

- `tests/fixtures/broken/pyproject.toml` — Supplies malformed project metadata for parser-failure coverage.
- `tests/fixtures/e2e-run/README.md` — Provides the original README in a manual CLI end-to-end fixture copy.
- `tests/fixtures/e2e-run/fixture_normal/__init__.py` — Supplies a Python package in the manual CLI fixture copy.
- `tests/fixtures/e2e-run/pyproject.toml` — Supplies project metadata and an entry point in the manual CLI fixture copy.
- `tests/fixtures/empty/README.md` — Represents an empty/no-supported-files repository case.
- `tests/fixtures/missing/pyproject.toml` — Supplies incomplete metadata for missing-fact handling.
- `tests/fixtures/normal/README.md` — Provides source README facts for the normal fixture.
- `tests/fixtures/normal/README.md.bak` — Preserves the pre-update README for safe-writer verification.
- `tests/fixtures/normal/docs/api.md` — Provides the generated API document in the normal fixture.
- `tests/fixtures/normal/docs/api.md.bak` — Preserves the prior API document for safe-writer verification.
- `tests/fixtures/normal/fixture_normal/__init__.py` — Supplies a public Python module for API extraction.
- `tests/fixtures/normal/pyproject.toml` — Supplies representative project metadata and an entry point.
- `tests/fixtures/verification-cli-run/README.md` — Captures README output from a manual end-to-end CLI run.
- `tests/fixtures/verification-cli-run/README.md.bak` — Captures the README backup produced during that CLI run.
- `tests/fixtures/verification-cli-run/docs/api.md` — Captures API output from the manual end-to-end CLI run.
- `tests/fixtures/verification-cli-run/docs/api.md.bak` — Captures the API backup produced during that CLI run.
- `tests/fixtures/verification-cli-run/fixture_normal/__init__.py` — Supplies the Python module scanned during that CLI run.
- `tests/fixtures/verification-cli-run/pyproject.toml` — Supplies project metadata scanned during that CLI run.

### Tests

- `tests/test_cli.py` — Covers CLI parsing, help, and target validation.
- `tests/test_facts.py` — Covers fact provenance, resolution, missing values, and conflicts.
- `tests/test_integration.py` — Exercises the pipeline against integrated repository scenarios.
- `tests/test_markers.py` — Covers safe insertion and replacement of marked sections.
- `tests/test_pipeline.py` — Covers end-to-end pipeline behavior and failure handling.
- `tests/test_project_config.py` — Covers extraction from project and configuration files.
- `tests/test_project_metadata.py` — Verifies package metadata and dependency/runtime declarations.
- `tests/test_python_api.py` — Covers static extraction of public Python API facts.
- `tests/test_rendering.py` — Verifies Markdown output and missing-fact rendering.
- `tests/test_scanner.py` — Covers supported-file discovery, exclusions, and scan limits.
- `tests/test_security.py` — Covers secret path/value detection and sanitization.
- `tests/test_verification_suite.py` — Covers fixture scenarios, generated content, and secret-leak prevention.
- `tests/test_writer.py` — Covers backup, safe-write, and refusal behavior.

## Test Evidence

Command:

```text
.\.venv\Scripts\python.exe -m pytest -q
```

Actual output:

```text
.........................................                                [100%]
41 passed in 0.64s
```

## Known Limitations

- Python 3.11 was not tested locally; the available local runtime is Python 3.13.
- The automated vulnerable-dependency scan was not run because `pip-audit` is not installed. The code-review report rates dependency safety as PASS, but that is not a substitute for an advisory scan.
- Generated fields without verifiable evidence intentionally contain the exact text `Not Found`.
- The requirements mark support for languages other than Python as out of scope.
- Hosted-repository integration, GitHub API access, and authentication are out of scope; the tool operates on local repositories or folders.
- Commit history, CI files, and tests are out of scope as documentation sources.
- Scheduled or background execution is out of scope; runs are manual and on demand.
- Sending repository content to external services is out of scope.
- `docs/requirements.md` records the exact CLI command name and invocation syntax, beyond the `--yes` option, as `Not Found`.

## Reviewer Checklist

- [x] Requirements met, based on the implementation plan and code-review record.
- [x] Tests pass; full pytest suite reports 41 passed.
- [x] No secrets exposed; secret-handling tests pass and generated artifacts contain no reported secret values.
- [x] Documentation updated, including the verification report and changelog.
- [x] No vulnerable dependencies; pip-audit reported no known vulnerabilities (the project package itself is unpublished, so it was skipped).
- [x] Code reviewed; see docs/code-review.md