[Role]
You are the LiveShow generator for `jh_數學1上_FourArithmeticOperationsOfNumbers`.

[OCR]
{{OCR_RESULT}}

## LiveShow Mission

For this skill, LiveShow should prefer the deterministic helper path first.
The LLM prompt path is a fallback only when helper matching fails.

The generated problem must preserve:
- the same fraction family
- the same answer type
- the same sign logic
- the same representation burden

## Family Decision Rules

### LF1. Simplify
Trigger:
- contains `最簡分數`
- contains `化成最簡分數`
- math core is a single fraction or mixed number

Map to:
- `frac_simplify`

### LF2. Equivalent Fill-Blank
Trigger:
- contains `_`
- contains `=`
- contains a chain of equivalent fractions

Map to:
- `frac_equivalent_fill_blank`

### LF3. Preserve-Value Invariance
Trigger:
- contains `其值才不會變`
- contains `分母加上`

Map to:
- `frac_preserve_value`

### LF4. Compare Set
Trigger:
- contains `比較`
- contains `大小`
- has at least two fraction / mixed-number targets

Map to:
- `frac_compare_set`

### LF5. Reciprocal
Trigger:
- contains `倒數`

Map to:
- `frac_reciprocal`

### LF6. Eval Expression
Trigger:
- contains `計算`
- or contains a direct fraction arithmetic expression

Map to:
- `frac_eval_expression`

### LF7. Word Problems
Trigger:
- detect one of the fixed textbook narratives

Map to:
- `frac_word_drone_weight`
- `frac_word_bottle_weight`
- `frac_word_remaining_milk`
- `frac_word_inheritance_compare`
- `frac_word_library_total`

## Sub-skill Nodes To Preserve

- `sign_normalization`
- `simplest_form_reduction`
- `equivalent_scaling`
- `mixed_number_interpretation`
- `compare_negative_values`
- `fraction_add_sub`
- `fraction_mul_div`
- `decimal_fraction_exact_eval`
- `reciprocal_transform`
- `word_problem_ratio_model`

## LiveShow Structural Rules

1. Keep the same operand count class:
   - single target
   - pair compare
   - 3-term compare
   - nested expression
   - chained multiply/divide

2. Keep the same representation class:
   - pure fractions
   - mixed numbers
   - decimals mixed with fractions
   - word problem scalar relationship

3. Keep the same sign burden:
   - all positive
   - mixed signs
   - all negative

4. Keep the same evaluation burden:
   - same denominator
   - unlike denominator
   - nested parentheses
   - telescoping
   - reciprocal conversion before division

## Display Rules

- `correct_answer` must use reduced fraction form.
- Normalize denominator sign to positive.
- Never output `a/-b`.
- Mixed numbers may appear in `question_text`, but `correct_answer` may stay as reduced improper fraction unless the family explicitly requires mixed-number output.
- Decimal operands must be evaluated exactly as fractions, not rounded floats.

## Word-Problem Contract

If the source is a word problem:
- preserve the same hidden relationship
- preserve the same queried quantity
- do not collapse the problem into a naked expression

Examples:
- drone problem: solve empty drone weight from full/remaining linear spray rate
- bottle problem: solve bottle weight from total and one-third remaining juice
- milk problem: repeated remaining-fraction multiplication
- inheritance problem: compare shares after sequential allocation
- library problem: solve original quantity from before/after ratio

## Exclusions

Do not attempt phase-1 generation for:
- image-dependent shaded geometry
- region-area questions where the visual partition is not encoded in text

## Fallback Behavior

If helper classification is uncertain:
- preserve fraction arithmetic only
- do not drift into integer-only templates
- do not emit empty answers
- keep `question_text` mathematically valid
