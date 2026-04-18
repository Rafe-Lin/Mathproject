# -*- coding: utf-8 -*-
"""
=============================================================================
Module: core/skill_policies/radical_logic.py
Description:
    RadicalLogicEngine — Neuro-Symbolic engine for
    jh_數學2上_FourOperationsOfRadicals.

    Provides a high-level API that the Qwen-VL-8B generated code calls.
    The model only selects a pattern_id and a numeric range; this engine
    handles every step of variable generation, symbolic computation, and
    LaTeX formatting deterministically.

    Supported pattern IDs
    ─────────────────────
    SimpleAdd    k₁√r₁ ± k₂√r₂ [± k₃√r₃]  (like-radical combining)
    Multiply     k₁√r₁ × k₂√r₂  or  k√r × (a√p ± b√q)
    Rationalize  a/√b  or  1/(b√q ± c)  denominator rationalization
    Combo        multi-step: multiply then add/subtract

    Architecture contract
    ─────────────────────
    The generated ProblemSet code must look exactly like:

        from core.skill_policies.radical_logic import RadicalLogicEngine as RLE

        def generate(level=1, **kwargs):
            engine = RLE()
            pattern = "SimpleAdd"     # ← AI decision
            vars    = engine.get_safe_values(pattern, range=(2, 50))
            ans, steps = engine.solve_and_format(pattern, vars)
            question_text = engine.format_question(pattern, vars)
            return {
                'question_text': question_text,
                'answer': '',
                'correct_answer': ans,
                'solution_steps': steps,
                'mode': 1,
                '_o1_healed': False,
            }

    The model must NOT write any math logic beyond picking pattern + range.

Version: 1.0.0
=============================================================================
"""

import math
import random
from typing import Dict, List, Optional, Tuple

# Re-use the low-level symbolic primitives from radical_solver (no duplication).
from core.math_solvers.radical_solver import (
    _simplify_rad,
    _format_term,
    _format_term_unsimplified,
    _format_expression,
    _merge_terms,
    _multiply_term_dicts,
    _add_term_dicts,
    TermsDict,
    StepList,
)

# ---------------------------------------------------------------------------
# Registry stub — the skill is already registered via radical.py; this file
# contributes no new policy rows but must be importable by the registry scan.
# ---------------------------------------------------------------------------
POLICIES: List = []


# ===========================================================================
# Internal helpers
# ===========================================================================

def _prime_factors(n: int) -> Dict[int, int]:
    """Return {prime: exponent} for |n|."""
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


def _has_square_factor(n: int) -> bool:
    """Return True if √n can be simplified (n has a perfect-square factor > 1)."""
    if n <= 1:
        return False
    for p, exp in _prime_factors(n).items():
        if exp >= 2:
            return True
    return False


def _filter_simplifiable(lo: int, hi: int) -> List[int]:
    """All integers in [lo, hi] whose square root can be simplified."""
    return [n for n in range(max(2, lo), hi + 1) if _has_square_factor(n)]


def _filter_prime_radicals(lo: int, hi: int) -> List[int]:
    """All prime integers in [lo, hi] (already-simplest radicands)."""
    def _is_prime(n):
        if n < 2:
            return False
        for i in range(2, int(n ** 0.5) + 1):
            if n % i == 0:
                return False
        return True
    return [n for n in range(max(2, lo), hi + 1) if _is_prime(n)]


# ===========================================================================
# RadicalLogicEngine
# ===========================================================================

class RadicalLogicEngine:
    """
    Neuro-Symbolic engine for radical four-operations problems.

    The generated code uses only three public methods:
        get_safe_values(pattern, range)  → vars dict
        solve_and_format(pattern, vars)  → (answer_latex, steps_list)
        format_question(pattern, vars)   → question_text string

    Three lower-level primitives are also exposed for advanced composition:
        simplify(n)                       → (coeff, radicand, latex_str)
        rationalize(num, den_rad)         → (latex_str, steps)
        operate(op1, op2, operator)       → (answer_latex, steps)
    """

    # -----------------------------------------------------------------------
    # Primitive: simplify
    # -----------------------------------------------------------------------

    def simplify(self, n: int) -> Tuple[int, int, str]:
        """
        Simplify √n symbolically.

        Args:
            n: positive integer radicand

        Returns:
            (coeff, simplified_radicand, latex_str)
            e.g. simplify(72) → (6, 2, "6\\sqrt{2}")
        """
        coeff, rad = _simplify_rad(1, int(n))
        latex = _format_expression({rad: coeff})
        return coeff, rad, latex

    # -----------------------------------------------------------------------
    # Primitive: rationalize
    # -----------------------------------------------------------------------

    def rationalize(
        self,
        num: int,
        den_rad: int,
        *,
        b: int = 1,
        c: int = 0,
        sign: int = 1,
        conjugate: bool = False,
    ) -> Tuple[str, StepList]:
        """
        Rationalize the denominator.

        Simple form   (conjugate=False):  num / √den_rad
        Conjugate form (conjugate=True):  num / (b·√den_rad + sign·c)

        Args:
            num      : integer numerator (or 1 for pure-radical numerator)
            den_rad  : radicand of denominator
            b, c     : coefficients in conjugate denominator (conjugate only)
            sign     : +1 or -1 for ± in conjugate denominator
            conjugate: True → use conjugate rationalization

        Returns:
            (answer_latex, steps_list)
        """
        if conjugate:
            return self._rationalize_conjugate(num, b, den_rad, c, sign)
        return self._rationalize_simple(num, den_rad)

    def _rationalize_simple(self, a: int, b: int) -> Tuple[str, StepList]:
        """a / √b → a·√b / b, with GCD reduction."""
        steps: StepList = []
        nc_raw, nr = _simplify_rad(a, b)
        latex_ans = _format_expression({nr: nc_raw}, denominator=b)
        steps.append(
            rf"\text{{Step 1: 分子分母同乘 }}\sqrt{{{b}}} \quad "
            rf"\frac{{{a}}}{{\sqrt{{{b}}}}} = \frac{{{a}\sqrt{{{b}}}}}{{{b}}}"
        )
        steps.append(
            rf"\text{{Step 2: 化簡}} \quad = {latex_ans}"
        )
        return latex_ans, steps

    def _rationalize_conjugate(
        self, num: int, b: int, q: int, c: int, sign: int
    ) -> Tuple[str, StepList]:
        """num / (b√q + sign·c) via conjugate multiplication."""
        new_denom = b * b * q - c * c
        if new_denom == 0:
            raise ValueError(
                f"Conjugate denominator is zero: b={b}, q={q}, c={c}."
            )
        steps: StepList = []
        sign_str = "+" if sign == 1 else "-"
        b_str = "" if b == 1 else str(b)
        conjugate_terms: TermsDict = {q: b, 1: -sign * c}
        expanded = _multiply_term_dicts({1: num}, conjugate_terms)
        expanded_latex = _format_expression(expanded)
        latex_ans = _format_expression(expanded, denominator=new_denom)
        steps.append(
            rf"\text{{Step 1: 乘以共軛式 }} ({b_str}\sqrt{{{q}}}{'-' if sign==1 else '+'}{c})"
        )
        steps.append(
            rf"\text{{Step 2: 新分母}} = ({b_str}\sqrt{{{q}}})^2 - {c}^2 = {new_denom}"
        )
        steps.append(
            rf"\text{{Step 3: 展開分子 → 化簡}} \quad = {latex_ans}"
        )
        return latex_ans, steps

    # -----------------------------------------------------------------------
    # Primitive: operate
    # -----------------------------------------------------------------------

    def operate(
        self,
        op1: Tuple[int, int],
        op2: Tuple[int, int],
        operator: str,
    ) -> Tuple[str, StepList]:
        """
        Perform a binary operation on two radical objects.

        Args:
            op1, op2: (coefficient, radicand) tuples
            operator: one of '+', '-', '*', '/'

        Returns:
            (answer_latex, steps_list)

        Raises:
            ValueError for unsupported operator or divide-by-zero.
        """
        c1, r1 = int(op1[0]), int(op1[1])
        c2, r2 = int(op2[0]), int(op2[1])

        if operator == "+":
            return self._op_add_sub(c1, r1, c2, r2, "+")
        if operator == "-":
            return self._op_add_sub(c1, r1, c2, r2, "-")
        if operator == "*":
            return self._op_multiply(c1, r1, c2, r2)
        if operator == "/":
            return self._op_divide(c1, r1, c2, r2)
        raise ValueError(f"Unsupported operator '{operator}'. Use +, -, *, /.")

    def _op_add_sub(
        self, c1: int, r1: int, c2: int, r2: int, op: str
    ) -> Tuple[str, StepList]:
        c2_signed = c2 if op == "+" else -c2
        sc1, sr1 = _simplify_rad(c1, r1)
        sc2, sr2 = _simplify_rad(c2_signed, r2)
        merged = _add_term_dicts({sr1: sc1}, {sr2: sc2})
        ans = _format_expression(merged)
        steps: StepList = [
            rf"\text{{Step 1: 化簡各項}} \quad "
            rf"{_format_term_unsimplified(c1, r1, True)} = {_format_term(sc1, sr1, True)}, \quad "
            rf"{_format_term_unsimplified(c2, r2, True)} = {_format_term(abs(sc2), sr2, True)}",
            rf"\text{{Step 2: 合併同類根式}} \quad = {ans}",
        ]
        return ans, steps

    def _op_multiply(
        self, c1: int, r1: int, c2: int, r2: int
    ) -> Tuple[str, StepList]:
        new_c, new_r = _simplify_rad(c1 * c2, r1 * r2)
        ans = _format_expression({new_r: new_c})
        steps: StepList = [
            rf"\text{{Step 1: 合併}} \quad "
            rf"{_format_term_unsimplified(c1, r1, True)} \times "
            rf"{_format_term_unsimplified(c2, r2, True)} = {c1*c2}\sqrt{{{r1*r2}}}",
            rf"\text{{Step 2: 化簡}} \quad = {ans}",
        ]
        return ans, steps

    def _op_divide(
        self, c1: int, r1: int, c2: int, r2: int
    ) -> Tuple[str, StepList]:
        if c2 == 0:
            raise ValueError("Division by zero radical.")
        # c1√r1 / (c2√r2) = (c1/c2) × √(r1/r2)
        # Use rationalization if r1/r2 is not integer
        if r1 % r2 == 0:
            nc, nr = _simplify_rad(c1, r1 // r2)
            denom = c2
            ans = _format_expression({nr: nc}, denominator=denom)
        else:
            # Rationalize: c1√r1/(c2√r2) = c1√(r1·r2)/(c2·r2)
            nc_raw, nr = _simplify_rad(c1, r1 * r2)
            ans = _format_expression({nr: nc_raw}, denominator=c2 * r2)
        steps: StepList = [
            rf"\text{{Step 1: 有理化分母}} \quad "
            rf"\frac{{{_format_term_unsimplified(c1, r1, True)}}}"
            rf"{{{_format_term_unsimplified(c2, r2, True)}}}",
            rf"\text{{Step 2: 化簡}} \quad = {ans}",
        ]
        return ans, steps

    # -----------------------------------------------------------------------
    # generate_step_by_step
    # -----------------------------------------------------------------------

    def generate_step_by_step(
        self, pattern_id: str, params: dict
    ) -> StepList:
        """
        Deterministic step-by-step solution for a given pattern + params.

        Args:
            pattern_id: "SimpleAdd" | "Multiply" | "Rationalize" | "Combo"
            params:     variable dict (same structure as returned by get_safe_values)

        Returns:
            Ordered list of LaTeX step strings.
        """
        _, steps = self.solve_and_format(pattern_id, params)
        return steps

    # -----------------------------------------------------------------------
    # High-level API: get_safe_values
    # -----------------------------------------------------------------------

    def get_safe_values(
        self,
        pattern: str,
        range: Tuple[int, int] = (2, 50),
        max_retries: int = 300,
    ) -> dict:
        """
        Generate safe, integer-only variable dictionaries for the chosen pattern.

        Args:
            pattern   : "SimpleAdd" | "Multiply" | "Rationalize" | "Combo"
            range     : (lo, hi) inclusive bounds for radicands
            max_retries: retry attempts before raising RuntimeError

        Returns:
            A dict of variables consumed by solve_and_format and format_question.

        Raises:
            RuntimeError if valid variables cannot be found within max_retries.
        """
        lo, hi = int(range[0]), int(range[1])
        generator = {
            "SimpleAdd":   self._vars_simple_add,
            "Multiply":    self._vars_multiply,
            "Rationalize": self._vars_rationalize,
            "Combo":       self._vars_combo,
        }
        pid = pattern.strip()
        if pid not in generator:
            raise ValueError(
                f"Unknown pattern '{pattern}'. "
                f"Valid patterns: {list(generator.keys())}"
            )

        import builtins
        for attempt in builtins.range(max_retries):
            try:
                return generator[pid](lo, hi)
            except _RetrySignal:
                continue
            except Exception as exc:
                if attempt >= max_retries - 1:
                    raise RuntimeError(
                        f"get_safe_values failed for pattern '{pattern}' "
                        f"after {max_retries} attempts: {exc}"
                    ) from exc
        raise RuntimeError(
            f"get_safe_values: could not generate valid vars for '{pattern}' "
            f"within {max_retries} attempts."
        )

    # -----------------------------------------------------------------------
    # High-level API: solve_and_format
    # -----------------------------------------------------------------------

    def solve_and_format(
        self, pattern: str, vars: dict
    ) -> Tuple[str, StepList]:
        """
        Compute the exact answer and solution steps for pattern + vars.

        Args:
            pattern: "SimpleAdd" | "Multiply" | "Rationalize" | "Combo"
            vars:    variable dict from get_safe_values

        Returns:
            (answer_latex: str, solution_steps: List[str])
        """
        pid = pattern.strip()
        solver = {
            "SimpleAdd":   self._solve_simple_add,
            "Multiply":    self._solve_multiply,
            "Rationalize": self._solve_rationalize,
            "Combo":       self._solve_combo,
        }
        if pid not in solver:
            raise ValueError(f"Unknown pattern '{pattern}'.")
        return solver[pid](vars)

    # -----------------------------------------------------------------------
    # High-level API: format_question
    # -----------------------------------------------------------------------

    def format_question(self, pattern: str, vars: dict) -> str:
        """
        Build the LaTeX question text string for pattern + vars.

        Args:
            pattern: "SimpleAdd" | "Multiply" | "Rationalize" | "Combo"
            vars:    variable dict from get_safe_values

        Returns:
            Complete question string with $...$ LaTeX wrapping, e.g.:
            "化簡 $2\\sqrt{12} - \\sqrt{27}$。"
        """
        pid = pattern.strip()
        formatter = {
            "SimpleAdd":   self._fmt_simple_add,
            "Multiply":    self._fmt_multiply,
            "Rationalize": self._fmt_rationalize,
            "Combo":       self._fmt_combo,
        }
        if pid not in formatter:
            raise ValueError(f"Unknown pattern '{pattern}'.")
        return formatter[pid](vars)

    # =======================================================================
    # Variable generators (private)
    # =======================================================================

    def _vars_simple_add(self, lo: int, hi: int) -> dict:
        """
        SimpleAdd: k₁√r₁ ± k₂√r₂ [± k₃√r₃]
        Constraint: after simplification at least two terms share a radicand.
        """
        pool = _filter_simplifiable(lo, hi)
        if len(pool) < 2:
            raise _RetrySignal()

        n_terms = random.choice([2, 2, 3])  # weighted toward 2-term
        terms = []
        for i in range(n_terms):
            c = random.choice([-4, -3, -2, -1, 1, 2, 3, 4])
            r = random.choice(pool)
            op = "+" if i == 0 else random.choice(["+", "-"])
            terms.append((c, r, op))

        # At least two terms must collapse to the same simplified radicand
        simplified_rads = [_simplify_rad(1, t[1])[1] for t in terms]
        if len(set(simplified_rads)) == len(simplified_rads):
            raise _RetrySignal()

        return {"terms": terms}

    def _vars_multiply(self, lo: int, hi: int) -> dict:
        """
        Multiply: direct  k₁√r₁ × k₂√r₂
                  or distributive  k₁√r₁ × (k₂√r₂ ± k₃√r₃)
        """
        pool_s = _filter_simplifiable(lo, hi)
        if not pool_s:
            raise _RetrySignal()

        sub = random.choice(["direct", "distrib"])
        c1 = random.choice([-3, -2, -1, 1, 2, 3])
        r1 = random.choice(pool_s)
        c2 = random.choice([-3, -2, -1, 1, 2, 3])
        r2 = random.choice(pool_s)
        if sub == "direct":
            return {"sub": "direct", "c1": c1, "r1": r1, "c2": c2, "r2": r2}

        # distributive: c1√r1 × (c2√r2 ± c3√r3)
        pool_p = _filter_simplifiable(lo, hi)
        c3 = random.choice([-3, -2, -1, 1, 2, 3])
        r3 = random.choice(pool_p)
        op = random.choice(["+", "-"])
        return {"sub": "distrib", "c1": c1, "r1": r1, "c2": c2, "r2": r2,
                "c3": c3, "r3": r3, "op": op}

    def _vars_rationalize(self, lo: int, hi: int) -> dict:
        """
        Rationalize: simple  a/√b
                     or conjugate  1/(b√q ± c)
        """
        sub = random.choice(["simple", "conjugate"])
        if sub == "simple":
            pool_p = _filter_simplifiable(lo, min(hi, 20))
            if not pool_p:
                raise _RetrySignal()
            a = random.randint(1, 6)
            b = random.choice(pool_p)
            return {"sub": "simple", "a": a, "b": b}

        # conjugate: 1/(b√q ± c)
        primes = [p for p in [2, 3, 5, 7, 11] if lo <= p <= hi]
        if not primes:
            primes = [2, 3, 5, 7, 11]
        for _ in range(50):
            b = random.choice([1, 2, 3])
            q = random.choice(primes)
            c = random.randint(1, 5)
            sign = random.choice([1, -1])
            if b * b * q - c * c != 0:
                return {"sub": "conjugate", "b": b, "q": q, "c": c, "sign": sign}
        raise _RetrySignal()

    def _vars_combo(self, lo: int, hi: int) -> dict:
        """
        Combo: solve two sub-problems then combine their results.
        Sub-patterns: (Multiply, SimpleAdd) or (Rationalize, SimpleAdd).
        """
        sub_choices = [("Multiply", "SimpleAdd"), ("Rationalize", "SimpleAdd")]
        sp1_name, sp2_name = random.choice(sub_choices)
        combo_op = random.choice(["+", "-"])
        return {
            "sp1": sp1_name,
            "vars1": self.get_safe_values(sp1_name, range=(lo, hi)),
            "sp2": sp2_name,
            "vars2": self.get_safe_values(sp2_name, range=(lo, hi)),
            "combo_op": combo_op,
        }

    # =======================================================================
    # Solvers (private)
    # =======================================================================

    def _solve_simple_add(self, v: dict) -> Tuple[str, StepList]:
        terms = v["terms"]
        steps: StepList = []
        simplified: TermsDict = {}
        details = []

        for coeff, radicand, op in terms:
            actual = coeff if op == "+" else -coeff
            sc, sr = _simplify_rad(actual, radicand)
            simplified[sr] = simplified.get(sr, 0) + sc
            q_str = _format_term_unsimplified(coeff, radicand, True)
            s_str = _format_term(actual, radicand, True)
            details.append(f"{q_str} = {s_str}")

        simplified = _merge_terms(simplified)
        steps.append(
            rf"\text{{Step 1: 逐項化簡}} \quad " + r", \quad ".join(details)
        )
        steps.append(
            rf"\text{{Step 2: 合併同類根式}} \quad "
            rf"\Rightarrow {_format_expression(simplified)}"
        )
        return _format_expression(simplified), steps

    def _solve_multiply(self, v: dict) -> Tuple[str, StepList]:
        if v["sub"] == "direct":
            return self._op_multiply(v["c1"], v["r1"], v["c2"], v["r2"])

        # distributive
        c1, r1 = v["c1"], v["r1"]
        c2, r2 = v["c2"], v["r2"]
        c3, r3 = v["c3"], v["r3"]
        op = v.get("op", "+")
        c3_signed = c3 if op == "+" else -c3
        result = _multiply_term_dicts({r1: c1}, {r2: c2, r3: c3_signed})
        ans = _format_expression(result)
        q1 = _format_term_unsimplified(c1, r1, True)
        q2 = _format_term_unsimplified(c2, r2, True)
        q3 = _format_term_unsimplified(c3_signed, r3, False)
        steps: StepList = [
            rf"\text{{Step 1: 分配律展開}} \quad "
            rf"{q1}({q2}{q3})",
            rf"\text{{Step 2: 逐項相乘後化簡}} \quad = {ans}",
        ]
        return ans, steps

    def _solve_rationalize(self, v: dict) -> Tuple[str, StepList]:
        if v["sub"] == "simple":
            return self._rationalize_simple(v["a"], v["b"])
        return self._rationalize_conjugate(
            num=1, b=v["b"], q=v["q"], c=v["c"], sign=v["sign"]
        )

    def _solve_combo(self, v: dict) -> Tuple[str, StepList]:
        ans1, steps1 = self.solve_and_format(v["sp1"], v["vars1"])
        ans2, steps2 = self.solve_and_format(v["sp2"], v["vars2"])
        combo_op = v.get("combo_op", "+")
        op_sym = "+" if combo_op == "+" else "-"

        all_steps: StepList = [
            rf"\text{{--- 子題一 ({v['sp1']}) ---}}",
            *steps1,
            rf"\text{{--- 子題二 ({v['sp2']}) ---}}",
            *steps2,
        ]

        # Best-effort symbolic combine; fall back to string display
        try:
            t1 = self._parse_single_term_latex(ans1)
            t2 = self._parse_single_term_latex(ans2)
            if combo_op == "-":
                t2 = {r: -c for r, c in t2.items()}
            merged = {}
            for r, c in {**t1, **t2}.items():
                merged[r] = merged.get(r, 0) + c
            final = _format_expression(_merge_terms(merged))
        except Exception:
            final = f"({ans1}) {op_sym} ({ans2})"

        all_steps.append(
            rf"\text{{--- 最終合併 ---}} \quad ({ans1}) {op_sym} ({ans2}) = {final}"
        )
        return final, all_steps

    # =======================================================================
    # Question formatters (private)
    # =======================================================================

    def _fmt_simple_add(self, v: dict) -> str:
        parts = []
        for i, (coeff, radicand, op) in enumerate(v["terms"]):
            display_c = coeff if op == "+" else -coeff
            parts.append(_format_term_unsimplified(display_c, radicand, i == 0))
        return rf"化簡 ${''.join(parts)}$。"

    def _fmt_multiply(self, v: dict) -> str:
        q1 = _format_term_unsimplified(v["c1"], v["r1"], True)
        q2 = _format_term_unsimplified(v["c2"], v["r2"], True)
        if v["sub"] == "direct":
            return rf"化簡 ${q1} \times {q2}$。"
        c3, r3 = v["c3"], v["r3"]
        op = v.get("op", "+")
        c3d = c3 if op == "+" else -c3
        q3 = _format_term_unsimplified(c3d, r3, False)
        return rf"化簡 ${q1} \times ({q2}{q3})$。"

    def _fmt_rationalize(self, v: dict) -> str:
        if v["sub"] == "simple":
            a, b = v["a"], v["b"]
            return rf"化簡 $\dfrac{{{a}}}{{\sqrt{{{b}}}}}$。"
        b, q, c, sign = v["b"], v["q"], v["c"], v["sign"]
        b_str = "" if b == 1 else str(b)
        sign_str = "+" if sign == 1 else "-"
        return rf"化簡 $\dfrac{{1}}{{{b_str}\sqrt{{{q}}}{sign_str}{c}}}$。"

    def _fmt_combo(self, v: dict) -> str:
        sp1, sp2 = v.get("sp1", "?"), v.get("sp2", "?")
        return rf"計算下列根式運算（{sp1} 結果與 {sp2} 結果的組合）。"

    # =======================================================================
    # Utility: parse simple LaTeX term for symbolic combination
    # =======================================================================

    def _parse_single_term_latex(self, s: str) -> TermsDict:
        """
        Parse simple LaTeX like "3\\sqrt{2}" or "-4" into a TermsDict.
        Raises ValueError for complex expressions (triggers string-fallback).
        """
        import re
        s = s.strip()
        if s.lstrip("-").isdigit():
            return {1: int(s)}
        m = re.fullmatch(r"(-?)(\d*)\s*\\sqrt\{(\d+)\}", s)
        if m:
            neg, k_str, r_str = m.groups()
            k = int(k_str) if k_str else 1
            r = int(r_str)
            return {r: -k if neg else k}
        raise ValueError(f"Cannot parse '{s}' for symbolic combination.")


# ---------------------------------------------------------------------------
# Internal retry sentinel
# ---------------------------------------------------------------------------

class _RetrySignal(Exception):
    """Raised inside variable generators to trigger a clean retry."""
    pass
