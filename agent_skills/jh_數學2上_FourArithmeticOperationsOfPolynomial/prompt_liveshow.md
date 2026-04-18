/no_think

Return Python code only.

You are generating LiveShow code for `jh_數學2上_FourArithmeticOperationsOfPolynomial`.

Input OCR text:

`{{OCR_RESULT}}`

Goal:
- identify the canonical family first
- preserve the same family and answer type
- output a stable randomized generator for repeated LiveShow use

## A. Canonical Family Catalogue

Use exactly one of these as your internal target family:

- `F1 poly_add_sub_flat`
- `F2 poly_add_sub_nested`
- `F3 poly_add_sub_unknown`
- `F4 poly_mul_monomial`
- `F5 poly_mul_poly`
- `F6 poly_mul_special_identity`
- `F7 poly_div_monomial_eval`
- `F8 poly_div_monomial_qr`
- `F9 poly_div_poly_qr`
- `F10 poly_div_reverse`
- `F11 poly_mixed_simplify`
- `F12 poly_geom_formula_direct`
- `F13 poly_geom_region_composite`

## B. Sub-skill Nodes

The family may depend on one or more of:

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

Do not destroy the original node combination when randomizing.

## C. Family Decision Rules

1. If the question asks for an unknown polynomial, choose `F3`.
2. If the question explicitly asks for quotient and remainder with a monomial divisor, choose `F8`.
3. If the question explicitly asks for quotient and remainder with a polynomial divisor, choose `F9`.
4. If the question reconstructs dividend or divisor from quotient/remainder information, choose `F10`.
5. If the wording uses a multiplication identity, choose `F6`.
6. If the question is geometry-first, choose `F12` or `F13`, not a plain algebra family.
7. If the expression is multi-step mixed simplification, choose `F11`.
8. If multiple families appear possible, prefer the most semantically specific family, not the simplest one.

## D. Hard Rules

1. Define `generate(level=1, **kwargs)` and `check(user_answer, correct_answer)`.
2. Preserve the detected family.
3. Do not downgrade unknown/division/geometry problems into basic add/sub or multiplication.
4. `question_text` math must use `$...$`.
5. Use `x^{2}`, not `x^2`, in `question_text`.
6. `correct_answer` must never be empty.
7. Prefer `PolynomialOps.format_latex`, `format_plain`, `add`, `sub`, `mul`, `normalize`.
8. If needed, write small local helpers only for long division, quotient/remainder, reverse-division, or geometry formulas.

## E. Answer-Type Rules

- `F1-F7`, `F11`: plain polynomial expression answer
- `F8-F9`: quotient and remainder answer
- `F10`: reconstructed polynomial answer
- `F12`: target geometric quantity as polynomial
- `F13`: usually two targets such as perimeter and area

Answer formatting examples:

- plain polynomial: `3x^2-2x+1`
- quotient/remainder: `商式：x+2；餘式：3`
- two targets: `周長：6x+18；面積：3x^2+4x+7`

## F. Randomization Rules

1. Randomize coefficients and constants, not the family.
2. Preserve degree profile.
3. Preserve bracket topology when nested structure matters.
4. Preserve whether the task is direct evaluation, unknown solving, quotient/remainder, reverse reconstruction, or geometry application.
5. Avoid generating zero coefficients that collapse the family unexpectedly.

## G. Minimal Implementation Shape

Use this shape:

```python
import random

def generate(level=1, **kwargs):
    # family-preserving randomized logic
    return {
        "question_text": "...",
        "answer": "",
        "correct_answer": "...",
        "mode": 1
    }

def check(user_answer, correct_answer):
    u = str(user_answer).strip().replace(" ", "")
    c = str(correct_answer).strip().replace(" ", "")
    return {"correct": u == c, "result": "正確" if u == c else "錯誤"}
```

## H. Final Output Rules

1. Output Python code only.
2. Do not output markdown fences.
3. Do not output analysis or explanations.
4. Use textbook Chinese wording.
