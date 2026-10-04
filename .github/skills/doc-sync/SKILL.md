---
name: doc-sync
description: "Scan a repository, extract verifiable facts from source and project files, and create or update documentation. Use when documenting a repository, syncing docs to code, or checking documentation for missing facts."
user-invocable: true
---
# Documentation Sync

## Procedure
1. Inspect the repository with `git ls-files --cached --others --exclude-standard` when it is a Git checkout. Otherwise, use a recursive file listing that excludes `.git`, virtual environments, caches, and generated artifacts. Also inspect the existing docs, README, configuration, tests, and relevant source files.
2. If the repository or expected paths are empty or missing, continue gracefully and record what could not be inspected. Do not infer implementation details from directory names alone.
3. For each requested documentation field, find direct evidence in authoritative source, configuration, tests, or existing docs. Prefer current behavior in code over stale descriptions.
4. Keep a brief evidence map with the field, supporting file and line, and any conflict or uncertainty. Separate verified facts from assumptions; resolve conflicts when evidence permits and otherwise disclose them.
5. Write only the requested documentation. Use the exact text `Not Found` for every field that cannot be determined; do not guess or leave an unknown field blank.
6. Recheck the finished document against the evidence map and ensure links and file references exist.

## Safety
- Never copy, print, or log secrets, tokens, or API keys. Redact them and describe only where they were found.
- Do not modify application code or unrelated files while syncing documentation.
- Handle missing files, empty repositories, and unavailable sources explicitly and without failing the entire documentation task.