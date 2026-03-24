# Polynomial Skill Specification

This skill covers junior-high polynomial four operations and closely related application problems for `jh_數學2上_FourArithmeticOperationsOfPolynomial`.

The objective is to produce stable, family-preserving generators for:

- LiveShow
- benchmark
- repeated randomization
- regression testing
- family-aware answer checking

## Skill Identity

- `skill_id`: `jh_數學2上_FourArithmeticOperationsOfPolynomial`
- `display_name`: Polynomial Four Operations
- `family`: `polynomial`
- supported modes: `BENCHMARK`, `LIVESHOW`

## Output Contract

Every final script must define exactly:

```python
def generate(level=1, **kwargs):
    ...

def check(user_answer, correct_answer):
    ...
```

`generate()` must return:

```python
{
    "question_text": str,
    "answer": "",
    "correct_answer": str,
    "mode": 1
}
```

Rules:

1. `question_text` must contain textbook Chinese wording.
2. Visible math must be wrapped with `$...$`.
3. Use `x^{2}`, not `x^2`, in `question_text`.
4. Use `\\frac{a}{b}` when fractions are visible.
5. Use `\\times` and `\\div` when multiplication/division are shown.
6. `correct_answer` must never be empty.

## Hard Rules

1. `generate(level=1, **kwargs)` is mandatory.
2. The script must compile successfully.
3. The output should be a randomized family-preserving generator whenever possible.
4. Do not degrade unknown-polynomial, division, reverse-division, or geometry families into simpler add/sub or multiply families.
5. Prefer `PolynomialOps` for formatting, normalization, addition, subtraction, and multiplication.
6. You may define small local helpers only when required for long division, quotient/remainder, reverse-division, or geometry formulas.
7. Do not import `sympy`, `numpy`, `pandas`, or other heavy libraries.
8. Do not output markdown fences, explanations, or prose to the user in the final response.

## Family Catalogue

Use these family IDs as the canonical classification for this skill.

### F1 `poly_add_sub_flat`

Definition:
- Flat polynomial addition or subtraction
- No nested brackets

Typical examples:
- `計算 $(4x+5+2x^{2}) + (1+2x+x^{2})$。`
- `計算 $(2x^{2}-5) + (-x^{2}+2x+1)$。`
- `計算 $(x^{2}+5x+1) - (2-3x^{2})$。`

Quality gate:
- Only `+` and `-`
- At least two grouped polynomials
- Like terms must exist across groups

### F2 `poly_add_sub_nested`

Definition:
- Polynomial addition/subtraction with nested grouping
- Outer minus may apply to an entire bracketed expression

Typical examples:
- `計算 $(-3x^{2}-7+x)-[(1-2x^{2})-(2x+6)]$。`

Quality gate:
- Nested bracket depth >= 2
- Sign distribution must matter

### F3 `poly_add_sub_unknown`

Definition:
- Solve for an unknown polynomial from an addition/subtraction equation

Typical examples:
- `若 $A+(-4x^{2}+1+5x)=x^{3}+5-2x$，則多項式 $A=$？`
- `若 $B-(6x^{3}-2+x^{2})=5x^{2}+11-3x$，則多項式 $B=$？`

Quality gate:
- Must preserve the unknown polynomial target
- Final answer must be the unknown polynomial itself

### F4 `poly_mul_monomial`

Definition:
- Monomial by monomial or monomial by polynomial multiplication

Typical examples:
- `計算 $(-7x)\\cdot 5x$。`
- `計算 $3x(x+2)$。`
- `計算 $(-2x+3)(-3x)$。`

Quality gate:
- At least one factor is a monomial
- Structure must remain multiplication

### F5 `poly_mul_poly`

Definition:
- General polynomial multiplication and expansion

Typical examples:
- `計算 $(x^{2}-x+1)(x+2)$。`
- `計算 $(x-1)(x^{2}+x+1)$。`
- `計算 $(5x^{2}-4)(-2x+3)$。`

Quality gate:
- Both factors are explicit polynomials
- Expansion and combination of like terms are required

### F6 `poly_mul_special_identity`

Definition:
- Special products such as square of a binomial or product of conjugates

Typical examples:
- `利用乘法公式計算 $(3x+4)^{2}$。`
- `利用乘法公式計算 $(2x-5)^{2}$。`
- `利用乘法公式計算 $(4x+7)(4x-7)$。`

Quality gate:
- Structure must remain a formula pattern
- Do not rewrite as generic multiplication wording

### F7 `poly_div_monomial_eval`

Definition:
- Divide a monomial or polynomial by a monomial and directly simplify

Typical examples:
- `計算 $(15x^{2})\\div(3x)$。`
- `計算 $(-4x^{3})\\div(2x)$。`

Quality gate:
- Divisor is a monomial
- Output is a direct simplified result

### F8 `poly_div_monomial_qr`

Definition:
- Divide a polynomial by a monomial and report quotient and remainder

Typical examples:
- `求 $(4x^{2}+8x-2)$ 除以 $4x$ 的商式與餘式。`
- `求 $(-6x^{2}+4x-5)\\div 2x$ 的商式與餘式。`

Quality gate:
- Must ask for quotient and remainder
- Final answer must clearly include both

### F9 `poly_div_poly_qr`

Definition:
- Polynomial long division with quotient and remainder

Typical examples:
- `求 $(2x^{2}-x-6)\\div(x-2)$ 的商式與餘式。`
- `求 $(3x^{2}+5)\\div(x-4)$ 的商式與餘式。`
- `求 $(2x^{2}-x-6)\\div(2x+3)$ 的商式與餘式。`

Quality gate:
- Quotient and remainder must both be present
- Remainder degree must be lower than divisor degree

### F10 `poly_div_reverse`

Definition:
- Reconstruct dividend or divisor from quotient and remainder information

Typical examples:
- `如果一個多項式 $A$ 除以 $x+2$ 的商式為 $3x^{2}+1$，餘式為 $4$，試求此多項式 $A$。`
- `已知 $2x^{2}+7x+1$ 除以另一個多項式 $A$ 後，得到商式為 $2x+1$，餘式為 $-2$，試求此多項式 $A$。`

Quality gate:
- Preserve reverse-division wording
- Do not turn into a direct division task

### F11 `poly_mixed_simplify`

Definition:
- Multi-step polynomial simplification combining expansion, formula use, and add/sub

Typical examples:
- `計算 $(x+2)^{2}+(2x+1)$。`
- `計算 $5(2x+1)^{2}-3(x+1)(x+3)$。`
- `計算 $(x+1)(x+2)-(x+3)(x+4)$。`

Quality gate:
- Requires at least two operations
- Must not collapse into a single-family wording

### F12 `poly_geom_formula_direct`

Definition:
- Geometry formula application with polynomial expressions
- Usually asks for an unknown geometric quantity from known ones

Typical examples:
- `右圖是大象造型的梯形溜滑梯，若溜滑梯的上底為 $x-3$、下底為 $3x+5$、面積為 $2x^{2}+5x+2$，試以 $x$ 的多項式表示此溜滑梯的高。`

Quality gate:
- Identify the shape
- Use the correct geometry formula first

### F13 `poly_geom_region_composite`

Definition:
- Composite region perimeter or area using polynomial expressions

Typical examples:
- `右圖中，大長方形的長為 $2x+5$、寬為 $x+4$，小長方形的長為 $2x+1$、寬為 $x-1$。試以 $x$ 的多項式表示橘色部分的周長與面積。`

Quality gate:
- Preserve the region-composition meaning
- Perimeter and area are separate targets

## Sub-skill Graph

These are the reusable sub-skill nodes behind the catalogue.

- `node.poly.normalize_terms`
- `node.poly.combine_like_terms`
- `node.poly.sign_distribution`
- `node.poly.expand_monomial`
- `node.poly.expand_binomial`
- `node.poly.special_identity`
- `node.poly.long_division`
- `node.poly.quotient_remainder_format`
- `node.poly.reverse_division_reconstruction`
- `node.poly.geometry_formula`
- `node.poly.composite_region_modeling`
- `node.poly.family_isomorphism`

Family-to-node mapping:

- `F1` -> `normalize_terms`, `combine_like_terms`
- `F2` -> `sign_distribution`, `combine_like_terms`, `family_isomorphism`
- `F3` -> `sign_distribution`, unknown-target preservation
- `F4` -> `expand_monomial`
- `F5` -> `expand_binomial`, `combine_like_terms`
- `F6` -> `special_identity`
- `F7` -> `normalize_terms`
- `F8` -> `long_division`, `quotient_remainder_format`
- `F9` -> `long_division`, `quotient_remainder_format`
- `F10` -> `reverse_division_reconstruction`
- `F11` -> multiple nodes combined
- `F12` -> `geometry_formula`
- `F13` -> `geometry_formula`, `composite_region_modeling`

## Structural Schema / Generator Hints

When a family needs explicit structure planning, prefer pure structured vars rather than opaque expression strings.

- `F1`: `{"left_terms": [...], "right_terms": [...], "op": "+"|"-"}`
- `F2`: `{"outer_terms": [...], "inner_groups": [...], "outer_op": "-"}`
- `F3`: `{"unknown_name": "A"|"B", "known_poly": [...], "result_poly": [...], "op": "+"|"-"}`
- `F4`: `{"factor1": [...], "factor2": [...]}`
- `F5`: `{"factor1": [...], "factor2": [...]}`
- `F6`: `{"pattern": "square"|"conjugate", "a": int, "b": int}`
- `F7`: `{"dividend": [...], "divisor": [...]}`
- `F8`: `{"dividend": [...], "divisor": [...], "ask_qr": true}`
- `F9`: `{"dividend": [...], "divisor": [...], "ask_qr": true}`
- `F10`: `{"known_divisor_or_dividend": [...], "quotient": [...], "remainder": int}`
- `F11`: `{"segments": [...], "ops": [...]}`
- `F12`: `{"shape": "trapezoid"|..., "formula_inputs": {...}, "target": "height"|...}`
- `F13`: `{"outer_shape": {...}, "inner_shape": {...}, "targets": ["perimeter", "area"]}`

## Answer-Type Contract

- Plain polynomial:
  - Example: `3x^2-2x+1`
- Quotient and remainder:
  - Example: `商式：x+2；餘式：3`
- Two targets:
  - Example: `周長：6x+18；面積：3x^2+4x+7`
- Unknown polynomial:
  - Answer is the unknown polynomial itself

## Level Guidance

Levels express difficulty within families, not a one-to-one family mapping.

- Level 1:
  - `F1`
  - `F4`
  - easy `F6`
- Level 2:
  - `F2`
  - `F5`
  - `F7`
  - basic `F11`
- Level 3:
  - `F3`
  - `F8`
  - `F9`
  - `F10`
  - `F12`
  - `F13`

## Generator Priority

When producing final code, prefer:

1. A randomized isomorphic generator for the same family
2. A randomized generator with the same difficulty profile
3. A compilable generator that preserves the same family and answer type
4. A fixed single question only as a last-resort fallback

## Verification Logic

Before returning code, verify:

1. The selected family is preserved.
2. The wording matches the expected answer type.
3. `question_text` uses textbook Chinese.
4. The display layer uses valid LaTeX.
5. `correct_answer` matches the actual computed result.
6. Geometry families do not silently drop geometric meaning.

## Minimum check() Guidance

At minimum:

```python
def check(user_answer, correct_answer):
    u = str(user_answer).strip().replace(" ", "")
    c = str(correct_answer).strip().replace(" ", "")
    return {"correct": u == c, "result": "正確" if u == c else "錯誤"}
```

=== SKILL_END_PROMPT ===
