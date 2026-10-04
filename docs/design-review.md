# Design Review: Automated Documentation Sync

**Status:** Findings dispositioned; accepted findings applied to the requirements and architecture  
**Review basis:** `docs/architecture.md` against `docs/requirements.md`

## Findings

### DR-01: Requirements baseline drift

**Severity:** High  
**Decision:** Accepted  
**Rationale:** The requirements left marker behavior, backup policy, diff behavior, and empty-repository output unresolved after the architecture specified them. The requirements also used a broader credential-file phrase than the selected filename rule. This weakened traceability.  
**Resolution:** Synchronized the requirements with the accepted decisions and scan limits. The requirements status now reflects user approval.

### DR-02: Secret screening boundary

**Severity:** High  
**Decision:** Accepted  
**Rationale:** Screening only before Fact Model insertion did not define whether parsers, diffs, or backups could receive raw secret values.  
**Resolution:** Specified a shared pre-parser Secret Guard. It discards matched values before parsing or Fact Model insertion, skips a file if safe sanitization is uncertain, and blocks diff/backup/write for a secret-bearing output target. Warnings contain paths only.

### DR-03: Empty-repository flow bypassed write safety

**Severity:** Medium  
**Decision:** Accepted  
**Rationale:** The empty path did not clearly pass through diff, approval, backup, and writing.  
**Resolution:** Routed the empty README section through the normal diff/approval/writer path; API generation is skipped, and successful completion prints a clear non-error message.

### DR-04: Scan scalability and resource bounds

**Severity:** Medium  
**Decision:** Accepted  
**Rationale:** Excluding files only from extraction could still traverse `.git` and other large directories; parser resource use was unbounded.  
**Resolution:** Prune `.git`, tests, CI, excluded directories, and out-of-root symlinks before descent. Set limits of 1,000 supported files, 5 MiB per file, and 100 MiB aggregate, and specify a timed performance test under the 60-second active-processing target.

### DR-05: Stale diff and time-of-check/time-of-use risk

**Severity:** Medium  
**Decision:** Accepted  
**Rationale:** A target could change after approval but before replacement, causing an unseen overwrite.  
**Resolution:** Fingerprint each target when preparing its diff and revalidate after approval and immediately before replacement. If content changed, regenerate the diff and obtain approval again.

### DR-06: Public API discovery rules

**Severity:** Medium  
**Decision:** Accepted  
**Rationale:** Leading underscores and `__all__` alone did not define treatment of static re-exports or ambiguous and dynamic exports.  
**Resolution:** Define public names as non-underscore top-level functions/classes, overridden by literal `__all__`; include simple statically resolvable relative re-exports. Do not execute dynamic exports; mark ambiguous API facts `Not Found`. Add fixtures for these cases.

### DR-07: Testability coverage

**Severity:** Medium  
**Decision:** Accepted  
**Rationale:** The architecture named pytest but did not map key safety and reliability behavior to concrete tests.  
**Resolution:** Added unit, security, writer, integration, and performance scenarios covering malformed inputs, secret leakage, approval, markers, backups, target changes, empty repositories, and the 1,000-file budget.

### DR-08: Dependency version and update policy

**Severity:** Low  
**Decision:** Deferred  
**Rationale:** Dependency pinning, licensing, and update policy can be decided during implementation planning without blocking the accepted architecture corrections. `PyYAML` and `packaging` remain the proposed dependencies for now.

## Review Result

All High- and Medium-severity findings were accepted and applied. The Low-severity dependency policy finding is deferred. No application code was changed during this review.