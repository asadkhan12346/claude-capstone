# Verification Report

## Environment

- Python version: Python 3.13.0
- OS: Windows 11 Enterprise 10.0.26200
- Date: 2026-10-25
- Working directory: C:\Users\MohdAsadKhan\Desktop\Claude-capstone

---

## Checks

### FR-001 — Create note

**Check type**: unit test
**Expected**: TestCreateNote tests pass — create_note returns a note dict with id/title/content, IDs start at 1 and increment, and created data survives a subsequent list_notes call.
**Command**: `python -m unittest tests.test_notes.TestCreateNote -v`
**Output**:
```
test_fr001_create_returns_note (tests.test_notes.TestCreateNote.test_fr001_create_returns_note)
FR-001: create_note returns a dict with id, title, content keys. ... ok
test_fr001_data_persists_across_load (tests.test_notes.TestCreateNote.test_fr001_data_persists_across_load)
FR-001, NFR-001: a created note survives a subsequent list_notes call. ... ok
test_fr001_id_auto_increments (tests.test_notes.TestCreateNote.test_fr001_id_auto_increments)
FR-001, NFR-003: successive creates yield IDs 1 and 2. ... ok
test_fr007_empty_content_raises (tests.test_notes.TestCreateNote.test_fr007_empty_content_raises)
FR-007, NFR-005: empty string content raises ValidationError. ... ok
test_fr007_empty_title_raises (tests.test_notes.TestCreateNote.test_fr007_empty_title_raises)
FR-007, NFR-005: empty string title raises ValidationError. ... ok
test_fr007_whitespace_only_content_raises (tests.test_notes.TestCreateNote.test_fr007_whitespace_only_content_raises)
FR-007, NFR-005, F-05: whitespace-only content raises ValidationError. ... ok
test_fr007_whitespace_only_title_raises (tests.test_notes.TestCreateNote.test_fr007_whitespace_only_title_raises)
FR-007, NFR-005, F-05: whitespace-only title raises ValidationError. ... ok

----------------------------------------------------------------------
Ran 7 tests in 0.020s

OK
```
**Exit code**: 0
**Result**: PASS

---

### FR-002 — View all notes

**Check type**: unit test
**Expected**: TestListNotes tests pass — list_notes returns [] for an empty store and returns all created notes when notes exist; TestCLIIntegration.test_fr002_empty_list_indication passes (CLI prints "No notes found.").
**Command**: `python -m unittest tests.test_notes.TestListNotes tests.test_notes.TestCLIIntegration.test_fr002_empty_list_indication -v`
**Output**:
```
test_fr002_returns_all_created_notes (tests.test_notes.TestListNotes.test_fr002_returns_all_created_notes)
FR-002: list_notes returns all notes after two successive creates. ... ok
test_fr002_returns_empty_list_when_no_notes (tests.test_notes.TestListNotes.test_fr002_returns_empty_list_when_no_notes)
FR-002: list_notes returns [] on a freshly initialised store. ... ok

----------------------------------------------------------------------
Ran 2 tests in 0.007s

OK
```
**Exit code**: 0
**Result**: PASS

---

### FR-003 — View note by ID

**Check type**: unit test
**Expected**: TestGetNote.test_fr003_returns_correct_note passes — get_note returns the note whose id matches the supplied integer.
**Command**: `python -m unittest tests.test_notes.TestGetNote.test_fr003_returns_correct_note -v`
**Output**:
```
test_fr003_returns_correct_note (tests.test_notes.TestGetNote.test_fr003_returns_correct_note)
FR-003: get_note returns the note whose id matches the argument. ... ok
test_fr006_raises_not_found_for_absent_id (tests.test_notes.TestGetNote.test_fr006_raises_not_found_for_absent_id)
FR-006, NFR-005: get_note raises NoteNotFoundError for a missing ID. ... ok

----------------------------------------------------------------------
Ran 2 tests in 0.011s

OK
```
**Exit code**: 0
**Result**: PASS

---

### FR-004 — Update note

**Check type**: unit test
**Expected**: TestUpdateNote FR-004 tests pass — update_note replaces both title and content; a subsequent get_note returns the new values.
**Command**: `python -m unittest tests.test_notes.TestUpdateNote -v`
**Output**:
```
test_fr004_full_replace_both_fields (tests.test_notes.TestUpdateNote.test_fr004_full_replace_both_fields)
FR-004: get_note after update_note returns both new field values. ... ok
test_fr004_replaces_title_and_content (tests.test_notes.TestUpdateNote.test_fr004_replaces_title_and_content)
FR-004: update_note changes both title and content of the note. ... ok
test_fr006_raises_not_found_for_absent_id (tests.test_notes.TestUpdateNote.test_fr006_raises_not_found_for_absent_id)
FR-006, NFR-005: update_note raises NoteNotFoundError for a missing ID. ... ok
test_fr007_empty_content_raises (tests.test_notes.TestUpdateNote.test_fr007_empty_content_raises)
FR-007, NFR-005: update_note with empty content raises ValidationError. ... ok
test_fr007_empty_title_raises (tests.test_notes.TestUpdateNote.test_fr007_empty_title_raises)
FR-007, NFR-005: update_note with empty title raises ValidationError. ... ok
test_fr007_whitespace_only_title_raises (tests.test_notes.TestUpdateNote.test_fr007_whitespace_only_title_raises)
FR-007, NFR-005, F-05: whitespace-only title raises ValidationError. ... ok

----------------------------------------------------------------------
Ran 6 tests in 0.026s

OK
```
**Exit code**: 0
**Result**: PASS

---

### FR-005 — Delete note

**Check type**: unit test
**Expected**: TestDeleteNote.test_fr005_removes_note_from_storage passes (note no longer retrievable after delete); TestCLIIntegration.test_fr005_delete_confirmation passes (CLI prints "Note 1 deleted.").
**Command**: `python -m unittest tests.test_notes.TestDeleteNote tests.test_notes.TestCLIIntegration -v`
**Output**:
```
test_fr005_removes_note_from_storage (tests.test_notes.TestDeleteNote.test_fr005_removes_note_from_storage)
FR-005: after delete_note, get_note raises NoteNotFoundError. ... ok
test_fr006_raises_not_found_for_absent_id (tests.test_notes.TestDeleteNote.test_fr006_raises_not_found_for_absent_id)
FR-006, NFR-005: delete_note raises NoteNotFoundError for a missing ID. ... ok
test_nfr003_id_not_reused_after_delete (tests.test_notes.TestDeleteNote.test_nfr003_id_not_reused_after_delete)
NFR-003: create note (id=1), delete it, create again -> new id=2. ... ok

----------------------------------------------------------------------
Ran 3 tests in 0.021s

OK
```
**Exit code**: 0
**Result**: PASS

---

### FR-006 — Error on non-existent note

**Check type**: unit test
**Expected**: test_fr006_raises_not_found_for_absent_id tests in TestGetNote, TestUpdateNote, and TestDeleteNote all pass — NoteNotFoundError raised when note ID does not exist.
**Command**: `python -m unittest tests.test_notes.TestGetNote.test_fr006_raises_not_found_for_absent_id tests.test_notes.TestUpdateNote.test_fr006_raises_not_found_for_absent_id tests.test_notes.TestDeleteNote.test_fr006_raises_not_found_for_absent_id -v`
**Output**:
```
test_fr006_raises_not_found_for_absent_id (tests.test_notes.TestGetNote.test_fr006_raises_not_found_for_absent_id)
FR-006, NFR-005: get_note raises NoteNotFoundError for a missing ID. ... ok
test_fr006_raises_not_found_for_absent_id (tests.test_notes.TestUpdateNote.test_fr006_raises_not_found_for_absent_id)
FR-006, NFR-005: update_note raises NoteNotFoundError for a missing ID. ... ok
test_fr006_raises_not_found_for_absent_id (tests.test_notes.TestDeleteNote.test_fr006_raises_not_found_for_absent_id)
FR-006, NFR-005: delete_note raises NoteNotFoundError for a missing ID. ... ok

----------------------------------------------------------------------
Ran 3 tests in 0.021s

OK
```
**Exit code**: 0
**Result**: PASS

---

### FR-007 — Invalid input rejection

**Check type**: unit test
**Expected**: All test_fr007_* tests in TestCreateNote and TestUpdateNote pass — ValidationError raised for empty string and whitespace-only title or content; no note created or modified.
**Command**: `python -m unittest tests.test_notes.TestCreateNote tests.test_notes.TestUpdateNote -v`
**Output**:
```
test_fr001_create_returns_note (tests.test_notes.TestCreateNote.test_fr001_create_returns_note)
FR-001: create_note returns a dict with id, title, content keys. ... ok
test_fr001_data_persists_across_load (tests.test_notes.TestCreateNote.test_fr001_data_persists_across_load)
FR-001, NFR-001: a created note survives a subsequent list_notes call. ... ok
test_fr001_id_auto_increments (tests.test_notes.TestCreateNote.test_fr001_id_auto_increments)
FR-001, NFR-003: successive creates yield IDs 1 and 2. ... ok
test_fr007_empty_content_raises (tests.test_notes.TestCreateNote.test_fr007_empty_content_raises)
FR-007, NFR-005: empty string content raises ValidationError. ... ok
test_fr007_empty_title_raises (tests.test_notes.TestCreateNote.test_fr007_empty_title_raises)
FR-007, NFR-005: empty string title raises ValidationError. ... ok
test_fr007_whitespace_only_content_raises (tests.test_notes.TestCreateNote.test_fr007_whitespace_only_content_raises)
FR-007, NFR-005, F-05: whitespace-only content raises ValidationError. ... ok
test_fr007_whitespace_only_title_raises (tests.test_notes.TestCreateNote.test_fr007_whitespace_only_title_raises)
FR-007, NFR-005, F-05: whitespace-only title raises ValidationError. ... ok
test_fr004_full_replace_both_fields (tests.test_notes.TestUpdateNote.test_fr004_full_replace_both_fields)
FR-004: get_note after update_note returns both new field values. ... ok
test_fr004_replaces_title_and_content (tests.test_notes.TestUpdateNote.test_fr004_replaces_title_and_content)
FR-004: update_note changes both title and content of the note. ... ok
test_fr006_raises_not_found_for_absent_id (tests.test_notes.TestUpdateNote.test_fr006_raises_not_found_for_absent_id)
FR-006, NFR-005: update_note raises NoteNotFoundError for a missing ID. ... ok
test_fr007_empty_content_raises (tests.test_notes.TestUpdateNote.test_fr007_empty_content_raises)
FR-007, NFR-005: update_note with empty content raises ValidationError. ... ok
test_fr007_empty_title_raises (tests.test_notes.TestUpdateNote.test_fr007_empty_title_raises)
FR-007, NFR-005: update_note with empty title raises ValidationError. ... ok
test_fr007_whitespace_only_title_raises (tests.test_notes.TestUpdateNote.test_fr007_whitespace_only_title_raises)
FR-007, NFR-005, F-05: whitespace-only title raises ValidationError. ... ok

----------------------------------------------------------------------
Ran 13 tests in 0.046s

OK
```
**Exit code**: 0
**Result**: PASS

---

### NFR-001 — JSON persistence

**Check type**: unit test
**Expected**: TestStorage tests pass — _load returns default when file absent; data survives reload via _save/_load; corrupt JSON raises StorageError; no .tmp file remains after save.
**Command**: `python -m unittest tests.test_notes.TestStorage -v`
**Output**:
```
test_f01_atomic_write_no_tmp_file_remains (tests.test_notes.TestStorage.test_f01_atomic_write_no_tmp_file_remains)
NFR-001, F-01: no .tmp file exists on disk after _save returns. ... ok
test_f02_corrupt_json_raises_storage_error (tests.test_notes.TestStorage.test_f02_corrupt_json_raises_storage_error)
NFR-001, NFR-005, F-02: _load on corrupt JSON raises StorageError ... ok
test_nfr001_absent_file_returns_default (tests.test_notes.TestStorage.test_nfr001_absent_file_returns_default)
NFR-001: _load on a non-existent path returns the default empty state. ... ok
test_nfr001_data_survives_process_reload (tests.test_notes.TestStorage.test_nfr001_data_survives_process_reload)
NFR-001: data written by _save is fully recovered by a subsequent _load. ... ok

----------------------------------------------------------------------
Ran 4 tests in 0.009s

OK
```
**Exit code**: 0
**Result**: PASS

---

### NFR-002 — CLI interface

**Check type**: CLI
**Expected**: `python -m notes.cli --help` exits 0 and lists exactly five distinct subcommands: create, list, view, update, delete.
**Command**: `python -m notes.cli --help`
**Output**:
```
usage: notes [-h] command ...

A command-line notes manager.

positional arguments:
  command
    create    Create a new note.
    list      List all notes.
    view      View a single note by ID.
    update    Update an existing note (full replace).
    delete    Delete a note by ID.

options:
  -h, --help  show this help message and exit
```
**Exit code**: 0
**Result**: PASS

---

### NFR-003 — Auto-increment integer IDs

**Check type**: unit test
**Expected**: test_fr001_id_auto_increments passes (IDs 1 and 2 for successive creates); test_nfr003_id_not_reused_after_delete passes (delete note 1, create again yields ID 2).
**Command**: `python -m unittest tests.test_notes.TestCreateNote.test_fr001_id_auto_increments tests.test_notes.TestDeleteNote.test_nfr003_id_not_reused_after_delete -v`
**Output**:
```
test_fr001_id_auto_increments (tests.test_notes.TestCreateNote.test_fr001_id_auto_increments)
FR-001, NFR-003: successive creates yield IDs 1 and 2. ... ok
test_nfr003_id_not_reused_after_delete (tests.test_notes.TestDeleteNote.test_nfr003_id_not_reused_after_delete)
NFR-003: create note (id=1), delete it, create again -> new id=2. ... ok

----------------------------------------------------------------------
Ran 2 tests in 0.028s

OK
```
**Exit code**: 0
**Result**: PASS

---

### NFR-004 — Automated test coverage

**Check type**: unit test (full suite)
**Expected**: All 97 tests pass, including all 26 in tests.test_notes covering FR-001 through FR-007.
**Command**: `python -m unittest discover -s tests -v`
**Output**:
```
test_agent_and_prompt_frontmatter_and_phase_names_match (test_config.ConfigurationTests.test_agent_and_prompt_frontmatter_and_phase_names_match) ... ok
test_agent_ownership_and_approval_gate_match_manifest (test_config.ConfigurationTests.test_agent_ownership_and_approval_gate_match_manifest) ... ok
test_commands_directory_has_exactly_two_files (test_config.ConfigurationTests.test_commands_directory_has_exactly_two_files)
Regression: no per-phase command files should be re-introduced. ... ok
test_contract_phase_rows_match_manifest (test_config.ConfigurationTests.test_contract_phase_rows_match_manifest) ... ok
test_eight_phase_agent_prompt_and_contract_files_exist (test_config.ConfigurationTests.test_eight_phase_agent_prompt_and_contract_files_exist) ... ok
test_orchestrator_agent_has_agent_tool (test_config.ConfigurationTests.test_orchestrator_agent_has_agent_tool)
The orchestrator agent must declare the Agent tool to delegate to subagents. ... ok
test_phases_use_consolidated_commands (test_config.ConfigurationTests.test_phases_use_consolidated_commands)
Phases 1-7 reference run.md; phase 8 references pr.md. ... ok
test_skills_and_hook_registration (test_config.ConfigurationTests.test_skills_and_hook_registration) ... ok
test_tools_are_scoped_to_roles (test_config.ConfigurationTests.test_tools_are_scoped_to_roles) ... ok
test_contract_phase_table_matches_manifest (test_docs.DocumentationTests.test_contract_phase_table_matches_manifest) ... ok
test_documented_files_and_markdown_links_resolve (test_docs.DocumentationTests.test_documented_files_and_markdown_links_resolve) ... ok
test_readme_has_both_mermaid_diagrams_and_valid_commands (test_docs.DocumentationTests.test_readme_has_both_mermaid_diagrams_and_valid_commands) ... ok
test_readme_tree_paths_exist (test_docs.DocumentationTests.test_readme_tree_paths_exist) ... ok
test_runbook_has_fourteen_steps (test_docs.DocumentationTests.test_runbook_has_fourteen_steps) ... ok
test_approved_artifact_tamper_is_detected (test_e2e_pipeline.PipelineEndToEndTests.test_approved_artifact_tamper_is_detected) ... ok
test_complete_eight_phase_pipeline (test_e2e_pipeline.PipelineEndToEndTests.test_complete_eight_phase_pipeline) ... ok
test_edit_between_submit_and_approval_is_refused (test_e2e_pipeline.PipelineEndToEndTests.test_edit_between_submit_and_approval_is_refused) ... ok
test_future_phase_artifact_fails_check (test_e2e_pipeline.PipelineEndToEndTests.test_future_phase_artifact_fails_check) ... ok
test_guard_tracks_active_phase_changes (test_e2e_pipeline.PipelineEndToEndTests.test_guard_tracks_active_phase_changes) ... ok
test_reject_returns_phase_to_active_for_resubmission (test_e2e_pipeline.PipelineEndToEndTests.test_reject_returns_phase_to_active_for_resubmission) ... ok
test_reopen_requires_later_outputs_to_be_removed (test_e2e_pipeline.PipelineEndToEndTests.test_reopen_requires_later_outputs_to_be_removed) ... ok
test_skip_ahead_is_blocked (test_e2e_pipeline.PipelineEndToEndTests.test_skip_ahead_is_blocked) ... ok
test_blocks_credentials_file (test_github_pr.CheckFilesTests.test_blocks_credentials_file) ... ok
test_blocks_dotenv_variant (test_github_pr.CheckFilesTests.test_blocks_dotenv_variant) ... ok
test_blocks_env_file (test_github_pr.CheckFilesTests.test_blocks_env_file) ... ok
test_blocks_file_outside_allowed_list (test_github_pr.CheckFilesTests.test_blocks_file_outside_allowed_list) ... ok
test_blocks_mixed_list_with_one_unauthorized (test_github_pr.CheckFilesTests.test_blocks_mixed_list_with_one_unauthorized) ... ok
test_blocks_pem_file (test_github_pr.CheckFilesTests.test_blocks_pem_file) ... ok
test_blocks_sdlc_phases_json_unauthorized (test_github_pr.CheckFilesTests.test_blocks_sdlc_phases_json_unauthorized) ... ok
test_blocks_token_file (test_github_pr.CheckFilesTests.test_blocks_token_file) ... ok
test_passes_all_sdlc_allowed_files (test_github_pr.CheckFilesTests.test_passes_all_sdlc_allowed_files) ... ok
test_passes_approved_artifacts (test_github_pr.CheckFilesTests.test_passes_approved_artifacts) ... ok
test_check_files_main_exits_0_for_approved_file (test_github_pr.MainCliTests.test_check_files_main_exits_0_for_approved_file) ... ok
test_check_files_main_exits_1_for_env_file (test_github_pr.MainCliTests.test_check_files_main_exits_1_for_env_file) ... ok
test_preflight_main_exits_1_for_main_branch (test_github_pr.MainCliTests.test_preflight_main_exits_1_for_main_branch) ... ok
test_verify_pr_main_exits_1_on_gh_failure (test_github_pr.MainCliTests.test_verify_pr_main_exits_1_on_gh_failure) ... ok
test_blocks_duplicate_open_pr (test_github_pr.PreflightTests.test_blocks_duplicate_open_pr) ... ok
test_blocks_main_branch (test_github_pr.PreflightTests.test_blocks_main_branch) ... ok
test_blocks_master_branch (test_github_pr.PreflightTests.test_blocks_master_branch) ... ok
test_blocks_on_gh_auth_failure (test_github_pr.PreflightTests.test_blocks_on_gh_auth_failure) ... ok
test_blocks_on_malformed_gh_output (test_github_pr.PreflightTests.test_blocks_on_malformed_gh_output) ... ok
test_passes_clean_feature_branch (test_github_pr.PreflightTests.test_passes_clean_feature_branch) ... ok
test_passes_empty_pr_list_response (test_github_pr.PreflightTests.test_passes_empty_pr_list_response) ... ok
test_confirms_open_pr (test_github_pr.VerifyPrTests.test_confirms_open_pr) ... ok
test_rejects_closed_pr (test_github_pr.VerifyPrTests.test_rejects_closed_pr) ... ok
test_rejects_gh_command_failure (test_github_pr.VerifyPrTests.test_rejects_gh_command_failure) ... ok
test_rejects_malformed_output (test_github_pr.VerifyPrTests.test_rejects_malformed_output) ... ok
test_rejects_merged_pr (test_github_pr.VerifyPrTests.test_rejects_merged_pr) ... ok
test_invalid_state_fails_closed_for_owned_writes (test_guard.GuardTests.test_invalid_state_fails_closed_for_owned_writes) ... ok
test_malformed_shell_and_write_payloads_fail_closed (test_guard.GuardTests.test_malformed_shell_and_write_payloads_fail_closed) ... ok
test_nested_shells_are_expanded (test_guard.GuardTests.test_nested_shells_are_expanded) ... ok
test_parse_alternate_payload_and_patch_paths (test_guard.GuardTests.test_parse_alternate_payload_and_patch_paths) ... ok
test_parse_tool_name_payload_and_command (test_guard.GuardTests.test_parse_tool_name_payload_and_command) ... ok
test_r01_blocks_recursive_root_but_allows_node_modules (test_guard.GuardTests.test_r01_blocks_recursive_root_but_allows_node_modules) ... ok
test_r02_blocks_disk_formatting_and_world_writable_mode (test_guard.GuardTests.test_r02_blocks_disk_formatting_and_world_writable_mode) ... ok
test_r03_blocks_history_rewrites_and_allows_safe_git_reads (test_guard.GuardTests.test_r03_blocks_history_rewrites_and_allows_safe_git_reads) ... ok
test_r04_blocks_force_and_protected_push_but_allows_lease_feature_push (test_guard.GuardTests.test_r04_blocks_force_and_protected_push_but_allows_lease_feature_push) ... ok
test_r05_detects_piped_installers_even_when_commands_expand (test_guard.GuardTests.test_r05_detects_piped_installers_even_when_commands_expand) ... ok
test_r06_blocks_agent_human_approval_commands (test_guard.GuardTests.test_r06_blocks_agent_human_approval_commands) ... ok
test_r07_and_r08_follow_phase_state (test_guard.GuardTests.test_r07_and_r08_follow_phase_state) ... ok
test_fr002_empty_list_indication (test_notes.TestCLIIntegration.test_fr002_empty_list_indication)
FR-002, NFR-004, F-03: list on an empty store exits 0 and prints ... ok
test_fr005_delete_confirmation (test_notes.TestCLIIntegration.test_fr005_delete_confirmation)
FR-005, NFR-004, F-03: after creating a note, delete exits 0 and ... ok
test_fr001_create_returns_note (test_notes.TestCreateNote.test_fr001_create_returns_note)
FR-001: create_note returns a dict with id, title, content keys. ... ok
test_fr001_data_persists_across_load (test_notes.TestCreateNote.test_fr001_data_persists_across_load)
FR-001, NFR-001: a created note survives a subsequent list_notes call. ... ok
test_fr001_id_auto_increments (test_notes.TestCreateNote.test_fr001_id_auto_increments)
FR-001, NFR-003: successive creates yield IDs 1 and 2. ... ok
test_fr007_empty_content_raises (test_notes.TestCreateNote.test_fr007_empty_content_raises)
FR-007, NFR-005: empty string content raises ValidationError. ... ok
test_fr007_empty_title_raises (test_notes.TestCreateNote.test_fr007_empty_title_raises)
FR-007, NFR-005: empty string title raises ValidationError. ... ok
test_fr007_whitespace_only_content_raises (test_notes.TestCreateNote.test_fr007_whitespace_only_content_raises)
FR-007, NFR-005, F-05: whitespace-only content raises ValidationError. ... ok
test_fr007_whitespace_only_title_raises (test_notes.TestCreateNote.test_fr007_whitespace_only_title_raises)
FR-007, NFR-005, F-05: whitespace-only title raises ValidationError. ... ok
test_fr005_removes_note_from_storage (test_notes.TestDeleteNote.test_fr005_removes_note_from_storage)
FR-005: after delete_note, get_note raises NoteNotFoundError. ... ok
test_fr006_raises_not_found_for_absent_id (test_notes.TestDeleteNote.test_fr006_raises_not_found_for_absent_id)
FR-006, NFR-005: delete_note raises NoteNotFoundError for a missing ID. ... ok
test_nfr003_id_not_reused_after_delete (test_notes.TestDeleteNote.test_nfr003_id_not_reused_after_delete)
NFR-003: create note (id=1), delete it, create again -> new id=2. ... ok
test_fr003_returns_correct_note (test_notes.TestGetNote.test_fr003_returns_correct_note)
FR-003: get_note returns the note whose id matches the argument. ... ok
test_fr006_raises_not_found_for_absent_id (test_notes.TestGetNote.test_fr006_raises_not_found_for_absent_id)
FR-006, NFR-005: get_note raises NoteNotFoundError for a missing ID. ... ok
test_fr002_returns_all_created_notes (test_notes.TestListNotes.test_fr002_returns_all_created_notes)
FR-002: list_notes returns all notes after two successive creates. ... ok
test_fr002_returns_empty_list_when_no_notes (test_notes.TestListNotes.test_fr002_returns_empty_list_when_no_notes)
FR-002: list_notes returns [] on a freshly initialised store. ... ok
test_f01_atomic_write_no_tmp_file_remains (test_notes.TestStorage.test_f01_atomic_write_no_tmp_file_remains)
NFR-001, F-01: no .tmp file exists on disk after _save returns. ... ok
test_f02_corrupt_json_raises_storage_error (test_notes.TestStorage.test_f02_corrupt_json_raises_storage_error)
NFR-001, NFR-005, F-02: _load on corrupt JSON raises StorageError ... ok
test_nfr001_absent_file_returns_default (test_notes.TestStorage.test_nfr001_absent_file_returns_default)
NFR-001: _load on a non-existent path returns the default empty state. ... ok
test_nfr001_data_survives_process_reload (test_notes.TestStorage.test_nfr001_data_survives_process_reload)
NFR-001: data written by _save is fully recovered by a subsequent _load. ... ok
test_fr004_full_replace_both_fields (test_notes.TestUpdateNote.test_fr004_full_replace_both_fields)
FR-004: get_note after update_note returns both new field values. ... ok
test_fr004_replaces_title_and_content (test_notes.TestUpdateNote.test_fr004_replaces_title_and_content)
FR-004: update_note changes both title and content of the note. ... ok
test_fr006_raises_not_found_for_absent_id (test_notes.TestUpdateNote.test_fr006_raises_not_found_for_absent_id)
FR-006, NFR-005: update_note raises NoteNotFoundError for a missing ID. ... ok
test_fr007_empty_content_raises (test_notes.TestUpdateNote.test_fr007_empty_content_raises)
FR-007, NFR-005: update_note with empty content raises ValidationError. ... ok
test_fr007_empty_title_raises (test_notes.TestUpdateNote.test_fr007_empty_title_raises)
FR-007, NFR-005: update_note with empty title raises ValidationError. ... ok
test_fr007_whitespace_only_title_raises (test_notes.TestUpdateNote.test_fr007_whitespace_only_title_raises)
FR-007, NFR-005, F-05: whitespace-only title raises ValidationError. ... ok
test_check_detects_locked_outputs_and_missing_protected_path (test_orchestrator.OrchestratorCliTests.test_check_detects_locked_outputs_and_missing_protected_path) ... ok
test_hash_drift_refuses_approval (test_orchestrator.OrchestratorCliTests.test_hash_drift_refuses_approval) ... ok
test_human_approval_requires_tty_confirmation (test_orchestrator.OrchestratorCliTests.test_human_approval_requires_tty_confirmation) ... ok
test_initial_state_and_derived_status (test_orchestrator.OrchestratorCliTests.test_initial_state_and_derived_status) ... ok
test_invalid_cli_syntax_returns_usage_exit_code (test_orchestrator.OrchestratorCliTests.test_invalid_cli_syntax_returns_usage_exit_code) ... ok
test_locked_phase_cannot_be_submitted_and_is_audited (test_orchestrator.OrchestratorCliTests.test_locked_phase_cannot_be_submitted_and_is_audited) ... ok
test_missing_manifest_returns_rule_violation_exit_code (test_orchestrator.OrchestratorCliTests.test_missing_manifest_returns_rule_violation_exit_code) ... ok
test_reject_clears_hashes_and_returns_phase_to_active (test_orchestrator.OrchestratorCliTests.test_reject_clears_hashes_and_returns_phase_to_active) ... ok
test_reopen_refuses_until_later_outputs_are_removed (test_orchestrator.OrchestratorCliTests.test_reopen_refuses_until_later_outputs_are_removed) ... ok
test_second_submit_raises_rule_violation (test_orchestrator.OrchestratorCliTests.test_second_submit_raises_rule_violation)
AWAITING_APPROVAL phase cannot be submitted again; orchestrator must check status first. ... ok
test_submit_then_approve_activates_next_phase (test_orchestrator.OrchestratorCliTests.test_submit_then_approve_activates_next_phase) ... ok

----------------------------------------------------------------------
Ran 97 tests in 0.741s

OK
```
**Exit code**: 0
**Result**: PASS

---

### NFR-005 — Informative error messages

**Check type**: CLI (using NOTES_PATH env var for temp isolation)
**Expected**: CLI view with non-existent ID prints "Note not found: 999" to stderr and exits 1; CLI create with empty title prints "Title must not be empty." to stderr and exits 1.
**Command**: `NOTES_PATH=<tempfile> python -m notes.cli view --id 999` and `NOTES_PATH=<tempfile> python -m notes.cli create --title "" --content "body"`
**Output**:
```
Note not found: 999
EXIT:1
```
```
Title must not be empty.
EXIT:1
```
**Exit code**: 1 (both cases)
**Result**: PASS

---

### NFR-006 — README documentation

**Check type**: manual inspection
**Expected**: README.md includes setup instructions (Python version requirement, notes.json auto-creation) and usage examples for all five CLI operations: create, list, view, update, delete.
**Command**: Read `C:\Users\MohdAsadKhan\Desktop\Claude-capstone\README.md` lines 1–67
**Observed**:
- Line 1: `# Notes CLI` — title present
- Lines 7–13: Setup section — Python 3.11+ requirement, `python --version`, notes.json auto-created on first write
- Lines 23–26: Create example — `python -m notes.cli create --title "Shopping list" --content "Milk, eggs, bread"`
- Lines 28–36: List example — `python -m notes.cli list`, empty-store indicator "No notes found."
- Lines 38–40: View example — `python -m notes.cli view --id 1`
- Lines 42–45: Update example (full replace noted) — `python -m notes.cli update --id 1 --title ... --content ...`
- Lines 47–55: Delete example — `python -m notes.cli delete --id 1`, confirms "Note 1 deleted."
- Lines 57–68: Error handling description and test instructions

All five subcommands documented with examples; setup instructions present.
**Exit code**: N/A
**Result**: PASS

---

## git status --short

```
 M .claude/agents/architecture.md
 M .claude/agents/design-review.md
 M .claude/agents/implementation.md
 M .claude/agents/orchestrator.md
 M .claude/agents/planning.md
 M .claude/agents/pr.md
 M .claude/agents/requirements.md
 M .claude/agents/review.md
 M .claude/agents/verify.md
 D .claude/commands/architecture.md
 D .claude/commands/design-review.md
 D .claude/commands/implementation.md
 D .claude/commands/planning.md
 M .claude/commands/pr.md
 D .claude/commands/requirements.md
 D .claude/commands/review.md
 M .claude/commands/run.md
 D .claude/commands/verify.md
 M .claude/skills/pr/SKILL.md
 M .mcp.json
 D CHANGELOG.md
 M README.md
 M artifacts/architecture.md
 M artifacts/design-review.md
 M artifacts/implementation-plan.md
 D artifacts/pr.md
 M artifacts/requirements.md
 M artifacts/review.md
 D artifacts/verify.md
 M docs/CONTRACT.md
 M docs/RUNBOOK.md
 M sdlc/audit.log.jsonl
 M sdlc/phases.json
 M sdlc/state.json
 M tests/test_config.py
 M tests/test_github_pr.py
 M tests/test_orchestrator.py
 D tests/test_todo.py
 D todo/__init__.py
 D todo/app.py
 D todo/cli.py
 M tools/github_pr.py
 M user_story.md
?? docs/codemie/
?? notes/
?? tests/test_notes.py
?? tools/update_phases.py
```

---

## Results table

| ID | Description | Check type | Result |
|----|-------------|------------|--------|
| FR-001 | Create note | unit test | PASS |
| FR-002 | View all notes | unit test | PASS |
| FR-003 | View note by ID | unit test | PASS |
| FR-004 | Update note | unit test | PASS |
| FR-005 | Delete note | unit test | PASS |
| FR-006 | Error on non-existent note | unit test | PASS |
| FR-007 | Invalid input rejection | unit test | PASS |
| NFR-001 | JSON persistence | unit test | PASS |
| NFR-002 | CLI interface | CLI | PASS |
| NFR-003 | Auto-increment integer IDs | unit test | PASS |
| NFR-004 | Automated test coverage | unit test (full suite) | PASS |
| NFR-005 | Informative error messages | CLI | PASS |
| NFR-006 | README documentation | manual inspection | PASS |

---

## Failures and notes

None.

---

## Final verdict

Result: PASS
