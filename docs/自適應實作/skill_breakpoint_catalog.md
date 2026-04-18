# Skill Breakpoint Catalog

這份表把四個核心技能整理成可直接用於「學生學習斷點」標記的 family / 子技能清單。

對應技能：
- `jh_數學1上_FourArithmeticOperationsOfIntegers`
- `jh_數學1上_FourArithmeticOperationsOfNumbers`
- `jh_數學2上_FourArithmeticOperationsOfPolynomial`
- `jh_數學2上_FourOperationsOfRadicals`

對應 CSV：
- [skill_breakpoint_catalog.csv](/E:/Python/MathProject_AST_Research/docs/skill_breakpoint_catalog.csv)

## Integers

來源：[SKILL.md](/E:/Python/MathProject_AST_Research/agent_skills/jh_數學1上_FourArithmeticOperationsOfIntegers/SKILL.md)

全域子技能節點：
- `node.int.sign_handling`
- `node.int.add_sub`
- `node.int.mul_div`
- `node.int.order_of_operations`
- `node.int.bracket_scope`
- `node.int.absolute_value`
- `node.int.exact_divisibility`
- `node.int.isomorphic_structure`

| Family ID | Family Name | 建議中文標籤 | 主要子技能節點 |
| --- | --- | --- | --- |
| `I1` | `int_numberline_add_sub` | 數線型整數加減 | `sign_handling`, `add_sub` |
| `I2` | `int_flat_add_sub` | 平面整數加減 | `sign_handling`, `add_sub` |
| `I3` | `int_flat_mul_div_exact` | 平面整數乘除 | `sign_handling`, `mul_div`, `exact_divisibility` |
| `I4` | `int_flat_mixed_four_ops` | 整數四則混合 | `sign_handling`, `add_sub`, `mul_div`, `order_of_operations` |
| `I5` | `int_bracket_mixed` | 括號整數四則 | `sign_handling`, `bracket_scope`, `order_of_operations` |
| `I6` | `int_abs_value` | 絕對值整數四則 | `sign_handling`, `absolute_value` |
| `I7` | `int_division_exact_nested` | 巢狀整除結構 | `sign_handling`, `mul_div`, `bracket_scope`, `absolute_value`, `exact_divisibility` |
| `I8` | `int_composite_structure` | 綜合結構題 | `sign_handling`, `add_sub`, `mul_div`, `order_of_operations`, `bracket_scope`, `absolute_value`, `exact_divisibility`, `isomorphic_structure` |

## Fractions

來源：[SKILL.md](/E:/Python/MathProject_AST_Research/agent_skills/jh_數學1上_FourArithmeticOperationsOfNumbers/SKILL.md)

全域子技能節點：
- `proper_improper_fraction`
- `mixed_numbers`
- `sign_normalization`
- `decimal_to_fraction_exact_conversion`
- `simplest_form_reduction`
- `equivalent_fraction_scaling`
- `reciprocal_transform`
- `preserve_value_invariance`
- `positive_fraction_comparison`
- `negative_fraction_comparison`
- `mixed_number_comparison`
- `add_sub`
- `multiply`
- `divide`
- `nested_parentheses`
- `decimal_fraction_mixed_arithmetic`
- `telescoping_products`
- `remaining_amount`
- `container_weight`
- `before_after_ratio`
- `share_comparison`

| Family ID | Family Name | 建議中文標籤 | 主要子技能節點 |
| --- | --- | --- | --- |
| `F1` | `Fraction Simplification` | 分數化簡 | `proper_improper_fraction`, `mixed_numbers`, `sign_normalization`, `simplest_form_reduction` |
| `F2` | `Equivalent Fraction Fill-Blank` | 等值分數填空 | `equivalent_fraction_scaling`, `sign_normalization` |
| `F3` | `Preserve-Value Fraction Invariance` | 分數值不變 | `preserve_value_invariance`, `equivalent_fraction_scaling` |
| `F4` | `Fraction Comparison` | 分數比較 | `positive_fraction_comparison`, `negative_fraction_comparison`, `mixed_number_comparison` |
| `F5` | `Fraction Add/Subtract` | 分數加減 | `add_sub`, `nested_parentheses`, `mixed_numbers` |
| `F6` | `Fraction Multiply` | 分數乘法 | `multiply`, `mixed_numbers`, `telescoping_products` |
| `F7` | `Fraction Divide` | 分數除法 | `divide`, `mixed_numbers`, `decimal_fraction_mixed_arithmetic` |
| `F8` | `Reciprocal` | 倒數 | `reciprocal_transform` |
| `F9` | `Decimal-Fraction Mixed Evaluation` | 分數小數混合四則 | `decimal_to_fraction_exact_conversion`, `add_sub`, `multiply`, `divide`, `nested_parentheses` |
| `F10` | `Fraction Word Problems` | 分數應用題 | `remaining_amount`, `container_weight`, `before_after_ratio`, `share_comparison` |

`F10` 代表子題型：
- 無人機剩餘藥量
- 果汁瓶與空瓶重量
- 牛奶剩餘量
- 遺產分配比較
- 圖書館前後冊數

## Polynomials

來源：[SKILL.md](/E:/Python/MathProject_AST_Research/agent_skills/jh_數學2上_FourArithmeticOperationsOfPolynomial/SKILL.md)

全域子技能節點：
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

| Family ID | Family Name | 建議中文標籤 | 主要子技能節點 |
| --- | --- | --- | --- |
| `F1` | `poly_add_sub_flat` | 平面多項式加減 | `normalize_terms`, `combine_like_terms` |
| `F2` | `poly_add_sub_nested` | 巢狀多項式加減 | `sign_distribution`, `combine_like_terms`, `family_isomorphism` |
| `F3` | `poly_add_sub_unknown` | 未知多項式求解 | `sign_distribution`, `unknown_target_preservation` |
| `F4` | `poly_mul_monomial` | 單項式乘法 | `expand_monomial` |
| `F5` | `poly_mul_poly` | 多項式乘法展開 | `expand_binomial`, `combine_like_terms` |
| `F6` | `poly_mul_special_identity` | 乘法公式 | `special_identity` |
| `F7` | `poly_div_monomial_eval` | 單項式除法直接化簡 | `normalize_terms` |
| `F8` | `poly_div_monomial_qr` | 單項式除法商餘 | `long_division`, `quotient_remainder_format` |
| `F9` | `poly_div_poly_qr` | 多項式長除法 | `long_division`, `quotient_remainder_format` |
| `F10` | `poly_div_reverse` | 反推除法 | `reverse_division_reconstruction` |
| `F11` | `poly_mixed_simplify` | 綜合化簡 | `expand_binomial`, `special_identity`, `combine_like_terms`, `family_isomorphism` |
| `F12` | `poly_geom_formula_direct` | 幾何公式應用 | `geometry_formula` |
| `F13` | `poly_geom_region_composite` | 複合圖形應用 | `geometry_formula`, `composite_region_modeling` |

## Radicals

來源：[SKILL.md](/E:/Python/MathProject_AST_Research/agent_skills/jh_數學2上_FourOperationsOfRadicals/SKILL.md)

全域子技能節點：
- `node.rad.simplify`
- `node.rad.combine_like_terms`
- `node.rad.multiply_terms`
- `node.rad.divide_terms`
- `node.rad.distribute`
- `node.rad.binomial_expand`
- `node.rad.conjugate_rationalize`
- `node.rad.fractional_radical`
- `node.rad.mixed_number_radical`
- `node.rad.bracket_scope`
- `node.rad.structure_isomorphism`

| Pattern ID | Pattern Name | 建議中文標籤 | 主要子技能節點 |
| --- | --- | --- | --- |
| `p0` | `p0_simplify` | 單根式化簡 | `simplify` |
| `p1` | `p1_add_sub` | 純根式加減 | `combine_like_terms` |
| `p1b` | `p1b_add_sub_bracket` | 括號根式加減 | `combine_like_terms`, `bracket_scope` |
| `p1c` | `p1c_mixed_frac_rad_add_sub` | 分數根式加減 | `combine_like_terms`, `fractional_radical` |
| `p2a` | `p2a_mult_direct` | 根式直接相乘 | `multiply_terms` |
| `p2b` | `p2b_mult_distrib` | 根式分配律乘法 | `multiply_terms`, `distribute` |
| `p2c` | `p2c_mult_binomial` | 根式雙括號展開 | `multiply_terms`, `distribute`, `binomial_expand` |
| `p2d` | `p2d_perfect_square` | 根式完全平方 | `multiply_terms`, `binomial_expand` |
| `p2e` | `p2e_diff_of_squares` | 根式平方差 | `multiply_terms`, `binomial_expand` |
| `p2f` | `p2f_int_mult_rad` | 整數乘根式 | `multiply_terms` |
| `p2g` | `p2g_rad_mult_frac` | 根式乘分數 | `multiply_terms`, `fractional_radical` |
| `p2h` | `p2h_frac_mult_rad` | 分數乘根式 | `multiply_terms`, `fractional_radical` |
| `p3a` | `p3a_div_expr` | 表達式除以根式 | `divide_terms`, `bracket_scope` |
| `p3b` | `p3b_div_simple` | `a/√b` 有理化 | `divide_terms`, `conjugate_rationalize` |
| `p3c` | `p3c_div_direct` | 根式直接相除 | `divide_terms` |
| `p4` | `p4_frac_mult` | 分式根式乘法 | `fractional_radical`, `structure_isomorphism` |
| `p4b` | `p4b_frac_rad_div` | 根式分式相除 | `divide_terms`, `conjugate_rationalize` |
| `p4c` | `p4c_nested_frac_chain` | 根號內分數連算 | `fractional_radical`, `structure_isomorphism` |
| `p4d` | `p4d_frac_rad_div_mixed` | 混合根式分式除法 | `divide_terms`, `conjugate_rationalize`, `fractional_radical` |
| `p5a` | `p5a_conjugate_int` | 整數分子共軛有理化 | `divide_terms`, `conjugate_rationalize` |
| `p5b` | `p5b_conjugate_rad` | 根式分子共軛有理化 | `divide_terms`, `conjugate_rationalize` |
| `p6` | `p6_combo` | 多步驟綜合題 | `simplify`, `combine_like_terms`, `multiply_terms`, `divide_terms`, `structure_isomorphism` |
| `p7` | `p7_mixed_rad_add` | 帶分數根式加減 | `mixed_number_radical`, `combine_like_terms` |

## 使用建議

如果你要把它接到學生診斷，我建議最少分兩層：
- `family_id / pattern_id`：用來判斷學生卡在哪一類題型
- `subskill_nodes`：用來判斷學生真正卡在哪個能力點

例如：
- 同樣都是分數題，學生可能不是卡在 `F5`，而是卡在 `mixed_numbers`
- 同樣都是多項式題，學生可能不是卡在 `F9`，而是卡在 `long_division`
- 同樣都是根式題，學生可能不是卡在 `p5b`，而是卡在 `conjugate_rationalize`
