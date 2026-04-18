from __future__ import annotations

import random
import re
from fractions import Fraction
from typing import Any


def _trim_zero_poly(coeffs: dict[int, Fraction]) -> dict[int, Fraction]:
    return {int(k): Fraction(v) for k, v in coeffs.items() if Fraction(v) != 0}


def _poly_add(a: dict[int, Fraction], b: dict[int, Fraction]) -> dict[int, Fraction]:
    out = dict(a)
    for exp, coeff in b.items():
        out[exp] = out.get(exp, Fraction(0)) + Fraction(coeff)
    return _trim_zero_poly(out)


def _poly_sub(a: dict[int, Fraction], b: dict[int, Fraction]) -> dict[int, Fraction]:
    out = dict(a)
    for exp, coeff in b.items():
        out[exp] = out.get(exp, Fraction(0)) - Fraction(coeff)
    return _trim_zero_poly(out)


def _poly_mul(a: dict[int, Fraction], b: dict[int, Fraction]) -> dict[int, Fraction]:
    out: dict[int, Fraction] = {}
    for e1, c1 in a.items():
        for e2, c2 in b.items():
            out[e1 + e2] = out.get(e1 + e2, Fraction(0)) + Fraction(c1) * Fraction(c2)
    return _trim_zero_poly(out)


def _poly_scalar_mul(a: dict[int, Fraction], k: Fraction) -> dict[int, Fraction]:
    return _trim_zero_poly({exp: Fraction(coeff) * Fraction(k) for exp, coeff in a.items()})


def _poly_degree(a: dict[int, Fraction]) -> int:
    return max(a.keys()) if a else -1


def _poly_long_division(
    dividend: dict[int, Fraction],
    divisor: dict[int, Fraction],
) -> tuple[dict[int, Fraction], dict[int, Fraction]]:
    divisor = _trim_zero_poly(divisor)
    if not divisor:
        raise ValueError("division by zero polynomial")

    remainder = dict(dividend)
    quotient: dict[int, Fraction] = {}
    div_deg = _poly_degree(divisor)
    div_lead = divisor[div_deg]

    while remainder and _poly_degree(remainder) >= div_deg:
        rem_deg = _poly_degree(remainder)
        rem_lead = remainder[rem_deg]
        q_exp = rem_deg - div_deg
        q_coeff = Fraction(rem_lead, div_lead)
        quotient[q_exp] = quotient.get(q_exp, Fraction(0)) + q_coeff
        subtract_poly = _poly_scalar_mul({exp + q_exp: coeff for exp, coeff in divisor.items()}, q_coeff)
        remainder = _poly_sub(remainder, subtract_poly)

    return _trim_zero_poly(quotient), _trim_zero_poly(remainder)


def _fraction_to_text(val: Fraction) -> str:
    if val.denominator == 1:
        return str(val.numerator)
    return f"{val.numerator}/{val.denominator}"


def _fraction_to_latex(val: Fraction) -> str:
    if val.denominator == 1:
        return str(val.numerator)
    return f"\\frac{{{val.numerator}}}{{{val.denominator}}}"


class PolynomialFunctionHelper:
    def normalize_text(self, text: str) -> str:
        s = str(text or "").strip()
        repl = {
            "（": "(",
            "）": ")",
            "［": "[",
            "］": "]",
            "【": "[",
            "】": "]",
            "＋": "+",
            "－": "-",
            "−": "-",
            "×": "*",
            "·": "*",
            "．": "*",
            "＊": "*",
            "÷": "/",
            "／": "/",
            "　": "",
            " ": "",
        }
        for old, new in repl.items():
            s = s.replace(old, new)
        s = re.sub(r"\\frac\{([^{}]+)\}\{([^{}]+)\}", r"(\1/\2)", s)
        s = re.sub(r"\((-?\d+(?:/\d+)?)\)x\^", r"\1x^", s)
        s = re.sub(r"\((-?\d+(?:/\d+)?)\)x(?![\^A-Za-z0-9])", r"\1x", s)
        s = s.replace("\\left", "").replace("\\right", "")
        s = s.replace("[", "(").replace("]", ")")
        s = s.replace("\\cdot", "*").replace("\\times", "*").replace("\\div", "/")
        s = s.replace("{", "").replace("}", "")
        s = s.replace("$", "")
        s = s.replace("。", "")
        s = s.replace("：", ":")
        return s

    def split_subquestions(self, text: str) -> list[str]:
        src = str(text or "").strip()
        if not src:
            return []
        cleaned = src.replace("\r", "")
        parts = re.split(r"[⑴⑵⑶⑷⑸]\s*", cleaned)
        out = []
        for part in parts:
            part = part.strip().strip('"').strip()
            if part:
                out.append(part)
        return out or [src]

    def _has_all_keywords(self, text: str, *keywords: str) -> bool:
        content = str(text or "")
        return all(keyword in content for keyword in keywords)

    def _looks_like_reverse_division_word_problem(self, text: str) -> bool:
        content = str(text or "")
        return (
            re.search(r"[A-Z]", content) is not None
            and self._has_all_keywords(content, "\u9664\u4ee5", "\u5546\u5f0f", "\u9918\u5f0f")
        )

    def _looks_like_trapezoid_height_problem(self, text: str) -> bool:
        content = str(text or "")
        return (
            self._has_all_keywords(content, "\u68af\u5f62", "\u9762\u7a4d", "\u9ad8")
            and any(keyword in content for keyword in ("\u4e0a\u5e95", "\u4e0b\u5e95"))
        )

    def _looks_like_composite_region_problem(self, text: str) -> bool:
        content = str(text or "")
        return self._has_all_keywords(content, "\u9577\u65b9\u5f62", "\u5468\u9577", "\u9762\u7a4d")

    def can_handle(self, question_text: str) -> bool:
        try:
            return bool(self.build_config(question_text))
        except Exception:
            return False

    def build_generator_code(self, question_text: str) -> str:
        config = self.build_config(question_text)
        config_repr = repr(config)
        return f"""import re
from fractions import Fraction
from core.polynomial_domain_functions import PolynomialFunctionHelper

_POLY_HELPER = PolynomialFunctionHelper()
_POLY_CONFIG = {config_repr}

def generate(level=1, **kwargs):
    return _POLY_HELPER.generate_from_config(_POLY_CONFIG)

def check(user_answer, correct_answer):
    def _norm(text):
        s = str(text or "").strip().replace(" ", "")
        s = s.replace("（", "(").replace("）", ")")
        s = s.replace("＋", "+").replace("－", "-").replace("−", "-")
        return s
    u = _norm(user_answer)
    c = _norm(correct_answer)
    return {{"correct": u == c, "result": "正確" if u == c else "錯誤"}}
"""

    def build_config(self, question_text: str) -> dict[str, Any]:
        src = str(question_text or "").strip()
        norm = self.normalize_text(src)
        variable = self.detect_variable(norm)
        if self._looks_like_reverse_division_word_problem(src):
            return self.build_reverse_division_config(src, norm, variable)
        if self._looks_like_trapezoid_height_problem(src):
            return {
                "family": "poly_geom_formula_direct",
                "source_text": src,
                "variable": variable,
            }
        if self._looks_like_composite_region_problem(src):
            return {
                "family": "poly_geom_region_composite",
                "source_text": src,
                "variable": variable,
            }
        if "除以" in src and "商式為" in src and "餘式為" in src:
            return self.build_reverse_division_config(src, norm, variable)
        if "梯形" in src and "面積" in src and "高" in src:
            return {
                "family": "poly_geom_formula_direct",
                "source_text": src,
                "variable": variable,
            }
        if "周長" in src and "面積" in src and "長方形" in src:
            return {
                "family": "poly_geom_region_composite",
                "source_text": src,
                "variable": variable,
            }
        family = self.detect_family(src)
        config: dict[str, Any] = {
            "family": family,
            "source_text": src,
            "variable": variable,
        }

        if family in {
            "poly_add_sub_flat",
            "poly_add_sub_nested",
            "poly_mul_monomial",
            "poly_mul_poly",
            "poly_mul_special_identity",
            "poly_mixed_simplify",
        }:
            if family == "poly_mul_monomial" and "\\frac" in src:
                config["fraction_product"] = True
                return config
            expr = self.extract_expression(src)
            config["ast"] = self.parse_expr(expr, variable)
            return config

        if family == "poly_add_sub_unknown":
            lhs, rhs = self.extract_equation(norm)
            unknown_name = re.search(r"\b([A-Z])\b", lhs) or re.search(r"\b([A-Z])\b", rhs)
            unknown = unknown_name.group(1) if unknown_name else "A"
            side = "lhs" if unknown in lhs else "rhs"
            config.update({
                "unknown_name": unknown,
                "unknown_side": side,
                "lhs_template": self.parse_equation_side(lhs, unknown, variable),
                "rhs_template": self.parse_equation_side(rhs, unknown, variable),
            })
            return config

        if family in {"poly_div_monomial_eval", "poly_div_monomial_qr", "poly_div_poly_qr"}:
            dividend_text, divisor_text = self.extract_division_operands(src)
            config.update({
                "dividend_template": self.parse_poly(dividend_text, variable),
                "divisor_template": self.parse_poly(divisor_text, variable),
            })
            return config

        if family == "poly_div_reverse":
            return self.build_reverse_division_config(src, norm, variable)

        if family in {"poly_geom_formula_direct", "poly_geom_region_composite"}:
            return config

        raise ValueError(f"Unsupported polynomial family: {family}")

    def structure_signature(self, question_text: str) -> dict[str, Any]:
        config = self.build_config(question_text)
        return {
            "family": config["family"],
            "variable": config.get("variable", "x"),
            "signature": self._signature_from_config(config),
        }

    def same_family_and_structure(self, source_text: str, generated_text: str) -> tuple[bool, str, dict[str, Any], dict[str, Any]]:
        src = self.structure_signature(source_text)
        gen = self.structure_signature(generated_text)
        if src["family"] != gen["family"]:
            return False, f"family mismatch: {src['family']} != {gen['family']}", src, gen
        if src["signature"] != gen["signature"]:
            return False, f"signature mismatch: {src['signature']} != {gen['signature']}", src, gen
        return True, "", src, gen

    def detect_variable(self, text: str) -> str:
        match = re.search(r"[a-z]", text)
        return match.group(0) if match else "x"

    def detect_family(self, question_text: str) -> str:
        norm = self.normalize_text(question_text)
        segments = self.extract_math_segments(question_text)
        expr = self.extract_expression(question_text)
        expr_norm = self.normalize_text(expr)
        has_div_signal = ("除以" in question_text) or ("\\div" in question_text) or ("÷" in question_text)
        has_mul_signal = ("\\times" in question_text) or ("×" in question_text) or ("·" in question_text) or ("．" in question_text)
        raw_text = str(question_text or "")
        if self._looks_like_reverse_division_word_problem(raw_text):
            return "poly_div_reverse"
        if self._looks_like_composite_region_problem(raw_text):
            return "poly_geom_region_composite"
        if self._looks_like_trapezoid_height_problem(raw_text):
            return "poly_geom_formula_direct"
        if all(token in raw_text for token in ("除以", "商式為", "餘式為")):
            return "poly_div_reverse"
        if "周長" in question_text and "面積" in question_text and "長方形" in question_text:
            return "poly_geom_region_composite"
        if "梯形" in question_text and "面積" in question_text and "高" in question_text:
            return "poly_geom_formula_direct"
        if "商式為" in question_text and "餘式為" in question_text:
            return "poly_div_reverse"
        if len(segments) >= 3 and re.search(r"\b[A-Z]\b", question_text):
            return "poly_div_reverse"
        if "商式" in question_text and "餘式" in question_text:
            if "另一個多項式" in question_text or "此多項式A" in norm or "此多項式B" in norm:
                return "poly_div_reverse"
            if "除以" in question_text or "/" in norm:
                dividend_text, divisor_text = self.extract_division_operands(question_text)
                divisor_terms = self.parse_poly(divisor_text, self.detect_variable(norm))
                return "poly_div_monomial_qr" if len(divisor_terms["terms"]) == 1 else "poly_div_poly_qr"
        if segments and "=" in segments[0] and re.search(r"[A-Z]", segments[0]):
            return "poly_add_sub_unknown"
        if "=" in norm:
            try:
                lhs, rhs = self.extract_equation(norm)
                if re.search(r"[A-Z]", lhs + rhs):
                    return "poly_add_sub_unknown"
            except Exception:
                if re.search(r"[A-Z]", norm):
                    return "poly_add_sub_unknown"
        if (has_mul_signal or "*" in expr_norm or self._has_implicit_mul(expr_norm)) and not has_div_signal:
            if self._looks_like_mixed(expr_norm):
                return "poly_mixed_simplify"
            if self._looks_like_special(expr_norm, question_text):
                return "poly_mul_special_identity"
            factors = self._top_level_mul_parts(expr_norm)
            if factors and any(
                self.is_poly_text(f, self.detect_variable(expr_norm))
                and len(self.parse_poly(f, self.detect_variable(expr_norm))["terms"]) == 1
                for f in factors
            ):
                return "poly_mul_monomial"
            return "poly_mul_poly"
        if has_div_signal or ("/" in norm and ("求" in question_text or "計算" in question_text)):
            dividend_text, divisor_text = self.extract_division_operands(question_text)
            divisor_terms = self.parse_poly(divisor_text, self.detect_variable(norm))
            return "poly_div_monomial_eval" if len(divisor_terms["terms"]) == 1 else "poly_div_poly_qr"
        if self._looks_like_mixed(expr_norm):
            return "poly_mixed_simplify"
        if self._looks_like_special(expr_norm, question_text):
            return "poly_mul_special_identity"
        if "*" in expr_norm or self._has_implicit_mul(expr_norm):
            factors = self._top_level_mul_parts(expr_norm)
            if factors and any(
                self.is_poly_text(f, self.detect_variable(expr_norm))
                and len(self.parse_poly(f, self.detect_variable(expr_norm))["terms"]) == 1
                for f in factors
            ):
                return "poly_mul_monomial"
            return "poly_mul_poly"
        if self._has_nested_groups(expr_norm):
            return "poly_add_sub_nested"
        return "poly_add_sub_flat"

    def extract_math_segments(self, text: str) -> list[str]:
        return [seg.strip() for seg in re.findall(r"\$([^$]+)\$", str(text or "")) if seg.strip()]

    def extract_expression(self, question_text: str) -> str:
        segments = self.extract_math_segments(question_text)
        if len(segments) == 1:
            return segments[0]
        if len(segments) >= 2 and ("除以" in question_text or "/" in self.normalize_text(question_text)):
            return f"{segments[0]}/{segments[1]}"
        text = self.normalize_text(question_text)
        if self._looks_like_complete_expression(text):
            return text
        if "=" in text and ("A" in text or "B" in text):
            match = re.search(r"([A-Z][^=]*=[^，,？?。]+)", text)
            return match.group(1) if match else text
        candidates = re.findall(r"[\(\[].+?[\)\]](?:\^\d+)?(?:[\+\-\*/][\(\[].+?[\)\]](?:\^\d+)?)*", text)
        if candidates:
            return max(candidates, key=len)
        match = re.search(r"([0-9A-Za-z\(\)\[\]\+\-\*/\^]+)", text)
        return match.group(1) if match else text

    def extract_equation(self, norm_text: str) -> tuple[str, str]:
        if "=" not in norm_text:
            raise ValueError("equation expected")
        eq_idx = norm_text.find("=")
        allowed = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789()+-*/^[]")

        left_start = eq_idx - 1
        while left_start >= 0 and norm_text[left_start] in allowed:
            left_start -= 1

        right_end = eq_idx + 1
        while right_end < len(norm_text) and norm_text[right_end] in allowed:
            right_end += 1

        lhs = norm_text[left_start + 1:eq_idx].strip()
        rhs = norm_text[eq_idx + 1:right_end].strip()
        if not lhs or not rhs:
            match = re.search(r"([A-Z][^=]*=[^，,？?。]+)", norm_text)
            core = match.group(1) if match else norm_text
            return core.split("=", 1)
        return lhs, rhs

    def parse_equation_side(self, side_text: str, unknown: str, variable: str) -> dict[str, Any]:
        side_text = side_text.strip()
        if unknown in side_text:
            if side_text == unknown:
                return {"kind": "unknown", "name": unknown}
            idx = side_text.find(unknown)
            if idx == 0 and len(side_text) > 1:
                return {
                    "kind": "unknown_expr",
                    "unknown_first": True,
                    "op": side_text[1],
                    "other": self.parse_expr(side_text[2:], variable),
                    "name": unknown,
                }
            if idx > 0:
                return {
                    "kind": "unknown_expr",
                    "unknown_first": False,
                    "op": side_text[idx - 1],
                    "other": self.parse_expr(side_text[: idx - 1], variable),
                    "name": unknown,
                }
        return {"kind": "expr", "expr": self.parse_expr(side_text, variable)}

    def extract_division_operands(self, question_text: str) -> tuple[str, str]:
        segments = self.extract_math_segments(question_text)
        if len(segments) >= 2 and ("除以" in question_text or "/" in self.normalize_text(question_text)):
            return segments[0], segments[1]
        norm = self.normalize_text(question_text)
        match = re.search(r"(\([^\n]+?\)|[0-9A-Za-z\^\+\-]+)\s*/\s*(\([^\n]+?\)|[0-9A-Za-z\^\+\-]+)", norm)
        if match:
            return match.group(1), match.group(2)
        match = re.search(r"求(.+?)除以(.+?)的商式與餘式", norm)
        if match:
            return match.group(1), match.group(2)
        match = re.search(r"計算(.+?)除以(.+)", norm)
        if match:
            return match.group(1), match.group(2)
        raise ValueError(f"Cannot extract division operands from: {question_text}")

    def build_reverse_division_config(self, src: str, norm: str, variable: str) -> dict[str, Any]:
        segments = self.extract_math_segments(src)
        unknown_match = re.search(r"多項式([A-Z])", src)
        unknown = unknown_match.group(1) if unknown_match else ("A" if "A" in src else "B")
        if "商式為" in src and "餘式為" in src:
            find_dividend_match = re.search(
                r"如果一個多項式\s*([A-Z])\s*除以\s*(.+?)\s*的商式為\s*(.+?)\s*，\s*餘式為\s*(.+?)\s*[，,]",
                src,
            )
            if find_dividend_match:
                unknown = find_dividend_match.group(1)
                divisor_text = find_dividend_match.group(2).strip()
                quotient_text = find_dividend_match.group(3).strip()
                remainder_text = find_dividend_match.group(4).strip()
                return {
                    "family": "poly_div_reverse",
                    "source_text": src,
                    "variable": variable,
                    "reverse_kind": "find_dividend",
                    "unknown_name": unknown,
                    "divisor_template": self.parse_poly(divisor_text, variable),
                    "quotient_template": self.parse_poly(quotient_text, variable),
                    "remainder_template": self.parse_poly(remainder_text, variable),
                }

            find_divisor_match = re.search(
                r"已知\s*(.+?)\s*除以(?:另一個多項式\s*([A-Z])|([A-Z]))\s*後\s*，\s*得到商式為\s*(.+?)\s*，\s*餘式為\s*(.+?)\s*[，,]",
                src,
            )
            if find_divisor_match:
                dividend_text = find_divisor_match.group(1).strip()
                unknown = find_divisor_match.group(2) or find_divisor_match.group(3) or unknown
                quotient_text = find_divisor_match.group(4).strip()
                remainder_text = find_divisor_match.group(5).strip()
                return {
                    "family": "poly_div_reverse",
                    "source_text": src,
                    "variable": variable,
                    "reverse_kind": "find_divisor",
                    "unknown_name": unknown,
                    "dividend_template": self.parse_poly(dividend_text, variable),
                    "quotient_template": self.parse_poly(quotient_text, variable),
                    "remainder_template": self.parse_poly(remainder_text, variable),
                }

        if re.search(rf"{unknown}\s*除以", norm) or re.search(rf"多項式{unknown}除以", norm):
            if len(segments) >= 3:
                divisor_text, quotient_text, remainder_text = segments[:3]
            else:
                divisor_match = re.search(r"除以(.+?)的商式為", norm)
                quotient_match = re.search(r"商式為(.+?)餘式為", norm)
                remainder_match = re.search(r"餘式為(.+?)(?:，|,|試求|求)", norm)
                if not (divisor_match and quotient_match and remainder_match):
                    raise ValueError("Unsupported reverse division pattern")
                divisor_text, quotient_text, remainder_text = divisor_match.group(1), quotient_match.group(1), remainder_match.group(1)
            return {
                "family": "poly_div_reverse",
                "source_text": src,
                "variable": variable,
                "reverse_kind": "find_dividend",
                "unknown_name": unknown,
                "divisor_template": self.parse_poly(divisor_text, variable),
                "quotient_template": self.parse_poly(quotient_text, variable),
                "remainder_template": self.parse_poly(remainder_text, variable),
            }

        if len(segments) >= 3:
            dividend_text, quotient_text, remainder_text = segments[:3]
        else:
            dividend_match = re.search(r"已知(.+?)除以另一個多項式", norm) or re.search(r"已知(.+?)除以(.+?)後", norm)
            quotient_match = re.search(r"商式為(.+?)餘式為", norm)
            remainder_match = re.search(r"餘式為(.+?)(?:，|,|試求|求)", norm)
            if not (dividend_match and quotient_match and remainder_match):
                raise ValueError("Unsupported reverse division pattern")
            dividend_text, quotient_text, remainder_text = dividend_match.group(1), quotient_match.group(1), remainder_match.group(1)
        return {
            "family": "poly_div_reverse",
            "source_text": src,
            "variable": variable,
            "reverse_kind": "find_divisor",
            "unknown_name": unknown,
            "dividend_template": self.parse_poly(dividend_text, variable),
            "quotient_template": self.parse_poly(quotient_text, variable),
            "remainder_template": self.parse_poly(remainder_text, variable),
        }

    def is_poly_text(self, text: str, variable: str) -> bool:
        s = self.normalize_text(text)
        if not s or any(ch in s for ch in "[]"):
            return False
        if "(" in s or ")" in s or "*" in s:
            return False
        num = r"(?:\d+(?:/\d+)?)"
        pattern = rf"[+\-]?(?:{num}{variable}\^\d+|{num}{variable}|{variable}\^\d+|{variable}|{num})"
        whole = "".join(re.findall(pattern, s))
        return bool(re.fullmatch(rf"{pattern}+", s)) and whole == s

    def parse_poly(self, text: str, variable: str) -> dict[str, Any]:
        s = self.normalize_text(text)
        s = self._strip_wrapping_group(s)
        if s and s[0] not in "+-":
            s = "+" + s
        parts = re.findall(r"([+\-])([^+\-]+)", s)
        terms = []
        for sign_ch, body in parts:
            sign = -1 if sign_ch == "-" else 1
            exponent = 0
            if variable in body:
                if "^" in body:
                    coeff_text, exp_text = body.split(variable + "^", 1)
                    exponent = int(exp_text)
                else:
                    coeff_text = body.split(variable, 1)[0]
                    exponent = 1
                coeff = Fraction(coeff_text) if coeff_text else Fraction(1)
            else:
                coeff = Fraction(body)
            terms.append({
                "sign": sign if coeff >= 0 else -sign,
                "magnitude": abs(coeff),
                "fractional": abs(coeff).denominator != 1,
                "exponent": exponent,
            })
        return {"kind": "poly", "terms": terms}

    def parse_expr(self, text: str, variable: str) -> dict[str, Any]:
        s = self.normalize_text(text)
        wrapped = self._wrapped_group_info(s)
        if wrapped is not None:
            open_ch, close_ch, inner = wrapped
            return {"kind": "group", "open": open_ch, "close": close_ch, "inner": self.parse_expr(inner, variable)}

        s = self._strip_wrapping_group(s)
        if self.is_poly_text(s, variable):
            return self.parse_poly(s, variable)

        parts = self._split_top_level_sum(s)
        if len(parts) > 1:
            node = self.parse_expr(parts[0], variable)
            for op, rhs_text in zip(parts[1::2], parts[2::2]):
                node = {"kind": "binop", "op": op, "left": node, "right": self.parse_expr(rhs_text, variable)}
            return node

        if s.endswith("^2"):
            return {"kind": "pow2", "base": self.parse_expr(s[:-2], variable)}

        mul_parts = self._top_level_mul_parts(s)
        if len(mul_parts) > 1:
            return {"kind": "mul", "factors": [self.parse_expr(part, variable) for part in mul_parts]}

        if (s.startswith("(") and s.endswith(")")) or (s.startswith("[") and s.endswith("]")):
            return {"kind": "group", "open": s[0], "close": s[-1], "inner": self.parse_expr(s[1:-1], variable)}

        raise ValueError(f"Unsupported expression: {text}")

    def generate_from_config(self, config: dict[str, Any]) -> dict[str, Any]:
        family = config["family"]
        if family in {
            "poly_add_sub_flat",
            "poly_add_sub_nested",
            "poly_mul_monomial",
            "poly_mul_poly",
            "poly_mixed_simplify",
        }:
            if config.get("fraction_product"):
                return self.generate_fraction_monomial_product(config)
            node = self.instantiate_node(config["ast"])
            expr = self.render_node(node, config["variable"])
            answer = self.poly_plain(self.eval_node(node), config["variable"])
            prefix = self.default_prefix(family, config["source_text"])
            return {
                "question_text": f"{prefix} ${expr}$。",
                "answer": answer,
                "correct_answer": answer,
                "mode": 1,
            }
        if family == "poly_mul_special_identity":
            node = self.instantiate_special_identity_node(config["ast"])
            expr = self.render_node(node, config["variable"])
            answer = self.poly_plain(self.eval_node(node), config["variable"])
            prefix = self.default_prefix(family, config["source_text"])
            return {
                "question_text": f"{prefix} ${expr}$。",
                "answer": answer,
                "correct_answer": answer,
                "mode": 1,
            }

        if family == "poly_add_sub_unknown":
            return self.generate_unknown(config)
        if family in {"poly_div_monomial_eval", "poly_div_monomial_qr", "poly_div_poly_qr"}:
            return self.generate_division(config)
        if family == "poly_div_reverse":
            return self.generate_reverse_division(config)
        if family == "poly_geom_formula_direct":
            return self.generate_geometry_direct(config)
        if family == "poly_geom_region_composite":
            return self.generate_geometry_region(config)
        raise ValueError(f"Unsupported polynomial family: {family}")

    def generate_fraction_monomial_product(self, config: dict[str, Any]) -> dict[str, Any]:
        x = config["variable"]
        a = Fraction(random.randint(1, 5), random.randint(2, 6))
        b = Fraction(random.randint(1, 5), random.randint(2, 6))
        result = {3: -(a * b)}
        question = (
            f"計算 $\\frac{{{a.numerator}}}{{{a.denominator}}}{x}"
            f"\\times\\left(-\\frac{{{b.numerator}}}{{{b.denominator}}}{x}^{{2}}\\right)$。"
        )
        answer = self.poly_plain(result, x)
        return {
            "question_text": question,
            "answer": answer,
            "correct_answer": answer,
            "mode": 1,
        }

    def default_prefix(self, family: str, source_text: str) -> str:
        if family == "poly_mul_special_identity" and "乘法公式" in source_text:
            return "利用乘法公式計算"
        return "計算"

    def instantiate_node(self, node: dict[str, Any]) -> dict[str, Any]:
        kind = node["kind"]
        if kind == "poly":
            terms = []
            for term in node["terms"]:
                if term.get("fractional"):
                    numerator = random.randint(1, 5)
                    denominator = random.randint(2, 6)
                    magnitude = Fraction(numerator, denominator)
                else:
                    magnitude = Fraction(random.randint(1, 9 if term["exponent"] != 0 else 12))
                terms.append({"coeff": magnitude * term["sign"], "exponent": term["exponent"]})
            return {"kind": "poly", "terms": terms}
        if kind == "group":
            return {"kind": "group", "open": node["open"], "close": node["close"], "inner": self.instantiate_node(node["inner"])}
        if kind == "pow2":
            return {"kind": "pow2", "base": self.instantiate_node(node["base"])}
        if kind == "mul":
            return {"kind": "mul", "factors": [self.instantiate_node(f) for f in node["factors"]]}
        if kind == "binop":
            return {"kind": "binop", "op": node["op"], "left": self.instantiate_node(node["left"]), "right": self.instantiate_node(node["right"])}
        raise ValueError(f"Unsupported node kind: {kind}")

    def instantiate_special_identity_node(self, node: dict[str, Any]) -> dict[str, Any]:
        kind = node["kind"]
        if kind == "pow2":
            base = self._instantiate_formula_binomial(node["base"])
            return {"kind": "pow2", "base": base}
        if kind == "mul":
            factors = node.get("factors", [])
            if len(factors) == 2:
                left_bin = self._unwrap_formula_binomial(factors[0])
                right_bin = self._unwrap_formula_binomial(factors[1])
                if left_bin and right_bin and left_bin["op"] != right_bin["op"]:
                    lead = self._randomized_poly_like(left_bin["left"])
                    tail = self._randomized_poly_like(left_bin["right"])
                    return {
                        "kind": "mul",
                        "factors": [
                            {
                                "kind": "group",
                                "open": factors[0].get("open", "("),
                                "close": factors[0].get("close", ")"),
                                "inner": {"kind": "binop", "op": left_bin["op"], "left": lead, "right": tail},
                            },
                            {
                                "kind": "group",
                                "open": factors[1].get("open", "("),
                                "close": factors[1].get("close", ")"),
                                "inner": {"kind": "binop", "op": right_bin["op"], "left": self._clone_node(lead), "right": self._clone_node(tail)},
                            },
                        ],
                    }
        return self.instantiate_node(node)

    def _unwrap_formula_binomial(self, node: dict[str, Any]) -> dict[str, Any] | None:
        if node.get("kind") != "group":
            return None
        inner = node.get("inner", {})
        if inner.get("kind") != "binop":
            return None
        return inner

    def _instantiate_formula_binomial(self, node: dict[str, Any]) -> dict[str, Any]:
        if node.get("kind") == "group" and node.get("inner", {}).get("kind") == "binop":
            inner = node["inner"]
            return {
                "kind": "group",
                "open": node.get("open", "("),
                "close": node.get("close", ")"),
                "inner": {
                    "kind": "binop",
                    "op": inner["op"],
                    "left": self._randomized_poly_like(inner["left"]),
                    "right": self._randomized_poly_like(inner["right"]),
                },
            }
        return self.instantiate_node(node)

    def _randomized_poly_like(self, node: dict[str, Any]) -> dict[str, Any]:
        if node.get("kind") != "poly":
            return self.instantiate_node(node)
        return self.instantiate_node(self._clone_node(node))

    def _clone_node(self, node: dict[str, Any]) -> dict[str, Any]:
        kind = node.get("kind")
        if kind == "poly":
            return {"kind": "poly", "terms": [dict(term) for term in node.get("terms", [])]}
        if kind == "group":
            return {
                "kind": "group",
                "open": node.get("open", "("),
                "close": node.get("close", ")"),
                "inner": self._clone_node(node["inner"]),
            }
        if kind == "pow2":
            return {"kind": "pow2", "base": self._clone_node(node["base"])}
        if kind == "mul":
            return {"kind": "mul", "factors": [self._clone_node(f) for f in node.get("factors", [])]}
        if kind == "binop":
            return {
                "kind": "binop",
                "op": node["op"],
                "left": self._clone_node(node["left"]),
                "right": self._clone_node(node["right"]),
            }
        return dict(node)

    def eval_node(self, node: dict[str, Any]) -> dict[int, Fraction]:
        kind = node["kind"]
        if kind == "poly":
            out: dict[int, Fraction] = {}
            for term in node["terms"]:
                out[term["exponent"]] = out.get(term["exponent"], Fraction(0)) + Fraction(term["coeff"])
            return _trim_zero_poly(out)
        if kind == "group":
            return self.eval_node(node["inner"])
        if kind == "pow2":
            base = self.eval_node(node["base"])
            return _poly_mul(base, base)
        if kind == "mul":
            current = {0: Fraction(1)}
            for factor in node["factors"]:
                current = _poly_mul(current, self.eval_node(factor))
            return current
        if kind == "binop":
            left = self.eval_node(node["left"])
            right = self.eval_node(node["right"])
            return _poly_add(left, right) if node["op"] == "+" else _poly_sub(left, right)
        raise ValueError(f"Unsupported node kind: {kind}")

    def render_node(self, node: dict[str, Any], variable: str) -> str:
        kind = node["kind"]
        if kind == "poly":
            return self.render_poly(node["terms"], variable)
        if kind == "group":
            return f"{node['open']}{self.render_node(node['inner'], variable)}{node['close']}"
        if kind == "pow2":
            base = self.render_node(node["base"], variable)
            if node["base"]["kind"] == "poly":
                base = f"({base})"
            return f"{base}^{{2}}"
        if kind == "mul":
            parts = []
            for factor in node["factors"]:
                rendered = self.render_node(factor, variable)
                if factor["kind"] == "binop":
                    rendered = f"({rendered})"
                parts.append(rendered)
            return "".join(parts)
        if kind == "binop":
            left = self.render_node(node["left"], variable)
            right = self.render_node(node["right"], variable)
            if node["op"] == "+":
                if right.startswith("-"):
                    return f"{left}-{self._strip_leading_negative(right)}"
                return f"{left}+{right}"
            if right.startswith("-"):
                return f"{left}+{self._strip_leading_negative(right)}"
            return f"{left}-{right}"
        raise ValueError(f"Unsupported node kind: {kind}")

    def render_poly(self, terms: list[dict[str, Any]], variable: str) -> str:
        parts = []
        for idx, term in enumerate(terms):
            coeff = Fraction(term["coeff"])
            exp = int(term["exponent"])
            sign = "-" if coeff < 0 else "+"
            mag = abs(coeff)
            mag_txt = _fraction_to_text(mag)
            if exp == 0:
                body = mag_txt
            elif exp == 1:
                body = variable if mag == 1 else f"{mag_txt}{variable}"
            else:
                body = f"{variable}^{{{exp}}}" if mag == 1 else f"{mag_txt}{variable}^{{{exp}}}"
            if idx == 0:
                parts.append(body if sign == "+" else f"-{body}")
            else:
                parts.append(f"{sign}{body}")
        return "".join(parts) if parts else "0"

    def poly_plain(self, coeffs: dict[int, Fraction], variable: str) -> str:
        if not coeffs:
            return "0"
        parts = []
        for idx, exp in enumerate(sorted(coeffs.keys(), reverse=True)):
            coeff = Fraction(coeffs[exp])
            if coeff == 0:
                continue
            sign = "-" if coeff < 0 else "+"
            mag = abs(coeff)
            coeff_txt = _fraction_to_text(mag)
            if exp == 0:
                body = coeff_txt
            elif exp == 1:
                if mag == 1:
                    body = variable
                else:
                    coeff_part = f"({coeff_txt})" if mag.denominator != 1 else coeff_txt
                    body = f"{coeff_part}{variable}"
            else:
                if mag == 1:
                    body = f"{variable}^{exp}"
                else:
                    coeff_part = f"({coeff_txt})" if mag.denominator != 1 else coeff_txt
                    body = f"{coeff_part}{variable}^{exp}"
            if idx == 0:
                parts.append(body if sign == "+" else f"-{body}")
            else:
                parts.append(f"{sign}{body}")
        return "".join(parts) if parts else "0"

    def poly_latex_from_coeffs(self, coeffs: dict[int, Fraction], variable: str) -> str:
        if not coeffs:
            return "0"
        parts = []
        for idx, exp in enumerate(sorted(coeffs.keys(), reverse=True)):
            coeff = Fraction(coeffs[exp])
            sign = "-" if coeff < 0 else "+"
            mag = abs(coeff)
            coeff_txt = _fraction_to_latex(mag)
            if exp == 0:
                body = coeff_txt
            elif exp == 1:
                body = variable if mag == 1 else f"{coeff_txt}{variable}"
            else:
                body = f"{variable}^{{{exp}}}" if mag == 1 else f"{coeff_txt}{variable}^{{{exp}}}"
            if idx == 0:
                parts.append(body if sign == "+" else f"-{body}")
            else:
                parts.append(f"{sign}{body}")
        return "".join(parts)

    def _wrap_negative_poly_for_display(self, text: str) -> str:
        s = str(text or "")
        return f"({s})" if s.startswith("-") else s

    def random_poly_from_degree(self, max_degree: int) -> dict[int, Fraction]:
        degree = random.randint(1, max_degree)
        return self.random_poly_exact_degree(degree)

    def random_poly_exact_degree(self, degree: int) -> dict[int, Fraction]:
        out: dict[int, Fraction] = {}
        for exp in range(degree, -1, -1):
            if exp != degree and exp != 0 and random.random() < 0.35:
                continue
            coeff = random.choice([-1, 1]) * random.randint(1, 7)
            out[exp] = Fraction(coeff)
        return _trim_zero_poly(out)

    def randomize_poly_from_template(self, template: dict[str, Any]) -> dict[int, Fraction]:
        out: dict[int, Fraction] = {}
        for term in template["terms"]:
            if term.get("fractional"):
                coeff = Fraction(random.randint(1, 5), random.randint(2, 6)) * term["sign"]
            else:
                coeff = Fraction(random.randint(1, 8)) * term["sign"]
            out[term["exponent"]] = Fraction(coeff)
        return _trim_zero_poly(out)

    def instantiate_terms_from_template(self, template: dict[str, Any]) -> list[dict[str, Any]]:
        terms = []
        for term in template["terms"]:
            if term.get("fractional"):
                coeff = Fraction(random.randint(1, 5), random.randint(2, 6)) * term["sign"]
            else:
                coeff = Fraction(random.randint(1, 8)) * term["sign"]
            terms.append({"coeff": coeff, "exponent": term["exponent"]})
        return terms

    def terms_to_poly_dict(self, terms: list[dict[str, Any]]) -> dict[int, Fraction]:
        out: dict[int, Fraction] = {}
        for term in terms:
            out[int(term["exponent"])] = out.get(int(term["exponent"]), Fraction(0)) + Fraction(term["coeff"])
        return _trim_zero_poly(out)

    def generate_unknown(self, config: dict[str, Any]) -> dict[str, Any]:
        variable = config["variable"]
        unknown_poly = self.random_poly_from_degree(3)
        lhs_text, _ = self.instantiate_equation_side(config["lhs_template"], unknown_poly, variable)
        rhs_text, _ = self.instantiate_equation_side(config["rhs_template"], unknown_poly, variable)
        correct = self.poly_plain(unknown_poly, variable)
        return {
            "question_text": f"若 ${lhs_text}={rhs_text}$，則多項式 ${config['unknown_name']}$ = ？",
            "answer": correct,
            "correct_answer": correct,
            "mode": 1,
        }

    def instantiate_equation_side(
        self,
        template: dict[str, Any],
        unknown_poly: dict[int, Fraction],
        variable: str,
    ) -> tuple[str, dict[int, Fraction]]:
        kind = template["kind"]
        if kind == "unknown":
            return template.get("name", "A"), unknown_poly
        if kind == "unknown_expr":
            other_node = self.instantiate_node(template["other"])
            other_text = self.render_node(other_node, variable)
            other_val = self.eval_node(other_node)
            name = template.get("name", "A")
            shown_other = other_text
            if other_text.startswith("-"):
                shown_other = f"({other_text})"
            if template["unknown_first"]:
                text = f"{name}{template['op']}{shown_other}"
                val = _poly_add(unknown_poly, other_val) if template["op"] == "+" else _poly_sub(unknown_poly, other_val)
            else:
                text = f"{shown_other}{template['op']}{name}"
                val = _poly_add(other_val, unknown_poly) if template["op"] == "+" else _poly_sub(other_val, unknown_poly)
            return text, val
        node = self.instantiate_node(template["expr"])
        return self.render_node(node, variable), self.eval_node(node)

    def generate_division(self, config: dict[str, Any]) -> dict[str, Any]:
        variable = config["variable"]
        dividend_terms = self.instantiate_terms_from_template(config["dividend_template"])
        divisor_terms = self.instantiate_terms_from_template(config["divisor_template"])
        dividend = self.terms_to_poly_dict(dividend_terms)
        divisor = self.terms_to_poly_dict(divisor_terms)
        if not divisor:
            divisor = {1: Fraction(1)}
        quotient, remainder = _poly_long_division(dividend, divisor)
        dividend_q = self.render_poly(dividend_terms, variable)
        divisor_q = self.render_poly(divisor_terms, variable)
        dividend_q = self._wrap_negative_poly_for_display(dividend_q)
        divisor_q = self._wrap_negative_poly_for_display(divisor_q)

        if config["family"] == "poly_div_monomial_eval":
            if remainder:
                answer = f"商式：{self.poly_plain(quotient, variable)}；餘式：{self.poly_plain(remainder, variable)}"
            else:
                answer = self.poly_plain(quotient, variable)
            return {
                "question_text": f"計算 $({dividend_q}) \\div ({divisor_q})$。",
                "answer": answer,
                "correct_answer": answer,
                "mode": 1,
            }

        answer = f"商式：{self.poly_plain(quotient, variable)}；餘式：{self.poly_plain(remainder, variable)}"
        return {
            "question_text": f"求 $({dividend_q})$ 除以 $({divisor_q})$ 的商式與餘式。",
            "answer": answer,
            "correct_answer": answer,
            "mode": 1,
        }

    def generate_reverse_division(self, config: dict[str, Any]) -> dict[str, Any]:
        variable = config["variable"]
        quotient = self.randomize_poly_from_template(config["quotient_template"])
        remainder = self.randomize_poly_from_template(config["remainder_template"])

        if config["reverse_kind"] == "find_dividend":
            divisor = self.randomize_poly_from_template(config["divisor_template"])
            dividend = _poly_add(_poly_mul(divisor, quotient), remainder)
            answer = self.poly_plain(dividend, variable)
            return {
                "question_text": (
                    f"如果一個多項式 {config['unknown_name']} 除以 ${self.poly_latex_from_coeffs(divisor, variable)}$ 的商式為 "
                    f"${self.poly_latex_from_coeffs(quotient, variable)}$，餘式為 ${self.poly_latex_from_coeffs(remainder, variable)}$，"
                    f"試求此多項式 {config['unknown_name']}。"
                ),
                "answer": answer,
                "correct_answer": answer,
                "mode": 1,
            }

        target_dividend_degree = max(config["dividend_template"]["terms"], key=lambda t: int(t["exponent"]))["exponent"]
        quotient_degree = max(config["quotient_template"]["terms"], key=lambda t: int(t["exponent"]))["exponent"]
        divisor_degree = max(1, int(target_dividend_degree) - int(quotient_degree))
        target_exponents = tuple(int(t["exponent"]) for t in config["dividend_template"]["terms"])
        divisor = self.random_poly_exact_degree(divisor_degree)
        dividend = _poly_add(_poly_mul(divisor, quotient), remainder)
        for _ in range(60):
            candidate_divisor = self.random_poly_exact_degree(divisor_degree)
            candidate_dividend = _poly_add(_poly_mul(candidate_divisor, quotient), remainder)
            if tuple(sorted(candidate_dividend.keys(), reverse=True)) == target_exponents:
                divisor = candidate_divisor
                dividend = candidate_dividend
                break
        answer = self.poly_plain(divisor, variable)
        return {
            "question_text": (
                f"已知 ${self.poly_latex_from_coeffs(dividend, variable)}$ 除以另一個多項式 {config['unknown_name']} 後，"
                f"得到商式為 ${self.poly_latex_from_coeffs(quotient, variable)}$，餘式為 ${self.poly_latex_from_coeffs(remainder, variable)}$，"
                f"試求此多項式 {config['unknown_name']}。"
            ),
            "answer": answer,
            "correct_answer": answer,
            "mode": 1,
        }

    def generate_geometry_direct(self, config: dict[str, Any]) -> dict[str, Any]:
        x = config["variable"]
        top = {1: Fraction(random.randint(1, 3)), 0: Fraction(random.randint(-3, 4))}
        bottom = {1: Fraction(random.randint(2, 5)), 0: Fraction(random.randint(1, 7))}
        height = {1: Fraction(random.randint(1, 3)), 0: Fraction(random.randint(1, 5))}
        area = _poly_scalar_mul(_poly_mul(_poly_add(top, bottom), height), Fraction(1, 2))
        answer = self.poly_plain(height, x)
        return {
            "question_text": (
                f"右圖是大象造型的梯形溜滑梯，若溜滑梯的上底為 ${self.poly_latex_from_coeffs(top, x)}$、"
                f"下底為 ${self.poly_latex_from_coeffs(bottom, x)}$、面積為 ${self.poly_latex_from_coeffs(area, x)}$，"
                f"試以 {x} 的多項式表示此溜滑梯的高。"
            ),
            "answer": answer,
            "correct_answer": answer,
            "mode": 1,
        }

    def generate_geometry_region(self, config: dict[str, Any]) -> dict[str, Any]:
        x = config["variable"]
        outer_len = {1: Fraction(random.randint(2, 4)), 0: Fraction(random.randint(3, 8))}
        outer_wid = {1: Fraction(random.randint(1, 3)), 0: Fraction(random.randint(2, 6))}
        inner_len = {1: Fraction(random.randint(1, 3)), 0: Fraction(random.randint(1, 4))}
        inner_wid = {1: Fraction(random.randint(1, 2)), 0: Fraction(random.randint(-1, 3))}
        area = _poly_sub(_poly_mul(outer_len, outer_wid), _poly_mul(inner_len, inner_wid))
        perimeter = _poly_add(
            _poly_scalar_mul(_poly_add(outer_len, outer_wid), Fraction(2)),
            _poly_scalar_mul(_poly_add(inner_len, inner_wid), Fraction(2)),
        )
        answer = f"周長：{self.poly_plain(perimeter, x)}；面積：{self.poly_plain(area, x)}"
        return {
            "question_text": (
                f"右圖中，大長方形的長為 ${self.poly_latex_from_coeffs(outer_len, x)}$、寬為 ${self.poly_latex_from_coeffs(outer_wid, x)}$，"
                f"小長方形的長為 ${self.poly_latex_from_coeffs(inner_len, x)}$、寬為 ${self.poly_latex_from_coeffs(inner_wid, x)}$。"
                f"試以 {x} 的多項式表示橘色部分的周長與面積。"
            ),
            "answer": answer,
            "correct_answer": answer,
            "mode": 1,
        }

    def _strip_wrapping_group(self, s: str) -> str:
        while len(s) >= 2 and ((s[0], s[-1]) in {("(", ")"), ("[", "]")}):
            depth = 0
            ok = True
            for idx, ch in enumerate(s):
                if ch in "([":
                    depth += 1
                elif ch in ")]":
                    depth -= 1
                if depth == 0 and idx != len(s) - 1:
                    ok = False
                    break
            if not ok:
                break
            s = s[1:-1]
        return s

    def _wrapped_group_info(self, s: str) -> tuple[str, str, str] | None:
        if len(s) < 2 or (s[0], s[-1]) not in {("(", ")"), ("[", "]")}:
            return None
        depth = 0
        for idx, ch in enumerate(s):
            if ch in "([":
                depth += 1
            elif ch in ")]":
                depth -= 1
            if depth == 0 and idx != len(s) - 1:
                return None
        return s[0], s[-1], s[1:-1]

    def _strip_leading_negative(self, text: str) -> str:
        s = str(text or "")
        if s.startswith("-(") and s.endswith(")"):
            return s[2:-1]
        if s.startswith("-"):
            return s[1:]
        return s

    def _split_top_level_sum(self, s: str) -> list[str]:
        parts = []
        depth = 0
        start = 0
        for idx, ch in enumerate(s):
            if ch in "([":
                depth += 1
            elif ch in ")]":
                depth -= 1
            elif depth == 0 and ch in "+-" and idx > 0:
                parts.append(s[start:idx])
                parts.append(ch)
                start = idx + 1
        parts.append(s[start:])
        return [p for p in parts if p != ""]

    def _top_level_mul_parts(self, s: str) -> list[str]:
        pieces = []
        start = 0
        depth = 0
        for idx in range(1, len(s)):
            prev = s[idx - 1]
            if prev in "([":
                depth += 1
            elif prev in ")]":
                depth -= 1
            ch = s[idx]
            if depth == 0 and ch == "*":
                pieces.append(s[start:idx])
                start = idx + 1
            elif depth == 0 and self._is_implicit_mul_boundary(prev, ch):
                pieces.append(s[start:idx])
                start = idx
        pieces.append(s[start:])
        return [p for p in pieces if p]

    def _is_implicit_mul_boundary(self, left: str, right: str) -> bool:
        if right in "([":
            return left.isdigit() or left.isalpha() or left in ")]"
        return left in ")]" and (right.isdigit() or right.isalpha() or right in "([")

    def _has_implicit_mul(self, s: str) -> bool:
        return any(self._is_implicit_mul_boundary(s[idx - 1], s[idx]) for idx in range(1, len(s)))

    def _has_nested_groups(self, s: str) -> bool:
        depth = 0
        max_depth = 0
        for ch in s:
            if ch in "([":
                depth += 1
                max_depth = max(max_depth, depth)
            elif ch in ")]":
                depth -= 1
        return max_depth >= 2 or ("[" in s and "(" in s)

    def _looks_like_complete_expression(self, s: str) -> bool:
        text = str(s or "").strip()
        if not text:
            return False
        if re.search(r"[^0-9A-Za-z\(\)\[\]\+\-\*/\^]", text):
            return False
        depth = 0
        for ch in text:
            if ch in "([":
                depth += 1
            elif ch in ")]":
                depth -= 1
                if depth < 0:
                    return False
        return depth == 0 and any(op in text for op in "+-*/")

    def _looks_like_special(self, expr_norm: str, source_text: str) -> bool:
        if "乘法公式" in source_text:
            return True
        if expr_norm.endswith("^2") and (")^2" in expr_norm or "]^2" in expr_norm):
            return True
        factors = self._top_level_mul_parts(expr_norm)
        if len(factors) == 2 and all(f.startswith("(") and f.endswith(")") for f in factors):
            left = self.normalize_text(factors[0][1:-1])
            right = self.normalize_text(factors[1][1:-1])
            return left.replace("+", "-", 1) == right or left.replace("-", "+", 1) == right
        return False

    def _looks_like_mixed(self, expr_norm: str) -> bool:
        depth = 0
        top_ops = []
        for idx, ch in enumerate(expr_norm):
            if ch in "([":
                depth += 1
            elif ch in ")]":
                depth -= 1
            elif depth == 0 and ch in "+-" and idx > 0:
                top_ops.append(ch)
        has_group_square = ")^2" in expr_norm or "]^2" in expr_norm
        return bool(top_ops) and (has_group_square or "*" in expr_norm or self._has_implicit_mul(expr_norm))

    def _signature_from_config(self, config: dict[str, Any]) -> Any:
        family = config["family"]
        if "ast" in config:
            return self._signature_from_node(config["ast"])
        if family == "poly_add_sub_unknown":
            return {
                "unknown_name": config["unknown_name"],
                "unknown_side": config["unknown_side"],
                "lhs": self._signature_from_equation_side(config["lhs_template"]),
                "rhs": self._signature_from_equation_side(config["rhs_template"]),
            }
        if family in {"poly_div_monomial_eval", "poly_div_monomial_qr", "poly_div_poly_qr"}:
            return {
                "dividend": self._signature_from_node(config["dividend_template"]),
                "divisor": self._signature_from_node(config["divisor_template"]),
            }
        if family == "poly_div_reverse":
            payload = {
                "reverse_kind": config["reverse_kind"],
                "unknown_name": config["unknown_name"],
                "quotient": self._signature_from_node(config["quotient_template"]),
                "remainder": self._signature_from_node(config["remainder_template"]),
            }
            if "divisor_template" in config:
                payload["divisor"] = self._signature_from_node(config["divisor_template"])
            if "dividend_template" in config:
                payload["dividend"] = self._signature_from_node(config["dividend_template"])
            return payload
        return {"family": family}

    def _signature_from_equation_side(self, template: dict[str, Any]) -> Any:
        kind = template["kind"]
        if kind == "unknown":
            return {"kind": "unknown"}
        if kind == "unknown_expr":
            return {
                "kind": "unknown_expr",
                "unknown_first": template["unknown_first"],
                "op": template["op"],
                "other": self._signature_from_node(template["other"]),
            }
        return {"kind": "expr", "expr": self._signature_from_node(template["expr"])}

    def _signature_from_node(self, node: dict[str, Any]) -> Any:
        kind = node["kind"]
        if kind == "poly":
            return {
                "kind": "poly",
                "terms": tuple((int(term["exponent"]), bool(term.get("fractional", False))) for term in node["terms"]),
            }
        if kind == "group":
            return {"kind": "group", "brackets": "()", "inner": self._signature_from_node(node["inner"])}
        if kind == "pow2":
            return {"kind": "pow2", "base": self._signature_from_node(node["base"])}
        if kind == "mul":
            return {"kind": "mul", "factors": tuple(self._signature_from_node(f) for f in node["factors"])}
        if kind == "binop":
            return {
                "kind": "binop",
                "op": node["op"],
                "left": self._signature_from_node(node["left"]),
                "right": self._signature_from_node(node["right"]),
            }
        return {"kind": kind}
