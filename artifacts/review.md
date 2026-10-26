# Code Review

## Summary

Review of the Notes CLI implementation delivered in phase 5 (implementation). The codebase
consists of three new files (`notes/__init__.py`, `notes/app.py`, `notes/cli.py`) plus
`tests/test_notes.py` and `README.md`. All 97 tests pass, compilation is clean, all seven
functional requirements and six non-functional requirements are satisfied, all seven
implementation-plan tasks are complete, and all six design-review findings are resolved.
Three Nit-level and one Minor finding were raised; none are blocking.

### Test run output (real, unedited)

```
python -m unittest discover -s tests -v

test_agent_and_prompt_frontmatter_and_phase_names_match (test_config.ConfigurationTests...) ... ok
test_agent_ownership_and_approval_gate_match_manifest (test_config.ConfigurationTests...) ... ok
test_commands_directory_has_exactly_two_files (test_config.ConfigurationTests...) ... ok
test_contract_phase_rows_match_manifest (test_config.ConfigurationTests...) ... ok
test_eight_phase_agent_prompt_and_contract_files_exist (test_config.ConfigurationTests...) ... ok
test_orchestrator_agent_has_agent_tool (test_config.ConfigurationTests...) ... ok
test_phases_use_consolidated_commands (test_config.ConfigurationTests...) ... ok
test_skills_and_hook_registration (test_config.ConfigurationTests...) ... ok
test_tools_are_scoped_to_roles (test_config.ConfigurationTests...) ... ok
test_contract_phase_table_matches_manifest (test_docs.DocumentationTests...) ... ok
test_documented_files_and_markdown_links_resolve (test_docs.DocumentationTests...) ... ok
test_readme_has_both_mermaid_diagrams_and_valid_commands (test_docs.DocumentationTests...) ... ok
test_readme_tree_paths_exist (test_docs.DocumentationTests...) ... ok
test_runbook_has_fourteen_steps (test_docs.DocumentationTests...) ... ok
test_approved_artifact_tamper_is_detected (test_e2e_pipeline.PipelineEndToEndTests...) ... ok
test_complete_eight_phase_pipeline (test_e2e_pipeline.PipelineEndToEndTests...) ... ok
test_edit_between_submit_and_approval_is_refused (test_e2e_pipeline.PipelineEndToEndTests...) ... ok
test_future_phase_artifact_fails_check (test_e2e_pipeline.PipelineEndToEndTests...) ... ok
test_guard_tracks_active_phase_changes (test_e2e_pipeline.PipelineEndToEndTests...) ... ok
test_reject_returns_phase_to_active_for_resubmission (test_e2e_pipeline.PipelineEndToEndTests...) ... ok
test_reopen_requires_later_outputs_to_be_removed (test_e2e_pipeline.PipelineEndToEndTests...) ... ok
test_skip_ahead_is_blocked (test_e2e_pipeline.PipelineEndToEndTests...) ... ok
test_blocks_credentials_file (test_github_pr.CheckFilesTests...) ... ok
test_blocks_dotenv_variant (test_github_pr.CheckFilesTests...) ... ok
test_blocks_env_file (test_github_pr.CheckFilesTests...) ... ok
test_blocks_file_outside_allowed_list (test_github_pr.CheckFilesTests...) ... ok
test_blocks_mixed_list_with_one_unauthorized (test_github_pr.CheckFilesTests...) ... ok
test_blocks_pem_file (test_github_pr.CheckFilesTests...) ... ok
test_blocks_sdlc_phases_json_unauthorized (test_github_pr.CheckFilesTests...) ... ok
test_blocks_token_file (test_github_pr.CheckFilesTests...) ... ok
test_passes_all_sdlc_allowed_files (test_github_pr.CheckFilesTests...) ... ok
test_passes_approved_artifacts (test_github_pr.CheckFilesTests...) ... ok
test_check_files_main_exits_0_for_approved_file (test_github_pr.MainCliTests...) ... ok
test_check_files_main_exits_1_for_env_file (test_github_pr.MainCliTests...) ... ok
test_preflight_main_exits_1_for_main_branch (test_github_pr.MainCliTests...) ... ok
test_verify_pr_main_exits_1_on_gh_failure (test_github_pr.MainCliTests...) ... ok
test_blocks_duplicate_open_pr (test_github_pr.PreflightTests...) ... ok
test_blocks_main_branch (test_github_pr.PreflightTests...) ... ok
test_blocks_master_branch (test_github_pr.PreflightTests...) ... ok
test_blocks_on_gh_auth_failure (test_github_pr.PreflightTests...) ... ok
test_blocks_on_malformed_gh_output (test_github_pr.PreflightTests...) ... ok
test_passes_clean_feature_branch (test_github_pr.PreflightTests...) ... ok
test_passes_empty_pr_list_response (test_github_pr.PreflightTests...) ... ok
test_confirms_open_pr (test_github_pr.VerifyPrTests...) ... ok
test_rejects_closed_pr (test_github_pr.VerifyPrTests...) ... ok
test_rejects_gh_command_failure (test_github_pr.VerifyPrTests...) ... ok
test_rejects_malformed_output (test_github_pr.VerifyPrTests...) ... ok
test_rejects_merged_pr (test_github_pr.VerifyPrTests...) ... ok
test_invalid_state_fails_closed_for_owned_writes (test_guard.GuardTests...) ... ok
test_malformed_shell_and_write_payloads_fail_closed (test_guard.GuardTests...) ... ok
test_nested_shells_are_expanded (test_guard.GuardTests...) ... ok
test_parse_alternate_payload_and_patch_paths (test_guard.GuardTests...) ... ok
test_parse_tool_name_payload_and_command (test_guard.GuardTests...) ... ok
test_r01_blocks_recursive_root_but_allows_node_modules (test_guard.GuardTests...) ... ok
test_r02_blocks_disk_formatting_and_world_writable_mode (test_guard.GuardTests...) ... ok
test_r03_blocks_history_rewrites_and_allows_safe_git_reads (test_guard.GuardTests...) ... ok
test_r04_blocks_force_and_protected_push_but_allows_lease_feature_push (test_guard.GuardTests...) ... ok
test_r05_detects_piped_installers_even_when_commands_expand (test_guard.GuardTests...) ... ok
test_r06_blocks_agent_human_approval_commands (test_guard.GuardTests...) ... ok
test_r07_and_r08_follow_phase_state (test_guard.GuardTests...) ... ok
test_fr002_empty_list_indication (test_notes.TestCLIIntegration...) ... ok
test_fr005_delete_confirmation (test_notes.TestCLIIntegration...) ... ok
test_fr001_create_returns_note (test_notes.TestCreateNote...) ... ok
test_fr001_data_persists_across_load (test_notes.TestCreateNote...) ... ok
test_fr001_id_auto_increments (test_notes.TestCreateNote...) ... ok
test_fr007_empty_content_raises (test_notes.TestCreateNote...) ... ok
test_fr007_empty_title_raises (test_notes.TestCreateNote...) ... ok
test_fr007_whitespace_only_content_raises (test_notes.TestCreateNote...) ... ok
test_fr007_whitespace_only_title_raises (test_notes.TestCreateNote...) ... ok
test_fr005_removes_note_from_storage (test_notes.TestDeleteNote...) ... ok
test_fr006_raises_not_found_for_absent_id (test_notes.TestDeleteNote...) ... ok
test_nfr003_id_not_reused_after_delete (test_notes.TestDeleteNote...) ... ok
test_fr003_returns_correct_note (test_notes.TestGetNote...) ... ok
test_fr006_raises_not_found_for_absent_id (test_notes.TestGetNote...) ... ok
test_fr002_returns_all_created_notes (test_notes.TestListNotes...) ... ok
test_fr002_returns_empty_list_when_no_notes (test_notes.TestListNotes...) ... ok
test_f01_atomic_write_no_tmp_file_remains (test_notes.TestStorage...) ... ok
test_f02_corrupt_json_raises_storage_error (test_notes.TestStorage...) ... ok
test_nfr001_absent_file_returns_default (test_notes.TestStorage...) ... ok
test_nfr001_data_survives_process_reload (test_notes.TestStorage...) ... ok
test_fr004_full_replace_both_fields (test_notes.TestUpdateNote...) ... ok
test_fr004_replaces_title_and_content (test_notes.TestUpdateNote...) ... ok
test_fr006_raises_not_found_for_absent_id (test_notes.TestUpdateNote...) ... ok
test_fr007_empty_content_raises (test_notes.TestUpdateNote...) ... ok
test_fr007_empty_title_raises (test_notes.TestUpdateNote...) ... ok
test_fr007_whitespace_only_title_raises (test_notes.TestUpdateNote...) ... ok
test_check_detects_locked_outputs_and_missing_protected_path (test_orchestrator...) ... ok
test_hash_drift_refuses_approval (test_orchestrator...) ... ok
test_human_approval_requires_tty_confirmation (test_orchestrator...) ... ok
test_initial_state_and_derived_status (test_orchestrator...) ... ok
test_invalid_cli_syntax_returns_usage_exit_code (test_orchestrator...) ... ok
test_locked_phase_cannot_be_submitted_and_is_audited (test_orchestrator...) ... ok
test_missing_manifest_returns_rule_violation_exit_code (test_orchestrator...) ... ok
test_reject_clears_hashes_and_returns_phase_to_active (test_orchestrator...) ... ok
test_reopen_refuses_until_later_outputs_are_removed (test_orchestrator...) ... ok
test_second_submit_raises_rule_violation (test_orchestrator...) ... ok
test_submit_then_approve_activates_next_phase (test_orchestrator...) ... ok

----------------------------------------------------------------------
Ran 97 tests in 1.391s

OK
```

### Compile check output (real, unedited)

```
python -m compileall -q .
(no output — zero errors)
```

---

## Findings

### R-01 — Minor — No schema validation in `_load` for structurally-invalid JSON

**File:** `notes/app.py:50-52`

`_load` correctly catches `json.JSONDecodeError` (design-review F-02) and re-raises as
`StorageError`. However, it does not validate the shape of successfully-parsed data. If a user
manually edits `notes.json` to contain syntactically valid but structurally wrong JSON (e.g.,
`{}`, `[]`, or `"string"`), `_load` returns that value unchanged. The first downstream call
that accesses `data["next_id"]` or `data["notes"]` then raises an unhandled `KeyError` or
`TypeError`. These exception types are not subclasses of `NoteError`, so the CLI's
`except NoteError` block at `notes/cli.py:107` does not intercept them; the user receives a raw
Python traceback rather than an actionable message, which is inconsistent with NFR-005. The
scenario requires deliberate manual file corruption and is not covered by any test.

### R-02 — Nit — Stored title/content not normalized (stripped) before persistence

**File:** `notes/app.py:102-115` (create_note) and `notes/app.py:175-186` (update_note)

Validation uses `title.strip()` and `content.strip()` to reject whitespace-only input, but the
original (un-stripped) value is stored in the JSON and echoed in CLI output. A title of
`"  hello  "` passes validation and is saved with the surrounding spaces, producing
`"[1]   hello  : world"` in list output. FR-001 and FR-007 do not require normalization, so
this is not a requirement violation; it is noted because the behaviour may surprise users.

### R-03 — Nit — `TestUpdateNote` missing a `test_fr007_whitespace_only_content_raises` variant

**File:** `tests/test_notes.py:162-207`

`TestCreateNote` has `test_fr007_whitespace_only_content_raises` (line 111) that verifies
`create_note("title", "   ", ...)` raises `ValidationError`. The symmetric test for
`update_note("title", "   ", ...)` is absent from `TestUpdateNote`. The code path is exercised
indirectly — `update_note` shares the same `if not content.strip()` guard (line 177) as
`create_note` — and the implementation plan's test table does not mandate this test, so this
is a coverage gap rather than a plan deviation.

### R-04 — Nit — README "Who does what" table references deleted `todo/` application files

**File:** `README.md:133`

The table row for the implementation phase still reads `todo/ and tests/test_todo.py`.
Those paths were deleted in the current pipeline run; the live application files are
`notes/` and `tests/test_notes.py`. The affected section is the generic SDLC framework
description, not the Notes CLI documentation section that satisfies NFR-006, so Notes CLI
users are unaffected. The inconsistency is misleading for readers following the SDLC
framework description.

---

## Traceability matrix

| Req | Implementation (file:function:lines) | Test method(s) |
|-----|--------------------------------------|----------------|
| FR-001 | notes/app.py:create_note:84-116 | TestCreateNote.test_fr001_create_returns_note; test_fr001_id_auto_increments; test_fr001_data_persists_across_load |
| FR-002 | notes/app.py:list_notes:119-129; notes/cli.py:main:88-93 | TestListNotes.test_fr002_returns_empty_list_when_no_notes; test_fr002_returns_all_created_notes; TestCLIIntegration.test_fr002_empty_list_indication |
| FR-003 | notes/app.py:get_note:132-151; notes/cli.py:main:95-97 | TestGetNote.test_fr003_returns_correct_note |
| FR-004 | notes/app.py:update_note:154-187; notes/cli.py:main:99-101 | TestUpdateNote.test_fr004_replaces_title_and_content; test_fr004_full_replace_both_fields |
| FR-005 | notes/app.py:delete_note:190-209; notes/cli.py:main:103-105 | TestDeleteNote.test_fr005_removes_note_from_storage; TestCLIIntegration.test_fr005_delete_confirmation |
| FR-006 | notes/app.py:get_note:151; update_note:187; delete_note:208 | TestGetNote.test_fr006_raises_not_found_for_absent_id; TestUpdateNote.test_fr006_raises_not_found_for_absent_id; TestDeleteNote.test_fr006_raises_not_found_for_absent_id |
| FR-007 | notes/app.py:create_note:102-105; update_note:175-178 | TestCreateNote.test_fr007_empty_title_raises; test_fr007_whitespace_only_title_raises; test_fr007_empty_content_raises; test_fr007_whitespace_only_content_raises; TestUpdateNote.test_fr007_empty_title_raises; test_fr007_whitespace_only_title_raises; test_fr007_empty_content_raises |
| NFR-001 | notes/app.py:_load:38-58; _save:61-76 | TestStorage.test_nfr001_absent_file_returns_default; test_nfr001_data_survives_process_reload; test_f01_atomic_write_no_tmp_file_remains; test_f02_corrupt_json_raises_storage_error |
| NFR-002 | notes/cli.py:_build_parser:28-65 | TestCLIIntegration.test_fr002_empty_list_indication; test_fr005_delete_confirmation |
| NFR-003 | notes/app.py:create_note:113 (next_id increment); delete_note:203-208 (no decrement) | TestCreateNote.test_fr001_id_auto_increments; TestDeleteNote.test_nfr003_id_not_reused_after_delete |
| NFR-004 | tests/test_notes.py (all 26 test methods) | All 26 test methods in TestCreateNote, TestListNotes, TestGetNote, TestUpdateNote, TestDeleteNote, TestStorage, TestCLIIntegration |
| NFR-005 | notes/app.py:NoteNotFoundError:21-22; ValidationError:25-26; StorageError:29-30; notes/cli.py:main:107-109 | TestStorage.test_f02_corrupt_json_raises_storage_error; all test_fr006_* and test_fr007_* methods |
| NFR-006 | README.md lines 1-67 (setup + five subcommand examples + error handling + test instructions) | N/A (documentation artifact) |

---

## Plan adherence

| Task | Status | Notes |
|------|--------|-------|
| T-01 — Exception hierarchy in app.py + re-exported from __init__.py | Done | `NoteError`, `NoteNotFoundError`, `ValidationError`, `StorageError` defined at notes/app.py:17-31; re-exported at notes/__init__.py:10 |
| T-02 — `_load` and `_save` with atomic write and StorageError | Done | `_load` at notes/app.py:38-58; `_save` uses `.tmp` + `flush` + `fsync` + `os.replace` at notes/app.py:61-76 |
| T-03 — Five public CRUD functions with `.strip()` validation | Done | All five functions present with type annotations; `.strip()` guards at notes/app.py:102-105 and 175-178 |
| T-04 — CLI layer with argparse, 5 subparsers, empty-list and delete confirmation | Done | `_build_parser` at notes/cli.py:28-65; empty-list at line 90; delete confirmation at line 105 |
| T-05 — Unit tests for FR-001–FR-007 | Done | 24 unit tests across 6 test classes; all FRs exercised with per-test tempfile isolation |
| T-06 — CLI integration tests for FR-002 and FR-005 (subprocess) | Done | `TestCLIIntegration` at tests/test_notes.py:284-324; uses `NOTES_PATH` env var for isolation |
| T-07 — README.md with all 5 subcommand examples | Done | README.md lines 1-67 contain setup, five subcommand examples with `python -m notes.cli`, error handling, and test instructions |

Design-review findings resolved: F-01 (atomic write) — Done; F-02 (StorageError on JSONDecodeError) — Done; F-03 (CLI integration tests) — Done; F-04 (README ownership) — Done; F-05 (.strip() validation) — Done; F-06 (argparse type error acceptable) — Documented; F-07 (sole invocation documented) — Done.

---

Verdict: APPROVE
