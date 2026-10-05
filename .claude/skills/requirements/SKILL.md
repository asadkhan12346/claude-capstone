---
name: requirements
description: Elicit complete, testable requirements without making product decisions. Use this skill when running the requirements phase (/requirements).
---
# Requirements Method

## Numbering and testability
Number every behavior sentence. Use one FR per behavior, concrete Given/When/Then acceptance criteria, and measurable NFR thresholds. Cite the source story and keep assumptions separate from requirements.

## Ambiguity checklist
Check empty input, duplicates, persistence, limits, ordering, concurrency, errors, output format, and vague words. Collect all questions before asking. Ask once in a single numbered message, then wait for answers.

## Recording answers
Record each human answer as `- [x] Q: ... A: ... (source: human, YYYY-MM-DD)`. Do not leave unanswered `- [ ]` items in the submitted artifact. If no question remains, say `None` under Open Questions.

## Artifact template
Use headings: Requirements, Source, Functional Requirements, Non-Functional Requirements, Constraints, Assumptions, Open Questions. Define IDs as `FR-001` and `NFR-001`, increasing sequentially.

## Validation checklist
- Every story behavior has exactly one FR and concrete acceptance criteria.
- NFRs have measurable outcomes.
- Answers and sources are recorded accurately.
- No design, library, or implementation choices were introduced.
- Open Questions contains no unchecked items.

## Stop condition
Do not write until the human answers the clarification message. Submit only when the active phase and artifact checks pass; stop for human approval immediately after submit.
