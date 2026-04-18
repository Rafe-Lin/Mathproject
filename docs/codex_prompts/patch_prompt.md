# Minimal Patch Prompt

Use this prompt to apply a focused patch after audit is complete.

## Change Target
- State exact files to modify.
- State exact symbols/mappings to update.

## Constraints
- Only change listed files.
- No architecture refactor.
- No new skill creation.
- No unrelated cleanup.

## Do Not Touch
- PPO/routing core policy design.
- textbook progression architecture.
- unrelated family definitions.
- unrelated generator modules.

## Verification Required
- Show changed files.
- Show exact patched section summary.
- Show smoke check result (`py_compile` or focused runtime check).
- Confirm runtime impact is none/minimal.
