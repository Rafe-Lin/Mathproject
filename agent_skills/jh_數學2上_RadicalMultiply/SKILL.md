【角色】Edge AI — 根式相乘（單一題型 p2a）

════════════════════════════════════════════════════════════════
【工程約束】同 FourOperationsOfRadicals，嚴禁 sympy，使用 RadicalOps。
════════════════════════════════════════════════════════════════

**Pattern**: p2a_mult_direct — k₁√r₁×k₂√r₂ 兩根式相乘（例：2√8×3√45）

**vars**: `{"c1", "r1", "c2", "r2"}` 皆 int

**API**: DomainFunctionHelper.get_safe_vars_for_pattern("p2a_mult_direct", difficulty)
       DomainFunctionHelper.solve_problem_pattern("p2a_mult_direct", vars, difficulty)
       DomainFunctionHelper.format_question_LaTeX("p2a_mult_direct", vars)

=== SKILL_END_PROMPT ===
