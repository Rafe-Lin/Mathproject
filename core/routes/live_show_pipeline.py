# -*- coding: utf-8 -*-
"""Live Show pipeline helpers.

先以低風險方式抽出 Ab2 協調流程，讓 route 專注編排。
"""

import os
import re
import time
import uuid
import json
from difflib import SequenceMatcher
from typing import Any


def recompute_radical_style_fields_for_api(
    ocr_text: str,
    *,
    input_radical_style: str | None = None,
    ab3_question_text: str | None = None,
    ab2_question_text: str | None = None,
    style_mismatch_after_retry_ab3: bool = False,
) -> dict[str, Any]:
    """
    以「最終題幹字串」重新計算根式 style 欄位（與壓測相同：
    classify_radical_style + radical_hard_style_preserved）。

    input_radical_style：若提供（例如 pipeline 已對 OCR 分類），優先使用，避免與
    classify(canonical_ocr) 因字串正規化差異而與 gate 不一致。
    """
    from core.code_utils.live_show_math_utils import (
        classify_radical_style,
        radical_hard_style_preserved,
    )

    if input_radical_style is not None:
        inp = input_radical_style
    else:
        inp = classify_radical_style(ocr_text or "")
    out: dict[str, Any] = {"input_radical_style": inp}
    if ab3_question_text is not None:
        o3 = classify_radical_style(ab3_question_text or "")
        p3, r3 = radical_hard_style_preserved(inp, o3 or "mixed")
        if style_mismatch_after_retry_ab3 and not p3:
            r3 = f"{r3} [after_style_retry]".strip()
        out["output_radical_style"] = o3
        out["style_preserved"] = p3
        out["style_mismatch_reason"] = r3 if not p3 else ""
    if ab2_question_text is not None:
        o2 = classify_radical_style(ab2_question_text or "")
        p2, r2 = radical_hard_style_preserved(inp, o2 or "mixed")
        out["ab2_output_radical_style"] = o2
        out["ab2_style_preserved"] = p2
        out["ab2_style_mismatch_reason"] = r2 if not p2 else ""
    return out


# 根式新版本對照表：input_style -> allowed_patterns（8年級弱基礎）
RADICAL_STYLE_PATTERN_MAP = {
    "simple_radical": {
        "allowed_patterns": ["p0_simplify"],
        "default_pattern": "p0_simplify",
    },
    "simplifiable_radical": {
        "allowed_patterns": ["p0_simplify"],
        "default_pattern": "p0_simplify",
    },
    "fraction_radical": {
        "allowed_patterns": [
            "p2h_frac_mult_rad",
            "p2g_rad_mult_frac",
            "p3a_div_expr",
            "p3b_div_simple",
            "p5a_conjugate_int",
            "p5b_conjugate_rad",
            "p4_frac_mult",
        ],
        "default_pattern": "p2h_frac_mult_rad",
    },
    "mixed": {
        "allowed_patterns": [
            "p1_add_sub",
            "p2b_mult_distrib",
            "p2c_mult_binomial",
            "p2d_perfect_square",
            "p2e_diff_of_squares",
            "p3a_div_expr",
            "p3b_div_simple",
            "p4c_nested_frac_chain",
            "p4d_frac_rad_div_mixed",
            "p5a_conjugate_int",
            "p5b_conjugate_rad",
            "p6_combo",
            "p7_mixed_rad_add",
            "p4_frac_mult",
        ],
        "default_pattern": "p6_combo",
    },
}


def _allowed_patterns_for_radical_style(style: str | None) -> frozenset | None:
    entry = RADICAL_STYLE_PATTERN_MAP.get(style) if style else None
    if not entry:
        return None
    return frozenset(entry["allowed_patterns"])


def _style_gate_default_pid(input_style: str, ocr_text: str) -> str:
    entry = RADICAL_STYLE_PATTERN_MAP.get(input_style)
    if entry:
        default = entry.get("default_pattern")
        if default:
            return default
    ocr = ocr_text or ""
    if input_style == "fraction_radical":
        o = ocr.replace(" ", "")
        if re.fullmatch(r"\\sqrt\{\\frac\{[^{}]+\}\{[^{}]+\}\}", o):
            return "p0_simplify"
        if r"\div" in ocr:
            return "p3a_div_expr"
        if r"\frac" in ocr:
            return "p2h_frac_mult_rad"
        return "p3b_div_simple"
    return "p2a_mult_direct"


def apply_radical_style_pattern_gate(
    skill_id: str,
    input_radical_style: str | None,
    raw_pattern_id: str | None,
    ocr_text: str,
    healed_code: str,
    healed_exec_code: str,
    p1_guard_candidates: list[str] | None,
) -> tuple[str | None, str, str, dict]:
    """
    Restrict pattern_id to RADICAL_STYLE_PATTERN_MAP[input_style].allowed_patterns.
    Runs after apply_radical_pattern_p1_guard. Returns (effective_pid, hc, hx, trace).
    """
    pid_before = (raw_pattern_id or "").strip()
    trace: dict = {
        "input_radical_style": input_radical_style,
        "rejected_pattern_id": None,
        "selected_pattern_id": pid_before,
        "style_gate_reason": None,
        "style_gate_applied": False,
        "selected_pattern_before_style_gate": pid_before,
        "selected_pattern_after_style_gate": pid_before,
    }
    if "FourOperationsOfRadicals" not in (skill_id or ""):
        return raw_pattern_id, healed_code, healed_exec_code, trace

    allowed = _allowed_patterns_for_radical_style(input_radical_style)
    if allowed is None:
        trace["style_gate_reason"] = "skipped_unknown_style"
        return raw_pattern_id, healed_code, healed_exec_code, trace

    pid = pid_before
    if pid in allowed:
        trace["style_gate_reason"] = "pattern_ok"
        return raw_pattern_id, healed_code, healed_exec_code, trace

    trace["rejected_pattern_id"] = pid
    trace["style_gate_applied"] = True
    pool = [p for p in (p1_guard_candidates or []) if p in allowed]
    new_pid = pool[0] if pool else _style_gate_default_pid(input_radical_style or "", ocr_text)
    trace["style_gate_reason"] = f"remap_for_style:{input_radical_style}:{pid}->{new_pid}"
    trace["selected_pattern_id"] = new_pid
    trace["selected_pattern_after_style_gate"] = new_pid

    _pat = re.compile(
        r"^(\s*)pattern_id\s*=\s*[\"']([^\"']+)[\"']",
        re.MULTILINE,
    )

    def _patch(code: str) -> str:
        if not _pat.search(code):
            return code
        return _pat.sub(lambda m: f'{m.group(1)}pattern_id = "{new_pid}"', code, count=1)

    hc = _patch(healed_code)
    hx = _patch(healed_exec_code)
    print(
        f"[INFO] [PIPE] [STYLE_GATE] input_style={input_radical_style!r} "
        f"rejected={pid!r} -> {new_pid!r} reason={trace['style_gate_reason']!r}"
    )
    return new_pid, hc, hx, trace


def inject_required_radical_style_into_exec_code(
    code: str | None, required_style: str | None
) -> str:
    """Inject required_radical_style for RADICAL_V4 scaffold (after model decision lines)."""
    if not code or not required_style:
        return code or ""
    code = code.replace("\r\n", "\n").replace("\r", "\n")
    if "required_radical_style" in code:
        return code
    insert = f'\n    required_radical_style = "{required_style}"'
    m = re.search(r"^(\s*term_count\s*=.*)$", code, re.MULTILINE)
    if m:
        return code[: m.end()] + insert + code[m.end() :]
    m2 = re.search(r"^(\s*difficulty\s*=.*)$", code, re.MULTILINE)
    if m2:
        return code[: m2.end()] + insert + code[m2.end() :]
    return code


def inject_radical_style_retry_hint(code: str | None) -> str:
    if not code or "_radical_style_retry" in code:
        return code or ""
    code = code.replace("\r\n", "\n").replace("\r", "\n")
    insert = "\n    _radical_style_retry = True"
    m = re.search(r"^(\s*required_radical_style\s*=.*)$", code, re.MULTILINE)
    if m:
        return code[: m.end()] + insert + code[m.end() :]
    m2 = re.search(r"^(\s*term_count\s*=.*)$", code, re.MULTILINE)
    if m2:
        return code[: m2.end()] + insert + code[m2.end() :]
    m3 = re.search(r"^(\s*difficulty\s*=.*)$", code, re.MULTILINE)
    if m3:
        return code[: m3.end()] + insert + code[m3.end() :]
    return code


def inject_radical_anti_echo_retry_hint(code: str | None) -> str:
    if not code or "_anti_echo_retry" in code:
        return code or ""
    code = code.replace("\r\n", "\n").replace("\r", "\n")
    insert = "\n    _anti_echo_retry = True"
    m = re.search(r"^(\s*_radical_style_retry\s*=.*)$", code, re.MULTILINE)
    if m:
        return code[: m.end()] + insert + code[m.end() :]
    m2 = re.search(r"^(\s*required_radical_style\s*=.*)$", code, re.MULTILINE)
    if m2:
        return code[: m2.end()] + insert + code[m2.end() :]
    m3 = re.search(r"^(\s*term_count\s*=.*)$", code, re.MULTILINE)
    if m3:
        return code[: m3.end()] + insert + code[m3.end() :]
    return code


def _prepend_missing_runtime_stubs(code: str | None, skill_id: str | None, api_stubs: str | None) -> str:
    payload = code or ""
    stubs = api_stubs or ""
    try:
        from core.prompts.domain_function_library import get_domain_helpers_code, get_required_domains

        needed_domains = list(get_required_domains(skill_id) or []) if skill_id else []
        code_lower = payload.lower()
        if ("integerops." in code_lower) and ("integerops" not in needed_domains):
            needed_domains.append("integerops")
        if ("fractionops." in code_lower) and ("fractionops" not in needed_domains):
            needed_domains.append("fractionops")
        if ("radicalops." in code_lower) and ("radicalops" not in needed_domains):
            needed_domains.append("radicalops")

        missing_domains = []
        for domain, cls_name in (
            ("integerops", "class IntegerOps"),
            ("fractionops", "class FractionOps"),
            ("radicalops", "class RadicalOps"),
        ):
            if (domain in needed_domains) and (cls_name not in payload) and (cls_name not in stubs):
                missing_domains.append(domain)

        if missing_domains:
            extra = get_domain_helpers_code(missing_domains, stub_mode=True) or ""
            if extra:
                stubs = (stubs + "\n\n" + extra).strip() if stubs else extra
    except Exception:
        pass

    return (stubs + "\n\n" + payload).strip() if stubs else payload


def _build_fixed_question_script(question_text: str, correct_answer: str) -> str:
    qt = repr(str(question_text or ""))
    ans = repr(str(correct_answer or ""))
    return (
        "def generate(level=1, **kwargs):\n"
        f"    return {{'question_text': {qt}, 'correct_answer': {ans}, 'mode': 1}}\n\n"
        "def check(user_answer, correct_answer):\n"
        "    try:\n"
        "        if str(user_answer).strip() == str(correct_answer).strip():\n"
        "            return {'correct': True, 'result': '正確'}\n"
        "        if abs(float(user_answer) - float(correct_answer)) < 1e-6:\n"
        "            return {'correct': True, 'result': '正確'}\n"
        "    except Exception:\n"
        "        pass\n"
        "    return {'correct': False, 'result': '錯誤'}\n"
    )


def _build_randomized_radical_question_script(source_expr: str, prompt_word: str = "化簡") -> str:
    """Build a deterministic-safe generator script that preserves expression structure
    while randomizing numeric tokens each call to generate().
    """
    expr = str(source_expr or "").strip()
    expr = re.sub(r"\s+", "", expr)
    if not expr:
        expr = r"\sqrt{2}+\sqrt{3}"

    numbers: list[int] = []

    def _num_repl(m):
        numbers.append(int(m.group(0)))
        return f"__N{len(numbers)-1}__"

    expr_tpl = re.sub(r"\d+", _num_repl, expr)
    if not numbers:
        numbers = [2, 3]
        expr_tpl = expr_tpl + "__N0__+__N1__"

    ranges: list[tuple[int, int]] = []
    for n in numbers:
        delta_lo = max(1, n // 3)
        delta_hi = max(2, n // 2)
        lo = max(1, n - delta_lo)
        hi = max(lo + 1, min(500, n + delta_hi))
        ranges.append((lo, hi))

    pw = prompt_word if prompt_word in {"化簡", "計算"} else "化簡"
    tpl = repr(expr_tpl)
    rg = repr(ranges)
    return (
        "import random\n\n"
        f"_EXPR_TEMPLATE = {tpl}\n"
        f"_RANGES = {rg}\n"
        f"_PROMPT_WORD = {pw!r}\n\n"
        "def _render_expr():\n"
        "    expr = _EXPR_TEMPLATE\n"
        "    for i, (lo, hi) in enumerate(_RANGES):\n"
        "        val = random.randint(lo, hi)\n"
        "        expr = expr.replace(f'__N{i}__', str(val))\n"
        "    return expr\n\n"
        "def generate(level=1, **kwargs):\n"
        "    expr = _render_expr()\n"
        "    return {'question_text': _PROMPT_WORD + ' $' + expr + '$。', 'correct_answer': '', 'mode': 1}\n\n"
        "def check(user_answer, correct_answer):\n"
        "    try:\n"
        "        if str(user_answer).strip() == str(correct_answer).strip():\n"
        "            return {'correct': True, 'result': '正確'}\n"
        "        if abs(float(user_answer) - float(correct_answer)) < 1e-6:\n"
        "            return {'correct': True, 'result': '正確'}\n"
        "    except Exception:\n"
        "        pass\n"
        "    return {'correct': False, 'result': '錯誤'}\n"
    )


def _normalize_expr_for_echo(text: str) -> str:
    t = str(text or "")
    t = t.replace("$", "").replace("。", "").replace("．", "").replace(".", "")
    t = t.replace("（", "(").replace("）", ")").replace("＋", "+").replace("－", "-")
    t = t.replace(" ", "")
    return t.strip().lower()


def _input_operator_lock_type(ocr_expr: str) -> str:
    o = str(ocr_expr or "")
    if not o.strip():
        return "unknown"
    if r"\div" in o:
        return "divide"
    if r"\times" in o:
        return "multiply"
    return "unknown"


def _execute_with_stubs_if_needed(scaler, code: str, api_stubs: str):
    payload = code or ""
    stubs = api_stubs or ""
    if (
        "IntegerOps." in payload
        and "class IntegerOps" not in payload
        and "class IntegerOps" not in stubs
    ):
        # Fallback code (especially radical iso-fallback) may reference IntegerOps
        # even when skill-level stubs did not include integerops.
        try:
            from core.prompts.domain_function_library import get_domain_helpers_code

            integer_stub = get_domain_helpers_code(["integerops"], stub_mode=True) or ""
            if integer_stub and "class IntegerOps" in integer_stub:
                stubs = (stubs + "\n\n" + integer_stub).strip() if stubs else integer_stub
                print("[INFO] [PIPE] runtime_stub_injected=IntegerOps")
        except Exception as e:
            # Last-resort runtime shim to prevent NameError in fallback execution.
            integer_stub = (
                "class IntegerOps:\n"
                "    @staticmethod\n"
                "    def fmt_num(n):\n"
                "        return f\"({n})\" if n < 0 else str(n)\n"
                "\n"
                "    @staticmethod\n"
                "    def random_nonzero(min_val, max_val):\n"
                "        import random\n"
                "        pool = [x for x in range(min_val, max_val + 1) if x != 0]\n"
                "        if not pool:\n"
                "            raise ValueError(\"No non-zero integers in range\")\n"
                "        return random.choice(pool)\n"
            )
            stubs = (stubs + "\n\n" + integer_stub).strip() if stubs else integer_stub
            print(f"[WARN] [PIPE] runtime_stub_fallback=IntegerOps ({type(e).__name__})")
    if stubs:
        payload = stubs + "\n\n" + payload
    return scaler._execute_code(payload, level=1)


def _is_add_sub_only_expr(expr: str) -> bool:
    e = str(expr or "")
    if not e.strip():
        return False
    has_add_sub = bool(re.search(r"[+\-]", e))
    has_mul_div = (r"\times" in e) or (r"\div" in e)
    return has_add_sub and not has_mul_div


def _has_square_factor_local(n: int) -> bool:
    if not isinstance(n, int) or n < 4:
        return False
    i = 2
    while i * i <= n:
        if n % (i * i) == 0:
            return True
        i += 1
    return False


def _build_non_echo_radical_expr(source_ocr_expr: str) -> str:
    expr = str(source_ocr_expr or "").strip()
    if expr.startswith("$") and expr.endswith("$"):
        expr = expr[1:-1].strip()
    if not expr:
        return r"\sqrt{2}"

    exact_map = {
        r"(-2)\times3\sqrt{5}": r"(-3)\times4\sqrt{2}",
        r"\frac{1}{\sqrt{3}-\sqrt{2}}": r"\frac{1}{\sqrt{7}-\sqrt{5}}",
        r"\frac{\sqrt{2}}{3\sqrt{2}+4}": r"\frac{\sqrt{3}}{2\sqrt{3}+5}",
        r"\frac{1}{\sqrt{3}}\div\frac{\sqrt{6}}{\sqrt{2}}": r"\frac{1}{\sqrt{5}}\div\frac{\sqrt{10}}{\sqrt{2}}",
        r"\frac{1}{\sqrt{3}}-\frac{2}{3}\sqrt{3}": r"\frac{1}{\sqrt{5}}-\frac{2}{3}\sqrt{5}",
        r"\sqrt{\frac{1}{2}}\times\sqrt{\frac{1}{5}}\div\sqrt{\frac{1}{6}}": r"\sqrt{\frac{1}{3}}\times\sqrt{\frac{1}{7}}\div\sqrt{\frac{1}{21}}",
        r"2\sqrt{3}\times(\sqrt{12}-\sqrt{2})": r"3\sqrt{2}\times(\sqrt{18}-\sqrt{5})",
        r"(\sqrt{3}+2\sqrt{2})^2": r"(\sqrt{2}+3\sqrt{3})^2",
        r"\sqrt{1\frac{9}{16}}+\sqrt{4\frac{25}{36}}": r"\sqrt{2\frac{1}{4}}+\sqrt{5\frac{4}{9}}",
    }
    _expr_key = _normalize_expr_for_echo(expr)
    for _src, _dst in exact_map.items():
        if _expr_key == _normalize_expr_for_echo(_src):
            return _dst

    simplifiable_pool = [8, 12, 18, 20, 24, 27, 32, 45, 48, 50, 72, 75]
    simple_pool = [2, 3, 5, 6, 7, 10, 11, 13, 14, 15]

    out: list[str] = []
    i = 0
    sqrt_counter = 0
    while i < len(expr):
        m = re.match(r"-?\d+(?:\.\d+)?", expr[i:])
        if not m:
            out.append(expr[i])
            i += 1
            continue
        token = m.group(0)
        start = i
        end = i + len(token)
        prev = expr[:start].rstrip()
        is_decimal = "." in token
        in_sqrt = prev.endswith(r"\sqrt{") or prev.endswith(r"\sqrt")
        in_power = prev.endswith("^")

        if is_decimal:
            new_token = "1.2" if token != "1.2" else "0.6"
        elif in_power:
            new_token = token
        elif in_sqrt:
            sqrt_counter += 1
            n = abs(int(token))
            pool = simplifiable_pool if _has_square_factor_local(n) else simple_pool
            pick = pool[(sqrt_counter - 1) % len(pool)]
            if pick == n:
                pick = pool[sqrt_counter % len(pool)]
            new_token = str(pick)
        else:
            n = int(token)
            candidate = n + 1 if n >= 0 else n - 1
            if candidate == 0:
                candidate = 2
            if abs(candidate) == 1 and (r"\frac{" in expr or r"\div" in expr):
                candidate = 2 if candidate > 0 else -2
            new_token = str(candidate)

        out.append(new_token)
        i = end

    candidate_expr = "".join(out)
    if _normalize_expr_for_echo(candidate_expr) == _normalize_expr_for_echo(expr):
        candidate_expr = re.sub(r"\\sqrt\{(\d+)\}", r"\\sqrt{11}", candidate_expr, count=1)
    return candidate_expr


def _build_radical_fallback_question_text(source_ocr_expr: str) -> str:
    expr = _build_non_echo_radical_expr(source_ocr_expr)
    src = str(source_ocr_expr or "")
    if re.search(r"\\sqrt\{\d+\\frac\{[^{}]+\}\{[^{}]+\}\}\s*[+\-]\s*\\sqrt\{\d+\\frac\{[^{}]+\}\{[^{}]+\}\}", src):
        return f"計算 ${expr}$ 的值。"
    return f"化簡 ${expr}$。"


def evaluate_radical_quality_gate(
    *,
    source_ocr_expr: str,
    question_text: str,
    generated_expr: str,
) -> dict[str, Any]:
    from core.code_utils.live_show_math_utils import build_radical_complexity_mirror_profile

    reasons: list[str] = []
    qt = str(question_text or "")
    ge = str(generated_expr or "")
    src_norm = _normalize_expr_for_echo(source_ocr_expr)
    gen_norm = _normalize_expr_for_echo(ge)
    similarity = SequenceMatcher(None, src_norm, gen_norm).ratio() if src_norm and gen_norm else 0.0

    cmd_cnt = qt.count("化簡") + qt.count("計算")
    if ("；" in qt) or cmd_cnt > 1:
        reasons.append("single_problem_violation")
    if not ge.strip():
        reasons.append("empty_expr_violation")
    if src_norm and gen_norm and (src_norm == gen_norm):
        reasons.append("echo_violation")

    lock_type = _input_operator_lock_type(source_ocr_expr)
    if lock_type in {"multiply", "divide", "rationalize_den_sqrt"} and _is_add_sub_only_expr(ge):
        reasons.append("operator_lock_violation")

    if src_norm and gen_norm:
        src_profile = build_radical_complexity_mirror_profile(source_ocr_expr)
        gen_profile = build_radical_complexity_mirror_profile(ge)
        if src_profile.get("number_count") != gen_profile.get("number_count"):
            reasons.append("number_count_violation")
        if src_profile.get("operator_sequence") != gen_profile.get("operator_sequence"):
            reasons.append("operator_sequence_violation")
        if src_profile.get("rad_count") != gen_profile.get("rad_count"):
            reasons.append("rad_count_violation")
        if src_profile.get("simplifiable_count") != gen_profile.get("simplifiable_count"):
            reasons.append("simplifiable_count_violation")

    reasons = list(dict.fromkeys(reasons))

    return {
        "passed": len(reasons) == 0,
        "reasons": reasons,
        "anti_echo_similarity": similarity,
        "echo_rule_mode": "strict_equal",
        "operator_lock_type": lock_type,
    }


RADICAL_EXEMPLAR_POOL = frozenset(
    {
        r"(\sqrt{3}+2\sqrt{2})^2",
        r"(\sqrt{3}-2\sqrt{2})(\sqrt{3}+2\sqrt{2})",
        r"\frac{1}{\sqrt{3}-\sqrt{2}}",
        r"\frac{\sqrt{2}}{3\sqrt{2}+4}",
        r"\sqrt{\frac{1}{2}}\times\sqrt{\frac{1}{5}}\div\sqrt{\frac{1}{6}}",
        r"\frac{1}{\sqrt{3}}\div\frac{\sqrt{6}}{\sqrt{2}}",
    }
)


def extract_selected_pattern_id_from_code(code: str):
    """從執行用程式碼取出第一個非註解行的 pattern_id 賦值（略過 # 註解行，降低誤匹配）。"""
    if not code or not isinstance(code, str):
        return None
    for line in code.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        m = re.match(r'pattern_id\s*=\s*["\']([^"\']+)["\']', s)
        if m:
            return m.group(1).strip()
    return None


def apply_radical_pattern_p1_guard(
    skill_id: str,
    ocr_text: str,
    raw_pattern_id: str | None,
    healed_code: str,
    healed_exec_code: str,
) -> tuple[str | None, str, str, dict]:
    """
    Radicals：OCR 含 \\times / \\div 時禁止沿用 p1_add_sub，改選乘法/除法 pattern 並改寫程式碼中的 pattern_id 行。
    回傳 (effective_pattern_id, healed_code, healed_exec_code, trace)。
    """
    trace: dict = {
        "detected_signals": [],
        "candidate_patterns": [],
        "selected_pattern_id": raw_pattern_id,
        "reject_reason": None,
    }
    ocr = ocr_text or ""
    if r"\times" in ocr:
        trace["detected_signals"].append(r"\times")
    if r"\div" in ocr:
        trace["detected_signals"].append(r"\div")
    if re.search(r"\\sqrt\{\s*\d+\.\d+", ocr) or re.search(r"\\sqrt\{\s*\\frac", ocr):
        trace["detected_signals"].append("decimal_root")
    if re.search(r"\)\s*\^\s*\d+", ocr) or re.search(r"\\sqrt\{[^{}]*\}\s*\^\s*\d+", ocr):
        trace["detected_signals"].append("power_root")

    if "FourOperationsOfRadicals" not in (skill_id or ""):
        return raw_pattern_id, healed_code, healed_exec_code, trace

    pid = (raw_pattern_id or "").strip()
    o = ocr.replace(" ", "")

    _pat_any = re.compile(
        r"^(\s*)pattern_id\s*=\s*[\"']([^\"']+)[\"']",
        re.MULTILINE,
    )

    def _patch_or_inject_pid(code: str, new_pid: str) -> str:
        if _pat_any.search(code):
            return _pat_any.sub(
                lambda m: f'{m.group(1)}pattern_id = "{new_pid}"',
                code,
                count=1,
            )
        insert = f'\n    pattern_id = "{new_pid}"'
        for anchor in (
            r"^(\s*required_radical_style\s*=.*)$",
            r"^(\s*term_count\s*=.*)$",
            r"^(\s*difficulty\s*=.*)$",
        ):
            m = re.search(anchor, code, re.MULTILINE)
            if m:
                return code[: m.end()] + insert + code[m.end() :]
        mdef = re.search(r"^(\s*def\s+generate\s*\([^\)]*\):\s*)$", code, re.MULTILINE)
        if mdef:
            return code[: mdef.end()] + insert + code[mdef.end() :]
        return code

    # Strong OCR-to-pattern forcing for critical exemplar families and single-radical simplify.
    _forced_rules = [
        (r"(\sqrt{3}+2\sqrt{2})^2", "p2d_perfect_square", "ocr_exemplar:p2d"),
        (r"(\sqrt{3}-2\sqrt{2})(\sqrt{3}+2\sqrt{2})", "p2e_diff_of_squares", "ocr_exemplar:p2e"),
        (r"\frac{1}{\sqrt{3}-\sqrt{2}}", "p5a_conjugate_int", "ocr_exemplar:p5a"),
        (r"\frac{\sqrt{2}}{3\sqrt{2}+4}", "p5b_conjugate_rad", "ocr_exemplar:p5b"),
        (r"\sqrt{\frac{1}{2}}\times\sqrt{\frac{1}{5}}\div\sqrt{\frac{1}{6}}", "p4c_nested_frac_chain", "ocr_exemplar:p4c"),
        (r"\frac{1}{\sqrt{3}}\div\frac{\sqrt{6}}{\sqrt{2}}", "p4d_frac_rad_div_mixed", "ocr_exemplar:p4d"),
        (r"\sqrt{1\frac{9}{16}}+\sqrt{4\frac{25}{36}}", "p7_mixed_rad_add", "ocr_exemplar:p7"),
    ]
    _ocr_key = _normalize_expr_for_echo(ocr)
    for _expr, _forced_pid, _reason in _forced_rules:
        if _ocr_key == _normalize_expr_for_echo(_expr):
            if pid != _forced_pid:
                trace["reject_reason"] = _reason
                trace["candidate_patterns"] = [_forced_pid]
                trace["selected_pattern_id"] = _forced_pid
                hc = _patch_or_inject_pid(healed_code, _forced_pid)
                hx = _patch_or_inject_pid(healed_exec_code, _forced_pid)
                print(
                    f"[INFO] [PIPE] [PATTERN_FORCE] {_reason} "
                    f"{pid!r}->{_forced_pid!r}"
                )
                return _forced_pid, hc, hx, trace
            trace["selected_pattern_id"] = _forced_pid
            return _forced_pid, healed_code, healed_exec_code, trace

    # Single-radical OCR should be simplify family.
    _sqrt_n = len(re.findall(r"\\sqrt", o))
    _has_times_div = (r"\times" in ocr) or (r"\div" in ocr)
    _has_add_sub = bool(re.search(r"(?<!^)[+\-]", o))
    if (_sqrt_n == 1) and (not _has_times_div) and (not _has_add_sub):
        _forced_pid = "p0_simplify"
        if pid != _forced_pid:
            trace["reject_reason"] = "single_radical_requires_p0"
            trace["candidate_patterns"] = [_forced_pid]
            trace["selected_pattern_id"] = _forced_pid
            hc = _patch_or_inject_pid(healed_code, _forced_pid)
            hx = _patch_or_inject_pid(healed_exec_code, _forced_pid)
            print(
                f"[INFO] [PIPE] [PATTERN_FORCE] single_radical "
                f"{pid!r}->{_forced_pid!r}"
            )
            return _forced_pid, hc, hx, trace
        trace["selected_pattern_id"] = _forced_pid
        return _forced_pid, healed_code, healed_exec_code, trace

    if pid != "p1_add_sub":
        trace["selected_pattern_id"] = pid or None
        return raw_pattern_id, healed_code, healed_exec_code, trace

    new_pid: str | None = None
    candidates: list[str] = []

    # Formula-level detectors (highest priority)
    if re.search(r"\)\s*\^\s*2", o) and re.search(r"\\sqrt", o):
        trace["reject_reason"] = "p1_add_sub forbidden: perfect_square_formula"
        candidates = ["p2d_perfect_square", "p2c_mult_binomial", "p2b_mult_distrib"]
        new_pid = "p2d_perfect_square"
    elif re.search(r"\(.*-.*\)\(.*\+.*\)", o) and re.search(r"\\sqrt", o):
        trace["reject_reason"] = "p1_add_sub forbidden: diff_of_squares_formula"
        candidates = ["p2e_diff_of_squares", "p2c_mult_binomial", "p2b_mult_distrib"]
        new_pid = "p2e_diff_of_squares"
    elif re.search(r"\\frac\{1\}\{[^{}]*\\sqrt[^{}]*[+\-][^{}]*\}", o):
        trace["reject_reason"] = "p1_add_sub forbidden: conjugate_int_formula"
        candidates = ["p5a_conjugate_int", "p3b_div_simple", "p3a_div_expr"]
        new_pid = "p5a_conjugate_int"
    elif re.search(r"\\frac\{\\sqrt\{[^{}]+\}\}\{[^{}]*\\sqrt[^{}]*[+\-][^{}]*\}", o):
        trace["reject_reason"] = "p1_add_sub forbidden: conjugate_rad_formula"
        candidates = ["p5b_conjugate_rad", "p5a_conjugate_int", "p3a_div_expr"]
        new_pid = "p5b_conjugate_rad"
    elif re.search(r"\\sqrt\{\\frac\{[^{}]+\}\{[^{}]+\}\}.*\\times.*\\sqrt\{\\frac\{[^{}]+\}\{[^{}]+\}\}.*\\div.*\\sqrt\{\\frac\{[^{}]+\}\{[^{}]+\}\}", o):
        trace["reject_reason"] = "p1_add_sub forbidden: nested_frac_chain_formula"
        candidates = ["p4c_nested_frac_chain", "p4b_frac_rad_div", "p4d_frac_rad_div_mixed"]
        new_pid = "p4c_nested_frac_chain"
    elif re.search(r"\\frac\{[^{}]+\}\{\\sqrt\{[^{}]+\}\}.*\\div.*\\frac\{\\sqrt\{[^{}]+\}\}\{\\sqrt\{[^{}]+\}\}", o):
        trace["reject_reason"] = "p1_add_sub forbidden: frac_rad_div_mixed_formula"
        candidates = ["p4d_frac_rad_div_mixed", "p4b_frac_rad_div", "p3a_div_expr"]
        new_pid = "p4d_frac_rad_div_mixed"
    elif re.search(r"\\sqrt\{\d+\\frac\{[^{}]+\}\{[^{}]+\}\}\s*[+\-]\s*\\sqrt\{\d+\\frac\{[^{}]+\}\{[^{}]+\}\}", o):
        trace["reject_reason"] = "p1_add_sub forbidden: mixed_rad_add_formula"
        candidates = ["p7_mixed_rad_add", "p1_add_sub", "p6_combo"]
        new_pid = "p7_mixed_rad_add"

    if (not new_pid) and (("decimal_root" in trace["detected_signals"]) or ("power_root" in trace["detected_signals"])):
        trace["reject_reason"] = "p1_add_sub forbidden: OCR contains decimal_root/power_root"
        candidates = ["p0_simplify", "p2b_mult_distrib", "p2a_mult_direct", "p6_combo"]
        new_pid = "p0_simplify"
    elif (not new_pid) and r"\times" in ocr:
        trace["reject_reason"] = "p1_add_sub forbidden: OCR contains \\times"
        if re.search(r"\)\s*\\times", o) or re.search(r"\\times\s*\(", o):
            candidates = ["p2c_mult_binomial", "p2b_mult_distrib", "p2a_mult_direct"]
            new_pid = "p2c_mult_binomial"
        elif r"\frac" in o and r"\times" in ocr:
            candidates = ["p2b_mult_distrib", "p2a_mult_direct", "p2c_mult_binomial"]
            new_pid = "p2b_mult_distrib"
        else:
            candidates = ["p2a_mult_direct", "p2b_mult_distrib", "p2c_mult_binomial"]
            new_pid = "p2a_mult_direct"
    elif (not new_pid) and r"\div" in ocr:
        trace["reject_reason"] = "p1_add_sub forbidden: OCR contains \\div"
        if re.search(r"\\frac\{1\}", o) or re.search(r"1\\div\\sqrt", o):
            candidates = ["p5a_conjugate_int", "p3b_div_simple", "p3a_div_expr"]
            new_pid = "p5a_conjugate_int"
        elif re.search(r"\([^\)]*\\sqrt[^\)]*\)\\div", o) or ")\\div\\sqrt" in o:
            candidates = ["p3a_div_expr", "p3b_div_simple", "p5a_conjugate_int"]
            new_pid = "p3a_div_expr"
        else:
            candidates = ["p3b_div_simple", "p3a_div_expr", "p5a_conjugate_int"]
            new_pid = "p3b_div_simple"

    if not new_pid:
        trace["selected_pattern_id"] = pid
        return raw_pattern_id, healed_code, healed_exec_code, trace

    trace["candidate_patterns"] = candidates
    trace["selected_pattern_id"] = new_pid

    _pat = re.compile(
        r"^(\s*)pattern_id\s*=\s*[\"']p1_add_sub[\"']",
        re.MULTILINE,
    )

    def _patch(code: str) -> str:
        if not _pat.search(code):
            return code
        return _pat.sub(lambda m: f'{m.group(1)}pattern_id = "{new_pid}"', code, count=1)

    hc = _patch(healed_code)
    hx = _patch(healed_exec_code)
    print(
        f"[INFO] [PIPE] [PATTERN_GUARD] signals={trace['detected_signals']!r} "
        f"candidates={candidates!r} -> {new_pid!r} reason={trace['reject_reason']!r}"
    )
    return new_pid, hc, hx, trace


def run_ab2_interception(
    *,
    scaler,
    final_code,
    api_stubs,
    skill_id,
    expected_fp,
    decimal_style_mode,
    ocr_text,
    fraction_display_mode,
    ai_inference_time_sec,
    live_file_display_mode,
    optimize_live_execution_code_fn,
    patch_fraction_skill_eval_calls_fn,
    evaluate_iso_style_guard_fn,
    build_isomorphic_fallback_code_fn,
    extract_math_expr_from_question_fn,
    has_decimal_number_fn,
    is_expression_isomorphic_fn,
    sanitize_result_question_fn,
    format_result_question_display_fn,
    recompute_result_answer_fn,
    recompute_correct_answer_from_question_fn,
    maybe_add_o1_fix_fn,
):
    from core.code_utils.live_show_math_utils import classify_radical_style, radical_hard_style_preserved

    input_radical_style_ab2 = (
        classify_radical_style(ocr_text)
        if "FourOperationsOfRadicals" in (skill_id or "")
        else None
    )
    ab2_style_gate_trace: dict = {}

    ab2_exec_code = (final_code or "").strip()
    ab2_exec_code = ab2_exec_code.replace("\r\n", "\n")
    if ab2_exec_code.lower().startswith("```python"):
        ab2_exec_code = ab2_exec_code[len("```python"):].lstrip("\n")
    elif ab2_exec_code.startswith("```"):
        ab2_exec_code = ab2_exec_code[len("```"):].lstrip("\n")
    if ab2_exec_code.endswith("```"):
        ab2_exec_code = ab2_exec_code[:-3].rstrip()

    # [Fix] Apply execution optimizer to Ab2 as well, so that oversized range/while
    # loops are capped and time.sleep is stripped — same as Ab3.
    # This ensures CPU time comparison is fair (not confounded by loop size).
    ab2_exec_code = optimize_live_execution_code_fn(ab2_exec_code)
    ab2_exec_code = patch_fraction_skill_eval_calls_fn(ab2_exec_code, skill_id)
    import re as _re_ab2_safe

    ab2_exec_code = _re_ab2_safe.sub(r"\beval\s*\(", "safe_eval(", ab2_exec_code)

    ab2_healed_mirror = ab2_exec_code
    _raw_pat_ab2 = extract_selected_pattern_id_from_code(ab2_exec_code)
    _, ab2_healed_mirror, ab2_exec_code, ab2_pattern_guard_trace = apply_radical_pattern_p1_guard(
        skill_id, ocr_text, _raw_pat_ab2, ab2_healed_mirror, ab2_exec_code
    )
    _ab2_cur = extract_selected_pattern_id_from_code(ab2_exec_code)
    _, ab2_healed_mirror, ab2_exec_code, ab2_style_gate_trace = apply_radical_style_pattern_gate(
        skill_id,
        input_radical_style_ab2,
        _ab2_cur,
        ocr_text,
        ab2_healed_mirror,
        ab2_exec_code,
        ab2_pattern_guard_trace.get("candidate_patterns") or [],
    )
    if "FourOperationsOfRadicals" in (skill_id or "") and input_radical_style_ab2 is not None:
        ab2_exec_code = inject_required_radical_style_into_exec_code(
            ab2_exec_code, input_radical_style_ab2
        )
    ab2_style_retry_used = False
    ab2_style_output_exec_count = 0
    ab2_style_output_mismatch_history: list[dict] = []
    if ab2_pattern_guard_trace.get("reject_reason"):
        print(
            "[INFO] [PIPE] [Ab2] [PATTERN_GUARD] "
            f"signals={ab2_pattern_guard_trace.get('detected_signals')!r} "
            f"candidates={ab2_pattern_guard_trace.get('candidate_patterns')!r} "
            f"selected={ab2_pattern_guard_trace.get('selected_pattern_id')!r} "
            f"reason={ab2_pattern_guard_trace.get('reject_reason')!r}"
        )

    ab2_result = {}
    ab2_save_dir = "generated_scripts"
    if not os.path.exists(ab2_save_dir):
        os.makedirs(ab2_save_dir, exist_ok=True)
    ab2_filename = f"live_show_{int(time.time())}_{uuid.uuid4().hex[:6]}_ab2.py"
    ab2_file_path = os.path.join(ab2_save_dir, ab2_filename)
    ab2_final_exec_code = ab2_exec_code

    ab2_cpu_start = time.time()
    try:
        ab2_exe_res = _execute_with_stubs_if_needed(scaler, ab2_exec_code, api_stubs)
        ab2_exec_elapsed = time.time() - ab2_cpu_start

        if (
            "FourOperationsOfRadicals" in (skill_id or "")
            and input_radical_style_ab2 is not None
            and isinstance(ab2_exe_res, dict)
            and "error" not in ab2_exe_res
            and (ab2_exe_res.get("question_text") or "").strip()
        ):
            _ab2_out0 = classify_radical_style(ab2_exe_res.get("question_text", ""))
            _ab2_ok0, _ab2_rsn0 = radical_hard_style_preserved(
                input_radical_style_ab2, _ab2_out0 or "mixed"
            )
            ab2_style_output_exec_count = 1
            if not _ab2_ok0:
                ab2_style_output_mismatch_history.append(
                    {
                        "attempt": 1,
                        "input_style": input_radical_style_ab2,
                        "output_style": _ab2_out0,
                        "reason": _ab2_rsn0,
                    }
                )
                ab2_exec_code = inject_radical_style_retry_hint(ab2_exec_code)
                try:
                    ab2_exe_res = _execute_with_stubs_if_needed(scaler, ab2_exec_code, api_stubs)
                except Exception as _ab2_ex:
                    from core.domain_functions import StyleProfileExceededError
                    if isinstance(_ab2_ex, StyleProfileExceededError):
                        ab2_exe_res = {"question_text": "", "correct_answer": ""}
                    else:
                        raise
                ab2_style_retry_used = True
                ab2_style_output_exec_count = 2
                ab2_exec_elapsed = time.time() - ab2_cpu_start
                _ab2_out1 = classify_radical_style(ab2_exe_res.get("question_text", ""))
                _ab2_ok1, _ab2_rsn1 = radical_hard_style_preserved(
                    input_radical_style_ab2, _ab2_out1 or "mixed"
                )
                if not _ab2_ok1:
                    ab2_style_output_mismatch_history.append(
                        {
                            "attempt": 2,
                            "input_style": input_radical_style_ab2,
                            "output_style": _ab2_out1,
                            "reason": _ab2_rsn1,
                        }
                    )

        try:
            from scripts.evaluate_mcri import evaluate_math_hygiene

            if "question_text" in ab2_exe_res:
                h_score, _ = evaluate_math_hygiene(ab2_exe_res["question_text"])
                ab2_exe_res["_mcri_hygiene_score"] = h_score
        except Exception:
            pass

        ab2_result = ab2_exe_res
        ab2_final_exec_code = ab2_exec_code
    except Exception as e:
        ab2_exec_elapsed = time.time() - ab2_cpu_start
        ab2_result = {"error": f"執行錯誤: {e}"}

    # Radicals-only hard guarantee: Ab2 must not be missing/empty question_text.
    if "FourOperationsOfRadicals" in (skill_id or ""):
        _ab2_qt_now = ""
        if isinstance(ab2_result, dict) and "error" not in ab2_result:
            _ab2_qt_now = (ab2_result.get("question_text") or "").strip()
        if not _ab2_qt_now:
            try:
                _fb_code_ab2 = build_isomorphic_fallback_code_fn(ocr_text, skill_id=skill_id)
            except Exception:
                _fb_code_ab2 = ""
            if _fb_code_ab2:
                _fb_exec_ab2 = optimize_live_execution_code_fn(_fb_code_ab2)
                _fb_exec_ab2 = patch_fraction_skill_eval_calls_fn(_fb_exec_ab2, skill_id)
                _fb_exec_ab2 = re.sub(r"\beval\s*\(", "safe_eval(", _fb_exec_ab2)
                try:
                    _fb_exec_payload_ab2 = _fb_exec_ab2
                    if (
                        "IntegerOps." in _fb_exec_payload_ab2
                        and "class IntegerOps" not in _fb_exec_payload_ab2
                        and api_stubs
                    ):
                        _fb_exec_payload_ab2 = api_stubs + "\n\n" + _fb_exec_payload_ab2
                    _fb_res_ab2 = _execute_with_stubs_if_needed(scaler, _fb_exec_payload_ab2, api_stubs)
                except Exception:
                    _fb_res_ab2 = {}
                if isinstance(_fb_res_ab2, dict) and (_fb_res_ab2.get("question_text") or "").strip():
                    ab2_result = _fb_res_ab2
                    ab2_final_exec_code = _fb_exec_ab2
                    ab2_exec_elapsed = time.time() - ab2_cpu_start
            if not (isinstance(ab2_result, dict) and (ab2_result.get("question_text") or "").strip()):
                _ab2_qt_fb = _build_radical_fallback_question_text(ocr_text)
                try:
                    _ab2_ans_fb = recompute_correct_answer_from_question_fn(_ab2_qt_fb) or ""
                except Exception:
                    _ab2_ans_fb = ""
                ab2_result = {
                    "question_text": _ab2_qt_fb,
                    "correct_answer": _ab2_ans_fb,
                }
                _pw_ab2 = "計算" if str(_ab2_qt_fb).strip().startswith("計算") else "化簡"
                ab2_final_exec_code = _build_randomized_radical_question_script(ocr_text, _pw_ab2)

    ab2_output_radical_style = None
    ab2_style_preserved = True
    ab2_style_mismatch_reason = ""
    if input_radical_style_ab2 is not None:
        if isinstance(ab2_result, dict) and "error" not in ab2_result:
            _ab2_qt_final = (ab2_result.get("question_text") or "").strip()
            _ab2_meta = recompute_radical_style_fields_for_api(
                ocr_text,
                input_radical_style=input_radical_style_ab2,
                ab2_question_text=_ab2_qt_final,
            )
            ab2_output_radical_style = _ab2_meta.get("ab2_output_radical_style")
            ab2_style_preserved = bool(_ab2_meta.get("ab2_style_preserved", True))
            ab2_style_mismatch_reason = _ab2_meta.get("ab2_style_mismatch_reason", "")
        else:
            ab2_style_preserved = False
            ab2_style_mismatch_reason = "ab2_exec_error"

    if "FourOperationsOfRadicals" in (skill_id or ""):
        _ab2_qt_check = ""
        if isinstance(ab2_result, dict):
            _ab2_qt_check = (ab2_result.get("question_text") or "").strip()
        _ab2_qg_reasons: list[str] = []
        if _ab2_qt_check:
            _ab2_qg = evaluate_radical_quality_gate(
                source_ocr_expr=ocr_text,
                question_text=_ab2_qt_check,
                generated_expr=extract_math_expr_from_question_fn(_ab2_qt_check),
            )
            _ab2_qg_reasons = list(_ab2_qg.get("reasons") or [])
        _ab2_invalid = (
            not isinstance(ab2_result, dict)
            or ("error" in ab2_result)
            or (not _ab2_qt_check)
            or (_ab2_qt_check == "Error")
            or ("$" not in _ab2_qt_check)
            or (ab2_style_preserved is False)
            or bool(_ab2_qg_reasons)
        )
        if _ab2_invalid:
            _ab2_qt_fix = _build_radical_fallback_question_text(ocr_text)
            try:
                _ab2_ans_fix = recompute_correct_answer_from_question_fn(_ab2_qt_fix) or ""
            except Exception:
                _ab2_ans_fix = ""
            ab2_result = {
                "question_text": _ab2_qt_fix,
                "correct_answer": _ab2_ans_fix,
            }
            _pw_ab2_fix = "計算" if str(_ab2_qt_fix).strip().startswith("計算") else "化簡"
            ab2_final_exec_code = _build_randomized_radical_question_script(ocr_text, _pw_ab2_fix)
            ab2_output_radical_style = classify_radical_style(ab2_result["question_text"])
            _ab2_ok_fix, _ab2_rsn_fix = radical_hard_style_preserved(
                input_radical_style_ab2,
                ab2_output_radical_style or "mixed",
            )
            ab2_style_preserved = bool(_ab2_ok_fix)
            ab2_style_mismatch_reason = "" if _ab2_ok_fix else _ab2_rsn_fix

    if (
        isinstance(ab2_result, dict)
        and "error" not in ab2_result
        and (ab2_result.get("question_text") or "").strip()
        and not str(ab2_result.get("correct_answer") or "").strip()
    ):
        try:
            _ab2_ans_final = recompute_correct_answer_from_question_fn(
                ab2_result.get("question_text", "")
            )
        except Exception:
            _ab2_ans_final = None
        if _ab2_ans_final is not None:
            ab2_result["correct_answer"] = str(_ab2_ans_final)

    _ab2_persist_code = _prepend_missing_runtime_stubs(
        ab2_final_exec_code,
        skill_id,
        api_stubs,
    )

    with open(ab2_file_path, "w", encoding="utf-8") as _fb:
        _fb.write(_ab2_persist_code)

    try:
        live_file_display_mode[os.path.abspath(ab2_file_path)] = {
            "mode": fraction_display_mode,
            "skill_id": skill_id,
            "ocr_text": ocr_text,
            "sticky_problem": (
                str(ab2_result.get("question_text") or "").strip()
                if "FourOperationsOfRadicals" in (skill_id or "")
                else ""
            ),
            "sticky_answer": (
                str(ab2_result.get("correct_answer") or "").strip()
                if "FourOperationsOfRadicals" in (skill_id or "")
                else ""
            ),
        }
    except Exception:
        pass

    ab2_result["file_path"] = ab2_file_path
    ab2_result["ai_inference_time_sec"] = ai_inference_time_sec
    ab2_result["cpu_execution_time_sec"] = ab2_exec_elapsed

    final_code_with_stubs = api_stubs + "\n\n" + final_code
    ab2_result["raw_code"] = final_code_with_stubs
    ab2_result["final_code"] = final_code_with_stubs

    return {
        "ab2_result": ab2_result,
        "ab2_exec_elapsed": ab2_exec_elapsed,
        "ab2_file_path": ab2_file_path,
        "ab2_final_exec_code": ab2_final_exec_code,
        "final_code_with_stubs": final_code_with_stubs,
        "ab2_pattern_guard_trace": ab2_pattern_guard_trace,
        "ab2_selected_pattern_id": extract_selected_pattern_id_from_code(ab2_exec_code),
        "ab2_input_radical_style": input_radical_style_ab2,
        "ab2_output_radical_style": ab2_output_radical_style,
        "ab2_style_preserved": ab2_style_preserved,
        "ab2_style_mismatch_reason": ab2_style_mismatch_reason,
        "ab2_style_gate_trace": ab2_style_gate_trace,
        "ab2_style_retry_used": ab2_style_retry_used,
        "ab2_style_output_exec_count": ab2_style_output_exec_count,
        "ab2_style_output_mismatch_history": ab2_style_output_mismatch_history,
    }


def run_ab3_full_healer(
    *,
    scaler,
    final_code,
    skill_id,
    expected_fp,
    decimal_style_mode,
    ocr_text,
    fraction_display_mode,
    live_file_display_mode,
    api_stubs="",
    optimize_live_execution_code_fn,
    patch_fraction_skill_eval_calls_fn,
    advanced_healer_fn,
    sanitize_result_question_fn,
    evaluate_iso_style_guard_fn,
    append_iso_style_guard_logs_fn,
    append_fallback_switch_log_fn,
    profile_diff_summary_fn,
    build_isomorphic_fallback_code_fn,
    extract_math_expr_from_question_fn,
    has_decimal_number_fn,
    is_expression_isomorphic_fn,
    build_structural_profile_fn,
    recompute_result_answer_fn,
    recompute_correct_answer_from_question_fn,
    format_result_question_display_fn,
    maybe_add_o1_fix_fn,
    # Optional: post-healer scaffold reassembler (used by Radical Orchestrator)
    radical_reassemble_fn=None,
):
    def _derive_answer_for_single_mult_template(expr: str) -> str | None:
        s = str(expr or "").replace(" ", "")
        if not s:
            return None
        m1 = re.fullmatch(r"\\sqrt\{(\d+)\}\\times(-?\d+)\\sqrt\{(\d+)\}", s)
        if m1:
            a = int(m1.group(1))
            b = int(m1.group(2))
            c = int(m1.group(3))
            return f"{b}\\sqrt{{{a * c}}}"
        m2 = re.fullmatch(r"\(?(-?\d+)\)?\\times\(?(-?\d+)\)?\\sqrt\{(\d+)\}", s)
        if m2:
            a = int(m2.group(1))
            b = int(m2.group(2))
            c = int(m2.group(3))
            return f"{a * b}\\sqrt{{{c}}}"
        return None

    def _sync_answer_after_question_override(_exe_res, _detail_logs):
        if not isinstance(_exe_res, dict):
            return
        _qt = (_exe_res.get("question_text") or "").strip()
        if not _qt:
            return
        _expr = extract_math_expr_from_question_fn(_qt)
        _ans_direct = _derive_answer_for_single_mult_template(_expr)
        if _ans_direct:
            _exe_res["correct_answer"] = _ans_direct
            _exe_res["_answer_sync_template_direct"] = _ans_direct
            _detail_logs.append("[ANSWER_SYNC][TEMPLATE_DIRECT] derived_from_single_mult_template")
            return
        try:
            _ans = recompute_correct_answer_from_question_fn(_qt)
        except Exception:
            _ans = None
        if _ans is not None:
            _exe_res["correct_answer"] = _ans
            _detail_logs.append("[ANSWER_SYNC] recomputed_after_question_override")

    cpu_start_ab3 = time.time()
    problems_result = []
    ab3_exec_elapsed = 0.0
    pattern_guard_trace = {
        "detected_signals": [],
        "candidate_patterns": [],
        "selected_pattern_id": None,
        "reject_reason": None,
    }
    pid_before_univ: str | None = None
    pattern_overwrite_reason = ""
    from core.code_utils.live_show_math_utils import classify_radical_style, radical_hard_style_preserved

    input_radical_style = (
        classify_radical_style(ocr_text)
        if "FourOperationsOfRadicals" in (skill_id or "")
        else None
    )
    style_gate_trace: dict = {}
    style_retry_used = False
    style_mismatch_after_retry = False
    style_profile_vars_error: str | None = None
    style_output_exec_count = 0
    style_output_mismatch_history: list[dict] = []
    quality_gate_passed = True
    quality_gate_reasons: list[str] = []
    anti_echo_retry_used = False
    anti_echo_similarity = 0.0
    exemplar_echo_hit = False
    exemplar_echo_retry_used = False
    radical_fallback_retry_used = False
    radical_fallback_retry_reason = ""
    radical_fallback_operator_lock_passed = True
    radical_fallback_echo_guarded = False
    radical_fallback_single_mult_perturb_used = False
    radical_fallback_single_mult_perturb_note = ""
    radical_fallback_single_mult_template_used = False
    radical_fallback_single_mult_template_reason = ""
    radical_fallback_token_delta_count = 0

    # [UNIVERSAL FIX] Force Radical Scaffold Assembly here, for BOTH text and image paths
    if "FourOperationsOfRadicals" in (skill_id or ""):
        from core.routes.live_show import _assemble_radical_orchestrator_code

        final_code = _assemble_radical_orchestrator_code(
            final_code,
            required_radical_style=input_radical_style,
        )
        print(f"[INFO] [ASSEMBLER] Applied orchestrator scaffold for skill_id={skill_id!r}")

    pid_before_univ = extract_selected_pattern_id_from_code(final_code)
    print(f"[INFO] [PIPE] selected_pattern_id_before_assemble={pid_before_univ!r}")

    healed_code = final_code
    regex_fixes = 0
    regex_code_fixes = 0
    regex_display_fixes = 0
    ast_fixes = 0
    o1_fixes = 0
    detail_logs = []
    generated_fp = {}
    iso_isomorphic = False
    iso_guard_triggered = False
    fallback_used = False

    healer_bypassed = bool("FourOperationsOfRadicals" in (skill_id or ""))

    if "FourOperationsOfRadicals" in (skill_id or ""):
        # Radical Orchestrator: skip the general healer entirely
        anti_dup_fixes = 0
        detail_logs.insert(0, "[HEALER_STATUS] [OK] Radical Orchestrator — general healer bypassed.")
        print("[INFO] [ASSEMBLER] Radical path: general healer bypassed.")
    else:
        try:
            healed_code, *healer_stats = advanced_healer_fn(final_code, ablation_id=3, skill_id=skill_id)
            regex_code_fixes = healer_stats[0] if len(healer_stats) > 0 else 0
            regex_fixes = regex_code_fixes
            ast_fixes = healer_stats[1] if len(healer_stats) > 1 else 0
            ast_stats = healer_stats[2] if len(healer_stats) > 2 else None
            # Collect AST healer logs before mutating detail_logs
            detail_logs = getattr(ast_stats, "logs", []) if ast_stats else []
            _healer_total = healer_stats[5] if len(healer_stats) > 5 and isinstance(healer_stats[5], int) else None
            anti_dup_fixes = max(0, (_healer_total - regex_code_fixes - ast_fixes)) if _healer_total is not None else 0
            regex_code_fixes += anti_dup_fixes
            regex_fixes = regex_code_fixes
            detail_logs.insert(0, f"[HEALER_STATUS] [OK] Active Healer ran — regex_code={regex_code_fixes}, ast={ast_fixes}, anti_dup={anti_dup_fixes}")
            print(
                f"[INFO] [HEALER] Success regex={regex_fixes} ast={ast_fixes} anti_dup={anti_dup_fixes}"
            )
        except Exception as _healer_exc:
            import traceback as _healer_tb
            print("[ERROR] [HEALER] CRASHED")
            _healer_tb.print_exc()
            healed_code = final_code
            anti_dup_fixes = 0
            detail_logs.append(f"[HEALER_STATUS] [ERROR] Healer CRASHED — {type(_healer_exc).__name__}: {_healer_exc}")
            detail_logs.append("[HEALER_STATUS] 使用原始 AI 輸出，Skip 所有修復。")

    _pid_healer = extract_selected_pattern_id_from_code(healed_code)
    print(f"[INFO] [PIPE] selected_pattern_id={_pid_healer!r} (after healer)")
    print(f"[INFO] [PIPE] healer_bypassed={healer_bypassed}")

    healed_exec_code = patch_fraction_skill_eval_calls_fn(
        optimize_live_execution_code_fn(healed_code),
        skill_id,
    )
    # [Bug 16 Fix] If AST healer exited early (e.g. syntax-repair loop), bare eval()
    # may survive.  Replace now so MCRI static scan sees safe_eval() instead.
    import re as _re16
    healed_exec_code = _re16.sub(r'\beval\s*\(', 'safe_eval(', healed_exec_code)

    _raw_pat = extract_selected_pattern_id_from_code(healed_exec_code)
    _, healed_code, healed_exec_code, pattern_guard_trace = apply_radical_pattern_p1_guard(
        skill_id, ocr_text, _raw_pat, healed_code, healed_exec_code
    )
    _pid_after_guard = extract_selected_pattern_id_from_code(healed_exec_code)
    print(f"[INFO] [PIPE] selected_pattern_id_after_guard={_pid_after_guard!r}")
    if pattern_guard_trace.get("reject_reason"):
        detail_logs.append(
            "[PATTERN_GUARD] "
            f"signals={pattern_guard_trace.get('detected_signals')!r} "
            f"candidates={pattern_guard_trace.get('candidate_patterns')!r} "
            f"selected={pattern_guard_trace.get('selected_pattern_id')!r} "
            f"reason={pattern_guard_trace.get('reject_reason')!r}"
        )

    _cur_style_pat = extract_selected_pattern_id_from_code(healed_exec_code)
    _, healed_code, healed_exec_code, style_gate_trace = apply_radical_style_pattern_gate(
        skill_id,
        input_radical_style,
        _cur_style_pat,
        ocr_text,
        healed_code,
        healed_exec_code,
        pattern_guard_trace.get("candidate_patterns") or [],
    )
    if style_gate_trace.get("style_gate_reason") not in (
        None,
        "pattern_ok",
        "skipped_unknown_style",
    ):
        detail_logs.append(
            "[STYLE_GATE] "
            f"reason={style_gate_trace.get('style_gate_reason')!r} "
            f"rejected={style_gate_trace.get('rejected_pattern_id')!r} "
            f"selected={style_gate_trace.get('selected_pattern_id')!r}"
        )

    if "FourOperationsOfRadicals" in (skill_id or "") and input_radical_style is not None:
        healed_exec_code = inject_required_radical_style_into_exec_code(
            healed_exec_code, input_radical_style
        )
        healed_code = inject_required_radical_style_into_exec_code(
            healed_code, input_radical_style
        )

    try:
        try:
            exe_res = _execute_with_stubs_if_needed(scaler, healed_exec_code, api_stubs)
        except Exception as _ex:
            from core.domain_functions import StyleProfileExceededError
            if isinstance(_ex, StyleProfileExceededError):
                style_profile_vars_error = str(_ex)
                detail_logs.append(f"[STYLE_PROFILE_VARS] {style_profile_vars_error}")
                exe_res = {"question_text": "", "correct_answer": ""}
            else:
                raise
        if "question_text" in exe_res:
            trace_seed = {
                "regex_code_fixes": regex_code_fixes,
                "regex_display_fixes": regex_display_fixes,
                "ast_fixes": ast_fixes,
                "o1_fixes": o1_fixes,
            }
            sanitize_report, trace_shadow = sanitize_result_question_fn(
                exe_res,
                detail_logs=detail_logs,
                after_fallback=False,
                trace_seed=trace_seed,
            )
            regex_display_fixes = int(trace_shadow.get("regex_display_fixes", 0) or 0)
            regex_fixes = int(trace_shadow.get("regex_fixes", 0) or 0)
            sanitize_meta = sanitize_report if isinstance(sanitize_report, dict) else {}
            double_paren_cnt = int(sanitize_meta.get("double_paren_fixes", 0) or 0)
            negative_wrap_cnt = int(sanitize_meta.get("negative_wrap_fixes", 0) or 0)
            if double_paren_cnt > 0:
                detail_logs.append(f"[DISPLAY_SANITIZE] collapsed {double_paren_cnt} nested numeric parenthesis pattern(s).")
            if negative_wrap_cnt > 0:
                detail_logs.append(f"[DISPLAY_SANITIZE] wrapped {negative_wrap_cnt} bare negative literal(s) with parentheses.")

        if (
            "FourOperationsOfRadicals" in (skill_id or "")
            and input_radical_style is not None
            and isinstance(exe_res, dict)
            and "error" not in exe_res
            and (exe_res.get("question_text") or "").strip()
        ):
            _out_rs0 = classify_radical_style(exe_res.get("question_text", ""))
            _ok_s0, _rsn0 = radical_hard_style_preserved(
                input_radical_style, _out_rs0 or "mixed"
            )
            style_output_exec_count = 1
            if not _ok_s0:
                style_output_mismatch_history.append(
                    {
                        "attempt": 1,
                        "input_style": input_radical_style,
                        "output_style": _out_rs0,
                        "reason": _rsn0,
                    }
                )
                detail_logs.append(
                    f"[STYLE_REGEN] same_pattern+style_profile exec#2 "
                    f"input={input_radical_style!r} was_output={_out_rs0!r} {_rsn0!r}"
                )
                healed_exec_code = inject_radical_style_retry_hint(healed_exec_code)
                healed_code = inject_radical_style_retry_hint(healed_code)
                try:
                    exe_res = _execute_with_stubs_if_needed(scaler, healed_exec_code, api_stubs)
                except Exception as _ex2:
                    from core.domain_functions import StyleProfileExceededError
                    if isinstance(_ex2, StyleProfileExceededError):
                        style_profile_vars_error = str(_ex2)
                        detail_logs.append(f"[STYLE_PROFILE_VARS][regen] {style_profile_vars_error}")
                        exe_res = {"question_text": "", "correct_answer": ""}
                    else:
                        raise
                style_retry_used = True
                style_output_exec_count = 2
                if "question_text" in exe_res:
                    trace_seed_sr = {
                        "regex_code_fixes": regex_code_fixes,
                        "regex_display_fixes": regex_display_fixes,
                        "ast_fixes": ast_fixes,
                        "o1_fixes": o1_fixes,
                    }
                    sanitize_report_sr, trace_shadow_sr = sanitize_result_question_fn(
                        exe_res,
                        detail_logs=detail_logs,
                        after_fallback=False,
                        trace_seed=trace_seed_sr,
                    )
                    regex_display_fixes = int(trace_shadow_sr.get("regex_display_fixes", 0) or 0)
                    regex_fixes = int(trace_shadow_sr.get("regex_fixes", 0) or 0)
                    sanitize_meta_sr = sanitize_report_sr if isinstance(sanitize_report_sr, dict) else {}
                    double_paren_cnt_sr = int(sanitize_meta_sr.get("double_paren_fixes", 0) or 0)
                    negative_wrap_cnt_sr = int(sanitize_meta_sr.get("negative_wrap_fixes", 0) or 0)
                    if double_paren_cnt_sr > 0:
                        detail_logs.append(
                            f"[DISPLAY_SANITIZE] collapsed {double_paren_cnt_sr} nested numeric parenthesis pattern(s)."
                        )
                    if negative_wrap_cnt_sr > 0:
                        detail_logs.append(
                            f"[DISPLAY_SANITIZE] wrapped {negative_wrap_cnt_sr} bare negative literal(s) with parentheses."
                        )
                _out_rs1 = classify_radical_style(exe_res.get("question_text", ""))
                _ok_s1, _rsn1 = radical_hard_style_preserved(
                    input_radical_style, _out_rs1 or "mixed"
                )
                if not _ok_s1:
                    style_mismatch_after_retry = True
                    style_output_mismatch_history.append(
                        {
                            "attempt": 2,
                            "input_style": input_radical_style,
                            "output_style": _out_rs1,
                            "reason": _rsn1,
                        }
                    )
                    detail_logs.append(
                        f"[STYLE_MISMATCH] after_regen output={_out_rs1!r} {_rsn1!r}"
                    )

        generated_expr = extract_math_expr_from_question_fn(exe_res.get("question_text", ""))

        _src_ocr_120 = (ocr_text or "")[:120]
        _gen_ex_120 = (generated_expr or "")[:120]
        print(f"[INFO] [PIPE] source_ocr_expr={_src_ocr_120!r}")
        print(f"[INFO] [PIPE] generated_expr={_gen_ex_120!r} (post-first-exec)")

        if "FourOperationsOfRadicals" in (skill_id or ""):
            _gen_norm0 = _normalize_expr_for_echo(generated_expr)
            exemplar_echo_hit = _gen_norm0 in {_normalize_expr_for_echo(x) for x in RADICAL_EXEMPLAR_POOL}
            if exemplar_echo_hit:
                detail_logs.append("[EXEMPLAR_ECHO] hit exemplar pool; regenerate same pattern once")
                healed_exec_code = inject_radical_anti_echo_retry_hint(healed_exec_code)
                healed_code = inject_radical_anti_echo_retry_hint(healed_code)
                exemplar_echo_retry_used = True
                try:
                    exe_res = _execute_with_stubs_if_needed(scaler, healed_exec_code, api_stubs)
                except Exception:
                    exe_res = {"question_text": "", "correct_answer": ""}
                generated_expr = extract_math_expr_from_question_fn(exe_res.get("question_text", ""))

            _qg = evaluate_radical_quality_gate(
                source_ocr_expr=ocr_text,
                question_text=exe_res.get("question_text", ""),
                generated_expr=generated_expr,
            )
            quality_gate_passed = bool(_qg.get("passed", True))
            quality_gate_reasons = list(_qg.get("reasons") or [])
            anti_echo_similarity = float(_qg.get("anti_echo_similarity", 0.0) or 0.0)
            if not quality_gate_passed:
                detail_logs.append(
                    "[QUALITY_GATE][FAIL] " + ", ".join(quality_gate_reasons)
                )
                # First remediation: anti-echo retry (same pattern, regenerate values).
                anti_echo_retry_used = True
                healed_exec_code = inject_radical_anti_echo_retry_hint(healed_exec_code)
                healed_code = inject_radical_anti_echo_retry_hint(healed_code)
                try:
                    exe_res = _execute_with_stubs_if_needed(scaler, healed_exec_code, api_stubs)
                except Exception:
                    exe_res = {"question_text": "", "correct_answer": ""}
                generated_expr = extract_math_expr_from_question_fn(exe_res.get("question_text", ""))
                _qg2 = evaluate_radical_quality_gate(
                    source_ocr_expr=ocr_text,
                    question_text=exe_res.get("question_text", ""),
                    generated_expr=generated_expr,
                )
                quality_gate_passed = bool(_qg2.get("passed", True))
                quality_gate_reasons = list(_qg2.get("reasons") or [])
                anti_echo_similarity = float(_qg2.get("anti_echo_similarity", 0.0) or 0.0)
                if not quality_gate_passed:
                    detail_logs.append(
                        "[QUALITY_GATE][RETRY_FAIL] " + ", ".join(quality_gate_reasons)
                    )

        # ── Hard bypass: Radical / Orchestrator skills ───────────────────────
        # Two independent signals trigger the bypass (belt-and-suspenders):
        #   (a) expected_fp is empty — set by _radical_bypass_expected_fp()
        #   (b) skill_id contains "Radicals" — catches any new radical variant
        # Without this gate the ISO-guard ALWAYS fires for radical skills because
        # _is_expression_isomorphic({}, expr) compared every field against None,
        # triggering an integer-based deterministic fallback that destroyed the
        # DomainFunctionHelper-generated LaTeX output.
        _bypass_iso_guard = (not expected_fp) or ("Radicals" in (skill_id or ""))
        if _bypass_iso_guard:
            try:
                from core.skill_policies.registry import get_skill_policy as _gsp_chk
                _chk_policy = _gsp_chk(skill_id) or {}
                if _chk_policy.get("skip_complexity_mirror", False) or "Radicals" in (skill_id or ""):
                    print(
                        f"[WARN] [ADVISOR] Radical Skill Detected: "
                        f"Bypassing Legacy Complexity Mirror. skill={skill_id!r}"
                    )
            except Exception:
                print(
                    f"[WARN] [ADVISOR] Radical Skill Detected: "
                    f"Bypassing Legacy Complexity Mirror. skill={skill_id!r}"
                )
            detail_logs.append(
                f"[COMPLEXITY_MIRROR][HARD_BYPASS] expected_fp=empty or 'Radicals' in skill_id — "
                f"ISO-guard skipped for {skill_id!r}."
            )
            guard_meta = {
                "triggered":       False,
                "expr":            generated_expr,
                "isomorphic":      True,
                "decimal_mismatch": False,
            }
            decimal_mismatch = False
        else:
            guard_meta = evaluate_iso_style_guard_fn(
                expected_fp=expected_fp,
                question_text=exe_res.get("question_text", ""),
                decimal_style_mode=decimal_style_mode,
                extract_expr_fn=extract_math_expr_from_question_fn,
                has_decimal_fn=has_decimal_number_fn,
                isomorphic_fn=is_expression_isomorphic_fn,
            )
            decimal_mismatch = bool(guard_meta.get("decimal_mismatch"))

        # [Bug 29 Guard] 明確的中括號↔絕對值結構錯位守衛（ISO guard 的備援保障）
        # 當 expected 有 [ ] (bracket_count>0, abs_count=0) 但生成含 | | 時強制 fallback。
        if not guard_meta.get("triggered"):
            _exp_brackets29 = expected_fp.get("bracket_count", 0)
            _exp_abs29 = expected_fp.get("abs_count", 0)
            _qt29 = exe_res.get("question_text", "")
            if _exp_brackets29 > 0 and _exp_abs29 == 0 and "|" in _qt29:
                guard_meta["triggered"] = True
                guard_meta["bracket_abs_mismatch"] = True
                detail_logs.append(
                    f"[BRACKET_ABS_GUARD][Bug29] 例題使用中括號（bracket_count={_exp_brackets29}，abs_count=0）"
                    f"但生成題目含 | 絕對值符號，強制觸發 iso-fallback。"
                )

        # [Bug 25 Guard] 非分數技能禁止在生成題目中出現 \frac{}{}
        # [Bug 26 Guard] 分數技能帶分數/純分數顯示風格必須與輸入例題一致
        #
        # [Orchestrator Bypass] Skills that set skip_complexity_mirror=True
        # (e.g. jh_數學2上_FourOperationsOfRadicals) generate LaTeX with
        # \frac / \sqrt via DomainFunctionHelper — this is intentional and
        # correct.  Applying Bug-25 or Bug-26 guards would falsely trigger
        # iso-fallback.  Skip both guards for those skills.
        if not guard_meta.get("triggered"):
            import re as _re_guard26
            from core.skill_policies.registry import get_skill_policy as _gsp
            _policy = _gsp(skill_id)
            _qt = exe_res.get("question_text", "")

            if _policy.get("skip_complexity_mirror", False):
                # Radical / orchestrator skill — structural guards don't apply.
                detail_logs.append(
                    f"[COMPLEXITY_MIRROR][BYPASS] skill={skill_id!r} has "
                    f"skip_complexity_mirror=True; Bug-25/26 guards skipped."
                )
            elif not _policy.get("enable_fraction_display", False):
                # Bug 25: 非分數技能（整數四則運算等）出現 \frac 時觸發 fallback
                if "\\frac" in _qt:
                    guard_meta["triggered"] = True
                    guard_meta["frac_forbidden"] = True
                    detail_logs.append(
                        f"[FRAC_GUARD][Bug25] 非分數技能({skill_id!r})生成含 \\frac 的題目，"
                        f"疑似 AI 幻覺，強制觸發 iso-fallback。"
                    )
            else:
                # Bug 26: 分數技能 — 帶分數 / 純分數顯示風格必須鏡像輸入例題
                # 帶分數pattern：整數緊接 \frac（前面非 \、{、/，避免誤抓 \frac 本體）
                _HAS_MIXED_RE = _re_guard26.compile(r'(?<![\\{/])\d+\s*\\frac\s*\{')
                _has_mixed_gen = bool(_HAS_MIXED_RE.search(_qt))
                if fraction_display_mode == "fraction" and _has_mixed_gen:
                    # 輸入只有純分數，但 AI 生成了帶分數
                    guard_meta["triggered"] = True
                    guard_meta["mixed_style_mismatch"] = True
                    detail_logs.append(
                        "[MIXED_GUARD][Bug26] 輸入為純分數（無帶分數），"
                        "生成題目含帶分數（整數+\\frac），強制觸發 iso-fallback。"
                    )
                elif fraction_display_mode == "mixed" and not _has_mixed_gen:
                    # 輸入有帶分數，但 AI 生成了純分數
                    guard_meta["triggered"] = True
                    guard_meta["mixed_style_mismatch"] = True
                    detail_logs.append(
                        "[MIXED_GUARD][Bug26] 輸入含帶分數，"
                        "生成題目無帶分數（僅 \\frac 無整數首項），強制觸發 iso-fallback。"
                    )

        iso_guard_triggered = bool(guard_meta.get("triggered"))
        print(f"[INFO] [PIPE] iso_guard_triggered={iso_guard_triggered} (pre-fallback branch)")

        if "FourOperationsOfRadicals" in (skill_id or "") and not quality_gate_passed:
            guard_meta["triggered"] = True
            guard_meta["quality_gate_reasons"] = quality_gate_reasons
            detail_logs.append(
                "[QUALITY_GATE] forcing deterministic fallback due to "
                + ", ".join(quality_gate_reasons)
            )

        if guard_meta.get("triggered"):
            append_iso_style_guard_logs_fn(
                detail_logs,
                expected_fp,
                generated_expr,
                decimal_mismatch,
                is_expression_isomorphic_fn,
                profile_diff_summary_fn,
            )

            fallback_code = build_isomorphic_fallback_code_fn(ocr_text, skill_id=skill_id)
            if not fallback_code:
                # Fallback returned empty string — OCR text may have no parseable numbers.
                # Log the failure clearly so diagnostics can catch it.
                detail_logs.append(
                    "[ISO_GUARD][FALLBACK_EMPTY] build_isomorphic_fallback_code 返回空字串"
                    "（OCR 文字可能無數字 span），跳過 fallback，保留原始 AI 輸出。"
                )
            if fallback_code:
                fallback_used = True
                healed_code = fallback_code
                healed_exec_code = optimize_live_execution_code_fn(healed_code)
                healed_exec_code = patch_fraction_skill_eval_calls_fn(healed_exec_code, skill_id)
                import re as _re_fb

                healed_exec_code = _re_fb.sub(r"\beval\s*\(", "safe_eval(", healed_exec_code)
                _raw_fb = extract_selected_pattern_id_from_code(healed_exec_code)
                _, healed_code, healed_exec_code, pattern_guard_trace = apply_radical_pattern_p1_guard(
                    skill_id, ocr_text, _raw_fb, healed_code, healed_exec_code
                )
                if pattern_guard_trace.get("reject_reason"):
                    detail_logs.append(
                        "[PATTERN_GUARD][POST_FALLBACK] "
                        f"signals={pattern_guard_trace.get('detected_signals')!r} "
                        f"selected={pattern_guard_trace.get('selected_pattern_id')!r} "
                        f"reason={pattern_guard_trace.get('reject_reason')!r}"
                    )
                _cur_fb = extract_selected_pattern_id_from_code(healed_exec_code)
                _, healed_code, healed_exec_code, style_gate_trace = apply_radical_style_pattern_gate(
                    skill_id,
                    input_radical_style,
                    _cur_fb,
                    ocr_text,
                    healed_code,
                    healed_exec_code,
                    pattern_guard_trace.get("candidate_patterns") or [],
                )
                if "FourOperationsOfRadicals" in (skill_id or "") and input_radical_style is not None:
                    healed_exec_code = inject_required_radical_style_into_exec_code(
                        healed_exec_code, input_radical_style
                    )
                    healed_code = inject_required_radical_style_into_exec_code(
                        healed_code, input_radical_style
                    )
                _exec_payload = healed_exec_code
                if (
                    "IntegerOps." in _exec_payload
                    and "class IntegerOps" not in _exec_payload
                    and api_stubs
                ):
                    _exec_payload = api_stubs + "\n\n" + _exec_payload
                exe_res = _execute_with_stubs_if_needed(scaler, _exec_payload, api_stubs)
                if "FourOperationsOfRadicals" in (skill_id or ""):
                    _qt_fb = (exe_res.get("question_text") or "").strip() if isinstance(exe_res, dict) else ""
                    _expr_fb = extract_math_expr_from_question_fn(_qt_fb)
                    _qg_fb = evaluate_radical_quality_gate(
                        source_ocr_expr=ocr_text,
                        question_text=_qt_fb,
                        generated_expr=_expr_fb,
                    )
                    _reasons_fb = list(_qg_fb.get("reasons") or [])
                    _op_lock_fail_fb = "operator_lock_violation" in _reasons_fb
                    _echo_fail_fb = "echo_violation" in _reasons_fb
                    _invalid_fb = (
                        (not isinstance(exe_res, dict))
                        or ("error" in exe_res)
                        or (not _qt_fb)
                        or ("$" not in _qt_fb)
                    )
                    _need_retry_fb = _invalid_fb or _op_lock_fail_fb or _echo_fail_fb
                    _retry_reason_parts: list[str] = []
                    if _invalid_fb:
                        _retry_reason_parts.append("invalid_question_text")
                    if _op_lock_fail_fb:
                        _retry_reason_parts.append("operator_lock_violation")
                    if _echo_fail_fb:
                        _retry_reason_parts.append("echo_violation")

                    _chosen_exe_res = exe_res
                    _retry_accepted = False

                    if _need_retry_fb:
                        radical_fallback_retry_used = True
                        radical_fallback_retry_reason = ",".join(_retry_reason_parts)
                        detail_logs.append(
                            "[ISO_GUARD][RADICAL_FALLBACK_RETRY] reason="
                            + radical_fallback_retry_reason
                        )
                        try:
                            _fb_code_retry = build_isomorphic_fallback_code_fn(ocr_text, skill_id=skill_id)
                        except Exception:
                            _fb_code_retry = ""
                        _single_mult_perturb = bool(
                            input_radical_style == "simple_radical"
                            and (r"\times" in (ocr_text or ""))
                            and (_op_lock_fail_fb or _echo_fail_fb)
                        )
                        if _single_mult_perturb and _fb_code_retry:
                            # Deterministic tiny perturbation for single-multiply radicals:
                            # shift first random_nonzero range to avoid OCR-echo regeneration.
                            _seed = (sum(ord(c) for c in (ocr_text or "")) % 3) + 1
                            _pat_rng = re.compile(
                                r"IntegerOps\.random_nonzero\(\s*(-?\d+)\s*,\s*(-?\d+)\s*\)",
                                re.MULTILINE,
                            )

                            def _bump_first_rng(m):
                                lo = int(m.group(1))
                                hi = int(m.group(2))
                                if hi - lo >= 4:
                                    lo2 = lo + _seed
                                    hi2 = hi + _seed
                                    return f"IntegerOps.random_nonzero({lo2}, {hi2})"
                                return m.group(0)

                            _fb_code_retry2, _n_sub = _pat_rng.subn(
                                _bump_first_rng, _fb_code_retry, count=1
                            )
                            if _n_sub > 0 and _fb_code_retry2 != _fb_code_retry:
                                _fb_code_retry = _fb_code_retry2
                                radical_fallback_single_mult_perturb_used = True
                                radical_fallback_single_mult_perturb_note = (
                                    f"single_mult_seeded_range_shift:+{_seed}"
                                )
                                detail_logs.append(
                                    "[ISO_GUARD][RADICAL_SINGLE_MULT_PERTURB] "
                                    + radical_fallback_single_mult_perturb_note
                                )
                        if _fb_code_retry:
                            _fb_exec_retry = optimize_live_execution_code_fn(_fb_code_retry)
                            _fb_exec_retry = patch_fraction_skill_eval_calls_fn(_fb_exec_retry, skill_id)
                            _fb_exec_retry = re.sub(r"\beval\s*\(", "safe_eval(", _fb_exec_retry)
                            try:
                                _fb_res_retry = _execute_with_stubs_if_needed(
                                    scaler, _fb_exec_retry, api_stubs
                                )
                            except Exception:
                                _fb_res_retry = {}

                            _qt_retry = (
                                (_fb_res_retry.get("question_text") or "").strip()
                                if isinstance(_fb_res_retry, dict)
                                else ""
                            )
                            _expr_retry = extract_math_expr_from_question_fn(_qt_retry)
                            _qg_retry = evaluate_radical_quality_gate(
                                source_ocr_expr=ocr_text,
                                question_text=_qt_retry,
                                generated_expr=_expr_retry,
                            )
                            _retry_reasons = list(_qg_retry.get("reasons") or [])
                            _src_norm_retry = _normalize_expr_for_echo(ocr_text)
                            _retry_norm = _normalize_expr_for_echo(_expr_retry)
                            _retry_not_echo_like_input = bool(
                                _retry_norm and _src_norm_retry and (_retry_norm != _src_norm_retry)
                            )
                            _retry_valid = (
                                isinstance(_fb_res_retry, dict)
                                and "error" not in _fb_res_retry
                                and bool(_qt_retry)
                                and ("$" in _qt_retry)
                                and ("operator_lock_violation" not in _retry_reasons)
                                and ("echo_violation" not in _retry_reasons)
                                and _retry_not_echo_like_input
                            )
                            if _retry_valid:
                                _retry_accepted = True
                                _chosen_exe_res = _fb_res_retry
                                detail_logs.append("[ISO_GUARD][RADICAL_FALLBACK_RETRY] accepted")
                            else:
                                detail_logs.append(
                                    "[ISO_GUARD][RADICAL_FALLBACK_RETRY] rejected reasons="
                                    + ",".join(_retry_reasons or ["invalid_question_text"])
                                )

                    if not _retry_accepted and _need_retry_fb:
                        _template_applied = False
                        _expr_input_fb = (extract_math_expr_from_question_fn(ocr_text) or ocr_text or "").strip()
                        _single_mult_input = bool(
                            re.search(r"\\times", _expr_input_fb)
                            and (
                                re.search(
                                    r"\(?\s*-?\d+\s*\)?\s*\\times\s*\(?\s*-?\d+\s*\)?\s*\\sqrt\{\d+\}",
                                    _expr_input_fb,
                                )
                                or re.search(r"\\sqrt\{\d+\}\s*\\times\s*\\sqrt\{\d+\}", _expr_input_fb)
                            )
                        )
                        if (
                            input_radical_style == "simple_radical"
                            and (r"\times" in (ocr_text or ""))
                            and (_op_lock_fail_fb or _echo_fail_fb)
                            and _single_mult_input
                        ):
                            nums_in = [int(x) for x in re.findall(r"-?\d+", _expr_input_fb)]
                            if nums_in:
                                # Deterministic safe pool that avoids input numbers entirely.
                                # This is intentionally local to radical single-mult fallback.
                                _seed3 = sum(ord(c) for c in (ocr_text or ""))
                                _root_pool = [7, 11, 13, 17, 19]
                                _coef_pool = [2, 3, 4, 5, 6]
                                _forbid = {abs(n) for n in nums_in}

                                def _pick(pool, start):
                                    for i in range(len(pool)):
                                        v = pool[(start + i) % len(pool)]
                                        if v not in _forbid:
                                            return v
                                    return pool[start % len(pool)]

                                A = _pick(_root_pool, _seed3 % len(_root_pool))
                                B = _pick(_coef_pool, (_seed3 // 3) % len(_coef_pool))
                                C = _pick(_root_pool, (_seed3 // 5) % len(_root_pool))
                                if C == A:
                                    C = _pick(_root_pool, (_seed3 // 7 + 1) % len(_root_pool))

                                _expr_tpl = f"\\sqrt{{{A}}}\\times{B}\\sqrt{{{C}}}"
                                _in_tokens = [str(x) for x in nums_in[:3]]
                                _out_tokens = [str(A), str(B), str(C)]
                                _delta = sum(1 for i, t in enumerate(_in_tokens) if i < len(_out_tokens) and t != _out_tokens[i])
                                radical_fallback_token_delta_count = _delta
                                _norm_in = _normalize_expr_for_echo(_expr_input_fb)
                                _norm_tpl = _normalize_expr_for_echo(_expr_tpl)
                                if _delta >= 3 and _norm_in != _norm_tpl:
                                    _ans_fb = (
                                        _chosen_exe_res.get("correct_answer", "")
                                        if isinstance(_chosen_exe_res, dict)
                                        else ""
                                    )
                                    _chosen_exe_res = {
                                        "question_text": _build_radical_fallback_question_text(_expr_tpl),
                                        "correct_answer": _ans_fb,
                                    }
                                    _sync_answer_after_question_override(_chosen_exe_res, detail_logs)
                                    radical_fallback_single_mult_template_used = True
                                    radical_fallback_single_mult_template_reason = (
                                        "single_mult_template_after_retry_fail"
                                    )
                                    detail_logs.append(
                                        "[ISO_GUARD][RADICAL_SINGLE_MULT_TEMPLATE] "
                                        f"used delta={_delta} expr={_expr_tpl!r}"
                                    )
                                    _template_applied = True

                        # Hard lock for the known single-mult echo trap: once template
                        # fallback is applied, mark it accepted so downstream cannot
                        # re-enter mirror fallback for this branch.
                        if _template_applied:
                            _retry_accepted = True

                        if _template_applied:
                            exe_res = _chosen_exe_res
                            _qt_final_fb = (
                                (exe_res.get("question_text") or "").strip()
                                if isinstance(exe_res, dict)
                                else ""
                            )
                            _expr_final_fb = extract_math_expr_from_question_fn(_qt_final_fb)
                            _qg_final_fb = evaluate_radical_quality_gate(
                                source_ocr_expr=ocr_text,
                                question_text=_qt_final_fb,
                                generated_expr=_expr_final_fb,
                            )
                            _final_reasons_fb = list(_qg_final_fb.get("reasons") or [])
                            radical_fallback_operator_lock_passed = (
                                "operator_lock_violation" not in _final_reasons_fb
                            )
                            radical_fallback_echo_guarded = (
                                "echo_violation" not in _final_reasons_fb
                            )

                    if (not _retry_accepted) and _need_retry_fb and (not radical_fallback_single_mult_template_used):
                        _expr_final_fallback = _build_non_echo_radical_expr(ocr_text)
                        if (
                            input_radical_style == "simple_radical"
                            and (r"\times" in (ocr_text or ""))
                            and _need_retry_fb
                        ):
                            _seed2 = (sum(ord(c) for c in (ocr_text or "")) % 2) + 1
                            _num_pat = re.compile(r"(?<![\\\w])(-?\d+)")
                            _changed_once = False

                            def _perturb_num(m):
                                nonlocal _changed_once
                                n = int(m.group(1))
                                if _changed_once:
                                    return m.group(0)
                                n2 = n + _seed2 if n >= 0 else n - _seed2
                                if n2 == 0:
                                    n2 = 1 if n > 0 else -1
                                if n2 != n:
                                    _changed_once = True
                                    return str(n2)
                                return m.group(0)

                            _expr2 = _num_pat.sub(_perturb_num, _expr_mirror, count=1)
                            if _changed_once and (r"\times" in _expr2):
                                _expr_final_fallback = _expr2
                                radical_fallback_single_mult_perturb_used = True
                                radical_fallback_single_mult_perturb_note = (
                                    f"single_mult_mirror_perturb:+/-{_seed2}"
                                )
                                detail_logs.append(
                                    "[ISO_GUARD][RADICAL_SINGLE_MULT_PERTURB][MIRROR_FALLBACK] "
                                    + radical_fallback_single_mult_perturb_note
                                )
                        _ans_fb = (
                            _chosen_exe_res.get("correct_answer", "")
                            if isinstance(_chosen_exe_res, dict)
                            else ""
                        )
                        _chosen_exe_res = {
                            "question_text": f"化簡 ${_expr_final_fallback}$。",
                            "correct_answer": _ans_fb,
                        }
                        _sync_answer_after_question_override(_chosen_exe_res, detail_logs)
                        detail_logs.append(
                            "[ISO_GUARD][RADICAL_FALLBACK_NORMALIZE] "
                            "retry unavailable/failed; used OCR-mirror fallback."
                        )

                    exe_res = _chosen_exe_res
                    _qt_final_fb = (
                        (exe_res.get("question_text") or "").strip()
                        if isinstance(exe_res, dict)
                        else ""
                    )
                    _expr_final_fb = extract_math_expr_from_question_fn(_qt_final_fb)
                    _qg_final_fb = evaluate_radical_quality_gate(
                        source_ocr_expr=ocr_text,
                        question_text=_qt_final_fb,
                        generated_expr=_expr_final_fb,
                    )
                    _final_reasons_fb = list(_qg_final_fb.get("reasons") or [])
                    radical_fallback_operator_lock_passed = (
                        "operator_lock_violation" not in _final_reasons_fb
                    )
                    radical_fallback_echo_guarded = (
                        "echo_violation" not in _final_reasons_fb
                    )
                if "question_text" in exe_res:
                    trace_seed_2 = {
                        "regex_code_fixes": regex_code_fixes,
                        "regex_display_fixes": regex_display_fixes,
                        "ast_fixes": ast_fixes,
                        "o1_fixes": o1_fixes,
                    }
                    sanitize_report2, trace_shadow_2 = sanitize_result_question_fn(
                        exe_res,
                        detail_logs=detail_logs,
                        after_fallback=True,
                        trace_seed=trace_seed_2,
                    )
                    regex_display_fixes = int(trace_shadow_2.get("regex_display_fixes", 0) or 0)
                    regex_fixes = int(trace_shadow_2.get("regex_fixes", 0) or 0)
                    sanitize_meta_2 = sanitize_report2 if isinstance(sanitize_report2, dict) else {}
                    double_paren_cnt_2 = int(sanitize_meta_2.get("double_paren_fixes", 0) or 0)
                    negative_wrap_cnt_2 = int(sanitize_meta_2.get("negative_wrap_fixes", 0) or 0)
                    if double_paren_cnt_2 > 0:
                        detail_logs.append(f"[DISPLAY_SANITIZE] collapsed {double_paren_cnt_2} nested numeric parenthesis pattern(s) after fallback.")
                    if negative_wrap_cnt_2 > 0:
                        detail_logs.append(f"[DISPLAY_SANITIZE] wrapped {negative_wrap_cnt_2} bare negative literal(s) after fallback.")
                append_fallback_switch_log_fn(detail_logs, decimal_mismatch)

                generated_expr_2 = extract_math_expr_from_question_fn(exe_res.get("question_text", ""))
                if "FourOperationsOfRadicals" in (skill_id or ""):
                    _qg_fb_final = evaluate_radical_quality_gate(
                        source_ocr_expr=ocr_text,
                        question_text=exe_res.get("question_text", ""),
                        generated_expr=generated_expr_2,
                    )
                    quality_gate_passed = bool(_qg_fb_final.get("passed", True))
                    quality_gate_reasons = list(_qg_fb_final.get("reasons") or [])
                    anti_echo_similarity = float(
                        _qg_fb_final.get("anti_echo_similarity", anti_echo_similarity) or 0.0
                    )
                _is_radical_skill = "FourOperationsOfRadicals" in (skill_id or "")
                _fallback_iso_ok = is_expression_isomorphic_fn(expected_fp, generated_expr_2)
                if not _fallback_iso_ok:
                    for d in profile_diff_summary_fn(expected_fp, generated_expr_2):
                        detail_logs.append(f"[ISO_GUARD][FALLBACK_FAIL] {d}")
                    if _is_radical_skill:
                        detail_logs.append(
                            "[ISO_GUARD][FALLBACK_FAIL][RADICAL_SOFT] keep fallback output "
                            "to avoid hard crash in radical orchestrator path."
                        )
                    else:
                        raise ValueError("ISO_GUARD fallback failed: generated structure still not isomorphic")

        generated_expr_final = extract_math_expr_from_question_fn(exe_res.get("question_text", ""))
        if (
            "FourOperationsOfRadicals" in (skill_id or "")
            and fallback_used
            and input_radical_style == "simple_radical"
            and (r"\times" in (ocr_text or ""))
        ):
            _qg_tail = evaluate_radical_quality_gate(
                source_ocr_expr=ocr_text,
                question_text=exe_res.get("question_text", ""),
                generated_expr=generated_expr_final,
            )
            _tail_reasons = list(_qg_tail.get("reasons") or [])
            if ("echo_violation" in _tail_reasons) or ("operator_lock_violation" in _tail_reasons):
                _nums_src = [int(x) for x in re.findall(r"-?\d+", (extract_math_expr_from_question_fn(ocr_text) or ocr_text or ""))]
                _forbid = {abs(n) for n in _nums_src}
                _roots = [7, 11, 13, 17, 19]
                _coefs = [2, 3, 4, 5, 6]
                _seed_tail = sum(ord(c) for c in (ocr_text or ""))

                def _pick_non_overlap(pool, start):
                    for i in range(len(pool)):
                        v = pool[(start + i) % len(pool)]
                        if v not in _forbid:
                            return v
                    return pool[start % len(pool)]

                _A = _pick_non_overlap(_roots, _seed_tail % len(_roots))
                _B = _pick_non_overlap(_coefs, (_seed_tail // 3) % len(_coefs))
                _C = _pick_non_overlap(_roots, (_seed_tail // 5) % len(_roots))
                if _C == _A:
                    _C = _pick_non_overlap(_roots, (_seed_tail // 7 + 1) % len(_roots))
                _expr_tail = f"\\sqrt{{{_A}}}\\times{_B}\\sqrt{{{_C}}}"
                exe_res["question_text"] = f"化簡 ${_expr_tail}$。"
                _sync_answer_after_question_override(exe_res, detail_logs)
                generated_expr_final = extract_math_expr_from_question_fn(exe_res.get("question_text", ""))
                radical_fallback_single_mult_template_used = True
                radical_fallback_single_mult_template_reason = "tail_enforce_after_fallback_qg"
                radical_fallback_token_delta_count = 3
                detail_logs.append(
                    "[ISO_GUARD][RADICAL_SINGLE_MULT_TEMPLATE][TAIL_ENFORCE] "
                    f"expr={_expr_tail!r} reasons={_tail_reasons!r}"
                )
        if "FourOperationsOfRadicals" in (skill_id or "") and not generated_expr_final.strip():
            if not isinstance(exe_res, dict):
                exe_res = {}
            exe_res["question_text"] = _build_radical_fallback_question_text(ocr_text)
            exe_res.setdefault("correct_answer", "")
            _sync_answer_after_question_override(exe_res, detail_logs)
            generated_expr_final = extract_math_expr_from_question_fn(exe_res.get("question_text", ""))
        print(f"[INFO] [PIPE] fallback_used={fallback_used}")
        _gen_final_120 = (generated_expr_final or "")[:120]
        print(f"[INFO] [PIPE] generated_expr={_gen_final_120!r} (final pre-profile)")

        # Radicals-only：複雜度鏡像 profile + 同構判斷（與 radical_reassemble 解耦，改以 skill_id gate）
        if "FourOperationsOfRadicals" in (skill_id or ""):
            from core.code_utils.live_show_math_utils import (
                build_radical_complexity_mirror_profile,
                radical_complexity_mirror_isomorphic,
            )

            generated_fp = build_radical_complexity_mirror_profile(generated_expr_final)
            iso_isomorphic = radical_complexity_mirror_isomorphic(
                expected_fp, generated_expr_final
            )
        else:
            generated_fp = build_structural_profile_fn(generated_expr_final)
            iso_isomorphic = is_expression_isomorphic_fn(expected_fp, generated_expr_final)
        recompute_result_answer_fn(
            exe_res,
            skill_id,
            recompute_answer_fn=recompute_correct_answer_from_question_fn,
            detail_logs=detail_logs,
            append_change_logs=True,
        )
        if isinstance(exe_res, dict):
            _template_direct_ans = exe_res.get("_answer_sync_template_direct")
            _cur_ans = exe_res.get("correct_answer")
            if _template_direct_ans and (str(_cur_ans).strip() in {"", "0", "0.0", "None"}):
                exe_res["correct_answer"] = _template_direct_ans
                detail_logs.append("[ANSWER_SYNC][TEMPLATE_DIRECT_RESTORE] recompute_overrode_to_zero")

        if "question_text" in exe_res:
            trace_seed_3 = {
                "regex_code_fixes": regex_code_fixes,
                "regex_display_fixes": regex_display_fixes,
                "ast_fixes": ast_fixes,
                "o1_fixes": o1_fixes,
            }
            _, trace_shadow_3 = format_result_question_display_fn(
                exe_res,
                skill_id,
                display_mode=fraction_display_mode,
                source_text=ocr_text,
                detail_logs=detail_logs,
                trace_seed=trace_seed_3,
            )
            regex_display_fixes = int(trace_shadow_3.get("regex_display_fixes", 0) or 0)
            regex_fixes = int(trace_shadow_3.get("regex_fixes", 0) or 0)

        if exe_res.get("_o1_healed"):
            trace_o1 = maybe_add_o1_fix_fn(
                exe_res,
                detail_logs=detail_logs,
                trace_seed={
                    "o1_fixes": o1_fixes,
                    "regex_code_fixes": regex_code_fixes,
                    "regex_display_fixes": regex_display_fixes,
                    "ast_fixes": ast_fixes,
                },
            )
            if isinstance(trace_o1, dict):
                o1_fixes = int(trace_o1.get("o1_fixes", o1_fixes) or o1_fixes)

        if (
            isinstance(exe_res, dict)
            and "error" not in exe_res
            and (exe_res.get("question_text") or "").strip()
            and not str(exe_res.get("correct_answer") or "").strip()
        ):
            try:
                _ab3_ans_final = recompute_correct_answer_from_question_fn(
                    exe_res.get("question_text", "")
                )
            except Exception:
                _ab3_ans_final = None
            if _ab3_ans_final is not None:
                exe_res["correct_answer"] = str(_ab3_ans_final)
                detail_logs.append("[ANSWER_SYNC] recomputed_non_empty_answer_before_response")

        ab3_exec_elapsed = time.time() - cpu_start_ab3

        try:
            from scripts.evaluate_mcri import evaluate_live_code

            if "question_text" in exe_res:
                # [Fix] Evaluate with api_stubs prepended so robustness detection
                # (class IntegerOps / FractionOps) is consistent with Ab2's evaluation.
                eval_code = (api_stubs + "\n\n" + healed_exec_code) if api_stubs else healed_exec_code
                _live_mcri = evaluate_live_code(
                    code=eval_code,
                    exec_result=exe_res,
                    healer_trace={"regex_fixes": regex_fixes, "ast_fixes": ast_fixes},
                    ablation_mode=False,
                )
                exe_res["_live_mcri"] = _live_mcri
                exe_res["_mcri_hygiene_score"] = _live_mcri["breakdown"].get("l4_3_hygiene", 15.0)
        except Exception:
            pass

        problems_result.append(exe_res)
    except Exception as e:
        ab3_exec_elapsed = time.time() - cpu_start_ab3
        problems_result.append({"error": f"執行錯誤: {e}"})

    save_dir = "generated_scripts"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir, exist_ok=True)
    unique_filename = f"live_show_{int(time.time())}_{uuid.uuid4().hex[:6]}.py"
    file_path = os.path.join(save_dir, unique_filename)
    _ab3_persist_code = _prepend_missing_runtime_stubs(
        healed_exec_code,
        skill_id,
        api_stubs,
    )
    _ab3_final_res = problems_result[-1] if problems_result and isinstance(problems_result[-1], dict) else {}
    _ab3_qt = str(_ab3_final_res.get("question_text") or "").strip()
    _ab3_ans = str(_ab3_final_res.get("correct_answer") or "").strip()
    _ab3_expr = extract_math_expr_from_question_fn(_ab3_qt) if _ab3_qt else ""
    _ab3_question_invalid = (
        (not _ab3_qt)
        or (_ab3_qt == "Error")
        or ("$" not in _ab3_qt)
        or (not str(_ab3_expr or "").strip())
    )
    if not _ab3_ans and _ab3_qt:
        try:
            _ab3_ans_recomputed = recompute_correct_answer_from_question_fn(_ab3_qt)
        except Exception:
            _ab3_ans_recomputed = None
        if _ab3_ans_recomputed is not None:
            _ab3_ans = str(_ab3_ans_recomputed)
    if (
        "FourOperationsOfRadicals" in (skill_id or "")
        and _ab3_qt
        and (_ab3_ans in {"", "0", "0.0"})
        and any(tok in _ab3_qt for tok in (r"\sqrt", r"\times", r"\div"))
    ):
        try:
            _ab3_ans_recomputed = recompute_correct_answer_from_question_fn(_ab3_qt)
        except Exception:
            _ab3_ans_recomputed = None
        if _ab3_ans_recomputed is not None and str(_ab3_ans_recomputed).strip():
            _ab3_ans = str(_ab3_ans_recomputed)

    # If radical flow needed fallback/normalization or final question is invalid,
    # prefer a runnable generator script so "next question" keeps producing new items.
    if "FourOperationsOfRadicals" in (skill_id or "") and (fallback_used or _ab3_question_invalid):
        _persisted = False

        def _is_valid_generator_code(_src: str) -> bool:
            if "def generate(" not in str(_src or ""):
                return False
            try:
                compile(str(_src), "<ab3_persist_candidate>", "exec")
                return True
            except Exception:
                return False

        # Priority 1: use random isomorphic radical generator to preserve next-question randomness.
        _pw_ab3_fallback = "計算" if str((_ab3_qt or _build_radical_fallback_question_text(ocr_text))).strip().startswith("計算") else "化簡"
        try:
            _rand_code = _build_randomized_radical_question_script(ocr_text, _pw_ab3_fallback)
        except Exception:
            _rand_code = ""
        if _rand_code and _is_valid_generator_code(_rand_code):
            _ab3_persist_code = _rand_code
            _persisted = True
            print("[INFO] [PIPE] ab3_persist_code switched to randomized radical generator.")

        # Priority 2: build a fresh deterministic isomorphic generator.
        if _persisted:
            _iso_code = ""
        else:
            _iso_code = ""
        try:
            if not _persisted:
                _iso_code = build_isomorphic_fallback_code_fn(ocr_text, skill_id=skill_id)
        except Exception:
            _iso_code = ""
        if _iso_code:
            _iso_code = optimize_live_execution_code_fn(_iso_code)
            _iso_code = patch_fraction_skill_eval_calls_fn(_iso_code, skill_id)
            _iso_code = re.sub(r"\beval\s*\(", "safe_eval(", _iso_code)
            _iso_code = _prepend_missing_runtime_stubs(_iso_code, skill_id, api_stubs)
            if _is_valid_generator_code(_iso_code):
                _ab3_persist_code = _iso_code
                _persisted = True
                print("[INFO] [PIPE] ab3_persist_code switched to isomorphic fallback generator.")

        # Priority 3: reuse Ab2 generator script if valid.
        if not _persisted:
            try:
                _ab2_fp = ""
                if isinstance(ab2_result, dict):
                    _ab2_fp = str(ab2_result.get("file_path") or "").strip()
                if _ab2_fp and os.path.exists(_ab2_fp):
                    with open(_ab2_fp, "r", encoding="utf-8") as _af:
                        _ab2_code = _af.read()
                    _ab2_code = _prepend_missing_runtime_stubs(_ab2_code, skill_id, api_stubs)
                    if _is_valid_generator_code(_ab2_code):
                        _ab3_persist_code = _ab2_code
                        _persisted = True
                        print("[INFO] [PIPE] ab3_persist_code switched to Ab2 generator for next-question continuity.")
            except Exception:
                _persisted = False

        # Priority 4: keep current Ab3 generator if valid; otherwise hard fallback.
        if (not _persisted) and (not _is_valid_generator_code(str(_ab3_persist_code or ""))):
            _qt_safe = _ab3_qt or _build_radical_fallback_question_text(ocr_text)
            if (
                (not _ab3_ans)
                or (
                    _ab3_ans in {"0", "0.0"}
                    and any(tok in _qt_safe for tok in (r"\sqrt", r"\times", r"\div"))
                )
            ):
                try:
                    _ans_safe = recompute_correct_answer_from_question_fn(_qt_safe) or ""
                except Exception:
                    _ans_safe = ""
            else:
                _ans_safe = _ab3_ans
            _pw_ab3 = "計算" if str(_qt_safe).strip().startswith("計算") else "化簡"
            _ab3_persist_code = _build_randomized_radical_question_script(ocr_text, _pw_ab3)

    with open(file_path, "w", encoding="utf-8") as _fb:
        _fb.write(_ab3_persist_code)

    try:
        live_file_display_mode[os.path.abspath(file_path)] = {
            "mode": fraction_display_mode,
            "skill_id": skill_id,
            "ocr_text": ocr_text,
            "sticky_problem": (
                str(_ab3_qt or "").strip()
                if "FourOperationsOfRadicals" in (skill_id or "")
                else ""
            ),
            "sticky_answer": (
                str(_ab3_ans or "").strip()
                if "FourOperationsOfRadicals" in (skill_id or "")
                else ""
            ),
        }
    except Exception:
        pass

    selected_pattern_id_after = extract_selected_pattern_id_from_code(healed_exec_code)
    selected_pattern_id = selected_pattern_id_after
    _gs = (pattern_guard_trace or {}).get("selected_pattern_id")
    _rej = (pattern_guard_trace or {}).get("reject_reason")
    if (
        _rej
        and _gs
        and _gs != "p1_add_sub"
        and selected_pattern_id_after == "p1_add_sub"
    ):
        print(
            f"[WARN] [PIPE] pattern_guard intended id={_gs!r} but final code still "
            f"p1_add_sub (regex patch likely missed pattern_id line)"
        )
        pattern_overwrite_reason = "pattern_guard_patch_failed"
        selected_pattern_id = _gs
    elif _rej:
        pattern_overwrite_reason = "pattern_guard"
    elif fallback_used:
        pattern_overwrite_reason = "iso_fallback_replaced_code"
    elif (
        pid_before_univ is not None
        and selected_pattern_id_after is not None
        and pid_before_univ != selected_pattern_id_after
    ):
        pattern_overwrite_reason = "pipeline_mutation"
    else:
        pattern_overwrite_reason = ""

    _patch_failed = bool(
        _rej
        and _gs
        and _gs != "p1_add_sub"
        and selected_pattern_id_after == "p1_add_sub"
    )
    pattern_overwritten = bool(
        _patch_failed
        or (
            pid_before_univ is not None
            and selected_pattern_id_after is not None
            and pid_before_univ != selected_pattern_id_after
        )
    )
    if pattern_overwritten:
        print(
            f"[WARN] [PIPE] pattern trace before_assemble={pid_before_univ!r} "
            f"after_code={selected_pattern_id_after!r} api_selected={selected_pattern_id!r} "
            f"overwrite_reason={pattern_overwrite_reason!r}"
        )

    _final_qt = ""
    if problems_result:
        _lr = problems_result[-1]
        if isinstance(_lr, dict):
            _final_qt = (_lr.get("question_text") or "").strip()

    if input_radical_style is None:
        output_radical_style = None
        style_preserved = True
        style_mismatch_reason = ""
    else:
        _ab3_meta = recompute_radical_style_fields_for_api(
            ocr_text,
            input_radical_style=input_radical_style,
            ab3_question_text=_final_qt,
            style_mismatch_after_retry_ab3=style_mismatch_after_retry,
        )
        input_radical_style = _ab3_meta["input_radical_style"]
        output_radical_style = _ab3_meta["output_radical_style"]
        style_preserved = _ab3_meta["style_preserved"]
        style_mismatch_reason = _ab3_meta["style_mismatch_reason"]

    return {
        "problems_result": problems_result,
        "cpu_execution_time_sec": ab3_exec_elapsed,
        "healed_code": healed_code,
        "healed_exec_code": healed_exec_code,
        "file_path": file_path,
        "regex_fixes": regex_fixes,
        "regex_code_fixes": regex_code_fixes,
        "regex_display_fixes": regex_display_fixes,
        "ast_fixes": ast_fixes,
        "o1_fixes": o1_fixes,
        "detail_logs": detail_logs,
        "generated_fp": generated_fp,
        "iso_isomorphic": iso_isomorphic,
        "iso_guard_triggered": iso_guard_triggered,
        "fallback_used": fallback_used,
        "selected_pattern_id": selected_pattern_id,
        "selected_pattern_id_before_assemble": pid_before_univ,
        "selected_pattern_id_after_assemble": selected_pattern_id_after,
        "pattern_overwritten": pattern_overwritten,
        "pattern_overwrite_reason": pattern_overwrite_reason,
        "healer_bypassed": healer_bypassed,
        "pattern_guard_trace": pattern_guard_trace,
        "input_radical_style": input_radical_style,
        "output_radical_style": output_radical_style,
        "style_preserved": style_preserved,
        "style_mismatch_reason": style_mismatch_reason,
        "style_gate_trace": style_gate_trace,
        "style_retry_used": style_retry_used,
        "style_mismatch_after_retry": style_mismatch_after_retry,
        "style_profile_vars_error": style_profile_vars_error,
        "style_output_exec_count": style_output_exec_count,
        "style_output_mismatch_history": style_output_mismatch_history,
        "quality_gate_passed": quality_gate_passed,
        "quality_gate_reasons": quality_gate_reasons,
        "anti_echo_retry_used": anti_echo_retry_used,
        "anti_echo_similarity": anti_echo_similarity,
        "exemplar_echo_hit": exemplar_echo_hit,
        "exemplar_echo_retry_used": exemplar_echo_retry_used,
        "radical_fallback_retry_used": radical_fallback_retry_used,
        "radical_fallback_retry_reason": radical_fallback_retry_reason,
        "radical_fallback_operator_lock_passed": radical_fallback_operator_lock_passed,
        "radical_fallback_echo_guarded": radical_fallback_echo_guarded,
        "radical_fallback_single_mult_perturb_used": radical_fallback_single_mult_perturb_used,
        "radical_fallback_single_mult_perturb_note": radical_fallback_single_mult_perturb_note,
        "radical_fallback_single_mult_template_used": radical_fallback_single_mult_template_used,
        "radical_fallback_single_mult_template_reason": radical_fallback_single_mult_template_reason,
        "radical_fallback_token_delta_count": radical_fallback_token_delta_count,
    }


def assemble_visual_output(
    *,
    problems_result,
    ai_inference_time_sec,
    cpu_execution_time_sec,
    raw_out,
    api_stubs,
    healed_code,
    file_path,
    system_prompt,
    json_spec,
    regex_fixes,
    regex_code_fixes,
    regex_display_fixes,
    ast_fixes,
    o1_fixes,
    detail_logs,
    expected_fp,
    generated_fp,
    iso_isomorphic,
    fraction_display_mode,
    ab2_result,
    selected_pattern_id=None,
    fallback_used=False,
    iso_guard_triggered=False,
    healer_bypassed=None,
    pattern_guard_trace=None,
    pattern_meta=None,
    style_meta=None,
    include_radical_style_fields: bool = True,
):
    _code_pid = extract_selected_pattern_id_from_code(api_stubs + "\n\n" + healed_code)
    _pgt = pattern_guard_trace if isinstance(pattern_guard_trace, dict) else {}
    _caller_pid = selected_pattern_id
    _gs = _pgt.get("selected_pattern_id")
    _rej = _pgt.get("reject_reason")
    if _rej and _gs and _gs != "p1_add_sub" and _code_pid == "p1_add_sub":
        _pid = _caller_pid if (_caller_pid and _caller_pid != "p1_add_sub") else _gs
        print(
            "[WARN] [PIPE] assemble_visual_output: healed code still p1_add_sub but "
            f"pattern_guard chose {_gs!r}; using selected_pattern_id={_pid!r} for debug_meta"
        )
    else:
        _pid = _code_pid if _code_pid else _caller_pid

    _pm = pattern_meta if isinstance(pattern_meta, dict) else {}
    _p_before = _pm.get("selected_pattern_id_before_assemble")
    _p_after = _pm.get("selected_pattern_id_after_assemble")
    _p_ow = bool(_pm.get("pattern_overwritten", False))
    _p_ow_r = _pm.get("pattern_overwrite_reason") or ""

    _sm = style_meta if isinstance(style_meta, dict) else {}

    _dm: dict[str, Any] = {
        "performance": {
            "ai_inference_time_sec": ai_inference_time_sec,
            "cpu_execution_time_sec": cpu_execution_time_sec,
        },
        "raw_code": raw_out,
        "final_code": api_stubs + "\n\n" + healed_code,
        "file_path": file_path,
        "bare_prompt": "",
        "scaffold_prompt": system_prompt,
        "architect_raw_spec": json.dumps(json_spec, ensure_ascii=False, indent=2) if json_spec else "",
        "gemini_raw_spec": json.dumps(json_spec, ensure_ascii=False, indent=2) if json_spec else "",
        "architect_model": "Qwen3-VL",
        "healer_trace": {
            "regex_fixes": regex_fixes,
            "regex_code_fixes": regex_code_fixes,
            "regex_display_fixes": regex_display_fixes,
            "ast_fixes": ast_fixes,
            "o1_fixes": o1_fixes,
        },
        "healer_logs": detail_logs if isinstance(detail_logs, list) else [],
        "iso_profile_expected": expected_fp,
        "iso_profile_generated": generated_fp,
        "iso_isomorphic": iso_isomorphic,
        "fraction_display_mode": fraction_display_mode,
        "selected_pattern_id": _pid,
        "selected_pattern_id_before_assemble": _p_before,
        "selected_pattern_id_after_assemble": _p_after,
        "pattern_overwritten": _p_ow,
        "pattern_overwrite_reason": _p_ow_r,
        "fallback_used": bool(fallback_used),
        "iso_guard_triggered": bool(iso_guard_triggered),
        "healer_bypassed": healer_bypassed,
        "detected_signals": _pgt.get("detected_signals", []),
        "candidate_patterns": _pgt.get("candidate_patterns", []),
        "reject_reason": _pgt.get("reject_reason"),
        "pattern_guard_trace": _pgt,
    }
    if include_radical_style_fields:
        _dm.update(
            {
                "input_radical_style": _sm.get("input_radical_style"),
                "output_radical_style": _sm.get("output_radical_style"),
                "style_preserved": _sm.get("style_preserved"),
                "style_mismatch_reason": _sm.get("style_mismatch_reason"),
                "selected_pattern_before_style_gate": _sm.get(
                    "selected_pattern_before_style_gate"
                ),
                "selected_pattern_after_style_gate": _sm.get(
                    "selected_pattern_after_style_gate"
                ),
                "style_gate_applied": _sm.get("style_gate_applied", False),
                "style_gate_reason": _sm.get("style_gate_reason"),
                "ab2_output_radical_style": _sm.get("ab2_output_radical_style"),
                "ab2_style_preserved": _sm.get("ab2_style_preserved"),
                "ab2_style_mismatch_reason": _sm.get("ab2_style_mismatch_reason"),
                "ab2_selected_pattern_before_style_gate": _sm.get(
                    "ab2_selected_pattern_before_style_gate"
                ),
                "ab2_selected_pattern_after_style_gate": _sm.get(
                    "ab2_selected_pattern_after_style_gate"
                ),
                "ab2_style_gate_applied": _sm.get("ab2_style_gate_applied", False),
                "ab2_style_gate_reason": _sm.get("ab2_style_gate_reason"),
                "style_retry_used": _sm.get("style_retry_used"),
                "style_mismatch_after_retry": _sm.get("style_mismatch_after_retry"),
                "style_profile_vars_error": _sm.get("style_profile_vars_error"),
                "style_output_exec_count": _sm.get("style_output_exec_count"),
                "style_output_mismatch_history": _sm.get("style_output_mismatch_history"),
                "ab2_style_output_exec_count": _sm.get("ab2_style_output_exec_count"),
                "ab2_style_output_mismatch_history": _sm.get(
                    "ab2_style_output_mismatch_history"
                ),
                "quality_gate_passed": _sm.get("quality_gate_passed"),
                "quality_gate_reasons": _sm.get("quality_gate_reasons"),
                "anti_echo_retry_used": _sm.get("anti_echo_retry_used"),
                "anti_echo_similarity": _sm.get("anti_echo_similarity"),
                "exemplar_echo_hit": _sm.get("exemplar_echo_hit"),
                "exemplar_echo_retry_used": _sm.get("exemplar_echo_retry_used"),
                "radical_fallback_retry_used": _sm.get("radical_fallback_retry_used"),
                "radical_fallback_retry_reason": _sm.get("radical_fallback_retry_reason"),
                "radical_fallback_operator_lock_passed": _sm.get(
                    "radical_fallback_operator_lock_passed"
                ),
                "radical_fallback_echo_guarded": _sm.get("radical_fallback_echo_guarded"),
            }
        )
    _dm["mcri_report"] = {
        "robustness_grade": "MODERATE",
        "robustness_reason": "Visual Generation with Full Healer",
    }

    return {
        "problems": problems_result,
        "debug_meta": _dm,
        "ab2_result": ab2_result,
    }
