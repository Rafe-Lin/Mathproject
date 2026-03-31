# Codex Project Guardrails

This file defines the mandatory rules for Codex-driven changes in this repository.
All future patches must comply with this document.

## 1) Three-Layer Architecture (Do Not Collapse)
- `progression` (textbook sequence): controls family progression and prerequisite intent.
- `routing` (PPO): controls policy action and skill/subskill routing.
- `remediation` (RAG): controls diagnostic hints and bridge candidate retrieval.

These layers are separate responsibilities. Do not refactor them into one flow.

## 2) Fixed Skill Structure
- Official arithmetic skills in this scope:
  - `jh_數學1上_FourArithmeticOperationsOfIntegers`
  - `jh_數學1上_FourArithmeticOperationsOfNumbers`
  - `jh_數學2上_FourArithmeticOperationsOfPolynomial`
- Do not add new standalone skills for exponent content.
- Explicitly forbidden as new runtime skills:
  - `jh_數學1上_IntegerExponentiation`
  - `jh_數學1上_PowerOfNumbers`

## 3) Family / Subskill Definition Rules
- Family definitions must stay in canonical catalog sources.
- Subskills must be consistent across:
  - source catalog
  - family-subskill map
  - config catalog json
  - UI map json
- Use `skill_id:family_id` as the canonical addressing key.

## 4) Generator Rules
- Family-to-generator mapping must be explicit and type-correct.
- Do not map a family to an unrelated question type.
- Any family addition/update requires verifying micro-generator coverage.
- Avoid placeholder/fallback-only output for production family mappings.

## 5) Remediation Rules
- Polynomial remediation bridges should prioritize prerequisite coverage through:
  - numbers-side exponent laws
  - integer-side sign/power interpretation
- Keep bridge direction coherent: polynomial -> numbers -> integers (as needed by diagnosis).

## 6) Required Power-Like Fallback Candidates
- The power-like fallback candidate set must include at least:
  - `signed_power_interpretation`
  - `same_base_multiplication_rule`
  - `power_of_power_rule`
  - `product_power_distribution`

## 7) Assessment Rules
- Standard score baseline: `100`.
- Uncovered required families count as `0` contribution.
- Core family set must be fixed by configured assessment gate.

## 8) Diagnostic Report Minimum Fields
- `score`
- `APR`
- `family_results`
- `strengths`
- `weaknesses`

## 9) RAG Identity Rules
- Chroma/bridge identity must be `skill_id:family_id`.
- Do not rely on global `family_id` uniqueness.

## 10) Catalog Regeneration Rule
- After catalog-source edits, run:
  - `python scripts/generate_skill_breakpoint_maps.py`
- Then verify `configs/skill_breakpoint_catalog.json` and `configs/skill_breakpoint_ui_map.json`.

## 11) Legacy Skill Handling
- `jh_數學1上_IntegerExponentiation`
- `jh_數學1上_PowerOfNumbers`

These are legacy artifacts and must not be reintroduced into runtime routing paths.

## 12) Hard Constraints
- Do not redesign PPO/routing/progression architecture in routine patches.
- Do not add new skills for this exponent integration.
- Do not use global-family shortcuts that break `skill_id:family_id` identity.
- Do not perform broad refactors when a minimal patch is sufficient.

## 13) Safe Change Zone
- Preferred safe edit areas:
  - docs and prompt templates
  - catalog source rows and generated maps
  - minimal mapping/fallback candidate additions
  - explicit legacy isolation notes
- Avoid invasive changes outside the requested scope.

## 14) Codex Workflow (Mandatory)
1. Audit first (consistency and impact).
2. Patch second (minimal, scoped, reversible).
3. Verify with focused checks.
4. Report touched files and runtime impact clearly.

