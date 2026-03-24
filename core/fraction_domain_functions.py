from __future__ import annotations

import math
import random
import re
from fractions import Fraction
from typing import Any


def _normalize_text(text: str) -> str:
    s = str(text or "").strip()
    replacements = {
        "（": "(",
        "）": ")",
        "［": "[",
        "］": "]",
        "【": "[",
        "】": "]",
        "｛": "{",
        "｝": "}",
        "＋": "+",
        "－": "-",
        "−": "-",
        "×": "*",
        "÷": "/",
        "•": "*",
        "．": ".",
        "，": ",",
        "、": ",",
        "；": ";",
        "：": ":",
        "＝": "=",
        "＿": "_",
        "　": " ",
        "\\times": "*",
        "\\div": "/",
        "\\cdot": "*",
        "\\left": "",
        "\\right": "",
        "\\;": " ",
        "\\ldots": "...",
    }
    for old, new in replacements.items():
        s = s.replace(old, new)
    s = re.sub(r"\$([^$]+)\$", r"\1", s)
    s = re.sub(r"(?<![\w])([+-]?\d+)\s*\\frac\{([^{}]+)\}\{([^{}]+)\}", r"\1 \2/\3", s)
    s = re.sub(r"\\frac\{([^{}]+)\}\{([^{}]+)\}", r"(\1/\2)", s)
    s = s.replace("{", "").replace("}", "")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _fraction_text(value: Fraction) -> str:
    value = Fraction(value)
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def _mixed_text(value: Fraction) -> str:
    value = Fraction(value)
    sign = "-" if value < 0 else ""
    mag = abs(value)
    whole = mag.numerator // mag.denominator
    rem = mag.numerator % mag.denominator
    if rem == 0:
        return f"{sign}{whole}"
    if whole == 0:
        return f"{sign}{rem}/{mag.denominator}"
    return f"{sign}{whole} {rem}/{mag.denominator}"


def _scalar_text(value: Fraction) -> str:
    value = Fraction(value)
    if value.denominator != 1:
        raise ValueError(f"expected integer-like fraction, got {value}")
    return str(value.numerator)


def _parse_number_token(token: str) -> tuple[Fraction, str]:
    raw = _normalize_text(token).strip().strip("()")
    mixed_match = re.fullmatch(r"([+-]?\d+)\s+(\d+)/(\d+)", raw)
    if mixed_match:
        whole = int(mixed_match.group(1))
        num = int(mixed_match.group(2))
        den = int(mixed_match.group(3))
        if den == 0:
            raise ValueError("zero denominator")
        total = abs(whole) * den + num
        value = Fraction(total, den)
        if whole < 0:
            value = -value
        return value, "mixed"

    frac_match = re.fullmatch(r"([+-]?\d+)\s*/\s*([+-]?\d+)", raw)
    if frac_match:
        return Fraction(int(frac_match.group(1)), int(frac_match.group(2))), "fraction"

    dec_match = re.fullmatch(r"[+-]?\d+\.\d+", raw)
    if dec_match:
        return Fraction(raw), "decimal"

    int_match = re.fullmatch(r"[+-]?\d+", raw)
    if int_match:
        return Fraction(int(raw), 1), "int"

    raise ValueError(f"Unsupported numeric token: {token!r}")


def _format_like_kind(value: Fraction, kind: str) -> str:
    if kind == "mixed":
        return _mixed_text(value)
    if kind == "decimal" and Fraction(value).denominator in {1, 2, 4, 5, 10}:
        return str(float(value)).rstrip("0").rstrip(".")
    return _fraction_text(value)


def _extract_number_tokens(text: str) -> list[str]:
    src = _normalize_text(text)
    pattern = re.compile(r"[+-]?\d+\s+\d+/\d+|[+-]?\d+/\d+|[+-]?\d+\.\d+|[+-]?\d+")
    return [m.group(0) for m in pattern.finditer(src)]


def _replace_mixed_numbers(expr: str) -> str:
    def repl(match: re.Match[str]) -> str:
        prefix = match.group(1)
        whole = int(match.group(2))
        num = int(match.group(3))
        den = int(match.group(4))
        total = abs(whole) * den + num
        if whole < 0:
            total = -total
        return f"{prefix}Fraction({total}, {den})"

    return re.sub(r"(^|[\(\[\+\-\*/])\s*([+-]?\d+)\s+(\d+)/(\d+)", repl, expr)


def _replace_simple_fractions(expr: str) -> str:
    return re.sub(
        r"(?<![\w)])([+-]?\d+)\s*/\s*([+-]?\d+)(?![\w(])",
        r"Fraction(\1,\2)",
        expr,
    )


def _replace_decimals(expr: str) -> str:
    return re.sub(
        r"(?<![\w'])([+-]?\d+\.\d+)(?![\w'])",
        lambda m: f"Fraction('{m.group(1)}')",
        expr,
    )


def _insert_implicit_multiplication(expr: str) -> str:
    s = expr
    s = re.sub(r"\)\s*\(", ")*(", s)
    s = re.sub(r"(Fraction\([^()]+\))\s*\(", r"\1*(", s)
    s = re.sub(r"\)\s*(Fraction\([^()]+\))", r")*\1", s)
    s = re.sub(r"(\d)\s*\(", r"\1*(", s)
    s = re.sub(r"\)\s*(\d)", r")*\1", s)
    return s


def _expression_to_fraction(expr: str) -> Fraction:
    s = _normalize_text(expr)
    if "..." in s:
        raise ValueError("ellipsis expression requires dedicated handler")
    s = s.replace("[", "(").replace("]", ")")
    s = _replace_mixed_numbers(s)
    s = _replace_decimals(s)
    s = _replace_simple_fractions(s)
    s = _insert_implicit_multiplication(s)
    value = eval(s, {"__builtins__": {}, "Fraction": Fraction}, {})
    return Fraction(value)


def _sorted_compare_chain(values: list[tuple[Fraction, str]]) -> str:
    ordered = sorted(values, key=lambda item: item[0])
    return " < ".join(label for _, label in ordered)


def _label_from_token(token: str, kind: str) -> str:
    cleaned = _normalize_text(token).strip().strip("()")
    cleaned = re.sub(r"\s+", " ", cleaned)
    if kind in {"fraction", "mixed", "int", "decimal"}:
        return cleaned
    return cleaned


def _latexize_non_math_text(text: str) -> str:
    s = text
    patterns = [
        r"(?<![\w$])[-]?\d+\s+\d+/\d+(?![\w$])",
        r"(?<![\w$])[-]?\d+/\d+(?![\w$])",
        r"(?<![\w$])[-]?\d+\.\d+(?![\w$])",
    ]
    for pattern in patterns:
        s = re.sub(pattern, lambda m: f"${m.group(0)}$", s)
    return s


def _looks_like_bare_math_text(text: str) -> bool:
    raw = str(text or "").strip()
    if not raw or "$" in raw:
        return False
    if re.search(r"[\u4e00-\u9fff]", raw):
        return False
    return bool(
        re.search(r"\\frac|\\times|\\div|\d+/\d+|\d+\s+\d+/\d+|[()\[\]+\-*/=]", raw)
    )


def _render_fraction_token_as_latex(token: str) -> str:
    raw = _normalize_text(token).strip()
    mixed_match = re.fullmatch(r"([+-]?\d+)\s+(\d+)/(\d+)", raw)
    if mixed_match:
        whole = int(mixed_match.group(1))
        num = mixed_match.group(2)
        den = mixed_match.group(3)
        sign = "-" if whole < 0 else ""
        return f"{sign}{abs(whole)}\\frac{{{num}}}{{{den}}}"

    frac_match = re.fullmatch(r"([+-]?\d+)\s*/\s*([+-]?\d+)", raw)
    if frac_match:
        num = int(frac_match.group(1))
        den = int(frac_match.group(2))
        sign = "-" if num * den < 0 else ""
        return f"{sign}\\frac{{{abs(num)}}}{{{abs(den)}}}"

    return raw


def _protect_fraction_like_tokens(segment: str) -> tuple[str, dict[str, str]]:
    text = str(segment or "")
    placeholders: dict[str, str] = {}
    counter = 0

    def keep(value: str) -> str:
        nonlocal counter
        key = f"@@FRAC{counter}@@"
        placeholders[key] = value
        counter += 1
        return key

    explicit_mixed = re.compile(r"(-?\d+)\s*\\frac\{(\d+)\}\{(\d+)\}")
    text = explicit_mixed.sub(
        lambda m: keep(
            f"{'-' if int(m.group(1)) < 0 else ''}{abs(int(m.group(1)))}\\frac{{{m.group(2)}}}{{{m.group(3)}}}"
        ),
        text,
    )

    explicit_frac = re.compile(r"(-?)\\frac\{([^{}]+)\}\{([^{}]+)\}")
    text = explicit_frac.sub(
        lambda m: keep(
            f"{m.group(1)}\\frac{{{m.group(2)}}}{{{m.group(3)}}}"
        ),
        text,
    )

    ascii_mixed = re.compile(r"(?<![\w\\])(-?\d+)\s+(\d+)\s*/\s*(\d+)(?![\w])")
    text = ascii_mixed.sub(
        lambda m: keep(_render_fraction_token_as_latex(m.group(0))),
        text,
    )

    ascii_frac = re.compile(r"(?<![\w\\])(-?\d+)\s*/\s*(-?\d+)(?![\w])")
    text = ascii_frac.sub(
        lambda m: keep(_render_fraction_token_as_latex(m.group(0))),
        text,
    )

    return text, placeholders


def _render_math_segment_as_textbook_latex(segment: str) -> str:
    s = str(segment or "").strip()
    replacements = {
        "\uff0b": "+",
        "\uff0d": "-",
        "\u00d7": r"\times",
        "\u00f7": r"\div",
        "\\left": "",
        "\\right": "",
        "\\cdot": r"\times",
        "\\;": " ",
        "[": "(",
        "]": ")",
    }
    for old, new in replacements.items():
        s = s.replace(old, new)
    s, placeholders = _protect_fraction_like_tokens(s)
    s = s.replace("*", r"\times ")
    s = s.replace("/", r"\div ")
    s = s.replace(r"\times", r"\times ")
    s = s.replace(r"\div", r"\div ")
    s = re.sub(r"\s+", " ", s).strip()
    s = s.replace(r"\times )", r"\times)")
    s = s.replace(r"\div )", r"\div)")
    for key, value in placeholders.items():
        s = s.replace(key, value)
    return s


def _latexize_question_text(text: str) -> str:
    raw = str(text or "").strip()
    if not raw:
        return raw

    if _looks_like_bare_math_text(raw):
        prewrapped = f"${raw}$"
    else:
        prewrapped = raw if "$" in raw else _latexize_non_math_text(raw)
    parts = prewrapped.split("$")

    out = _latexize_non_math_text(parts[0])
    for idx in range(1, len(parts)):
        if idx % 2 == 1:
            out += f"${_render_math_segment_as_textbook_latex(parts[idx])}$"
        else:
            out += _latexize_non_math_text(parts[idx])
    return out


class FractionFunctionHelper:
    def can_handle(self, question_text: str) -> bool:
        try:
            self.build_config(question_text)
            return True
        except Exception:
            return False

    def build_generator_code(self, question_text: str) -> str:
        config_repr = repr(self.build_config(question_text))
        return f"""from core.fraction_domain_functions import FractionFunctionHelper

_FRAC_HELPER = FractionFunctionHelper()
_FRAC_CONFIG = {config_repr}

def generate(level=1, **kwargs):
    runtime_config = _FRAC_HELPER.build_runtime_config(_FRAC_CONFIG, level=level, **kwargs)
    return _FRAC_HELPER.generate_from_config(runtime_config)

def check(user_answer, correct_answer):
    return _FRAC_HELPER.check_answer(_FRAC_CONFIG, user_answer, correct_answer)
"""

    def check_answer(
        self,
        config: dict[str, Any],
        user_answer: Any,
        correct_answer: Any,
    ) -> dict[str, Any]:
        family = config.get("family", "")
        u = str(user_answer or "").strip().replace(" ", "")
        c = str(correct_answer or "").strip().replace(" ", "")
        if u == c:
            return {"correct": True, "result": "甇答對"}

        if family in {
            "frac_simplify",
            "frac_equivalent_fill_blank",
            "frac_preserve_value",
            "frac_reciprocal",
            "frac_eval_expression",
            "frac_word_drone_weight",
            "frac_word_bottle_weight",
            "frac_word_remaining_milk",
            "frac_word_library_total",
        }:
            try:
                if Fraction(u) == Fraction(c):
                    return {"correct": True, "result": "甇答對"}
            except Exception:
                pass
        return {"correct": False, "result": "錯誤"}

    def build_config(self, question_text: str) -> dict[str, Any]:
        src = str(question_text or "").strip()
        norm = _normalize_text(src)

        if "灰色方塊" in norm or "白色方塊" in norm:
            raise ValueError("image-dependent fraction geometry is excluded from phase 1")

        if "空格內填入適當的數字" in norm or "_" in norm:
            return self._build_fill_blank_config(src)
        if "其值才不會變" in norm and "分母加上" in norm:
            return self._build_preserve_value_config(src)
        if "無人機" in norm and "農藥" in norm:
            return {"family": "frac_word_drone_weight", "source_text": src}
        if "果汁" in norm and "瓶子" in norm:
            return {"family": "frac_word_bottle_weight", "source_text": src}
        if "牛奶" in norm and "還剩下多少" in norm:
            return {"family": "frac_word_remaining_milk", "source_text": src}
        if "財產分給四個兒子" in norm:
            return {"family": "frac_word_inheritance_compare", "source_text": src}
        if "圖書館" in norm and "450 本新書" in norm:
            return {"family": "frac_word_library_total", "source_text": src}
        if "倒數" in norm:
            return self._build_reciprocal_config(src)
        if "比較" in norm and ("大小" in norm or "和" in norm):
            return self._build_compare_config(src)
        if "最簡分數" in norm or "化成最簡分數" in norm:
            return self._build_simplify_config(src)
        if "計算" in norm or re.search(r"\$[^$]+\$", src):
            return self._build_eval_config(src)
        if self._looks_like_bare_fraction_math(norm):
            return self._build_eval_config(src)
        raise ValueError(f"Unsupported fraction family: {src[:80]}")

    def generate_from_config(self, config: dict[str, Any]) -> dict[str, Any]:
        family = config["family"]
        method = getattr(self, f"_generate_{family}")
        result = method(config)
        result["question_text"] = _latexize_question_text(str(result.get("question_text") or ""))
        return result

    def build_runtime_config(self, config: dict[str, Any], level: int = 1, **kwargs: Any) -> dict[str, Any]:
        family = str(config.get("family") or "")
        builder = getattr(self, f"_runtime_{family}", None)
        if callable(builder):
            try:
                return builder(config, level=level, **kwargs)
            except Exception:
                return dict(config)
        return dict(config)

    def _looks_like_bare_fraction_math(self, text: str) -> bool:
        return bool(re.search(r"\d+/\d+|\d+\s+\d+/\d+|\d+\.\d+", text)) and any(
            token in text for token in ("+", "-", "*", "/", "(", ")", "[", "]")
        )

    def _runtime_frac_simplify(self, config: dict[str, Any], level: int = 1, **_: Any) -> dict[str, Any]:
        kind = str(config.get("kind") or "fraction")
        value = self._variant_value_like(Fraction(config["value"]), kind)
        return {
            "family": "frac_simplify",
            "source_text": f"將下列各分數化成最簡分數：${self._surface_token(value, kind)}$",
            "value": value,
            "kind": kind,
        }

    def _runtime_frac_equivalent_fill_blank(self, config: dict[str, Any], level: int = 1, **_: Any) -> dict[str, Any]:
        original_text = str(config.get("source_text") or "")
        blank_specs = list(config.get("blank_specs") or [])
        segment_layouts = list(config.get("segment_layouts") or [])

        def _build() -> dict[str, Any]:
            base = self._variant_value_like(Fraction(config["base_value"]), "fraction")
            if base.denominator == 1:
                base = Fraction(base.numerator, max(2, abs(base.numerator) + 1))
            segments = [self._surface_token(base, "fraction")]
            new_specs: list[dict[str, Any]] = []
            blank_idx = 0
            non_base_layout = segment_layouts[1:] if segment_layouts[:1] == ["base"] else segment_layouts
            if not non_base_layout:
                non_base_layout = ["blank"] * len(blank_specs)
            for idx, role in enumerate(non_base_layout, start=1):
                scale = random.choice([3, 4, 5, 6, 7, 8]) + idx
                if role == "known":
                    segments.append(f"({base.numerator * scale})/({base.denominator * scale})")
                    continue
                blank = blank_specs[min(blank_idx, len(blank_specs) - 1)]
                if blank["kind"] == "num":
                    den = base.denominator * scale
                    segments.append(f"(_)/({den})")
                    new_specs.append({"kind": "num", "den": den})
                else:
                    num = base.numerator * scale
                    segments.append(f"({num})/(_)")
                    new_specs.append({"kind": "den", "num": num})
                blank_idx += 1
            return {
                "family": "frac_equivalent_fill_blank",
                "source_text": "?其??征?澆憛怠?拍?摮?$" + "=".join(segments) + "$",
                "base_value": base,
                "blank_specs": new_specs,
                "segment_layouts": ["base"] + non_base_layout,
            }

        return self._ensure_runtime_variation(original_text, _build)

        blank_specs = list(config.get("blank_specs") or [])
        segment_layouts = list(config.get("segment_layouts") or [])
        base = self._variant_value_like(Fraction(config["base_value"]), "fraction")
        if base.denominator == 1:
            base = Fraction(base.numerator, max(2, abs(base.numerator) + 1))
        segments = [self._surface_token(base, "fraction")]
        new_specs: list[dict[str, Any]] = []
        blank_idx = 0
        non_base_layout = segment_layouts[1:] if segment_layouts[:1] == ["base"] else segment_layouts
        if not non_base_layout:
            non_base_layout = ["blank"] * len(blank_specs)
        for idx, role in enumerate(non_base_layout, start=1):
            scale = random.choice([2, 3, 4, 5, 6, 7]) + idx - 1
            if role == "known":
                segments.append(f"({base.numerator * scale})/({base.denominator * scale})")
                continue
            blank = blank_specs[min(blank_idx, len(blank_specs) - 1)]
            if blank["kind"] == "num":
                den = base.denominator * scale
                segments.append(f"(_)/({den})")
                new_specs.append({"kind": "num", "den": den})
            else:
                num = base.numerator * scale
                segments.append(f"({num})/(_)")
                new_specs.append({"kind": "den", "num": num})
            blank_idx += 1
        return {
            "family": "frac_equivalent_fill_blank",
            "source_text": "在下列空格內填入適當的數字：$" + "=".join(segments) + "$",
            "base_value": base,
            "blank_specs": new_specs,
            "segment_layouts": ["base"] + non_base_layout,
        }

    def _runtime_frac_preserve_value(self, config: dict[str, Any], level: int = 1, **_: Any) -> dict[str, Any]:
        original_text = str(config.get("source_text") or "")

        def _build() -> dict[str, Any]:
            value = self._variant_value_like(Fraction(config["value"]), "fraction")
            scale = random.choice([2, 3, 4, 5])
            delta = value.denominator * (scale - 1)
            return {
                "family": "frac_preserve_value",
                "source_text": f"如果 ${self._surface_token(value, 'fraction')}$ 的分母加上 {delta}，那麼分子要加上多少，其值才不會變？",
                "value": value,
                "delta": delta,
            }

        return self._ensure_runtime_variation(original_text, _build)

    def _runtime_frac_compare_set(self, config: dict[str, Any], level: int = 1, **_: Any) -> dict[str, Any]:
        original_text = str(config.get("source_text") or "")
        original_numbers = list(config.get("numbers") or [])

        def _build() -> dict[str, Any]:
            new_numbers: list[dict[str, Any]] = []
            labels: list[str] = []
            for item in original_numbers:
                label = str(item.get("label") or "")
                kind = self._infer_label_kind(label)
                value = self._variant_value_like(Fraction(item["value"]), kind)
                surface = self._surface_token(value, kind)
                new_numbers.append({"value": value, "label": surface})
                labels.append(f"${surface}$")
            return {
                "family": "frac_compare_set",
                "source_text": "比較下列各組數的大小：" + "、".join(labels),
                "numbers": new_numbers,
            }

        return self._ensure_runtime_variation(original_text, _build)

    def _runtime_frac_reciprocal(self, config: dict[str, Any], level: int = 1, **_: Any) -> dict[str, Any]:
        kind = str(config.get("kind") or "fraction")
        value = self._variant_value_like(Fraction(config["value"]), kind)
        if value == 0:
            value = Fraction(1, 2)
        return {
            "family": "frac_reciprocal",
            "source_text": f"寫出下列各數的倒數：${self._surface_token(value, kind)}$",
            "value": value,
            "kind": kind,
        }

    def _runtime_frac_eval_expression(self, config: dict[str, Any], level: int = 1, **_: Any) -> dict[str, Any]:
        if config.get("ellipsis"):
            compact = _normalize_text(str(config.get("expr") or "")).replace(" ", "")
            if compact.startswith("(1-2/3)(1-2/4)(1-2/5)"):
                whole = random.choice([2, 3])
                numer = 1
                start = 3 + random.choice([1, 2, 3])
                end = start + 13
                expr = f"({whole}-{numer}/{start})({whole}-{numer}/{start+1})({whole}-{numer}/{start+2})...({whole}-{numer}/{end-1})({whole}-{numer}/{end})"
                return {
                    "family": "frac_eval_expression",
                    "source_text": f"計算下列各式的值：${expr}$",
                    "expr": expr,
                    "ellipsis": True,
                    "ellipsis_meta": {"kind": "one_minus_fraction", "whole": whole, "numer": numer, "start": start, "end": end},
                }
            if compact.startswith("(-2/3)*(-3/4)*(-4/5)") or compact.startswith("(-2/3)(-3/4)(-4/5)"):
                start = random.choice([3, 4, 5, 6])
                end = start + 97
                expr = f"(-{start}/{start+1})*(-{start+1}/{start+2})*(-{start+2}/{start+3})*...*(-{end-1}/{end})*(-{end}/{end+1})"
                return {
                    "family": "frac_eval_expression",
                    "source_text": f"計算下列各式的值：${expr}$",
                    "expr": expr,
                    "ellipsis": True,
                    "ellipsis_meta": {"kind": "neg_n_over_n_plus_1", "start": start, "end": end},
                }
            if compact.startswith("(-3/2)*(-4/3)*(-5/4)") or compact.startswith("(-3/2)(-4/3)(-5/4)"):
                start = random.choice([3, 4, 5, 6])
                end = start + 98
                expr = f"(-{start+1}/{start})*(-{start+2}/{start+1})*(-{start+3}/{start+2})*...*(-{end}/{end-1})*(-{end+1}/{end})"
                return {
                    "family": "frac_eval_expression",
                    "source_text": f"計算下列各式的值：${expr}$",
                    "expr": expr,
                    "ellipsis": True,
                    "ellipsis_meta": {"kind": "neg_n_plus_1_over_n", "start": start, "end": end},
                }
            return dict(config)
        if self._is_grouped_decimal_mix_expression(str(config.get("expr") or "")):
            original_text = str(config.get("source_text") or "")

            def _build_grouped_decimal_mix() -> dict[str, Any]:
                expr = self._friendly_grouped_decimal_mix_expr(str(config.get("expr") or ""))
                built = self.build_config(expr)
                built["family"] = "frac_eval_expression"
                return built

            return self._ensure_runtime_variation(original_text, _build_grouped_decimal_mix)
        if self._is_decimal_mix_expression(str(config.get("expr") or "")):
            original_text = str(config.get("source_text") or "")

            def _build_decimal_mix() -> dict[str, Any]:
                expr = self._friendly_decimal_mix_expr(str(config.get("expr") or ""))
                built = self.build_config(expr)
                built["family"] = "frac_eval_expression"
                return built

            return self._ensure_runtime_variation(original_text, _build_decimal_mix)
        source_text = str(config.get("source_text") or "")
        original_tokens = self._math_number_tokens(source_text)
        for _ in range(24):
            variant_text = self._build_eval_expression_variant_text(source_text)
            variant_tokens = self._math_number_tokens(variant_text)
            if variant_text and variant_text != source_text and self._all_tokens_changed(original_tokens, variant_tokens):
                try:
                    return self.build_config(variant_text)
                except Exception:
                    continue
        return dict(config)

    def _runtime_frac_eval_common_factor(self, config: dict[str, Any], level: int = 1, **_: Any) -> dict[str, Any]:
        original_text = str(config.get("source_text") or "")
        pattern = dict(config.get("common_factor_pattern") or {})

        def _build() -> dict[str, Any]:
            expr = self._friendly_common_factor_expr(pattern)
            built = self.build_config(expr)
            built["family"] = "frac_eval_common_factor"
            built["common_factor_pattern"] = self._extract_common_factor_pattern(expr) or pattern
            return built

        return self._ensure_runtime_variation(original_text, _build)

    def _friendly_common_factor_expr(self, pattern: dict[str, Any]) -> str:
        op = str(pattern.get("op") or "-")
        shared_side = str(pattern.get("shared_side") or "right")
        factor_token = str(pattern.get("factor") or "")

        if shared_side == "left":
            factor = self._friendly_common_factor_mixed(op)
            left_int, right_int = self._friendly_common_factor_int_pair(op)
            return f"{factor}\\times{left_int}{op}{factor}\\times{right_int}"

        if "\\frac" in factor_token or "/" in factor_token:
            factor = self._friendly_common_factor_int(op, allow_negative=True)
            left_mixed, right_mixed = self._friendly_common_factor_mixed_pair(op)
            return f"{left_mixed}\\times{factor}{op}{right_mixed}\\times{factor}"

        factor = self._friendly_common_factor_int(op, allow_negative=True)
        left_mixed, right_mixed = self._friendly_common_factor_mixed_pair(op)
        return f"{left_mixed}\\times{factor}{op}{right_mixed}\\times{factor}"

    def _friendly_common_factor_int(self, op: str, *, allow_negative: bool) -> str:
        base = random.choice([2, 3, 4, 5, 6, 7, 8])
        if allow_negative:
            sign = random.choice([-1, 1])
            return f"({sign * base})" if sign < 0 else str(base)
        return str(base)

    def _friendly_common_factor_int_pair(self, op: str) -> tuple[str, str]:
        if op == "+":
            options = [
                (8, -4),
                (9, -3),
                (10, -5),
                (12, -6),
                (7, -2),
                (6, -4),
            ]
        else:
            options = [
                (7, 3),
                (8, 4),
                (9, 3),
                (10, 5),
                (11, 7),
                (12, 8),
            ]
        left, right = random.choice(options)
        return str(left), f"({right})" if right < 0 else str(right)

    def _friendly_common_factor_mixed(self, op: str) -> str:
        if op == "+":
            options = [
                (2, 1, 2),
                (2, 1, 3),
                (3, 1, 2),
                (3, 1, 4),
                (4, 1, 2),
            ]
        else:
            options = [
                (1, 1, 2),
                (2, 1, 2),
                (2, 1, 3),
                (3, 1, 2),
                (3, 1, 4),
            ]
        whole, num, den = random.choice(options)
        return f"{whole}\\frac{{{num}}}{{{den}}}"

    def _friendly_common_factor_mixed_pair(self, op: str) -> tuple[str, str]:
        if op == "+":
            options = [
                ((1, 1, 2), (2, 1, 2)),
                ((2, 1, 3), (1, 2, 3)),
                ((3, 1, 4), (1, 3, 4)),
                ((2, 1, 5), (1, 4, 5)),
                ((4, 1, 2), (1, 1, 2)),
            ]
        else:
            options = [
                ((4, 1, 2), (2, 1, 2)),
                ((3, 2, 3), (1, 2, 3)),
                ((4, 3, 4), (2, 3, 4)),
                ((3, 4, 5), (1, 4, 5)),
                ((3, 5, 6), (1, 5, 6)),
            ]
        left, right = random.choice(options)
        return self._mixed_latex(*left), self._mixed_latex(*right)

    def _mixed_latex(self, whole: int, num: int, den: int) -> str:
        return f"{whole}\\frac{{{num}}}{{{den}}}"

    def _is_decimal_mix_expression(self, expr: str) -> bool:
        compact = _normalize_text(expr).replace(" ", "")
        if "." not in compact:
            return False
        if "*" not in compact or "/" not in compact:
            return False
        fraction_count = len(re.findall(r"\d+/\d+", compact))
        if fraction_count < 2 or not any(op in compact for op in ["+", "-"]):
            return False
        return bool(re.search(r"/\(?-?\d+\.\d+\)?", compact))

    def _is_grouped_decimal_mix_expression(self, expr: str) -> bool:
        compact = _normalize_text(expr).replace(" ", "")
        if "." not in compact:
            return False
        if "*" not in compact or "/" not in compact:
            return False
        if "(" not in compact or ")" not in compact:
            return False
        fraction_count = len(re.findall(r"\d+/\d+", compact))
        if fraction_count < 3:
            return False
        has_grouped_fraction_decimal = (
            bool(re.search(r"\d+/\d+\)+[+-]\d+\.\d+", compact))
            or bool(re.search(r"\d+\.\d+[+-]\(+\d+/\d+", compact))
        )
        if not has_grouped_fraction_decimal:
            return False
        return bool(re.search(r"/\(-?\(?\d+/\d+\)?\)", compact))

    def _friendly_decimal_mix_expr(self, expr: str) -> str:
        compact = _normalize_text(expr).replace(" ", "")
        if "+" in compact:
            templates = [
                r"\frac{2}{3}\div(-0.5)\times(-\frac{1}{2})+\frac{1}{3}",
                r"\frac{3}{4}\div(-0.5)\times(-\frac{2}{3})+\frac{1}{4}",
                r"\frac{3}{5}\div(-0.2)\times(-\frac{1}{5})+\frac{2}{5}",
                r"\frac{5}{6}\div(-0.5)\times(-\frac{1}{2})+\frac{1}{6}",
                r"\frac{3}{4}\div(-0.25)\times(-\frac{1}{4})+\frac{1}{4}",
            ]
        else:
            templates = [
                r"\frac{3}{4}\div(-0.5)\times(-\frac{2}{3})-\frac{1}{4}",
                r"\frac{2}{3}\div(-0.25)\times(-\frac{1}{4})-\frac{1}{6}",
                r"\frac{3}{5}\div(-0.2)\times(-\frac{1}{5})-\frac{1}{5}",
                r"\frac{5}{6}\div(-0.5)\times(-\frac{1}{2})-\frac{1}{3}",
                r"\frac{4}{5}\div(-0.4)\times(-\frac{1}{2})-\frac{1}{5}",
            ]
        return random.choice(templates)

    def _friendly_grouped_decimal_mix_expr(self, expr: str) -> str:
        compact = _normalize_text(expr).replace(" ", "")
        if "+" in compact:
            templates = [
                r"(-\frac{1}{2})\times(\frac{1}{2}+0.5)\div(-2)",
                r"(-\frac{2}{5})\times(\frac{3}{5}+0.4)\div(-2)",
                r"(-\frac{3}{5})\times(\frac{2}{5}+0.6)\div(-3)",
                r"(-\frac{1}{4})\times(\frac{3}{4}+0.25)\div(-2)",
                r"(-\frac{3}{10})\times(\frac{7}{10}+0.3)\div(-2)",
            ]
        else:
            templates = [
                r"(-\frac{1}{2})\times(\frac{3}{2}-0.5)\div(-2)",
                r"(-\frac{2}{5})\times(\frac{7}{5}-0.4)\div(-2)",
                r"(-\frac{3}{5})\times(\frac{8}{5}-0.6)\div(-3)",
                r"(-\frac{1}{4})\times(\frac{5}{4}-0.25)\div(-2)",
                r"(-\frac{3}{10})\times(\frac{13}{10}-0.3)\div(-2)",
            ]
        return random.choice(templates)

    def _runtime_frac_word_drone_weight(self, config: dict[str, Any], level: int = 1, **_: Any) -> dict[str, Any]:
        original_text = str(config.get("source_text") or "")

        def _build() -> dict[str, Any]:
            empty = Fraction(random.choice([18, 21, 24, 27, 30, 33, 36]))
            pesticide = Fraction(random.choice([12, 14, 16, 18, 20, 24]))
            full = empty + pesticide
            total_minutes = random.choice([36, 42, 48, 54, 60])
            elapsed = random.choice([9, 12, 15, 18, 21, 24])
            remaining = pesticide * Fraction(total_minutes - elapsed, total_minutes)
            after = empty + remaining
            return {
                "family": "frac_word_drone_weight",
                "source_text": (
                    f"一臺農用無人機裝滿農藥的重量為 {full} 公斤，若每分鐘噴灑的農藥重量皆相等，"
                    f"噴灑飛行 {total_minutes} 分鐘後，可將農藥噴完沒有剩下。某次此無人機裝滿農藥噴灑飛行 "
                    f"{elapsed} 分鐘後，無人機與剩餘農藥重量為 {after} 公斤，則此無人機未裝農藥時的重量為多少公斤？"
                ),
                "full_weight": full,
                "total_minutes": total_minutes,
                "elapsed_minutes": elapsed,
                "after_weight": after,
            }

        return self._ensure_runtime_variation(original_text, _build)

    def _runtime_frac_word_bottle_weight(self, config: dict[str, Any], level: int = 1, **_: Any) -> dict[str, Any]:
        original_text = str(config.get("source_text") or "")

        def _build() -> dict[str, Any]:
            bottle = Fraction(random.choice([110, 140, 170, 200, 230]))
            juice = Fraction(random.choice([420, 540, 660, 780, 900]))
            drank = random.choice([Fraction(1, 2), Fraction(2, 3), Fraction(3, 4), Fraction(4, 5)])
            full = bottle + juice
            after = bottle + juice * (1 - drank)
            return {
                "family": "frac_word_bottle_weight",
                "source_text": (
                    f"有一瓶果汁，連瓶子共重 {full} 公克，喝了 ${self._surface_token(drank, 'fraction')}$ 瓶的果汁後，"
                    f"剩餘的果汁連瓶子共重 {after} 公克，求空瓶子重多少公克？"
                ),
                "full_total": full,
                "after_total": after,
                "drank_fraction": drank,
            }

        return self._ensure_runtime_variation(original_text, _build)

    def _runtime_frac_word_remaining_milk(self, config: dict[str, Any], level: int = 1, **_: Any) -> dict[str, Any]:
        original_text = str(config.get("source_text") or "")

        def _build() -> dict[str, Any]:
            total = Fraction(random.choice([360, 420, 540, 600, 660]))
            first = random.choice([Fraction(1, 2), Fraction(5, 8), Fraction(2, 3), Fraction(3, 4)])
            second = random.choice([Fraction(1, 2), Fraction(2, 3), Fraction(3, 4), Fraction(4, 5)])
            return {
                "family": "frac_word_remaining_milk",
                "source_text": (
                    f"一瓶 {total} 毫升的牛奶，美美第一次喝了全部的 ${self._surface_token(first, 'fraction')}$，"
                    f"第二次喝了剩下的 ${self._surface_token(second, 'fraction')}$，還剩下多少毫升的牛奶？"
                ),
                "total_ml": total,
                "first_fraction": first,
                "second_fraction": second,
            }

        return self._ensure_runtime_variation(original_text, _build)

    def _runtime_frac_word_inheritance_compare(self, config: dict[str, Any], level: int = 1, **_: Any) -> dict[str, Any]:
        original_text = str(config.get("source_text") or "")

        def _build() -> dict[str, Any]:
            first = random.choice([Fraction(1, 5), Fraction(1, 4), Fraction(2, 7)])
            second = random.choice([Fraction(1, 4), Fraction(1, 3), Fraction(2, 5)])
            third = random.choice([Fraction(2, 5), Fraction(1, 2), Fraction(3, 5)])
            return {
                "family": "frac_word_inheritance_compare",
                "source_text": (
                    "馬爺爺打算將財產分給四個兒子，分配的方法如下："
                    f"大兒子得到總財產的 ${self._surface_token(first, 'fraction')}$，"
                    f"二兒子得到分給大兒子後剩下的 ${self._surface_token(second, 'fraction')}$，"
                    f"三兒子得到分給大兒子和二兒子後剩下的 ${self._surface_token(third, 'fraction')}$，"
                    "四兒子得到最後剩下的財產。想想看，四個兒子中誰分到的比較多？誰分到的比較少？"
                ),
                "first_share_fraction": first,
                "second_share_fraction": second,
                "third_share_fraction": third,
            }

        return self._ensure_runtime_variation(original_text, _build)

    def _runtime_frac_word_library_total(self, config: dict[str, Any], level: int = 1, **_: Any) -> dict[str, Any]:
        original_text = str(config.get("source_text") or "")

        def _build() -> dict[str, Any]:
            added = Fraction(random.choice([180, 240, 300, 360, 540, 600]))
            ratio = random.choice([Fraction(2, 3), Fraction(3, 5), Fraction(4, 7), Fraction(5, 8)])
            return {
                "family": "frac_word_library_total",
                "source_text": (
                    f"已知康康國中圖書館今年添購了 {added} 本新書，且添購新書前的數量是添購後的 "
                    f"${self._surface_token(ratio, 'fraction')}$ 倍，試問添購前圖書館共有多少本書？"
                ),
                "added_books": added,
                "before_after_ratio": ratio,
            }

        return self._ensure_runtime_variation(original_text, _build)

    def _surface_token(self, value: Fraction, kind: str) -> str:
        value = Fraction(value)
        if kind == "mixed":
            return _mixed_text(value)
        if kind == "int":
            return _scalar_text(value)
        return _fraction_text(value)

    def _infer_label_kind(self, label: str) -> str:
        raw = _normalize_text(label)
        if re.fullmatch(r"-?\d+\s+\d+/\d+", raw):
            return "mixed"
        if re.fullmatch(r"-?\d+/\d+", raw):
            return "fraction"
        if re.fullmatch(r"-?\d+\.\d+", raw):
            return "decimal"
        return "int"

    def _variant_value_like(self, value: Fraction, kind: str) -> Fraction:
        value = Fraction(value)
        sign = -1 if value < 0 else 1
        if kind == "int":
            return Fraction(self._variant_int(value.numerator), 1)
        if kind == "mixed":
            num, den = self._random_reduced_proper_fraction_pair()
            whole = sign * random.randint(1, 5)
            total = abs(whole) * den + num
            return Fraction(sign * total, den)
        num_text = self._variant_fraction_text(value.numerator, value.denominator, latex=False)
        return Fraction(num_text)

    def _math_number_tokens(self, text: str) -> list[str]:
        return re.findall(
            r"-?\d+\s*\\frac\{\d+\}\{\d+\}|-?\\frac\{\d+\}\{\d+\}|-?\d+\s+\d+/\d+|-?\d+/\d+|-?\d+\.\d+|-?\d+",
            str(text or ""),
        )

    def _all_tokens_changed(self, original: list[str], variant: list[str]) -> bool:
        if not original or len(original) != len(variant):
            return False
        return all(o != v for o, v in zip(original, variant))

    def _ensure_runtime_variation(self, original_text: str, builder: Any, attempts: int = 24) -> dict[str, Any]:
        fallback = builder()
        for _ in range(attempts):
            candidate = builder()
            if self._all_tokens_changed(
                self._math_number_tokens(original_text),
                self._math_number_tokens(str(candidate.get("source_text") or "")),
            ):
                return candidate
            fallback = candidate
        return fallback

    def _build_eval_expression_variant_text(self, source_text: str) -> str:
        raw = str(source_text or "")
        if not raw:
            return raw

        if "$" in raw:
            parts = raw.split("$")
            for idx in range(1, len(parts), 2):
                varied = self._randomize_math_expression_segment(parts[idx])
                if varied != parts[idx]:
                    parts[idx] = varied
                    return "$".join(parts)
            return raw

        return self._randomize_math_expression_segment(raw)

    def _randomize_math_expression_segment(self, segment: str) -> str:
        token_pattern = re.compile(
            r"(?<![\w\\])-?\d+\s*\\frac\{\d+\}\{\d+\}"
            r"|(?<![\w\\])-?\\frac\{\d+\}\{\d+\}"
            r"|(?<![\w\\])-?\d+\s+\d+/\d+"
            r"|(?<![\w\\])-?\d+/\d+"
            r"|(?<![\w\\])-?\d+\.\d+"
            r"|(?<![\w\\])-?\d+"
        )

        matches = list(token_pattern.finditer(segment))
        if not matches:
            return segment

        changed = False
        pieces: list[str] = []
        last = 0
        for match in matches:
            pieces.append(segment[last:match.start()])
            original = match.group(0)
            randomized = self._randomize_numeric_token(original)
            if randomized != original:
                changed = True
            pieces.append(randomized)
            last = match.end()
        pieces.append(segment[last:])
        return "".join(pieces) if changed else segment

    def _randomize_numeric_token(self, token: str) -> str:
        raw = str(token or "")

        explicit_mixed = re.fullmatch(r"(-?\d+)\s*\\frac\{(\d+)\}\{(\d+)\}", raw)
        if explicit_mixed:
            whole = int(explicit_mixed.group(1))
            new_whole = self._variant_whole(whole)
            return self._render_random_mixed_token(new_whole, latex=True)

        explicit_frac = re.fullmatch(r"(-?)\\frac\{(\d+)\}\{(\d+)\}", raw)
        if explicit_frac:
            sign = -1 if explicit_frac.group(1) == "-" else 1
            num = int(explicit_frac.group(2))
            den = int(explicit_frac.group(3))
            return self._variant_fraction_text(sign * num, den, latex=True)

        ascii_mixed = re.fullmatch(r"(-?\d+)\s+(\d+)/(\d+)", raw)
        if ascii_mixed:
            whole = int(ascii_mixed.group(1))
            new_whole = self._variant_whole(whole)
            return self._render_random_mixed_token(new_whole, latex=False)

        ascii_frac = re.fullmatch(r"(-?\d+)/(-?\d+)", raw)
        if ascii_frac:
            num = int(ascii_frac.group(1))
            den = int(ascii_frac.group(2))
            return self._variant_fraction_text(num, den, latex=False)

        decimal_match = re.fullmatch(r"-?\d+\.\d+", raw)
        if decimal_match:
            sign = -1 if raw.startswith("-") else 1
            value = abs(Fraction(raw))
            options = [
                Fraction(1, 5),
                Fraction(3, 10),
                Fraction(1, 2),
                Fraction(7, 10),
                Fraction(6, 5),
                Fraction(3, 2),
                Fraction(9, 5),
                Fraction(11, 10),
            ]
            candidates = [opt for opt in options if opt != value]
            replacement = random.choice(candidates) if candidates else value
            replacement *= sign
            return str(float(replacement)).rstrip("0").rstrip(".")

        int_match = re.fullmatch(r"-?\d+", raw)
        if int_match:
            value = int(raw)
            return str(self._variant_int(value))

        return raw

    def _variant_whole(self, value: int) -> int:
        sign = -1 if value < 0 else 1
        mag = abs(value)
        if mag == 0:
            return sign * random.choice([1, 2])
        candidates = sorted({candidate for candidate in (mag - 1, mag + 1, mag + 2) if candidate >= 1 and candidate != mag})
        new_mag = random.choice(candidates)
        return sign * max(1, new_mag)

    def _variant_proper_numerator(self, num: int, den: int) -> int:
        if den <= 1:
            return num
        candidates = {num}
        for delta in (-2, -1, 1, 2):
            candidate = num + delta
            if 0 < candidate < den:
                candidates.add(candidate)
        candidates.discard(num)
        return random.choice(sorted(candidates)) if candidates else num

    def _variant_int(self, value: int) -> int:
        sign = -1 if value < 0 else 1
        mag = abs(value)
        if mag == 0:
            return sign * random.choice([1, 2, 3])
        candidates = sorted({candidate for candidate in (mag - 1, mag + 1, mag + 2) if candidate >= 1 and candidate != mag})
        new_mag = random.choice(candidates)
        return sign * max(1, new_mag)

    def _variant_fraction_text(self, num: int, den: int, *, latex: bool) -> str:
        sign = -1 if num * den < 0 else 1
        abs_num = abs(num)
        abs_den = abs(den) if den else 1
        proper = abs_num < abs_den
        candidates: list[tuple[int, int]] = []

        def add_candidate(c_num: int, c_den: int) -> None:
            if c_den <= 0 or c_num <= 0:
                return
            if proper and not (c_num < c_den):
                return
            if (not proper) and c_num < c_den:
                return
            if math.gcd(c_num, c_den) != 1:
                return
            if c_num == abs_num and c_den == abs_den:
                return
            candidates.append((c_num, c_den))

        preferred_dens = sorted(
            {
                d
                for d in (
                    2, 3, 4, 5, 6, 7, 8, 9, 10,
                    abs_den - 2,
                    abs_den - 1,
                    abs_den,
                    abs_den + 1,
                    abs_den + 2,
                )
                if d and d > 1
            },
            key=lambda d: (abs(d - abs_den), d),
        )

        if proper:
            for cand_den in preferred_dens:
                upper = min(cand_den, max(abs_num + 4, 6))
                for cand_num in range(1, upper):
                    add_candidate(cand_num, cand_den)
        else:
            for cand_den in preferred_dens:
                for bump in (1, max(1, cand_den // 3), max(1, cand_den // 2), cand_den):
                    add_candidate(abs_num + bump, cand_den)

        if candidates:
            new_num, new_den = random.choice(candidates)
        else:
            new_num, new_den = abs_num, abs_den
        prefix = "-" if sign < 0 else ""
        if latex:
            return f"{prefix}\\frac{{{new_num}}}{{{new_den}}}"
        return f"{prefix}{new_num}/{new_den}"

    def _random_reduced_proper_fraction_pair(self) -> tuple[int, int]:
        den = random.choice([2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
        nums = [n for n in range(1, den) if math.gcd(n, den) == 1]
        return random.choice(nums), den

    def _render_random_mixed_token(self, whole: int, *, latex: bool) -> str:
        sign = -1 if whole < 0 else 1
        num, den = self._random_reduced_proper_fraction_pair()
        whole_abs = abs(whole)
        if latex:
            return f"{'-' if sign < 0 else ''}{whole_abs}\\frac{{{num}}}{{{den}}}"
        return f"{'-' if sign < 0 else ''}{whole_abs} {num}/{den}"

    def _first_math_segment_or_src(self, src: str) -> str:
        math_parts = re.findall(r"\$([^$]+)\$", src)
        return math_parts[0] if math_parts else src

    def _build_simplify_config(self, src: str) -> dict[str, Any]:
        expr = self._first_math_segment_or_src(src)
        value, kind = _parse_number_token(expr)
        return {
            "family": "frac_simplify",
            "source_text": src,
            "value": value,
            "kind": kind,
        }

    def _build_fill_blank_config(self, src: str) -> dict[str, Any]:
        norm = _normalize_text(self._first_math_segment_or_src(src))
        segments = [seg.strip() for seg in norm.split("=")]
        if len(segments) < 2:
            raise ValueError("invalid equivalent-fraction chain")

        base_val: Fraction | None = None
        for seg in segments:
            if "_" in seg:
                continue
            candidate = seg.strip()
            if "/" not in candidate:
                continue
            try:
                base_val, _ = _parse_number_token(candidate)
                break
            except Exception:
                continue
        if base_val is None:
            raise ValueError("cannot identify base fraction")

        blank_specs: list[dict[str, Any]] = []
        segment_layouts: list[str] = []
        base_consumed = False
        for seg in segments:
            if not base_consumed:
                try:
                    current_val, _ = _parse_number_token(seg)
                    if current_val == base_val:
                        segment_layouts.append("base")
                        base_consumed = True
                        continue
                except Exception:
                    pass
            if "_" not in seg or "/" not in seg:
                segment_layouts.append("known")
                continue
            left, right = [part.strip(" ()") for part in seg.split("/", 1)]
            if "_" in left:
                blank_specs.append({"kind": "num", "den": int(right)})
                segment_layouts.append("blank")
            elif "_" in right:
                blank_specs.append({"kind": "den", "num": int(left)})
                segment_layouts.append("blank")
            else:
                segment_layouts.append("known")

        return {
            "family": "frac_equivalent_fill_blank",
            "source_text": src,
            "base_value": base_val,
            "blank_specs": blank_specs,
            "segment_layouts": segment_layouts,
        }

    def _build_preserve_value_config(self, src: str) -> dict[str, Any]:
        norm = _normalize_text(src)
        frac_match = re.search(r"([+-]?\d+/\d+)", norm)
        delta_match = re.search(r"分母加上\s*([+-]?\d+)", norm)
        if not frac_match or not delta_match:
            raise ValueError("invalid preserve-value question")
        value, _ = _parse_number_token(frac_match.group(1))
        return {
            "family": "frac_preserve_value",
            "source_text": src,
            "value": value,
            "delta": int(delta_match.group(1)),
        }

    def _build_compare_config(self, src: str) -> dict[str, Any]:
        math_parts = re.findall(r"\$([^$]+)\$", src)
        if math_parts:
            if len(math_parts) == 1 and "、" in math_parts[0]:
                parts = [part.strip() for part in math_parts[0].split("、") if part.strip()]
            else:
                parts = math_parts
        else:
            norm = _normalize_text(src)
            compare_tail = norm.split("比較", 1)[-1].split("的大小", 1)[0]
            parts = [part.strip() for part in re.split(r"[、,和]", compare_tail) if "/" in part or re.search(r"\d+\s+\d+/\d+", part)]
        if len(parts) < 2:
            raise ValueError("need at least two values to compare")

        numbers: list[dict[str, Any]] = []
        for token in parts:
            value, kind = _parse_number_token(token)
            numbers.append({"value": value, "label": _label_from_token(token, kind)})
        return {"family": "frac_compare_set", "source_text": src, "numbers": numbers}

    def _build_reciprocal_config(self, src: str) -> dict[str, Any]:
        expr = self._first_math_segment_or_src(src)
        value, kind = _parse_number_token(expr)
        return {
            "family": "frac_reciprocal",
            "source_text": src,
            "value": value,
            "kind": kind,
        }

    def _build_eval_config(self, src: str) -> dict[str, Any]:
        expr = self._first_math_segment_or_src(src)
        norm = _normalize_text(expr)
        common_factor = self._extract_common_factor_pattern(expr)
        if common_factor:
            return {
                "family": "frac_eval_common_factor",
                "source_text": src,
                "expr": norm,
                "common_factor_pattern": common_factor,
            }
        return {
            "family": "frac_eval_expression",
            "source_text": src,
            "expr": norm,
            "ellipsis": "..." in norm,
        }

    def _extract_common_factor_pattern(self, expr: str) -> dict[str, Any] | None:
        raw = str(expr or "").strip()
        if not raw:
            return None
        compact = re.sub(r"\s+", "", raw)
        m = re.fullmatch(
            r"(?P<left>.+?)(?:\\times|\*)(?P<factor>\([^()]+\)|-?\d+(?:\.\d+)?)"
            r"(?P<op>[+-])"
            r"(?P<right>.+?)(?:\\times|\*)(?P=factor)",
            compact,
        )
        if m:
            left = m.group("left")
            right = m.group("right")
            factor = m.group("factor")
            if "\\frac" not in left and "\\frac" not in right and "/" not in left and "/" not in right:
                return None
            return {
                "shared_side": "right",
                "left": left,
                "right": right,
                "factor": factor,
                "op": m.group("op"),
            }

        m = re.fullmatch(
            r"(?P<factor>.+?)(?:\\times|\*)(?P<left>\([^()]+\)|-?\d+(?:\.\d+)?)"
            r"(?P<op>[+-])"
            r"(?P=factor)(?:\\times|\*)(?P<right>\([^()]+\)|-?\d+(?:\.\d+)?)",
            compact,
        )
        if not m:
            return None
        factor = m.group("factor")
        left = m.group("left")
        right = m.group("right")
        if "\\frac" not in factor and "/" not in factor:
            return None
        return {
            "shared_side": "left",
            "left": left,
            "right": right,
            "factor": factor,
            "op": m.group("op"),
        }

    def _generate_frac_simplify(self, config: dict[str, Any]) -> dict[str, Any]:
        answer = _format_like_kind(Fraction(config["value"]), config.get("kind", "fraction"))
        return {
            "question_text": config["source_text"],
            "answer": "",
            "correct_answer": answer,
            "mode": 1,
        }

    def _generate_frac_equivalent_fill_blank(self, config: dict[str, Any]) -> dict[str, Any]:
        base = Fraction(config["base_value"])
        answers: list[str] = []
        for blank in config["blank_specs"]:
            if blank["kind"] == "num":
                answers.append(_scalar_text(base * blank["den"]))
            else:
                answers.append(_scalar_text(Fraction(blank["num"], 1) / base))
        return {
            "question_text": config["source_text"],
            "answer": "",
            "correct_answer": ",".join(answers),
            "mode": 1,
        }

    def _generate_frac_preserve_value(self, config: dict[str, Any]) -> dict[str, Any]:
        value = Fraction(config["value"])
        delta = int(config["delta"])
        new_den = value.denominator + delta
        if new_den == 0 or new_den % value.denominator != 0:
            raise ValueError("new denominator is not a valid equivalent-fraction multiple")
        scale = Fraction(new_den, value.denominator)
        new_num = value.numerator * scale
        add_num = Fraction(new_num, 1) - value.numerator
        return {
            "question_text": config["source_text"],
            "answer": "",
            "correct_answer": _scalar_text(add_num),
            "mode": 1,
        }

    def _generate_frac_compare_set(self, config: dict[str, Any]) -> dict[str, Any]:
        ordered = [(Fraction(item["value"]), item["label"]) for item in config["numbers"]]
        answer = _sorted_compare_chain(ordered)
        return {
            "question_text": config["source_text"],
            "answer": "",
            "correct_answer": answer,
            "mode": 1,
        }

    def _generate_frac_reciprocal(self, config: dict[str, Any]) -> dict[str, Any]:
        value = Fraction(config["value"])
        if value == 0:
            raise ValueError("zero has no reciprocal")
        answer = _fraction_text(1 / value)
        return {
            "question_text": config["source_text"],
            "answer": "",
            "correct_answer": answer,
            "mode": 1,
        }

    def _eval_ellipsis_expression(self, expr: str) -> Fraction:
        compact = _normalize_text(expr).replace(" ", "")
        if compact.startswith("(1-2/3)(1-2/4)(1-2/5)"):
            result = Fraction(1, 1)
            for n in range(3, 17):
                result *= Fraction(n - 2, n)
            return result
        if compact.startswith("(-2/3)*(-3/4)*(-4/5)") or compact.startswith("(-2/3)(-3/4)(-4/5)"):
            result = Fraction(1, 1)
            for n in range(2, 100):
                result *= Fraction(-n, n + 1)
            return result
        if compact.startswith("(-3/2)*(-4/3)*(-5/4)") or compact.startswith("(-3/2)(-4/3)(-5/4)"):
            result = Fraction(1, 1)
            for n in range(2, 101):
                result *= Fraction(-(n + 1), n)
            return result
        raise ValueError(f"unsupported ellipsis expression: {expr}")

    def _eval_ellipsis_meta(self, meta: dict[str, Any]) -> Fraction:
        kind = str(meta.get("kind") or "")
        if kind == "one_minus_fraction":
            whole = int(meta.get("whole", 1))
            numer = int(meta["numer"])
            start = int(meta["start"])
            end = int(meta["end"])
            result = Fraction(1, 1)
            for n in range(start, end + 1):
                result *= Fraction(whole, 1) - Fraction(numer, n)
            return result
        if kind == "neg_n_over_n_plus_1":
            start = int(meta["start"])
            end = int(meta["end"])
            result = Fraction(1, 1)
            for n in range(start, end + 1):
                result *= Fraction(-n, n + 1)
            return result
        if kind == "neg_n_plus_1_over_n":
            start = int(meta["start"])
            end = int(meta["end"])
            result = Fraction(1, 1)
            for n in range(start, end + 1):
                result *= Fraction(-(n + 1), n)
            return result
        raise ValueError(f"unsupported ellipsis meta: {meta}")

    def _generate_frac_eval_expression(self, config: dict[str, Any]) -> dict[str, Any]:
        if config.get("ellipsis_meta"):
            answer_value = self._eval_ellipsis_meta(config["ellipsis_meta"])
        elif config.get("ellipsis"):
            answer_value = self._eval_ellipsis_expression(config["expr"])
        else:
            answer_value = _expression_to_fraction(config["expr"])
        return {
            "question_text": self._wrap_eval_question_text(config["source_text"]),
            "answer": "",
            "correct_answer": _fraction_text(answer_value),
            "mode": 1,
        }

    def _generate_frac_eval_common_factor(self, config: dict[str, Any]) -> dict[str, Any]:
        answer_value = _expression_to_fraction(config["expr"])
        return {
            "question_text": self._wrap_eval_question_text(config["source_text"]),
            "answer": "",
            "correct_answer": _fraction_text(answer_value),
            "mode": 1,
        }

    def _wrap_eval_question_text(self, source_text: Any) -> str:
        raw = str(source_text or "").strip()
        if not raw:
            return raw
        if re.search(r"計算|求|值。", raw):
            return raw
        return f"計算 ${self._first_math_segment_or_src(raw)}$ 的值。"

    def _generate_frac_word_drone_weight(self, config: dict[str, Any]) -> dict[str, Any]:
        full_weight = Fraction(config.get("full_weight", 45))
        total_minutes = Fraction(config.get("total_minutes", 50))
        elapsed = Fraction(config.get("elapsed_minutes", 20))
        after_20 = Fraction(config.get("after_weight", 37))
        full_pesticide = (full_weight - after_20) / (elapsed / total_minutes)
        empty_drone = full_weight - full_pesticide
        return {
            "question_text": config["source_text"],
            "answer": "",
            "correct_answer": _fraction_text(empty_drone),
            "mode": 1,
        }

    def _generate_frac_word_bottle_weight(self, config: dict[str, Any]) -> dict[str, Any]:
        full = Fraction(config.get("full_total", 930))
        after = Fraction(config.get("after_total", 430))
        drank = Fraction(config.get("drank_fraction", Fraction(2, 3)))
        juice = (full - after) / drank
        bottle = full - juice
        return {
            "question_text": config["source_text"],
            "answer": "",
            "correct_answer": _fraction_text(bottle),
            "mode": 1,
        }

    def _generate_frac_word_remaining_milk(self, config: dict[str, Any]) -> dict[str, Any]:
        total = Fraction(config.get("total_ml", 480))
        first = Fraction(config.get("first_fraction", Fraction(7, 12)))
        second = Fraction(config.get("second_fraction", Fraction(3, 5)))
        remaining_after_first = total * (1 - first)
        remaining_final = remaining_after_first * (1 - second)
        return {
            "question_text": config["source_text"],
            "answer": "",
            "correct_answer": _fraction_text(remaining_final),
            "mode": 1,
        }

    def _generate_frac_word_inheritance_compare(self, config: dict[str, Any]) -> dict[str, Any]:
        total = Fraction(1, 1)
        first = total * Fraction(config.get("first_share_fraction", Fraction(1, 4)))
        remain = total - first
        second = remain * Fraction(config.get("second_share_fraction", Fraction(1, 3)))
        remain -= second
        third = remain * Fraction(config.get("third_share_fraction", Fraction(1, 2)))
        fourth = total - first - second - third
        shares = {
            "大兒子": first,
            "二兒子": second,
            "三兒子": third,
            "四兒子": fourth,
        }
        values = set(shares.values())
        if len(values) == 1:
            answer = "四人分得相同"
        else:
            max_share = max(shares.values())
            min_share = min(shares.values())
            most = "、".join(name for name, value in shares.items() if value == max_share)
            least = "、".join(name for name, value in shares.items() if value == min_share)
            answer = f"最多:{most};最少:{least}"
        return {
            "question_text": config["source_text"],
            "answer": "",
            "correct_answer": answer,
            "mode": 1,
        }

    def _generate_frac_word_library_total(self, config: dict[str, Any]) -> dict[str, Any]:
        added = Fraction(config.get("added_books", 450))
        ratio = Fraction(config.get("before_after_ratio", Fraction(7, 10)))
        before = added * ratio / (1 - ratio)
        return {
            "question_text": config["source_text"],
            "answer": "",
            "correct_answer": _fraction_text(before),
            "mode": 1,
        }
