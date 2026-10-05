# Changelog

All notable changes to this project are documented in this file.

## [Unreleased]

### Added

- Eight-phase, human-approved Copilot SDLC workflow with an orchestrator, tamper checks, audit logging, and a PreToolUse guard.
- Local Todo CLI using `tasks.json`, monotonic task IDs, and atomic storage updates.
- Requirement-tagged `unittest` coverage, infrastructure checks, clean-state audit, contract, and runbook.

### Changed

- Reorganized the repository from the documentation-sync project into the requested capstone structure.
- Standardized project verification on Python 3.11+ and the Python standard library.

### Fixed

- Reject inconsistent persisted `next_id` values so task IDs cannot be reused or collide.
- Preserve storage bytes for no-op and failure paths and escape terminal control and Unicode line separators in displayed titles.