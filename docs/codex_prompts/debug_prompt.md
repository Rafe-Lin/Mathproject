# Debug Prompt

Use this prompt for issue debugging with controlled scope.

## Input
- Problem statement (symptoms, logs, failing path).
- Reproduction context (module, endpoint, family/skill scope).

## Analysis First
- List likely root causes with evidence.
- Identify highest-probability cause first.
- Explain why alternatives are less likely.

## Patch Rules
- Do not apply broad refactor.
- Do not jump to large multi-file rewrites.
- Start with smallest valid fix.

## Required Output
- root cause
- changed files
- why fix is minimal
- validation results
