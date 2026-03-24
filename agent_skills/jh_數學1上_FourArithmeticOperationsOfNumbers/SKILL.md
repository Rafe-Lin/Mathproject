/no_think

# Fraction Arithmetic Skill Specification

Skill ID: `jh_數學1上_FourArithmeticOperationsOfNumbers`
Stage: Junior High Grade 7, Semester 1
Core topic: fractions, mixed numbers, signed fractions, decimal-fraction mixed arithmetic, reciprocal, and textbook word problems built on fraction invariance.

## Skill Positioning

This skill is best modeled as a hybrid of:
- `Family Catalogue` from polynomial
- `deterministic helper path` from integer
- `strict structural data contract` from radicals for fraction display and answer normalization

In production, this skill should prefer deterministic helper orchestration for textbook-shaped fraction questions. Prompt generation remains a fallback, not the primary source of truth.

## Output Contract

Generated code must define:

```python
def generate(level=1, **kwargs):
    return {
        "question_text": str,
        "answer": "",
        "correct_answer": str,
        "mode": 1,
    }

def check(user_answer, correct_answer):
    ...
```

Hard requirements:
- `correct_answer` must never be empty.
- Fraction answers must be reduced.
- Improper fractions are allowed in `correct_answer`; mixed numbers are reserved for display-sensitive family decisions only.
- Equivalent numeric forms are accepted in `check()` when the family is numeric-answer based.
- Comparison families must preserve the full order relation, not just the max/min endpoint.

## Hard Rules

1. The generated problem must stay in the same fraction family as the source.
2. Do not drift from fraction arithmetic into integer-only arithmetic unless the source answer simplifies to an integer.
3. Keep denominator sign normalized: use `-a/b`, never `a/-b`.
4. Mixed numbers must be interpreted structurally:
   `-2 3/4 = -(2 + 3/4)`, not `(-2) + 3/4`.
5. Decimal operands must be converted exactly to `Fraction` during evaluation.
6. Reciprocal families must reject zero.
7. Word problems must preserve the same governing fraction relationship, not just the same answer type.

## Family Catalogue

### F1. Fraction Simplification
Definition:
- judge whether a fraction or mixed number is already in simplest form
- if not, reduce it

Representative forms:
- `45/60`
- `-36/96`
- `16/-81`
- `-2 15/33`

Expected answer type:
- reduced fraction or reduced mixed number

### F2. Equivalent Fraction Fill-Blank
Definition:
- solve blanks in an equivalence chain of fractions

Representative forms:
- `-4/5 = -12/15 = 20/-25 = (_)/-50`
- `-7/3 = -35/15 = 28/(_) = (_)/-45`

Expected answer type:
- comma-separated scalar blanks in left-to-right order

### F3. Preserve-Value Fraction Invariance
Definition:
- one part of a fraction changes by a fixed amount; solve the required corresponding change so value stays the same

Representative form:
- `5/6` denominator plus `18`, numerator should plus how much

Expected answer type:
- integer

### F4. Fraction Comparison
Definition:
- compare two or more fractions or mixed numbers
- includes positive, negative, improper, and mixed-number comparison

Representative forms:
- `2/3, 3/4, 5/6`
- `-3/4, -7/9, -11/12`
- `-1 1/2, -1 2/3, -1 3/4`

Expected answer type:
- ascending order chain, e.g. `-11/12 < -7/9 < -3/4`

### F5. Fraction Add/Subtract
Definition:
- evaluate signed fraction addition/subtraction
- includes same denominator, unlike denominator, nested parentheses, and mixed numbers

Representative forms:
- `(-7/5)+(-9/5)`
- `2/3-(-3/4)+(-1/6)`
- `(-2 3/4)+1 2/7`

Expected answer type:
- reduced fraction or integer

### F6. Fraction Multiply
Definition:
- evaluate signed fraction or mixed-number multiplication
- includes chained products and telescoping products

Representative forms:
- `(-3/2) * 1/4`
- `(-2 1/3) * (-5/21) * (-1 1/5)`
- `(-2/3)(-3/4)(-4/5)...(-99/100)`

Expected answer type:
- reduced fraction or integer

### F7. Fraction Divide
Definition:
- evaluate division by fraction / mixed number / decimal
- may include mixed multiply-divide expressions

Representative forms:
- `5/6 ÷ (-3 1/3)`
- `(-9/8) ÷ (-3/4) ÷ 1/3`
- `3/2 ÷ (-0.6) * (-3/5) - 1/2`

Expected answer type:
- reduced fraction or integer

### F8. Reciprocal
Definition:
- write the reciprocal of a fraction, integer, or mixed number

Representative forms:
- `3 2/5`
- `-4/7`
- `-1`

Expected answer type:
- reduced fraction or integer

### F9. Decimal-Fraction Mixed Evaluation
Definition:
- fraction arithmetic where decimals and integers appear in the same expression

Representative forms:
- `0.3*2/3 - (-7/5) ÷ [5/3 + (-0.5)]`
- `(-1/3)*(3/5+1.5) ÷ (-2 1/5)`

Expected answer type:
- reduced fraction or integer

### F10. Fraction Word Problems
Definition:
- apply fraction relationships to rate, remaining amount, inheritance, or before/after ratio

Representative subfamilies:
- drone remaining pesticide weight
- bottle and juice weight
- remaining milk amount
- inheritance share comparison
- library before/after book count

Expected answer type:
- reduced scalar answer or verbal comparison result

## Sub-skill Graph

```text
Fraction Arithmetic
├─ Fraction Representation
│  ├─ proper / improper fractions
│  ├─ mixed numbers
│  ├─ sign normalization
│  └─ decimal-to-fraction exact conversion
├─ Structural Reasoning
│  ├─ simplest-form reduction
│  ├─ equivalent-fraction scaling
│  ├─ reciprocal transform
│  └─ preserve-value invariance
├─ Order Reasoning
│  ├─ positive fraction comparison
│  ├─ negative fraction comparison
│  └─ mixed-number comparison
├─ Expression Evaluation
│  ├─ add/sub
│  ├─ multiply
│  ├─ divide
│  ├─ nested parentheses
│  ├─ decimal-fraction mixed arithmetic
│  └─ telescoping products
└─ Applied Word Problems
   ├─ remaining amount
   ├─ container weight
   ├─ before/after ratio
   └─ share comparison
```

## Structural Schema

### Numeric Node Schema

```python
{
    "value": Fraction,
    "kind": "fraction" | "mixed" | "int" | "decimal",
    "label": str,
}
```

### Family Config Schema

```python
{
    "family": str,
    "source_text": str,
    ... family-specific fields ...
}
```

Examples:

```python
{
    "family": "frac_compare_set",
    "numbers": [
        {"value": Fraction(-3, 4), "label": "-3/4"},
        {"value": Fraction(-7, 9), "label": "-7/9"},
    ],
}
```

```python
{
    "family": "frac_equivalent_fill_blank",
    "base_value": Fraction(-4, 5),
    "blank_specs": [{"kind": "num", "den": -50}],
}
```

## Answer-Type Contract

- Simplify / eval / reciprocal / invariant / numeric word problems:
  reduced scalar string such as `-7/3`, `25`, `3/8`
- Comparison:
  ordered chain such as `2/7 < 3/13 < 5/23`
- Fill blank:
  comma-separated answers such as `40,-105`
- Inheritance comparison:
  verbal answer such as `四人分得相同`

## Engineering Path

Primary runtime path:
- `core/fraction_domain_functions.py`
  - `FractionFunctionHelper.build_config`
  - `FractionFunctionHelper.generate_from_config`

LiveShow deterministic route:
- `core/routes/live_show.py`
  - direct helper path when `skill_id` contains `FourArithmeticOperationsOfNumbers`

Support policy:
- `core/skill_policies/fraction.py`

## Phase-1 Scope

Covered:
- textbook-style simplify / compare / fill blank / reciprocal
- signed fraction add/sub/mul/div
- mixed numbers
- decimal-fraction exact arithmetic
- telescoping products
- listed non-image word problems

Excluded in phase 1:
- image-dependent shaded geometry
- OCR cases where the diagram contains unlabeled region partition information not present in text

=== SKILL_END_PROMPT ===
