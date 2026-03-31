# Test Prompt

Use this prompt to validate adaptive behavior after changes.

## Test Focus
- sequence tests (textbook progression continuity)
- remediation tests (bridge candidate reachability)
- assessment tests (score gate and coverage behavior)
- report tests (required output fields)

## Required Checks
- Verify no family mapping regressions.
- Verify no generator placeholder regression for touched families.
- Verify no `skill_id:family_id` identity break in RAG paths.

## Output
- pass/fail per test bucket
- failing case list with file hints
- residual risks
