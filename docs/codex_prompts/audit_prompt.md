# Consistency Audit Prompt

Use this prompt when you need to audit integration consistency before changing code.

## Scope
- Check skill/family definitions and ownership.
- Check generator mapping coverage and type correctness.
- Check catalog source -> generated config synchronization.
- Check RAG indexing path and key identity usage.
- Check remediation bridge candidate reachability.
- Check legacy residue and runtime exposure risk.

## Required Behavior
- Audit first, do not patch immediately.
- Report gaps as: `OK / Missing / Conflict`.
- Include exact file paths and line references.
- Distinguish data-present vs runtime-reachable.

## Expected Output
- Overall status: complete / partial / broken.
- Findings by layer:
  - skill/family
  - generator
  - catalog/UI
  - RAG
  - remediation
  - legacy
- Minimal fix order (top priority only).

