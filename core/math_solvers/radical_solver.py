# -*- coding: utf-8 -*-
"""
=============================================================================
Module: core/math_solvers/radical_solver.py
Description:
    RadicalSolver — The Radical Math Engine for jh_數學2上_FourOperationsOfRadicals.

    Implements 100% reliable, symbolically exact solutions for all radical
    operation patterns defined in SKILL.md. All arithmetic uses integer and
    Fraction types; floating-point comparison is strictly prohibited.

    Designed for the "Edge AI Orchestrator" architecture: the local model
    (Qwen3) delegates ALL mathematical computation to this engine and only
    handles pattern recognition and question-text formatting.

Version: 1.0.0
Maintainer: Math AI Project Team
=============================================================================
"""

import math
from fractions import Fraction
from typing import Dict, List, Tuple, Union

# ---------------------------------------------------------------------------
# Type aliases
# ---------------------------------------------------------------------------
RadObj = Tuple[int, int]        # (coefficient, radicand) — both pure integers
TermsDict = Dict[int, int]      # {radicand: coefficient}
StepList = List[str]            # ordered list of LaTeX step strings


# ===========================================================================
# Low-level symbolic helpers (all integer arithmetic, no floats)
# ===========================================================================

def _prime_factors(n: int) -> Dict[int, int]:
    """Return the prime factorisation of |n| as {prime: exponent}."""
    n = abs(int(n))
    factors: Dict[int, int] = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors


def _simplify_rad(coeff: int, radicand: int) -> RadObj:
    """
    Symbolically simplify c·√r → (new_c, new_r) using integer arithmetic.

    Algorithm: extract all pairs of prime factors from radicand.
    Example: simplify_rad(2, 18) → 2·√18 = 2·√(9·2) = 2·3·√2 = (6, 2)
    """
    if radicand == 0:
        return (0, 0)
    if radicand == 1:
        return (coeff, 1)
    factors = _prime_factors(radicand)
    out_factor = 1
    new_radicand = 1
    for p, exp in factors.items():
        out_factor *= p ** (exp // 2)
        new_radicand *= p ** (exp % 2)
    return (coeff * out_factor, new_radicand)


def _merge_terms(terms: TermsDict) -> TermsDict:
    """Remove zero-coefficient entries and return a clean TermsDict."""
    return {r: c for r, c in terms.items() if c != 0}


def _add_term_dicts(t1: TermsDict, t2: TermsDict) -> TermsDict:
    merged = dict(t1)
    for r, c in t2.items():
        merged[r] = merged.get(r, 0) + c
    return _merge_terms(merged)


def _multiply_term_dicts(t1: TermsDict, t2: TermsDict) -> TermsDict:
    """Expand the product of two radical expressions, simplifying each term."""
    result: TermsDict = {}
    for r1, c1 in t1.items():
        for r2, c2 in t2.items():
            if c1 == 0 or c2 == 0:
                continue
            new_c, new_r = _simplify_rad(c1 * c2, r1 * r2)
            result[new_r] = result.get(new_r, 0) + new_c
    return _merge_terms(result)


def _format_term(coeff: int, radicand: int, is_first: bool = True) -> str:
    """Format a single radical term as LaTeX (simplified form)."""
    if coeff == 0:
        return ""
    c_val, r_val = _simplify_rad(coeff, radicand)
    if c_val == 0:
        return ""

    # Sign handling
    sign = ""
    if not is_first:
        sign = " + " if c_val > 0 else " - "
    elif c_val < 0:
        sign = "-"

    abs_c = abs(c_val)

    if r_val == 1:
        return f"{sign}{abs_c}"

    c_str = "" if abs_c == 1 else str(abs_c)
    return f"{sign}{c_str}\\sqrt{{{r_val}}}"


def _format_term_unsimplified(coeff: int, radicand: int, is_first: bool = True) -> str:
    """Format a single radical term without simplification (for question display)."""
    if coeff == 0:
        return ""
    sign = ""
    if not is_first:
        sign = " + " if coeff > 0 else " - "
    elif coeff < 0:
        sign = "-"
    abs_c = abs(coeff)
    c_str = "" if abs_c == 1 else str(abs_c)
    return f"{sign}{c_str}\\sqrt{{{radicand}}}"


def _format_expression(terms: TermsDict, denominator: int = 1) -> str:
    """
    Format a full radical expression from a TermsDict as LaTeX.

    Handles:
    - Integer terms (radicand == 1)
    - GCD reduction with denominator
    - Negative denominator normalisation (flip signs, use positive denom)
    - Ordering: integer first, then by radicand ascending
    """
    if not terms:
        return "0"

    # Normalise negative denominator: flip all coefficient signs
    if denominator < 0:
        denominator = -denominator
        terms = {r: -c for r, c in terms.items()}

    # Reduce GCD with denominator
    if denominator != 1:
        all_coeffs = list(terms.values())
        common = abs(denominator)
        for c in all_coeffs:
            common = math.gcd(common, abs(int(c)))
        if common > 1:
            denominator //= common
            terms = {r: c // common for r, c in terms.items()}

    sorted_rads = sorted(terms.keys())
    if 1 in sorted_rads:
        sorted_rads.remove(1)
        sorted_rads.insert(0, 1)

    parts = []
    is_first = True
    for r in sorted_rads:
        c = terms[r]
        if c == 0:
            continue
        part = _format_term(c, r, is_first)
        if part:
            parts.append(part)
            is_first = False

    if not parts:
        return "0"

    expr = "".join(parts).lstrip()
    if denominator != 1:
        return rf"\frac{{{expr}}}{{{denominator}}}"
    return expr


# ===========================================================================
# RadicalSolver — Public Engine API
# ===========================================================================

class RadicalSolver:
    """
    Symbolic radical expression solver for jh_數學2上_FourOperationsOfRadicals.

    All methods operate on integer/Fraction arithmetic.
    Floating-point numbers are strictly prohibited in all computations.

    Usage (via DomainFunctionHelper):
        solver = RadicalSolver()
        latex_ans, steps = solver.solve_problem_pattern("p1_add_sub", vars_dict, "mid")
    """

    # -----------------------------------------------------------------------
    # Primitive solver: single radical simplification
    # -----------------------------------------------------------------------

    def simplify_single_radical(
        self, int_radicand: int
    ) -> Tuple[str, RadObj, StepList]:
        """
        Simplify sqrt(int_radicand) symbolically.

        Returns:
            latex_str  -- simplified LaTeX, e.g. "3\\sqrt{2}"
            rad_obj    -- (coefficient, simplified_radicand) as ints
            steps      -- ordered list of LaTeX step strings
        """
        r = int(int_radicand)
        coeff, simplified_r = _simplify_rad(1, r)
        latex_str = _format_term(coeff, simplified_r, is_first=True)

        steps: StepList = []

        if simplified_r == r:
            steps.append(rf"\sqrt{{{r}}} \text{{ 已為最簡根式}}")
        else:
            factors = _prime_factors(r)
            factor_str = " \\cdot ".join(
                f"{p}^{{{e}}}" if e > 1 else str(p)
                for p, e in sorted(factors.items())
            )
            steps.append(rf"\text{{Step 1: 質因數分解}} \quad \sqrt{{{r}}} = \sqrt{{{factor_str}}}")
            steps.append(rf"\text{{Step 2: 提出完全平方因子}} \quad = {latex_str}")

        return latex_str, (coeff, simplified_r), steps

    # -----------------------------------------------------------------------
    # Primitive solver: addition / subtraction
    # -----------------------------------------------------------------------

    def solve_add_subtract(
        self, rad1: RadObj, rad2: RadObj, op_str: str
    ) -> Tuple[str, StepList]:
        """
        Compute rad1 OP rad2 where OP ∈ {'+', '-'}.

        rad1, rad2 are (coefficient, radicand) pairs, e.g. (3, 12) = 3√12.

        Returns:
            latex_ans — simplified LaTeX answer
            steps     — ordered list of LaTeX step strings
        """
        c1, r1 = rad1
        c2, r2 = rad2
        if op_str == "-":
            c2 = -c2

        steps: StepList = []

        # Step 1: simplify each term
        sc1, sr1 = _simplify_rad(c1, r1)
        sc2, sr2 = _simplify_rad(c2, r2)

        q1_latex = _format_term_unsimplified(abs(c1) if c1 > 0 else -abs(c1), r1, is_first=True)
        q2_raw = _format_term_unsimplified(abs(rad2[1]) if rad2[0] > 0 else -abs(rad2[0]), r2, is_first=False)

        s1_latex = _format_term(sc1, sr1, is_first=True)
        s2_latex = _format_term(sc2, sr2, is_first=True)

        steps.append(
            rf"\text{{Step 1: 化簡各項}} \quad "
            rf"{_format_term_unsimplified(c1, r1, True)} = {_format_term(sc1, sr1, True)}, \quad "
            rf"{_format_term_unsimplified(rad2[0], r2, True)} = {_format_term(abs(sc2), sr2, True)}"
        )

        # Step 2: combine like terms
        merged = _add_term_dicts({sr1: sc1}, {sr2: sc2})
        latex_ans = _format_expression(merged)

        if sr1 == sr2:
            total_c = sc1 + sc2
            steps.append(
                rf"\text{{Step 2: 合併同類根式}} \quad "
                rf"({sc1} {'+' if sc2 >= 0 else ''}{sc2})\sqrt{{{sr1}}} = {latex_ans}"
            )
        else:
            steps.append(
                rf"\text{{Step 2: 根號不同類，保持分離}} \quad "
                rf"{_format_term(sc1, sr1, True)}{_format_term(sc2, sr2, False)} = {latex_ans}"
            )

        return latex_ans, steps

    # -----------------------------------------------------------------------
    # Primitive solver: multiplication
    # -----------------------------------------------------------------------

    def solve_multiply(
        self, rad1: RadObj, rad2: RadObj
    ) -> Tuple[str, StepList]:
        """
        Compute (c1√r1) · (c2√r2).

        Returns:
            latex_ans — simplified LaTeX answer
            steps     — ordered list of LaTeX step strings
        """
        c1, r1 = rad1
        c2, r2 = rad2
        steps: StepList = []

        # Intermediate product before simplification
        prod_c = c1 * c2
        prod_r = r1 * r2

        new_c, new_r = _simplify_rad(prod_c, prod_r)
        latex_ans = _format_expression({new_r: new_c})

        q1 = _format_term_unsimplified(c1, r1, True)
        q2 = _format_term_unsimplified(c2, r2, True)

        steps.append(
            rf"\text{{Step 1: 合併係數與根號}} \quad "
            rf"{q1} \times {q2} = {prod_c}\sqrt{{{prod_r}}}"
        )

        if new_r != prod_r or new_c != prod_c:
            steps.append(
                rf"\text{{Step 2: 化簡根式}} \quad "
                rf"{prod_c}\sqrt{{{prod_r}}} = {latex_ans}"
            )
        else:
            steps.append(rf"\text{{Step 2: 已為最簡}} \quad = {latex_ans}")

        return latex_ans, steps

    # -----------------------------------------------------------------------
    # Primitive solver: rationalize denominator  a·√m / √d
    # -----------------------------------------------------------------------

    def rationalize_denominator(
        self,
        numerator_coeff: int,
        numerator_radicand: int,
        denominator_radicand: int,
    ) -> Tuple[str, StepList]:
        """
        Rationalize: (numerator_coeff · √numerator_radicand) / √denominator_radicand.

        Two cases:
          Case 1: numerator_radicand % denominator_radicand == 0
                  → Direct simplification: c·√(m/d)
          Case 2: otherwise
                  → Multiply numerator & denominator by √d:
                    = c·√(m·d) / d  (coefficient must divide d exactly)

        Returns:
            latex_ans — simplified LaTeX answer
            steps     — ordered list of LaTeX step strings

        Raises:
            ValueError if the rationalization does not yield integer coefficients.
        """
        c = numerator_coeff
        m = numerator_radicand
        d = denominator_radicand
        steps: StepList = []

        q_latex = rf"\frac{{{_format_term_unsimplified(c, m, True)}}}{{\sqrt{{{d}}}}}"

        if m % d == 0:
            # Case 1: numerator radicand divisible by denominator radicand
            # c·√m / √d = c·√(m/d)
            nc, nr = _simplify_rad(c, m // d)
            latex_ans = _format_expression({nr: nc})
            steps.append(
                rf"\text{{Step 1: 直接整除}} \quad {q_latex} = "
                rf"{_format_term_unsimplified(c, m // d, True)}"
            )
            steps.append(
                rf"\text{{Step 2: 化簡}} \quad = {latex_ans}"
            )
        else:
            # Case 2: rationalize by multiplying numerator and denominator by √d
            # c·√m / √d × (√d/√d) = c·√(m·d) / d
            # Result may be a fraction \frac{k√r}{n} — use format_expression with denominator
            nc_raw, nr = _simplify_rad(c, m * d)
            # Use format_expression with denominator; GCD reduction is handled inside
            latex_ans = _format_expression({nr: nc_raw}, denominator=d)
            rationalized_num = _format_term_unsimplified(c, m * d, True)
            simplified_num = _format_term(nc_raw, nr, True)
            steps.append(
                rf"\text{{Step 1: 分子分母同乘 }}\sqrt{{{d}}} \quad "
                rf"{q_latex} = \frac{{{rationalized_num}}}{{{d}}}"
            )
            steps.append(
                rf"\text{{Step 2: 化簡根式}} \quad "
                rf"= \frac{{{simplified_num}}}{{{d}}}"
            )
            if latex_ans != rf"\frac{{{simplified_num}}}{{{d}}}":
                steps.append(
                    rf"\text{{Step 3: 約分}} \quad = {latex_ans}"
                )

        return latex_ans, steps

    # -----------------------------------------------------------------------
    # Primitive solver: conjugate rationalization  num / (b√q ± c)
    # -----------------------------------------------------------------------

    def rationalize_conjugate(
        self,
        numerator_terms: TermsDict,
        b: int,
        q: int,
        c: int,
        sign: int,
    ) -> Tuple[str, StepList]:
        """
        Rationalize expression / (b√q + sign·c) using conjugate multiplication.

        numerator_terms: TermsDict representing the numerator expression.
        b, q, c, sign: define denominator = b√q + sign·c (sign ∈ {+1, -1}).

        Conjugate: (b√q - sign·c)
        New denominator: (b√q)² - (sign·c)² = b²q - c² (must ≠ 0)

        Returns:
            latex_ans — simplified LaTeX answer
            steps     — ordered list of LaTeX step strings

        Raises:
            ValueError if new denominator == 0.
        """
        new_denom = b * b * q - c * c
        if new_denom == 0:
            raise ValueError(
                f"Conjugate denominator is zero: b={b}, q={q}, c={c}. Cannot rationalize."
            )

        steps: StepList = []
        sign_str = "+" if sign == 1 else "-"
        b_str = "" if b == 1 else str(b)
        denom_latex = rf"{b_str}\sqrt{{{q}}}{sign_str}{c}"

        # Conjugate terms: (b√q, -sign·c)
        conjugate_terms: TermsDict = {q: b, 1: -sign * c}

        # Expand numerator × conjugate
        expanded = _multiply_term_dicts(numerator_terms, conjugate_terms)

        steps.append(
            rf"\text{{Step 1: 分子分母乘以共軛式 }} ({b_str}\sqrt{{{q}}}{'-' if sign==1 else '+'}{c})"
        )
        steps.append(
            rf"\text{{Step 2: 新分母}} = ({b_str}\sqrt{{{q}}})^2 - ({c})^2 = {b*b*q} - {c*c} = {new_denom}"
        )

        expanded_latex = _format_expression(expanded)
        steps.append(
            rf"\text{{Step 3: 展開分子}} = {expanded_latex}"
        )

        latex_ans = _format_expression(expanded, denominator=new_denom)
        steps.append(
            rf"\text{{Step 4: 最終化簡}} \quad \frac{{{expanded_latex}}}{{{new_denom}}} = {latex_ans}"
        )

        return latex_ans, steps

    # -----------------------------------------------------------------------
    # High-level dispatcher: solve_problem_pattern
    # -----------------------------------------------------------------------

    def solve_problem_pattern(
        self,
        pattern_id: str,
        variables: dict,
        difficulty: str = "mid",
    ) -> Tuple[str, StepList]:
        """
        High-level coordinator. Given a pattern_id and a variables dict
        (as returned by DomainFunctionHelper.get_safe_vars_for_pattern),
        dispatch to the appropriate sub-solver(s) and return:
            (latex_answer: str, solution_steps: List[str])

        Supported pattern_ids (from SKILL.md Pattern Catalogue):
            p0_simplify, p1_add_sub,
            p2a_mult_direct, p2b_mult_distrib, p2c_mult_binomial,
            p3a_div_expr, p3b_div_simple,
            p4_frac_mult,
            p5a_conjugate_int, p5b_conjugate_rad,
            p6_combo

        All computation is exact (integer arithmetic). No floats used.
        """
        pid = pattern_id.lower().strip()
        dispatch = {
            "p0_simplify":         self._solve_p0,
            "p1_add_sub":          self._solve_p1,
            "p2a_mult_direct":     self._solve_p2a,
            "p2b_mult_distrib":    self._solve_p2b,
            "p2c_mult_binomial":   self._solve_p2c,
            "p2f_int_mult_rad":    self._solve_p2f,
            "p2g_rad_mult_frac":   self._solve_p2gh,
            "p2h_frac_mult_rad":   self._solve_p2gh,
            "p2d_perfect_square":  self._solve_p2d,
            "p2e_diff_of_squares": self._solve_p2e,
            "p3a_div_expr":        self._solve_p3a,
            "p3c_div_direct":      self._solve_p3c,
            "p3b_div_simple":      self._solve_p3b,
            "p4_frac_mult":        self._solve_p4,
            "p4b_frac_rad_div":    self._solve_p4b,
            "p4c_nested_frac_chain": self._solve_p4c,
            "p5a_conjugate_int":   self._solve_p5a,
            "p5b_conjugate_rad":   self._solve_p5b,
            "p6_combo":            self._solve_p6,
            "p7_mixed_rad_add":   self._solve_p7_mixed_rad_add,
        }
        if pid not in dispatch:
            raise ValueError(
                f"Unknown pattern_id '{pattern_id}'. "
                f"Valid IDs: {list(dispatch.keys())}"
            )
        return dispatch[pid](variables, difficulty)

    # -----------------------------------------------------------------------
    # Pattern implementations
    # -----------------------------------------------------------------------

    def _solve_p0(self, v: dict, difficulty: str) -> Tuple[str, StepList]:
        """P0: Simplify √r."""
        r = int(v["r"])
        latex_ans, _, steps = self.simplify_single_radical(r)
        return latex_ans, steps

    def _solve_p1(self, v: dict, difficulty: str) -> Tuple[str, StepList]:
        """P1: Add/subtract multiple radical terms k₁√r₁ ± k₂√r₂ [± ...]."""
        terms_raw: List[Tuple[int, int, str]] = v["terms"]
        steps: StepList = []

        simplified: TermsDict = {}
        simplify_details = []

        for i, (coeff, radicand, op) in enumerate(terms_raw):
            actual_coeff = coeff if op == "+" else -coeff
            sc, sr = _simplify_rad(actual_coeff, radicand)
            simplified[sr] = simplified.get(sr, 0) + sc
            q_str = _format_term_unsimplified(coeff, radicand, True)
            s_str = _format_term(actual_coeff, radicand, True)
            simplify_details.append(f"{q_str} = {s_str}")

        simplified = _merge_terms(simplified)

        steps.append(
            rf"\text{{Step 1: 逐項化簡}} \quad "
            + r", \quad ".join(simplify_details)
        )
        steps.append(
            rf"\text{{Step 2: 合併同類根式}} \quad "
            rf"\Rightarrow {_format_expression(simplified)}"
        )

        latex_ans = _format_expression(simplified)
        return latex_ans, steps

    def _solve_p2a(self, v: dict, difficulty: str) -> Tuple[str, StepList]:
        """P2a: Direct multiplication c1√r1 · c2√r2."""
        return self.solve_multiply(
            (v["c1"], v["r1"]),
            (v["c2"], v["r2"]),
        )

    def _solve_p2f(self, v: dict, difficulty: str) -> Tuple[str, StepList]:
        """P2f: Integer × radical c1 × c2√r. Multiply coefficients, radicand stays."""
        c1 = v["c1"]
        c2 = v["c2"]
        r = v["r"]
        ans_c = c1 * c2

        if ans_c == 1:
            ans_latex = f"\\sqrt{{{r}}}"
        elif ans_c == -1:
            ans_latex = f"-\\sqrt{{{r}}}"
        elif ans_c == 0:
            ans_latex = "0"
        else:
            ans_latex = f"{ans_c}\\sqrt{{{r}}}"

        steps = [r"將外部整數與根式係數直接相乘：c_1 \times c_2"]
        return ans_latex, steps

    def _solve_p2gh(self, v: dict, difficulty: str) -> Tuple[str, StepList]:
        """P2g/P2h: k√r × (num/den) or (num/den) × k√r. Result: (k*num/den)√r."""
        import math
        k, r, num, den = v["k"], v["r"], v["num"], v["den"]

        top = k * num
        bottom = den
        g = math.gcd(abs(top), bottom)
        top //= g
        bottom //= g

        if bottom == 1:
            if top == 1:
                ans_latex = f"\\sqrt{{{r}}}"
            elif top == -1:
                ans_latex = f"-\\sqrt{{{r}}}"
            elif top == 0:
                ans_latex = "0"
            else:
                ans_latex = f"{top}\\sqrt{{{r}}}"
        else:
            if top == 1:
                ans_latex = f"\\frac{{\\sqrt{{{r}}}}}{{{bottom}}}"
            elif top == -1:
                ans_latex = f"\\frac{{-\\sqrt{{{r}}}}}{{{bottom}}}"
            elif top > 0:
                ans_latex = f"\\frac{{{top}\\sqrt{{{r}}}}}{{{bottom}}}"
            else:
                ans_latex = f"-\\frac{{{-top}\\sqrt{{{r}}}}}{{{bottom}}}"

        steps = [r"將整數與分子相乘後進行約分化簡。"]
        return ans_latex, steps

    def _solve_p2b(self, v: dict, difficulty: str) -> Tuple[str, StepList]:
        """P2b: Distributive multiplication c1√r1 · (c2√r2 ± c3√r3)."""
        c1, r1 = v["c1"], v["r1"]
        c2, r2 = v["c2"], v["r2"]
        c3, r3 = v["c3"], v["r3"]
        op = v.get("op", "+")
        c3_signed = c3 if op == "+" else -c3

        steps: StepList = []
        left_terms: TermsDict = {r1: c1}
        right_terms: TermsDict = {r2: c2, r3: c3_signed}

        result = _multiply_term_dicts(left_terms, right_terms)
        latex_ans = _format_expression(result)

        q1 = _format_term_unsimplified(c1, r1, True)
        q2 = _format_term_unsimplified(c2, r2, True)
        q3 = _format_term_unsimplified(c3, r3, False)

        steps.append(
            rf"\text{{Step 1: 分配律展開}} \quad "
            rf"{q1}({q2}{q3}) = {q1} \cdot {q2} + {q1} \cdot ({_format_term_unsimplified(c3_signed, r3, True)})"
        )
        steps.append(
            rf"\text{{Step 2: 逐項化簡後合併}} \quad = {latex_ans}"
        )

        return latex_ans, steps

    def _solve_p2c(self, v: dict, difficulty: str) -> Tuple[str, StepList]:
        """P2c: Binomial multiplication (c1√r1 + c2√r2)(c3√r3 + c4√r4)."""
        terms1: TermsDict = {v["r1"]: v["c1"], v.get("r2", 1): v.get("c2", 0)}
        terms2: TermsDict = {v["r3"]: v["c3"], v.get("r4", 1): v.get("c4", 0)}
        terms1 = _merge_terms(terms1)
        terms2 = _merge_terms(terms2)

        result = _multiply_term_dicts(terms1, terms2)
        latex_ans = _format_expression(result)

        steps: StepList = [
            rf"\text{{Step 1: FOIL 展開雙括號}}",
            rf"\text{{Step 2: 逐項乘法化簡}}",
            rf"\text{{Step 3: 合併同類根式}} \quad = {latex_ans}",
        ]
        return latex_ans, steps

    def _solve_p2d(self, v: dict, difficulty: str) -> Tuple[str, StepList]:
        """P2d: Perfect-square expansion (c1√r1 ± c2√r2)².

        Formula: (a ± b)² = a² ± 2ab + b²
          where a = c1√r1, b = c2√r2
          → c1²·r1  ±  2·c1·c2·√(r1·r2)  +  c2²·r2
          → int_part = c1²·r1 + c2²·r2  (always positive)
          → cross term: ±2·c1·c2·√(r1·r2), simplified via _simplify_rad
        """
        c1, r1 = int(v["c1"]), int(v["r1"])
        c2, r2 = int(v["c2"]), int(v["r2"])
        op = v.get("op", "+")

        # Integer part: c1²·r1 + c2²·r2
        int_part = c1 * c1 * r1 + c2 * c2 * r2

        # Cross term: ±2·c1·c2·√(r1·r2), then simplify
        cross_coeff_raw = 2 * c1 * c2 if op == "+" else -(2 * c1 * c2)
        cross_r_raw = r1 * r2
        nc, nr = _simplify_rad(cross_coeff_raw, cross_r_raw)

        # Build answer TermsDict: integer key=1, radical key=nr
        result: TermsDict = {}
        if int_part != 0:
            result[1] = result.get(1, 0) + int_part
        if nc != 0:
            result[nr] = result.get(nr, 0) + nc
        result = _merge_terms(result)
        latex_ans = _format_expression(result)

        # Format question terms for step display
        t1_q = _format_term_unsimplified(c1, r1, True)
        t2_q = _format_term_unsimplified(c2, r2, True)
        op_str = "+" if op == "+" else "-"
        sq_str = rf"({t1_q} {op_str} {t2_q})^2"

        cross_nc_abs = abs(nc)
        cross_sign = "+" if nc >= 0 else "-"
        cross_latex = (
            rf"{cross_sign} {cross_nc_abs}\sqrt{{{nr}}}"
            if nr != 1
            else rf"{cross_sign} {cross_nc_abs}"
        )

        a_sq = c1 * c1 * r1
        b_sq = c2 * c2 * r2
        steps: StepList = [
            rf"\text{{Step 1: 套用完全平方公式}} \quad "
            rf"(a {op_str} b)^2 = a^2 {op_str} 2ab + b^2",
            rf"\text{{Step 2: 代入展開}} \quad "
            rf"{sq_str} = {a_sq} {cross_latex} + {b_sq}",
            rf"\text{{Step 3: 化簡合併}} \quad = {latex_ans}",
        ]

        return latex_ans, steps

    def _solve_p2e(self, v: dict, difficulty: str) -> Tuple[str, StepList]:
        """P2e: Difference-of-squares (c1√r1 - c2√r2)(c1√r1 + c2√r2).

        Formula: (a - b)(a + b) = a² - b²
          where a = c1√r1, b = c2√r2
          → c1²·r1 - c2²·r2  (pure integer result)
        """
        c1, r1 = int(v["c1"]), int(v["r1"])
        c2, r2 = int(v["c2"]), int(v["r2"])

        ans_int = c1 * c1 * r1 - c2 * c2 * r2
        latex_ans = str(ans_int)

        # r=1 renders as plain integer in the question display
        t1 = str(c1 * r1) if r1 == 1 else _format_term_unsimplified(c1, r1, True)
        t2 = str(c2 * r2) if r2 == 1 else _format_term_unsimplified(c2, r2, True)
        a_sq = c1 * c1 * r1
        b_sq = c2 * c2 * r2

        steps: StepList = [
            rf"\text{{Step 1: 套用平方差公式}} \quad (a-b)(a+b) = a^2 - b^2",
            rf"\text{{Step 2: 代入}} \quad ({t1}-{t2})({t1}+{t2}) = {a_sq} - {b_sq}",
            rf"\text{{Step 3: 計算結果}} \quad = {latex_ans}",
        ]
        return latex_ans, steps

    def _solve_p3a(self, v: dict, difficulty: str) -> Tuple[str, StepList]:
        """P3a: Expression ÷ single radical (c1√r1 ± c2√r2) ÷ √d."""
        c1, r1 = v["c1"], v["r1"]
        c2, r2 = v.get("c2", 0), v.get("r2", 1)
        op = v.get("op", "+")
        c2_signed = c2 if op == "+" else -c2
        d = v["denom_r"]

        steps: StepList = []
        final_terms: TermsDict = {}

        for coeff, radicand in [(c1, r1), (c2_signed, r2)]:
            if coeff == 0:
                continue
            if radicand % d == 0:
                nc, nr = _simplify_rad(coeff, radicand // d)
            else:
                nc_raw, nr = _simplify_rad(coeff, radicand * d)
                if nc_raw % d != 0:
                    raise ValueError(
                        f"P3a: term {coeff}*sqrt({radicand}) / sqrt({d}) is not exact. "
                        f"nc_raw={nc_raw}, d={d}. Retry with different vars."
                    )
                nc = nc_raw // d
            final_terms[nr] = final_terms.get(nr, 0) + nc

        final_terms = _merge_terms(final_terms)
        latex_ans = _format_expression(final_terms)

        q1 = _format_term_unsimplified(c1, r1, True)
        q2 = _format_term_unsimplified(c2_signed, r2, False)
        steps.append(
            rf"\text{{Step 1: 拆分表達式逐項除以 }}\sqrt{{{d}}} \quad "
            rf"({q1}{q2}) \div \sqrt{{{d}}}"
        )
        steps.append(
            rf"\text{{Step 2: 各項有理化或整除化簡}}"
        )
        steps.append(
            rf"\text{{Step 3: 合併結果}} \quad = {latex_ans}"
        )

        return latex_ans, steps

    def _solve_p3c(self, v: dict, difficulty: str) -> Tuple[str, StepList]:
        """P3c: Direct division (c1√r1) ÷ (c2√r2) = (c1/c2) * √(r1/r2).

        √(r1/r2) = √(r1*r2) / r2, so result = (c1 * √(r1*r2)) / (c2 * r2).
        Simplify √(r1*r2) and reduce the fraction.
        """
        c1, r1 = int(v["c1"]), int(v["r1"])
        c2, r2 = int(v["c2"]), int(v["r2"])

        out_c, out_r = _simplify_rad(1, r1 * r2)
        coeff = Fraction(c1 * out_c, c2 * r2)

        if out_r == 1:
            if coeff.denominator == 1:
                latex_ans = str(int(coeff))
            else:
                sgn = "-" if coeff.numerator < 0 else ""
                latex_ans = rf"{sgn}\frac{{{abs(coeff.numerator)}}}{{{coeff.denominator}}}"
        else:
            if coeff.denominator == 1:
                latex_ans = _format_term(int(coeff.numerator), out_r, True)
            else:
                num = coeff.numerator
                den = coeff.denominator
                sgn = "-" if num < 0 else ""
                latex_ans = rf"{sgn}\frac{{{abs(num)}\sqrt{{{out_r}}}}}{{{den}}}"

        t1 = _format_term_unsimplified(c1, r1, True)
        t2 = _format_term_unsimplified(c2, r2, True)
        left = f"({t1})" if c1 < 0 else t1
        right = f"({t2})" if c2 < 0 else t2

        steps: StepList = [
            rf"\text{{Step 1: 化為分數}} \quad {left} \div {right} = \frac{{{c1}\sqrt{{{r1}}}}}{{{c2}\sqrt{{{r2}}}}}",
            rf"\text{{Step 2: 有理化分母}} \quad = \frac{{{c1}\sqrt{{{r1*r2}}}}}{{{c2*r2}}}",
            rf"\text{{Step 3: 化簡根式並約分}} \quad = {latex_ans}",
        ]
        return latex_ans, steps

    def _solve_p3b(self, v: dict, difficulty: str) -> Tuple[str, StepList]:
        """P3b: Simple rationalization a/√b."""
        a = v["a"]
        b = v["b"]
        return self.rationalize_denominator(a, 1, b)

    def _solve_p4(self, v: dict, difficulty: str) -> Tuple[str, StepList]:
        """P4: (a/b) × (√r/c) — fraction times radical fraction."""
        a = v["a"]
        b = v["b"]
        r = v["r"]
        c = v["c"]
        steps: StepList = []

        # a/b × √r/c = a·√r / (b·c)
        denom = b * c
        new_c, new_r = _simplify_rad(a, r)
        latex_ans = _format_expression({new_r: new_c}, denominator=denom)

        steps.append(
            rf"\text{{Step 1: 乘法}} \quad "
            rf"\frac{{{a}}}{{{b}}} \times \frac{{\sqrt{{{r}}}}}{{{c}}} = \frac{{{a}\sqrt{{{r}}}}}{{{denom}}}"
        )
        steps.append(
            rf"\text{{Step 2: 化簡根式並約分}} \quad = {latex_ans}"
        )

        return latex_ans, steps

    def _solve_p4b(self, v: dict, difficulty: str) -> Tuple[str, StepList]:
        """P4b: (√n1/√d1) ÷ (√n2/√d2) = √((n1*d2)/(d1*n2)). Rationalize and simplify."""
        import sympy
        n1, d1 = int(v["n1"]), int(v["d1"])
        n2, d2 = int(v["n2"]), int(v["d2"])

        # (√n1/√d1) ÷ (√n2/√d2) = (√n1/√d1) * (√d2/√n2) = √(n1*d2/(d1*n2))
        num_rad = n1 * d2
        den_rad = d1 * n2
        expr = sympy.sqrt(sympy.Rational(num_rad, den_rad))
        simplified = sympy.simplify(expr)
        latex_ans = sympy.latex(simplified)

        steps: StepList = [
            rf"\text{{Step 1: 除改乘倒數}} \quad "
            rf"\frac{{\sqrt{{{n1}}}}}{{\sqrt{{{d1}}}}} \div \frac{{\sqrt{{{n2}}}}}{{\sqrt{{{d2}}}}} "
            rf"= \frac{{\sqrt{{{n1}}}}}{{\sqrt{{{d1}}}}} \times \frac{{\sqrt{{{d2}}}}}{{\sqrt{{{n2}}}}}",
            rf"\text{{Step 2: 合併根號}} \quad = \sqrt{{\frac{{{num_rad}}}{{{den_rad}}}}}",
            rf"\text{{Step 3: 有理化並化簡}} \quad = {latex_ans}",
        ]
        return latex_ans, steps

    def _solve_p4c(self, v: dict, difficulty: str) -> Tuple[str, StepList]:
        """P4c: √(n1/d1) × √(n2/d2) ÷ √(n3/d3) = √((n1*n2*d3)/(d1*d2*n3))."""
        import sympy
        n1, d1 = int(v["n1"]), int(v["d1"])
        n2, d2 = int(v["n2"]), int(v["d2"])
        n3, d3 = int(v["n3"]), int(v["d3"])

        num_rad = n1 * n2 * d3
        den_rad = d1 * d2 * n3
        expr = sympy.sqrt(sympy.Rational(num_rad, den_rad))
        simplified = sympy.simplify(expr)
        latex_ans = sympy.latex(simplified)

        steps: StepList = [
            rf"\text{{Step 1: 合併根號}} \quad "
            rf"\sqrt{{\frac{{{n1}}}{{{d1}}}}} \times \sqrt{{\frac{{{n2}}}{{{d2}}}}} \div \sqrt{{\frac{{{n3}}}{{{d3}}}}} "
            rf"= \sqrt{{\frac{{{num_rad}}}{{{den_rad}}}}}",
            rf"\text{{Step 2: 有理化並化簡}} \quad = {latex_ans}",
        ]
        return latex_ans, steps

    def _solve_p5a(self, v: dict, difficulty: str) -> Tuple[str, StepList]:
        """P5a: 1 / (b√q ± c) — conjugate rationalization, integer numerator."""
        b = v["b"]
        q = v["q"]
        c = v["c"]
        sign = v["sign"]
        return self.rationalize_conjugate(
            numerator_terms={1: 1},
            b=b, q=q, c=c, sign=sign
        )

    def _solve_p5b(self, v: dict, difficulty: str) -> Tuple[str, StepList]:
        """P5b: √p / (b√q ± c) — conjugate rationalization, radical numerator."""
        p = v["p"]
        b = v["b"]
        q = v["q"]
        c = v["c"]
        sign = v["sign"]
        return self.rationalize_conjugate(
            numerator_terms={p: 1},
            b=b, q=q, c=c, sign=sign
        )

    def _solve_p6(self, v: dict, difficulty: str) -> Tuple[str, StepList]:
        """
        P6: Multi-step combination. Composes two sub-patterns.

        Expected keys in v:
            sub_pattern1: str  (first sub-problem pattern_id)
            vars1: dict        (variables for sub-problem 1)
            sub_pattern2: str  (second sub-problem pattern_id)
            vars2: dict        (variables for sub-problem 2)
            combo_op: str      ('+' or '-' to combine the two sub-results)
        """
        sp1 = v["sub_pattern1"]
        sp2 = v["sub_pattern2"]
        combo_op = v.get("combo_op", "+")

        ans1, steps1 = self.solve_problem_pattern(sp1, v["vars1"], difficulty)
        ans2, steps2 = self.solve_problem_pattern(sp2, v["vars2"], difficulty)

        all_steps: StepList = [
            rf"\text{{--- 子題 1 ({sp1}) ---}}",
            *steps1,
            rf"\text{{--- 子題 2 ({sp2}) ---}}",
            *steps2,
        ]

        # Attempt symbolic combination if both answers are single-term radical forms
        try:
            from core.domain_functions import DomainFunctionHelper
            df = DomainFunctionHelper()
            combined_terms = df._combine_latex_answers(ans1, ans2, combo_op)
            final_ans = _format_expression(combined_terms)
        except Exception:
            op_display = "+" if combo_op == "+" else "-"
            final_ans = f"({ans1}) {op_display} ({ans2})"

        all_steps.append(
            rf"\text{{--- 最終合併 ---}} \quad ({ans1}) {'+' if combo_op=='+' else '-'} ({ans2}) = {final_ans}"
        )
        return final_ans, all_steps

    def _solve_p7_mixed_rad_add(self, v: dict, difficulty: str) -> Tuple[str, StepList]:
        """
        P7: √(w+n/d) ± √(w+n/d) — mixed-number radicals (perfect-square fractions).
        Expected keys: w1, f_n1, d1, n1, w2, f_n2, d2, n2, op ('+' or '-').
        """
        import sympy as sp
        expr1 = sp.sqrt(sp.Rational(v["n1"], v["d1"]))
        expr2 = sp.sqrt(sp.Rational(v["n2"], v["d2"]))
        expr = expr1 + expr2 if v["op"] == "+" else expr1 - expr2
        ans_latex = sp.latex(sp.simplify(expr))
        steps: StepList = [
            "將帶分數化為假分數，確認為完全平方數後開根號，再進行加減運算。"
        ]
        return ans_latex, steps
