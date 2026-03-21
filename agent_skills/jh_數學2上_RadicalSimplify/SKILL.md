【角色】Edge AI — 根式化簡（單一題型 p0）

════════════════════════════════════════════════════════════════
【工程約束】同 FourOperationsOfRadicals，嚴禁 sympy，使用 RadicalOps。
════════════════════════════════════════════════════════════════

**Pattern**: p0_simplify — √r 單一根式化簡（例：√72 → 6√2）

**vars**: `{"r": int}`

**API**: DomainFunctionHelper.get_safe_vars_for_pattern("p0_simplify", difficulty)
       DomainFunctionHelper.solve_problem_pattern("p0_simplify", vars, difficulty)
       DomainFunctionHelper.format_question_LaTeX("p0_simplify", vars)

=== SKILL_END_PROMPT ===
