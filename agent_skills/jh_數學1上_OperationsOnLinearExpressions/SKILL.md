# jh_\u6578\u5b781\u4e0a_OperationsOnLinearExpressions

本 skill 依教材題型分群，提供 L1~L7 家族出題。

## Family Mapping
- L1 `linear_flat_mul_div`：單項乘除轉寫（A 類）
- L2 `linear_combine_like_terms`：同類項合併（B 類）
- L3 `linear_flat_simplify_with_constants`：常數與同類項平面化簡（C 類）
- L4 `linear_outer_minus_scope`：括號前負號整包變號（D 類）
- L5 `linear_monomial_distribution`：單項分配到括號（E 類）
- L6 `linear_nested_simplify`：多括號綜合化簡（F 類）
- L7 `linear_fraction_expression_simplify`：分式代數式化簡（G 類）

## Subskills
- coefficient_sign_handling
- like_term_combination
- term_collection_with_constants
- outer_minus_scope
- monomial_distribution
- nested_bracket_scope
- structure_isomorphism
- fractional_expression_simplification

## Runtime Contract
- `generate(level=1, **kwargs)`
- `check(user_answer, correct_answer)`
- payload 至少含：`question_text`, `answer`, `correct_answer`, `family_id`, `subskill_nodes`
