【角色】Edge AI — 根式加減（單一題型 p1）

════════════════════════════════════════════════════════════════
【工程約束】同 FourOperationsOfRadicals，嚴禁 sympy，使用 RadicalOps。
════════════════════════════════════════════════════════════════

**Pattern**: p1_add_sub — k₁√r₁±k₂√r₂ 純根式加減（例：2√12−√27）

**vars**: `{"terms": [(coeff, radicand, op), ...]}` op ∈ {"+", "-"}

**API**: DomainFunctionHelper.get_safe_vars_for_pattern("p1_add_sub", difficulty)
       DomainFunctionHelper.solve_problem_pattern("p1_add_sub", vars, difficulty)
       DomainFunctionHelper.format_question_LaTeX("p1_add_sub", vars)

=== SKILL_END_PROMPT ===
