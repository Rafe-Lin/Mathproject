# -*- coding: utf-8 -*-
"""
=============================================================================
Module: core/domain_functions.py
Description:
    DomainFunctionHelper — High-level orchestration interface for the
    "Edge AI Orchestrator" architecture.

    This module is the ONLY surface the Qwen3-generated code is allowed to
    import from. It wraps the RadicalSolver engine and provides:

      1. get_golden_pattern_for_liveshow() — OCR-semantic → pattern_id mapping
      2. get_safe_vars_for_pattern()       — controlled random variable generation
      3. solve_problem_pattern()           — delegates to RadicalSolver
      4. format_question_LaTeX()           — LaTeX via RadicalOps（與沙盒一致）

    Design constraints:
      - All variable generation is seeded through integer-only arithmetic.
      - No floating-point values are ever inserted into variable dicts.
      - The generated code (from Qwen3) only calls these high-level methods;
        it never touches RadicalSolver directly.

Version: 1.0.0
Skill scope: jh_數學2上_FourOperationsOfRadicals
=============================================================================
"""

import math
import random
from fractions import Fraction
from typing import Dict, List, Optional, Tuple

from core.math_solvers.radical_solver import (
    RadicalSolver,
    _simplify_rad,
    _format_expression,
    _merge_terms,
    StepList,
    TermsDict,
)
from core.scaffold.domain_libs import RadicalOps

# ---------------------------------------------------------------------------
# Constant sets (match SKILL.md definitions)
# ---------------------------------------------------------------------------
PRIME_SET = [2, 3, 5, 7, 11]
SIMPLIFIABLE_SET = [8, 12, 18, 20, 24, 27, 32, 45, 48, 50, 72, 75]
# Square-free / already-simplified radicands when style == "simplified"
SIMPLIFIED_RADICALS = [2, 3, 5, 6, 7, 10, 11, 13, 14, 15]
NON_ZERO_COEFF = [-5, -4, -3, -2, -1, 1, 2, 3, 4, 5]
SMALL_DENOM = [2, 3, 4, 5, 6]

# OCR keyword → pattern_id mapping table (for get_golden_pattern_for_liveshow)
_OCR_KEYWORD_PATTERN_MAP = {
    # Conjugate rationalization keywords
    "共軛": "p5a_conjugate_int",
    "有理化分母": "p5a_conjugate_int",
    r"\frac{1}{\sqrt": "p5a_conjugate_int",
    r"\frac{\sqrt": "p5b_conjugate_rad",
    # Division keywords
    r"\div\sqrt": "p3a_div_expr",
    r"/\sqrt": "p3b_div_simple",
    # Multiplication with bracket
    r"\times(": "p2b_mult_distrib",
    r")(\sqrt": "p2c_mult_binomial",
    # Direct multiplication
    r"\times\sqrt": "p2a_mult_direct",
    r"\sqrt{}\times": "p2a_mult_direct",
    # Addition / subtraction (fallback after all others checked)
    "+": "p1_add_sub",
    "-": "p1_add_sub",
    # Single radical
    r"\sqrt{": "p0_simplify",
}


class DomainFunctionHelper:
    """
    High-level helper interface for the Edge AI Orchestrator.

    The Qwen3 model instantiates this class and calls its methods.
    All mathematical computation is handled internally by RadicalSolver;
    the model only provides pattern_id, difficulty, and optional OCR hints.

    Usage in Qwen3-generated code:
        from core.domain_functions import DomainFunctionHelper
        df = DomainFunctionHelper()

        pattern_id = "p1_add_sub"
        difficulty  = "mid"

        vars        = df.get_safe_vars_for_pattern(pattern_id, difficulty)
        ans, sol    = df.solve_problem_pattern(pattern_id, vars, difficulty)
        question    = df.format_question_LaTeX(pattern_id, vars)
    """

    def __init__(self):
        self._solver = RadicalSolver()

    # -----------------------------------------------------------------------
    # 1. OCR semantic → pattern_id (mocked)
    # -----------------------------------------------------------------------

    def get_golden_pattern_for_liveshow(
        self,
        skill_name: str,
        difficulty: str,
        uploaded_ocr_semantics: str,
    ) -> str:
        """
        [MOCKED] Given a skill name, difficulty level, and OCR-extracted text
        from the uploaded textbook image, return the most suitable pattern_id.

        In production this would call a lightweight classifier; currently uses
        a deterministic keyword-priority heuristic so the pipeline never fails.

        Args:
            skill_name: e.g. "jh_數學2上_FourOperationsOfRadicals"
            difficulty: "easy" | "mid" | "hard"
            uploaded_ocr_semantics: raw OCR text or structured LaTeX snippet

        Returns:
            A pattern_id string from SKILL.md Pattern Catalogue.
        """
        ocr = str(uploaded_ocr_semantics)

        # Priority-ordered keyword scan
        priority = [
            ("p5b_conjugate_rad", [r"\frac{\sqrt", r"√p/(", "共軛根式"]),
            ("p5a_conjugate_int", [r"\frac{1}{\sqrt", r"1/(", "共軛", "有理化分母"]),
            ("p2c_mult_binomial", [r")(\sqrt", r")×(", "雙括號"]),
            ("p2f_int_mult_rad",  [r")\s*\\times", r")\s*×", "整數與根式相乘"]),
            ("p2b_mult_distrib",  [r"\times(", r"×(", "分配律"]),
            ("p2a_mult_direct",   [r"\times\sqrt", r"×\sqrt", "直接相乘"]),
            ("p4_frac_mult",      [r"\frac{", r"分數×", "純分數"]),
            ("p3a_div_expr",      [r"\div\sqrt", r"÷\sqrt", "除以根式"]),
            ("p3b_div_simple",    [r"/\sqrt", r"有理化", "rationalize"]),
            ("p6_combo",          ["複合", "多步驟", "combined"]),
            ("p1_add_sub",        ["+", "-", "加減", "合併"]),
            ("p0_simplify",       [r"\sqrt{", "化簡", "simplify"]),
        ]

        for pid, keywords in priority:
            if any(kw in ocr for kw in keywords):
                return pid

        # Default by difficulty
        defaults = {"easy": "p0_simplify", "mid": "p1_add_sub", "hard": "p6_combo"}
        return defaults.get(difficulty, "p1_add_sub")

    # -----------------------------------------------------------------------
    # 2. Safe variable generation
    # -----------------------------------------------------------------------

    def get_safe_vars_for_pattern(
        self,
        pattern_id: str,
        difficulty: str,
        max_retries: int = 200,
        target_profile: Optional[dict] = None,
        term_count: int = None,
        style: str = "mixed",
        style_profile: Optional[str] = None,
        style_retry_pass: bool = False,
    ) -> dict:
        """
        Generate a dictionary of safe, controlled random variables for the
        given pattern and difficulty.

        All values are pure integers (no floats). The method retries up to
        max_retries times until all mathematical constraints are satisfied.

        Args:
            pattern_id:     one of the IDs from SKILL.md Pattern Catalogue
            difficulty:     "easy" | "mid" | "hard"
            max_retries:    max generation attempts before raising RuntimeError
            target_profile: optional Radical DNA dict from _build_radical_profile.
                            When provided, the generator tries to produce vars whose
                            simplifiable_count matches target_profile["simplifiable_count"].
                            If the constraint cannot be satisfied within max_retries the
                            best-effort vars (mathematically correct) are returned.
            term_count:     optional override for p1_add_sub term count.
            style:          "mixed" (default) or "simplified". When "simplified", radicands
                            are drawn only from SIMPLIFIED_RADICALS (square-free).
            style_profile:  optional teaching class from OCR / pipeline
                            (simple_radical | simplifiable_radical | fraction_radical | mixed);
                            tightens vars so format_question_LaTeX matches that class.
            style_retry_pass: when True (second exec after style mismatch), allow more retries.

        Returns:
            A dict of variables consumed by solve_problem_pattern and
            format_question_LaTeX for the given pattern_id.

        Raises:
            RuntimeError if valid vars cannot be generated within max_retries
            AND no best-effort result is available.
        """
        if style_retry_pass and style_profile:
            max_retries = max(max_retries, 380)
        elif style_profile:
            max_retries = min(max_retries, 20)

        # Radicand pool: simple_radical profile always uses square-free pool.
        if style_profile == "simple_radical":
            self._simplifiable_pool = SIMPLIFIED_RADICALS
        elif style == "simplified":
            self._simplifiable_pool = SIMPLIFIED_RADICALS
        else:
            self._simplifiable_pool = SIMPLIFIABLE_SET

        pid = pattern_id.lower().strip()
        generator_map = {
            "p0_simplify":         self._vars_p0,
            "p1_add_sub":          self._vars_p1,
            "p1b_add_sub_bracket": self._vars_p1b,
            "p1c_mixed_frac_rad_add_sub": self._vars_p1c,
            "p2a_mult_direct":     self._vars_p2a,
            "p2b_mult_distrib":    self._vars_p2b,
            "p2c_mult_binomial":   self._vars_p2c,
            "p2f_int_mult_rad":    self._vars_p2f,
            "p2g_rad_mult_frac":   self._vars_p2g_p2h,
            "p2h_frac_mult_rad":   self._vars_p2g_p2h,
            "p2d_perfect_square":  self._vars_p2d,
            "p2e_diff_of_squares": self._vars_p2e,
            "p3a_div_expr":        self._vars_p3a,
            "p3c_div_direct":      self._vars_p3c,
            "p3b_div_simple":      self._vars_p3b,
            "p4_frac_mult":        self._vars_p4,
            "p4b_frac_rad_div":    self._vars_p4b,
            "p4c_nested_frac_chain": self._vars_p4c,
            "p4d_frac_rad_div_mixed": self._vars_p4d,
            "p5a_conjugate_int":   self._vars_p5a,
            "p5b_conjugate_rad":   self._vars_p5b,
            "p6_combo":            self._vars_p6,
            "p7_mixed_rad_add":   self._vars_p7_mixed_rad_add,
        }
        if pid not in generator_map:
            raise ValueError(
                f"Unknown pattern_id '{pattern_id}'. "
                f"Valid IDs: {list(generator_map.keys())}"
            )

        target_sc = (
            target_profile.get("simplifiable_count")
            if isinstance(target_profile, dict)
            else None
        )

        best_effort_vars: Optional[dict] = None

        for attempt in range(max_retries):
            try:
                if pid == "p1_add_sub":
                    v = self._vars_p1(difficulty, term_count=term_count)
                elif pid == "p2f_int_mult_rad":
                    v = self._vars_p2f(difficulty)
                elif pid in ("p2g_rad_mult_frac", "p2h_frac_mult_rad"):
                    v = self._vars_p2g_p2h(difficulty)
                elif pid == "p6_combo":
                    v = self._vars_p6(difficulty, style_profile=style_profile)
                else:
                    v = generator_map[pid](difficulty)
                best_effort_vars = v  # always keep latest mathematically-valid vars

                if style_profile:
                    from core.code_utils.live_show_math_utils import (
                        classify_radical_style as _classify_rs,
                    )

                    if style_profile == "simple_radical":
                        sc = self.count_simplifiable_in_vars(pid, v)
                        if sc > 0:
                            raise _RetrySignal()
                        if sc == -1:
                            qchk = self.format_question_LaTeX(pid, v)
                            if _classify_rs(qchk) == "simplifiable_radical":
                                raise _RetrySignal()
                    elif style_profile == "simplifiable_radical":
                        sc = self.count_simplifiable_in_vars(pid, v)
                        if sc != -1 and sc == 0:
                            raise _RetrySignal()
                    elif style_profile == "fraction_radical":
                        qchk = self.format_question_LaTeX(pid, v)
                        if (r"\frac" not in qchk and r"\dfrac" not in qchk) or r"\sqrt" not in qchk:
                            raise _RetrySignal()
                    elif style_profile == "mixed":
                        qchk = self.format_question_LaTeX(pid, v)
                        if _classify_rs(qchk) != "mixed":
                            raise _RetrySignal()

                if target_sc is not None:
                    actual_sc = self.count_simplifiable_in_vars(pid, v)
                    # -1 means the pattern's radicand layout is not yet catalogued;
                    # skip the profile check rather than spinning endlessly.
                    if actual_sc != -1 and actual_sc != target_sc:
                        raise _RetrySignal()

                return v
            except _RetrySignal:
                continue
            except Exception as exc:
                if attempt >= max_retries - 1:
                    break
                continue

        # Profile constraint could not be met — return best-effort only when not
        # enforcing style_profile (otherwise pipeline must regen / fail visibly).
        if best_effort_vars is not None and not style_profile:
            return best_effort_vars

        if style_profile:
            raise StyleProfileExceededError(
                f"style_profile={style_profile!r} exceeded {max_retries} retries for "
                f"pattern_id={pattern_id!r} difficulty={difficulty!r}"
            )
        raise RuntimeError(
            f"get_safe_vars_for_pattern: could not generate valid vars for "
            f"'{pattern_id}' (difficulty='{difficulty}') within {max_retries} tries."
        )

    # -----------------------------------------------------------------------
    # 3. Solve (delegates to RadicalSolver)
    # -----------------------------------------------------------------------

    def solve_problem_pattern(
        self,
        pattern_id: str,
        variables: dict,
        difficulty: str = "mid",
    ) -> Tuple[str, StepList]:
        """
        純淨版：無 SymPy。p2f 由 RadicalOps 攔截（標準 LaTeX 括號）；其餘交 RadicalSolver。
        """
        pid = pattern_id.lower().strip()

        # 攔截 p2f：RadicalOps 答案；標準括號 + Healer 已辨識 \\sqrt 整項
        if pid == "p2f_int_mult_rad":
            c1 = variables.get("c1", 1)
            c2 = variables.get("c2", 1)
            r = variables.get("r", 1)

            ans_latex = RadicalOps.format_expression({r: c1 * c2})

            t1 = f"({c1})" if c1 < 0 else str(c1)

            if c2 == -1:
                raw_t2 = f"-\\sqrt{{{r}}}"
            elif c2 == 1:
                raw_t2 = f"\\sqrt{{{r}}}"
            else:
                raw_t2 = f"{c2}\\sqrt{{{r}}}"

            if c2 < 0:
                t2 = f"({raw_t2})"
            else:
                t2 = raw_t2

            step1 = f"原式 = ${t1} \\times {t2}$"

            c1_str = str(c1)
            c2_str = f"({c2})" if c2 < 0 else str(c2)
            if c2 < 0:
                step2_math = (
                    f"\\left[ {c1_str} \\times {c2_str} \\right] \\sqrt{{{r}}}"
                )
            else:
                step2_math = f"({c1_str} \\times {c2_str}) \\sqrt{{{r}}}"
            step2 = f"將括號外的整數與根式前的係數相乘：${step2_math}$"

            return ans_latex, [step1, step2, f"計算結果為：${ans_latex}$"]

        # --- 攔截 P2G / P2H（分數 × 根式）---
        if pid in ("p2g_rad_mult_frac", "p2h_frac_mult_rad"):
            k = variables.get("k", 1)
            r = variables.get("r", 1)
            num = variables.get("num", 1)
            den = variables.get("den", 1)

            ans_latex = RadicalOps.format_expression({r: k * num}, denominator=den)
            term_rad = self._format_single_fraction_radical(k, r)
            frac_str = f"\\dfrac{{{num}}}{{{den}}}"

            if pid == "p2g_rad_mult_frac":
                step1 = f"原式 = ${term_rad} \\times {frac_str}$"
            else:
                tr = term_rad
                if k < 0:
                    tr = f"\\left({tr}\\right)"
                step1 = f"原式 = ${frac_str} \\times {tr}$"

            if isinstance(k, Fraction):
                k_num, k_den = k.numerator, k.denominator
            else:
                k_num, k_den = k, 1

            s2_num, s2_den = k_num * num, k_den * den
            if s2_num == 1:
                s2_rad = rf"\sqrt{{{r}}}"
            elif s2_num == -1:
                s2_rad = rf"-\sqrt{{{r}}}"
            else:
                s2_rad = rf"{abs(s2_num)}\sqrt{{{r}}}"

            sign = "-" if s2_num < 0 else ""
            step2 = f"分子與分子相乘、分母與分母相乘：${sign}\\dfrac{{{s2_rad}}}{{{s2_den}}}$"

            return ans_latex, [step1, step2, f"化簡結果為：${ans_latex}$"]

        # --- 攔截 P4（純分數 × 分母根式分數）---
        if pid == "p4_frac_mult":
            a, b = variables.get("a", 1), variables.get("b", 1)
            r, c = variables.get("r", 1), variables.get("c", 1)
            k = variables.get("k", 1)
            swap = variables.get("swap", False)

            ans_latex = RadicalOps.format_expression({r: a * k}, denominator=b * c)

            if k == 1:
                rad_num = rf"\sqrt{{{r}}}"
            elif k == -1:
                rad_num = rf"-\sqrt{{{r}}}"
            else:
                rad_num = rf"{k}\sqrt{{{r}}}"

            frac1 = rf"\dfrac{{{a}}}{{{b}}}"
            frac2 = rf"\dfrac{{{rad_num}}}{{{c}}}"

            step1 = (
                f"原式 = ${frac2} \\times {frac1}$"
                if swap
                else f"原式 = ${frac1} \\times {frac2}$"
            )

            s2_num, s2_den = a * k, b * c
            if s2_num == 1:
                s2_rad = rf"\sqrt{{{r}}}"
            elif s2_num == -1:
                s2_rad = rf"-\sqrt{{{r}}}"
            else:
                s2_rad = rf"{abs(s2_num)}\sqrt{{{r}}}"

            sign = "-" if s2_num < 0 else ""
            step2 = (
                f"分子與分子相乘，分母與分母相乘："
                f"${sign}\\dfrac{{{s2_rad}}}{{{s2_den}}}$"
            )

            return ans_latex, [step1, step2, f"化簡結果為：${ans_latex}$"]

        return self._solver.solve_problem_pattern(pattern_id, variables, difficulty)

    # -----------------------------------------------------------------------
    # 4. Question LaTeX formatting
    # -----------------------------------------------------------------------

    def format_question_LaTeX(self, pattern_id: str, variables: dict) -> str:
        """
        Format the question text as a LaTeX-wrapped string for MathJax rendering.

        The generated code calls this INSTEAD of building LaTeX manually.
        Returns a string like: "化簡 $2\\sqrt{12} - \\sqrt{27}$。"

        Args:
            pattern_id: the pattern identifier
            variables:  the same dict returned by get_safe_vars_for_pattern

        Returns:
            A complete question_text string with $...$ LaTeX wrapping.
        """
        pid = pattern_id.lower().strip()
        if pid == "p2f_int_mult_rad":
            vars_ = variables
            c1 = vars_.get("c1", 1)
            c2 = vars_.get("c2", 1)
            r = vars_.get("r", 1)

            t1 = f"({c1})" if c1 < 0 else str(c1)

            if c2 == -1:
                raw_t2 = f"-\\sqrt{{{r}}}"
            elif c2 == 1:
                raw_t2 = f"\\sqrt{{{r}}}"
            else:
                raw_t2 = f"{c2}\\sqrt{{{r}}}"

            if c2 < 0:
                t2 = f"({raw_t2})"
            else:
                t2 = raw_t2

            return rf"化簡 ${t1} \times {t2}$。"

        formatter_map = {
            "p0_simplify":         self._fmt_p0,
            "p1_add_sub":          self._fmt_p1,
            "p1b_add_sub_bracket": self._fmt_p1b,
            "p1c_mixed_frac_rad_add_sub": self._fmt_p1c,
            "p2a_mult_direct":     self._fmt_p2a,
            "p2b_mult_distrib":    self._fmt_p2b,
            "p2c_mult_binomial":   self._fmt_p2c,
            "p2g_rad_mult_frac":   lambda v: self._fmt_p2gh(v, "p2g_rad_mult_frac"),
            "p2h_frac_mult_rad":   lambda v: self._fmt_p2gh(v, "p2h_frac_mult_rad"),
            "p2d_perfect_square":  self._fmt_p2d,
            "p2e_diff_of_squares": self._fmt_p2e,
            "p3a_div_expr":        self._fmt_p3a,
            "p3c_div_direct":      self._fmt_p3c,
            "p3b_div_simple":      self._fmt_p3b,
            "p4_frac_mult":        self._fmt_p4,
            "p4b_frac_rad_div":    self._fmt_p4b,
            "p4c_nested_frac_chain": self._fmt_p4c,
            "p4d_frac_rad_div_mixed": self._fmt_p4d,
            "p5a_conjugate_int":   self._fmt_p5a,
            "p5b_conjugate_rad":   self._fmt_p5b,
            "p6_combo":            self._fmt_p6,
            "p7_mixed_rad_add":   self._fmt_p7_mixed_rad_add,
        }
        if pid not in formatter_map:
            raise ValueError(f"Unknown pattern_id '{pattern_id}'.")
        return formatter_map[pid](variables)

    # 🚨 [新增這個方法] 這是教科書級分子根號排版器
    def _format_single_fraction_radical(self, coeff, r: int) -> str:
        """將分數係數的根式排版成標準的分子帶根號格式，例如 \dfrac{3\sqrt{7}}{4}"""
        from fractions import Fraction

        if isinstance(coeff, Fraction) and coeff.denominator != 1:
            n = abs(coeff.numerator)
            d = coeff.denominator
            sign = "-" if coeff < 0 else ""
            if n == 1:
                rad_str = rf"\sqrt{{{r}}}"
            else:
                rad_str = rf"{n}\sqrt{{{r}}}"
            return f"{sign}\\dfrac{{{rad_str}}}{{{d}}}"

        return RadicalOps.format_term_unsimplified(coeff, r, True)

    # -----------------------------------------------------------------------
    # 5. Radical DNA helpers
    # -----------------------------------------------------------------------

    def count_simplifiable_in_vars(self, pattern_id: str, variables: dict) -> int:
        """Return the number of simplifiable radicands that will appear in the
        question text for *pattern_id* given *variables*.

        A radicand N is *simplifiable* when √N can be reduced (e.g. √12 → 2√3).
        This count forms the ``simplifiable_count`` field of the Radical DNA
        profile and is used to validate that the generated question matches the
        structural complexity of the OCR input.

        Returns -1 for patterns whose radicand layout is not yet catalogued so
        callers can skip the check instead of looping endlessly.
        """
        from core.code_utils.live_show_math_utils import _has_square_factor

        pid = pattern_id.lower().strip()

        def _sc(radicands: list) -> int:
            return sum(
                1 for r in radicands
                if isinstance(r, int) and _has_square_factor(r)
            )

        if pid == "p0_simplify":
            return _sc([variables.get("r", 1)])

        if pid == "p1_add_sub":
            return _sc([t[1] for t in variables.get("terms", [])])

        if pid == "p1b_add_sub_bracket":
            return _sc([variables.get(f"r{i}") for i in range(1, 5)])

        if pid == "p1c_mixed_frac_rad_add_sub":
            return _sc([variables.get("b", 1)])

        if pid == "p2a_mult_direct":
            return _sc([variables.get("r1", 1), variables.get("r2", 1)])

        if pid == "p2f_int_mult_rad":
            return _sc([variables.get("r", 1)])

        if pid in ("p2g_rad_mult_frac", "p2h_frac_mult_rad"):
            return _sc([variables.get("r", 1)])

        if pid == "p2b_mult_distrib":
            # question: c1√r1 × (c2√r2 ± c3√r3) — r2 comes from SIMPLIFIABLE_SET
            return _sc([variables.get("r1", 1),
                        variables.get("r2", 1),
                        variables.get("r3", 1)])

        if pid == "p2c_mult_binomial":
            # question: (c1√r1 ± c2√r2)(c3√r3 ± c4) — all r from PRIME_SET
            return _sc([variables.get("r1", 1),
                        variables.get("r2", 1),
                        variables.get("r3", 1)])

        if pid == "p2d_perfect_square":
            # question: (c1√r1 ± c2√r2)² — r1, r2 from PRIME_SET → always 0
            return _sc([variables.get("r1", 1), variables.get("r2", 1)])

        if pid == "p2e_diff_of_squares":
            # question: (c1√r1 - c2√r2)(c1√r1 + c2√r2) — square-free radicands → always 0
            return _sc([variables.get("r1", 1), variables.get("r2", 1)])

        if pid == "p3a_div_expr":
            # question: (c1√r1 ± c2√r2) ÷ √denom_r
            return _sc([variables.get("r1", 1),
                        variables.get("r2", 1),
                        variables.get("denom_r", 1)])

        if pid == "p3c_div_direct":
            return _sc([variables.get("r1", 1), variables.get("r2", 1)])

        if pid == "p3b_div_simple":
            # question: a/√b — b from PRIME_SET → always 0
            return _sc([variables.get("b", 1)])

        if pid == "p4_frac_mult":
            return _sc([variables.get("r", 1)])

        if pid == "p4b_frac_rad_div":
            return _sc([variables.get("n1", 1), variables.get("d1", 1),
                       variables.get("n2", 1), variables.get("d2", 1)])

        if pid == "p4c_nested_frac_chain":
            return _sc([variables.get("n1", 1), variables.get("d1", 1),
                       variables.get("n2", 1), variables.get("d2", 1),
                       variables.get("n3", 1), variables.get("d3", 1)])

        if pid == "p4d_frac_rad_div_mixed":
            return _sc([variables.get("b", 1), variables.get("c", 1), variables.get("d", 1)])

        if pid in ("p5a_conjugate_int", "p5b_conjugate_rad"):
            # both use PRIME_SET radicands → always 0
            return 0

        if pid == "p6_combo":
            sp1 = variables.get("sub_pattern1", "")
            sp2 = variables.get("sub_pattern2", "")
            c1 = self.count_simplifiable_in_vars(sp1, variables.get("vars1", {})) if sp1 else 0
            c2 = self.count_simplifiable_in_vars(sp2, variables.get("vars2", {})) if sp2 else 0
            return (c1 if c1 != -1 else 0) + (c2 if c2 != -1 else 0)

        if pid == "p7_mixed_rad_add":
            return 2  # both radicands (n1/d1, n2/d2) are perfect squares

        return -1  # unknown — caller should skip the profile check

    def get_radical_profile(self, question_text: str) -> dict:
        """Return the Radical DNA profile of a *question_text* string.

        Delegates to ``_build_radical_profile`` in live_show_math_utils.
        Use this to inspect what the DomainFunctionHelper actually generated
        and compare it against the OCR target profile.

        Returns:
            dict with keys: rad_count, simplifiable_count,
                            rationalize_count, radicands
        """
        from core.code_utils.live_show_math_utils import _build_radical_profile
        return _build_radical_profile(question_text)

    # =======================================================================
    # Variable generators (private)
    # =======================================================================

    def _vars_p0(self, difficulty: str) -> dict:
        r = random.choice(SIMPLIFIABLE_SET)
        _, simplified_r = _simplify_rad(1, r)
        if simplified_r == r:
            raise _RetrySignal()
        return {"r": r}

    def _vars_p1(self, difficulty: str, term_count: int = None) -> dict:
        if term_count is not None and term_count >= 2:
            n_terms = term_count
        else:
            n_terms = {"easy": 2, "mid": 3, "hard": 4}.get(difficulty, 2)
        terms = []
        pool = getattr(self, "_simplifiable_pool", SIMPLIFIABLE_SET)
        for i in range(n_terms):
            c = random.choice(NON_ZERO_COEFF)
            r = random.choice(pool)
            op = "+" if i == 0 else random.choice(["+", "-"])
            terms.append((c, r, op))

        # Validate: at least two terms should simplify to same radicand
        simplified_radicands = [_simplify_rad(1, t[1])[1] for t in terms]
        if len(set(simplified_radicands)) == len(simplified_radicands):
            raise _RetrySignal()  # all distinct — no combination possible

        return {"terms": terms}

    def _vars_p1b(self, difficulty: str) -> dict:
        pool = getattr(self, "_simplifiable_pool", SIMPLIFIABLE_SET)
        return {
            "c1": random.choice(NON_ZERO_COEFF), "r1": random.choice(pool),
            "c2": random.choice(NON_ZERO_COEFF), "r2": random.choice(pool),
            "c3": random.choice(NON_ZERO_COEFF), "r3": random.choice(pool),
            "c4": random.choice(NON_ZERO_COEFF), "r4": random.choice(pool),
            "op_bracket": random.choice(["+", "-"]),
        }

    def _vars_p1c(self, difficulty: str) -> dict:
        b = random.choice([2, 3, 5])
        return {
            "a": random.randint(1, 5),
            "b": b,
            "c": random.randint(1, 5),
            "d": random.choice([2, 3, 4, 5, 6]),
            "op": random.choice(["+", "-"]),
        }

    def _vars_p2a(self, difficulty: str) -> dict:
        base = getattr(self, "_simplifiable_pool", SIMPLIFIABLE_SET)
        pool = base if difficulty != "easy" else (base[:6] if len(base) >= 6 else base)
        c1 = random.choice(NON_ZERO_COEFF)
        c2 = random.choice(NON_ZERO_COEFF)
        r1 = random.choice(pool)
        r2 = random.choice(pool)
        return {"c1": c1, "r1": r1, "c2": c2, "r2": r2}

    def _vars_p2b(self, difficulty: str) -> dict:
        c1 = random.choice([c for c in NON_ZERO_COEFF if abs(c) <= 3])
        r1 = random.choice(PRIME_SET)
        c2 = random.choice([c for c in NON_ZERO_COEFF if abs(c) <= 3])
        r2 = random.choice(getattr(self, "_simplifiable_pool", SIMPLIFIABLE_SET))
        c3 = random.choice([c for c in NON_ZERO_COEFF if abs(c) <= 3])
        r3 = random.choice(PRIME_SET)
        op = random.choice(["+", "-"])
        return {"c1": c1, "r1": r1, "c2": c2, "r2": r2, "c3": c3, "r3": r3, "op": op}

    def _vars_p2c(self, difficulty: str) -> dict:
        c1 = random.choice([c for c in NON_ZERO_COEFF if abs(c) <= 3])
        r1 = random.choice(PRIME_SET)
        c2 = random.choice([c for c in NON_ZERO_COEFF if abs(c) <= 3])
        r2 = random.choice(PRIME_SET)
        c3 = random.choice([c for c in NON_ZERO_COEFF if abs(c) <= 3])
        r3 = random.choice(PRIME_SET)
        c4 = random.choice([c for c in NON_ZERO_COEFF if abs(c) <= 4])
        return {"c1": c1, "r1": r1, "c2": c2, "r2": r2,
                "c3": c3, "r3": r3, "c4": c4, "r4": 1}

    def _vars_p2d(self, difficulty: str) -> dict:
        """P2d: Perfect-square expansion (c1√r1 ± c2√r2)²."""
        c1 = random.choice([c for c in range(1, 5)])
        c2 = random.choice([c for c in range(1, 5)])
        r1 = random.choice(PRIME_SET)
        r2 = random.choice([r for r in PRIME_SET if r != r1])
        op = random.choice(["+", "-"])
        return {"c1": c1, "r1": r1, "c2": c2, "r2": r2, "op": op}

    def _vars_p2e(self, difficulty: str) -> dict:
        """P2e: Difference-of-squares (c1√r1 - c2√r2)(c1√r1 + c2√r2)."""
        # r1 can be 1 (pure integer term) to allow e.g. (3 - √2)(3 + √2)
        SQFREE = [1, 2, 3, 5, 6, 7]
        c1 = random.choice(range(1, 5))
        c2 = random.choice(range(1, 5))
        r1 = random.choice(SQFREE)
        r2 = random.choice([r for r in SQFREE if r != r1])
        return {"c1": c1, "r1": r1, "c2": c2, "r2": r2}

    def _vars_p2f(self, difficulty: str) -> dict:
        """P2f: Integer × radical k₁ × k₂√r. c1 can be negative (parentheses)."""
        c1 = random.choice([-6, -5, -4, -3, -2, 2, 3, 4, 5, 6])
        c2 = random.choice([-4, -3, -2, 2, 3, 4])
        r = random.choice([2, 3, 5, 6, 7, 11])
        return {"c1": c1, "c2": c2, "r": r}

    def _vars_p2g_p2h(self, difficulty: str) -> dict:
        """P2g/P2h: k√r × (num/den) or (num/den) × k√r. Pure radical × pure fraction."""
        k = random.choice([-5, -4, -3, -2, 2, 3, 4, 5])
        r = random.choice([2, 3, 5, 6, 7])
        num = random.choice([1, 2, 3, 4, 5])
        den = random.choice([2, 3, 4, 5, 6])
        while num == den:
            den = random.choice([2, 3, 4, 5, 6])
        return {"k": k, "r": r, "num": num, "den": den}

    def _vars_p3a(self, difficulty: str) -> dict:
        for _ in range(50):
            c1 = random.choice([c for c in NON_ZERO_COEFF if abs(c) <= 4])
            r1 = random.choice(getattr(self, "_simplifiable_pool", SIMPLIFIABLE_SET))
            c2 = random.choice([c for c in NON_ZERO_COEFF if abs(c) <= 3])
            r2 = random.choice(PRIME_SET)
            d = random.choice(PRIME_SET)
            op = random.choice(["+", "-"])
            c2_signed = c2 if op == "+" else -c2

            # Verify both terms rationalize cleanly
            valid = True
            for coeff, radicand in [(c1, r1), (c2_signed, r2)]:
                if radicand % d == 0:
                    continue
                nc_raw, _ = _simplify_rad(coeff, radicand * d)
                if nc_raw % d != 0:
                    valid = False
                    break
            if valid:
                return {"c1": c1, "r1": r1, "c2": c2, "r2": r2, "denom_r": d, "op": op}
        raise _RetrySignal()

    def _vars_p3c(self, difficulty: str) -> dict:
        """P3c: Direct division k₁√r₁ ÷ k₂√r₂. r2 from [2,3,5,7], r1 = r2*k for nice division."""
        R2_POOL = [2, 3, 5, 7]
        K_POOL = [2, 3, 5, 6, 7, 10]
        c1 = random.choice([c for c in range(-15, 16) if c != 0])
        c2 = random.choice([c for c in range(-15, 16) if c != 0])
        r2 = random.choice(R2_POOL)
        k = random.choice(K_POOL)
        r1 = r2 * k
        return {"c1": c1, "r1": r1, "c2": c2, "r2": r2}

    def _vars_p3b(self, difficulty: str) -> dict:
        a = random.choice([c for c in range(1, 6)])
        b = random.choice(PRIME_SET)
        return {"a": a, "b": b}

    def _vars_p4(self, difficulty: str) -> dict:
        a = random.randint(1, 5)
        b = random.choice(SMALL_DENOM)
        r = random.choice(getattr(self, "_simplifiable_pool", SIMPLIFIABLE_SET))
        c = random.choice(SMALL_DENOM)
        return {"a": a, "b": b, "r": r, "c": c}

    def _vars_p4b(self, difficulty: str) -> dict:
        """P4b: (√n1/√d1) ÷ (√n2/√d2). Square-free integers."""
        SQFREE = [2, 3, 5, 6, 7, 10, 11, 13, 14, 15, 21, 22, 33]
        n1 = random.choice(SQFREE)
        d1 = random.choice([x for x in SQFREE if x != n1])
        n2 = random.choice(SQFREE)
        d2 = random.choice([x for x in SQFREE if x != n2])
        return {"n1": n1, "d1": d1, "n2": n2, "d2": d2}

    def _vars_p4c(self, difficulty: str) -> dict:
        """P4c: √(n1/d1) × √(n2/d2) ÷ √(n3/d3)."""
        n1 = random.choice([1, 2, 3])
        n2 = random.choice([1, 2, 3])
        n3 = random.choice([1, 2, 3])
        d1 = random.choice([2, 3, 5, 6, 7])
        d2 = random.choice([2, 3, 5, 6, 7])
        d3 = random.choice([2, 3, 5, 6, 7])
        return {"n1": n1, "d1": d1, "n2": n2, "d2": d2, "n3": n3, "d3": d3}

    def _vars_p4d(self, difficulty: str) -> dict:
        """P4d: (a/√b) ÷ (√c/√d)."""
        return {
            "a": random.randint(1, 5),
            "b": random.choice([2, 3, 5, 7]),
            "c": random.choice([2, 3, 5, 6, 7, 10]),
            "d": random.choice([2, 3, 5, 6, 7]),
        }

    def _vars_p5a(self, difficulty: str) -> dict:
        for _ in range(50):
            b = random.choice([1, 2, 3])
            q = random.choice(PRIME_SET)
            c = random.randint(1, 4)
            sign = random.choice([1, -1])
            denom = b * b * q - c * c
            if denom != 0:
                return {"b": b, "q": q, "c": c, "sign": sign}
        raise _RetrySignal()

    def _vars_p5b(self, difficulty: str) -> dict:
        for _ in range(50):
            p = random.choice(PRIME_SET)
            b = random.choice([1, 2, 3])
            q = random.choice(PRIME_SET)
            c = random.randint(1, 5)
            sign = random.choice([1, -1])
            denom = b * b * q - c * c
            if denom != 0 and p != q:
                return {"p": p, "b": b, "q": q, "c": c, "sign": sign}
        raise _RetrySignal()

    def _vars_p6(self, difficulty: str, style_profile: Optional[str] = None) -> dict:
        """Compose two sub-patterns for the multi-step combination."""
        combos_default = [
            ("p2b_mult_distrib", "p1_add_sub"),
            ("p3b_div_simple", "p1_add_sub"),
            ("p5a_conjugate_int", "p1_add_sub"),
        ]
        combos_mixed = [
            ("p2h_frac_mult_rad", "p1_add_sub"),
            ("p2g_rad_mult_frac", "p1_add_sub"),
            ("p4_frac_mult", "p0_simplify"),
            ("p4_frac_mult", "p2a_mult_direct"),
            ("p2h_frac_mult_rad", "p2a_mult_direct"),
        ]
        combos_simple = [
            ("p2a_mult_direct", "p1_add_sub"),
            ("p2b_mult_distrib", "p1_add_sub"),
            ("p2c_mult_binomial", "p1_add_sub"),
        ]
        if style_profile == "mixed":
            combos = combos_mixed
        elif style_profile == "simple_radical":
            combos = combos_simple
        elif style_profile == "fraction_radical":
            combos = combos_mixed
        else:
            combos = combos_default
        sp1, sp2 = random.choice(combos)
        combo_op = random.choice(["+", "-"])
        return {
            "sub_pattern1": sp1,
            "vars1": self.get_safe_vars_for_pattern(
                sp1, difficulty, max_retries=120, style_profile=None
            ),
            "sub_pattern2": sp2,
            "vars2": self.get_safe_vars_for_pattern(
                sp2, difficulty, max_retries=120, style_profile=None
            ),
            "combo_op": combo_op,
        }

    def _vars_p7_mixed_rad_add(self, difficulty: str) -> dict:
        """P7: √(w+n/d) ± √(w+n/d) — reverse-engineer perfect-square mixed numbers."""
        d1_root = random.choice([2, 3, 4])
        n1_root = d1_root + random.choice([1, 2])
        d1, n1 = d1_root**2, n1_root**2
        w1, f_n1 = n1 // d1, n1 % d1

        d2_root = random.choice([3, 4, 5, 6])
        n2_root = d2_root * 2 + random.choice([1, 5])
        d2, n2 = d2_root**2, n2_root**2
        w2, f_n2 = n2 // d2, n2 % d2

        op = random.choice(["+", "-"])
        return {
            "w1": w1, "f_n1": f_n1, "d1": d1, "n1": n1,
            "w2": w2, "f_n2": f_n2, "d2": d2, "n2": n2,
            "op": op,
        }

    # =======================================================================
    # Question formatters (private)
    # =======================================================================

    def _fmt_p0(self, v: dict) -> str:
        r = v["r"]
        return rf"化簡 ${RadicalOps.format_term_unsimplified(1, r, True)}$。"

    def _fmt_p1(self, v: dict) -> str:
        terms = v["terms"]
        parts = []
        for i, (coeff, radicand, op) in enumerate(terms):
            is_first = (i == 0)
            if is_first:
                parts.append(RadicalOps.format_term_unsimplified(coeff, radicand, True))
            else:
                parts.append(RadicalOps.format_term_unsimplified(
                    coeff if op == "+" else -coeff, radicand, False
                ))
        expr = "".join(parts)
        return rf"化簡 ${expr}$。"

    def _fmt_p1b(self, v: dict) -> str:
        t1 = self._fmt_term(v["c1"], v["r1"], True)
        t2 = self._fmt_term(v["c2"], v["r2"], False)
        t3 = self._fmt_term(v["c3"], v["r3"], True)
        t4 = self._fmt_term(v["c4"], v["r4"], False)

        op_bracket = " + " if v["op_bracket"] == "+" else " - "
        return rf"化簡 ${t1}{t2}{op_bracket}({t3}{t4})$。"

    def _fmt_p1c(self, v: dict) -> str:
        c, d, b = v["c"], v["d"], v["b"]
        coeff = Fraction(c, d) if v["op"] == "+" else -Fraction(c, d)
        tail = RadicalOps.format_term_unsimplified(coeff, b, False)
        return rf"化簡 $\dfrac{{{v['a']}}}{{\sqrt{{{b}}}}}{tail}$。"

    def _fmt_p2a(self, v: dict) -> str:
        """P2a: k₁√r₁ × k₂√r₂ — 根式一律經 RadicalOps。"""
        c1, r1 = v["c1"], v["r1"]
        c2, r2 = v["c2"], v["r2"]
        term1 = RadicalOps.format_term_unsimplified(c1, r1, True)
        term2 = RadicalOps.format_term_unsimplified(c2, r2, True)
        if c2 < 0:
            term2 = f"({term2})"
        if c1 < 0 and c1 != -1:
            term1 = f"({term1})"
        return rf"化簡 ${term1} \times {term2}$。"

    def _fmt_p2gh(self, v: dict, pattern_id: str) -> str:
        """P2g: k√r × (num/den). P2h: (num/den) × k√r."""
        k, r, num, den = v["k"], v["r"], v["num"], v["den"]
        frac_str = f"\\frac{{{num}}}{{{den}}}"
        term_rad = RadicalOps.format_term_unsimplified(k, r, True)
        if k < 0 and pattern_id == "p2h_frac_mult_rad":
            term_rad = f"({term_rad})"
        if pattern_id == "p2g_rad_mult_frac":
            inner = f"{term_rad} \\times {frac_str}"
        else:
            inner = f"{frac_str} \\times {term_rad}"
        return rf"化簡 ${inner}$。"

    def _fmt_term(self, c: int, r: int, is_first: bool = True) -> str:
        """根式／整數項 LaTeX，對齊 RadicalOps。"""
        if c == 0:
            return ""
        return RadicalOps.format_term_unsimplified(c, r, is_leading=is_first)

    def _fmt_p2b(self, v: dict) -> str:
        c1, r1 = v["c1"], v["r1"]
        c2, r2 = v["c2"], v["r2"]
        c3, r3 = v["c3"], v["r3"]
        op = v.get("op", "+")
        c3_display = c3 if op == "+" else -c3
        
        q1 = self._fmt_term(c1, r1, True)
        q2 = self._fmt_term(c2, r2, True)
        q3 = self._fmt_term(c3_display, r3, False)
        return rf"化簡 ${q1} \times ({q2}{q3})$。"

    def _fmt_p2c(self, v: dict) -> str:
        c1, r1 = v["c1"], v["r1"]
        c2, r2 = v.get("c2", 0), v.get("r2", 1)
        c3, r3 = v["c3"], v["r3"]
        c4 = v.get("c4", 0)
        
        t1 = self._fmt_term(c1, r1, True)
        t2 = self._fmt_term(c2, r2, False)
        t3 = self._fmt_term(c3, r3, True)
        t4 = self._fmt_term(c4, 1, False)  # r=1 handles the pure integer case
        return rf"化簡 $({t1}{t2})({t3}{t4})$。"

    def _fmt_p2d(self, v: dict) -> str:
        """P2d: Format (c1√r1 ± c2√r2)²."""
        c1, r1 = v["c1"], v["r1"]
        c2, r2 = v["c2"], v["r2"]
        op = v.get("op", "+")
        t1 = RadicalOps.format_term_unsimplified(c1, r1, True)
        t2 = RadicalOps.format_term_unsimplified(c2, r2, True)
        op_str = "+" if op == "+" else "-"
        return rf"展開化簡 $({t1} {op_str} {t2})^2$。"

    def _fmt_p2e(self, v: dict) -> str:
        """P2e: Format (c1√r1 - c2√r2)(c1√r1 + c2√r2)."""
        c1, r1 = v["c1"], v["r1"]
        c2, r2 = v["c2"], v["r2"]
        # r=1 means pure integer: render as c1, not c1√1
        t1 = str(c1 * r1) if r1 == 1 else RadicalOps.format_term_unsimplified(c1, r1, True)
        t2 = str(c2 * r2) if r2 == 1 else RadicalOps.format_term_unsimplified(c2, r2, True)
        return rf"展開化簡 $({t1} - {t2})({t1} + {t2})$。"

    def _fmt_p3a(self, v: dict) -> str:
        c1, r1 = v["c1"], v["r1"]
        c2, r2 = v.get("c2", 0), v.get("r2", 1)
        op = v.get("op", "+")
        d = v["denom_r"]
        c2_display = c2 if op == "+" else -c2
        q1 = RadicalOps.format_term_unsimplified(c1, r1, True)
        q2 = RadicalOps.format_term_unsimplified(c2_display, r2, False) if c2 else ""
        return rf"化簡 $({q1}{q2}) \div \sqrt{{{d}}}$。"

    def _fmt_p3c(self, v: dict) -> str:
        """P3c: (c1√r1) ÷ (c2√r2)。"""
        c1, r1 = v["c1"], v["r1"]
        c2, r2 = v["c2"], v["r2"]
        term1 = RadicalOps.format_term_unsimplified(c1, r1, True)
        term2 = RadicalOps.format_term_unsimplified(c2, r2, True)
        if c1 < 0:
            term1 = f"({term1})"
        if c2 < 0:
            term2 = f"({term2})"
        return rf"化簡 ${term1} \div {term2}$。"

    def _fmt_p3b(self, v: dict) -> str:
        a, b = v["a"], v["b"]
        return rf"化簡 $\dfrac{{{a}}}{{\sqrt{{{b}}}}}$。"

    def _fmt_p4(self, v: dict) -> str:
        a, b, r, c = v["a"], v["b"], v["r"], v["c"]
        sr = RadicalOps.format_term_unsimplified(1, r, True)
        return rf"計算 $\dfrac{{{a}}}{{{b}}} \times \dfrac{{{sr}}}{{{c}}}$ 的值。"

    def _fmt_p4b(self, v: dict) -> str:
        """P4b: (√n1/√d1) ÷ (√n2/√d2)."""
        n1, d1 = v["n1"], v["d1"]
        n2, d2 = v["n2"], v["d2"]
        t1, t2 = (
            RadicalOps.format_term_unsimplified(1, n1, True),
            RadicalOps.format_term_unsimplified(1, d1, True),
        )
        t3, t4 = (
            RadicalOps.format_term_unsimplified(1, n2, True),
            RadicalOps.format_term_unsimplified(1, d2, True),
        )
        return rf"化簡 $\dfrac{{{t1}}}{{{t2}}} \div \dfrac{{{t3}}}{{{t4}}}$。"

    def _fmt_p4c(self, v: dict) -> str:
        """P4c: √(n1/d1) × √(n2/d2) ÷ √(n3/d3)."""
        n1, d1 = v["n1"], v["d1"]
        n2, d2 = v["n2"], v["d2"]
        n3, d3 = v["n3"], v["d3"]
        return rf"化簡 $\sqrt{{\dfrac{{{n1}}}{{{d1}}}}} \times \sqrt{{\dfrac{{{n2}}}{{{d2}}}}} \div \sqrt{{\dfrac{{{n3}}}{{{d3}}}}}$。"

    def _fmt_p4d(self, v: dict) -> str:
        """P4d: (a/√b) ÷ (√c/√d)."""
        return rf"計算 $\dfrac{{{v['a']}}}{{\sqrt{{{v['b']}}}}} \div \dfrac{{\sqrt{{{v['c']}}}}}{{\sqrt{{{v['d']}}}}}$ 的值。"

    def _fmt_p5a(self, v: dict) -> str:
        b, q, c, sign = v["b"], v["q"], v["c"], v["sign"]
        b_str = "" if b == 1 else str(b)
        sign_str = "+" if sign == 1 else "-"
        return rf"化簡 $\dfrac{{1}}{{{b_str}\sqrt{{{q}}}{sign_str}{c}}}$。"

    def _fmt_p5b(self, v: dict) -> str:
        p, b, q, c, sign = v["p"], v["b"], v["q"], v["c"], v["sign"]
        b_str = "" if b == 1 else str(b)
        sign_str = "+" if sign == 1 else "-"
        return rf"化簡 $\dfrac{{\sqrt{{{p}}}}}{{{b_str}\sqrt{{{q}}}{sign_str}{c}}}$。"

    def _fmt_p6(self, v: dict) -> str:
        sp1 = v.get("sub_pattern1", "?")
        sp2 = v.get("sub_pattern2", "?")
        v1, v2 = v.get("vars1"), v.get("vars2")
        if isinstance(v1, dict) and isinstance(v2, dict) and sp1 != "?" and sp2 != "?":
            q1 = self.format_question_LaTeX(sp1, v1).rstrip("。").strip()
            q2 = self.format_question_LaTeX(sp2, v2).strip()
            return f"{q1}；{q2}。"
        return rf"計算下列複合根式運算（子題型：{sp1} 與 {sp2}）。"

    def _fmt_p7_mixed_rad_add(self, v: dict) -> str:
        """P7: √(w+n/d) ± √(w+n/d) 帶分數根式加減."""
        op_str = " + " if v["op"] == "+" else " - "
        return (
            rf"計算 $\sqrt{{{v['w1']}\frac{{{v['f_n1']}}}{{{v['d1']}}}}}"
            rf"{op_str}\sqrt{{{v['w2']}\frac{{{v['f_n2']}}}{{{v['d2']}}}}}$ 的值。"
        )

    # =======================================================================
    # Internal utilities
    # =======================================================================

    def _combine_latex_answers(
        self, ans1: str, ans2: str, op: str
    ) -> TermsDict:
        """
        Attempt to symbolically combine two LaTeX answer strings.

        This is a best-effort parser for simple forms like:
            "3\\sqrt{2}", "-\\sqrt{5}", "4", "\\frac{2\\sqrt{3}}{5}"

        Returns a TermsDict if successful, else raises ValueError so the
        caller can fall back to string concatenation.
        """
        def _parse_simple(s: str) -> TermsDict:
            s = s.strip()
            # Integer-only answer
            if s.lstrip("-").isdigit():
                return {1: int(s)}
            # k√r form
            import re
            m = re.fullmatch(
                r"(-?)(\d*)\s*\\sqrt\{(\d+)\}", s
            )
            if m:
                neg, k_str, r_str = m.groups()
                k = int(k_str) if k_str else 1
                r = int(r_str)
                return {r: -k if neg else k}
            raise ValueError(f"Cannot parse answer '{s}' for symbolic combination.")

        t1 = _parse_simple(ans1)
        t2 = _parse_simple(ans2)
        if op == "-":
            t2 = {r: -c for r, c in t2.items()}
        merged = {}
        for d, c in {**t1, **t2}.items():
            merged[d] = merged.get(d, 0) + c
        return _merge_terms(merged)


# ---------------------------------------------------------------------------
# Internal sentinel for clean retry signalling
# ---------------------------------------------------------------------------

class _RetrySignal(Exception):
    """Raised inside variable generators to trigger a retry loop cleanly."""
    pass


class StyleProfileExceededError(RuntimeError):
    """Raised when style_profile constraint cannot be satisfied within max retries."""
