# -*- coding: utf-8 -*-







"""







=============================================================================







?????? (Module Name): core/routes/analysis.py







?賹??方? (Description): AI ?????祇????荔????荒? AI ??鈭??? (Chat AI)?蹓??典??朱???蹓壇?蛛??蹌??祇??(Exam Analysis)?蹓選??選謓??拇?綜竣?????鞈玲?







????止等? (Usage): ?璇??舀０???







??秧?? (Version): V2.0







?皝??鈭? (Date): 2026-01-13







?砍?憸?謢? (Maintainer): Math AI Project Team







=============================================================================







"""















from flask import request, jsonify, render_template, current_app, url_for, session







from flask_login import current_user, login_required







from werkzeug.utils import secure_filename







import os
import base64
import re
import tempfile







import uuid







import traceback















from . import core_bp, practice_bp







from core.session import get_current







from core.ai_analyzer import (
    build_chat_prompt,
    get_chat_response,
    analyze,
    diagnose_error,
    diversify_follow_up_prompts,
    build_dynamic_follow_up_prompts_variant,
    clean_and_parse_json,
    enforce_strict_mode,
)
from core.ai_client import call_ai
from core.adaptive.judge import (
    judge_answer_with_feedback,
    _as_symbolic_tolerant,
    _normalize_math_text,
    _parse_quotient_remainder,
    _symbolic_equal,
    _extract_divisor_from_question,
)

from core.exam_analyzer import analyze_exam_image, save_analysis_result







from core.diagnosis_analyzer import perform_weakness_analysis







from core.rag_engine import rag_search, rag_chat







from models import db, MistakeNotebookEntry, ExamAnalysis, SkillInfo















ALLOWED_EXAM_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def _handwriting_not_recognized_response():
    """Missing image, invalid payload, unreadable OCR, or unusable expression ??do not run tutoring LLM."""
    return jsonify({"success": False, "reason": "handwriting_not_recognized"})


def _handwriting_expression_from_parsed(parsed):
    if not isinstance(parsed, dict):
        return ""
    v = parsed.get("expression")
    if v is None:
        v = parsed.get("transcribed_expression") or parsed.get("text")
    if v is None:
        return ""
    return str(v).strip()


def _handwriting_expression_is_usable(expr):
    if not expr:
        return False
    low = expr.lower().strip()
    bogus_exact = {
        "n/a", "na", "none", "null", "empty",
        "?", "??", "???",
        "no text", "unreadable", "illegible",
    }
    if low in bogus_exact or low in {".", "-", "?"}:
        return False
    if len(expr) <= 16 and (
        "unreadable" in low or "illegible" in low or "no text" in low
    ):
        return False
    mathish = set("+-*/=^()[]0123456789")
    if any((c in mathish or c.isdigit()) for c in expr):
        return True
    if any("a" <= c.lower() <= "z" for c in expr if c.isalpha()):
        return True
    if "\\" in expr or "$" in expr:
        return True
    if len(expr) >= 4 and any("\u4e00" <= c <= "\u9fff" for c in expr):
        return True
    return len(expr) >= 8


def _handwriting_expected_answer(data, state, question_text, question_context=""):
    """Resolve expected answer with strict priority:
    1) adaptive runtime current question correct_answer
    2) POST correct_answer
    3) answer parsed from question_context
    """

    def _extract_from_question_context(ctx):
        raw = str(ctx or "").strip()
        if not raw:
            return ""
        try:
            import json as _json
            obj = _json.loads(raw)
            if isinstance(obj, dict):
                for k in ("correct_answer", "expected_answer", "answer"):
                    v = str(obj.get(k) or "").strip()
                    if v:
                        return v
        except Exception:
            pass
        m = re.search(
            r"(?:正確答案|答案|correct_answer|expected_answer)\s*[:：=]\s*([^\n\r;；]+)",
            raw,
            flags=re.IGNORECASE,
        )
        if m:
            return m.group(1).strip().strip('"').strip("'")
        return ""

    sid = str(data.get("session_id") or state.get("session_id") or "").strip()
    qt = str(question_text or "").strip()
    store = session.get("adaptive_runtime") or {}

    # 1) session runtime current question correct_answer
    if isinstance(store, dict):
        if sid and isinstance(store.get(sid), dict):
            run = store.get(sid) or {}
            rq = str(run.get("question_text") or "").strip()
            ca = str(run.get("correct_answer") or "").strip()
            if ca and (not qt or not rq or rq == qt):
                return ca
        if qt:
            for _k, run in store.items():
                if not isinstance(run, dict):
                    continue
                rq = str(run.get("question_text") or "").strip()
                ca = str(run.get("correct_answer") or "").strip()
                if ca and rq == qt:
                    return ca

    # 2) POST correct_answer
    ca = str(data.get("correct_answer") or "").strip()
    if ca:
        return ca

    # 3) question_context answer
    return _extract_from_question_context(question_context)


def _handwriting_final_answer_candidates(expr):
    """Prefer last line / RHS of = as final answer when transcription has steps."""
    raw = (expr or "").strip()
    if not raw:
        return []
    chunks = []
    for part in re.split(r"[;\n\r]+", raw):
        p = part.strip()
        if not p:
            continue
        chunks.append(p)
        if "=" in p:
            rhs = p.split("=")[-1].strip()
            if rhs:
                chunks.append(rhs)
    if not chunks:
        return [raw]
    ordered = []
    seen = set()
    for c in reversed(chunks):
        key = c.lower()
        if key not in seen:
            seen.add(key)
            ordered.append(c)
    if raw.lower() not in seen:
        ordered.append(raw)
    return ordered


def _handwriting_pick_final_expression(expr):
    raw = str(expr or "").strip()
    if not raw:
        return ""
    parts = [p.strip() for p in re.split(r"[;\n\r]+", raw) if p.strip()]
    if not parts:
        return raw
    last = parts[-1]
    if "=" in last:
        rhs = last.split("=")[-1].strip()
        if rhs:
            return rhs
    return last


def _handwriting_skill_focus(family_id):
    fid = str(family_id or "").strip()
    by_id = {
        "F1": "同類項合併與符號整理",
        "F2": "去括號與負號分配，再合併同類項",
        "F3": "單項式對每一項完整分配",
        "F4": "運算順序與等值化簡",
        "F5": "多項式展開時每一項都要相乘",
        "F6": "公式辨識與正確套用",
        "F7": "逐項相除並保持次方規則",
        "F8": "商與餘式關係判斷",
        "F9": "長除法步驟與對齊",
        "F10": "反推除式與被除式關係",
        "F11": "混合式化簡與結果整理",
        "F12": "幾何公式代入與化簡",
        "F13": "複合情境建式與計算",
    }
    by_en = {
        "poly_add_sub_flat": "同類項合併與符號整理",
        "poly_add_sub_nested": "去括號與負號分配，再合併同類項",
        "poly_add_sub_unknown": "符號與同類項整理",
        "poly_mul_monomial": "單項式對每一項完整分配",
        "poly_mul_poly": "多項式展開時每一項都要相乘",
        "poly_mul_special_identity": "公式辨識與正確套用",
        "poly_div_monomial_eval": "逐項相除並保持次方規則",
        "poly_div_monomial_qr": "商與餘式關係判斷",
        "poly_div_poly_qr": "長除法步驟與對齊",
        "poly_div_reverse": "反推除式與被除式關係",
        "poly_mixed_simplify": "混合式化簡與結果整理",
        "poly_geom_formula_direct": "幾何公式代入與化簡",
        "poly_geom_region_composite": "複合情境建式與計算",
    }
    return by_id.get(fid) or by_en.get(fid) or ""


def _handwriting_expr_partially_close(user_segment, correct_answer):
    """True if sympy parses both and difference is a non-zero constant (typical small slip)."""
    try:
        from sympy import simplify

        su = _as_symbolic_tolerant(user_segment)
        sc = _as_symbolic_tolerant(correct_answer)
        if su is None or sc is None:
            return False
        diff = simplify(su - sc)
        if diff == 0:
            return False
        return not diff.free_symbols
    except Exception:
        return False


ERROR_MECHANISMS = (
    "structure_error",
    "sign_error",
    "combine_error",
    "operation_error",
    "substitution_error",
    "notation_error",
    "unknown",
)

ERROR_MECHANISM_FEEDBACK = {
    "structure_error": "前一步的結構轉換不正確，請先確認去括號或展開是否做對。",
    "sign_error": "正負號處理有誤，請再檢查負號如何分配到各項。",
    "combine_error": "同類項或常數項合併錯誤，請再檢查最後整理。",
    "operation_error": "運算規則使用有誤，請先確認這一步應用的運算關係。",
    "substitution_error": "代值或抄值可能有誤，請先核對代入的數值與位置。",
    "notation_error": "式子格式或記號不完整，請先補齊括號、變數與表示方式。",
    "unknown": "最後整理結果不正確，請再檢查最終答案。",
}

FAMILY_ERROR_PRIORITY = {
    "F1": ["sign_error", "combine_error", "notation_error", "unknown"],
    "poly_add_sub_flat": ["sign_error", "combine_error", "notation_error", "unknown"],
    "F2": ["structure_error", "sign_error", "combine_error", "unknown"],
    "poly_add_sub_nested": ["structure_error", "sign_error", "combine_error", "unknown"],
    "F3": ["structure_error", "combine_error", "notation_error", "unknown"],
    "poly_add_sub_unknown": ["structure_error", "combine_error", "notation_error", "unknown"],
    "F4": ["operation_error", "sign_error", "combine_error", "unknown"],
    "poly_mul_monomial": ["operation_error", "sign_error", "combine_error", "unknown"],
    "F5": ["structure_error", "operation_error", "sign_error", "combine_error", "unknown"],
    "poly_mul_poly": ["structure_error", "operation_error", "sign_error", "combine_error", "unknown"],
    "F9": ["structure_error", "sign_error", "operation_error", "notation_error", "unknown"],
    "poly_div_poly_qr": ["structure_error", "sign_error", "operation_error", "notation_error", "unknown"],
}

F9_ERROR_MAIN_ISSUE = {
    "structure_error": "長除法各列的對齊與次序關係不清楚，請先釐清商、乘回、相減三種列。",
    "sign_error": "相減時整行變號有誤，請逐項檢查正負。",
    "operation_error": "乘回除式或上下相減的規則有誤，請對照每一步係數。",
    "notation_error": "長除法書寫不完整，請補齊商與餘數的標示。",
}

_F9_TUTOR_ROWS = (
    # (mechanism, step_focus or "" for default, hint_focus, guided_question, micro_step)
    ("structure_error", "subtract_row_1", "對齊相減後各列", "次方直欄是否對齊？", "缺項可補零再減"),
    ("structure_error", "quotient_term_1", "對齊商與被除式", "第一次商對到哪一階項？", "先寫第一次商"),
    ("structure_error", "final_remainder", "最後一列要對齊", "餘式與除式次方？", "確認最底行寫完"),
    ("structure_error", "", "長除法列要對齊", "商、乘回、相減順序？", "由上到下逐步核對"),
    ("sign_error", "final_remainder", "相減後餘項變號", "最底行每項符號？", "整行相減逐項改"),
    ("sign_error", "subtract_row_1", "相減要逐項變號", "這列減上列每項？", "先改符號再加"),
    ("sign_error", "", "相減逐項變號", "上下相減有漏負？", "整行取反再相加"),
    ("operation_error", "final_remainder", "最後餘數要檢查", "餘式還能再除？", "看餘式次方"),
    ("operation_error", "quotient_term_2", "下一項商核對", "降次後再除一次？", "對齊再取下一商"),
    ("operation_error", "subtract_row_2", "第二次相減核對", "乘回列是否完整？", "先乘回再相減"),
    ("operation_error", "quotient_term_1", "第一次相除核對", "首項除以除式首項？", "只決定第一項商"),
    ("operation_error", "", "乘回與相減規則", "商的每項都乘除式？", "一步一步寫乘回"),
    ("notation_error", "final_remainder", "餘數要寫清楚", "最後有沒有標餘？", "用商餘格式彙整"),
    ("notation_error", "", "長除法書寫", "商與餘數標示？", "依題目格式整理"),
)


def _f9_long_division_layout_heuristic(expr: object) -> bool:
    """True when OCR-flattened work still looks like polynomial long division (not a single line)."""
    raw = str(expr or "").strip()
    if not raw:
        return False
    parts = [p.strip() for p in re.split(r"[;\n\r]+", raw) if p.strip()]
    if len(parts) >= 3:
        return True
    if raw.count(";") >= 2:
        return True
    if ")" in raw and len(parts) >= 2:
        return True
    if "..." in raw or "…" in raw:
        return True
    return False


def _f9_find_student_quotient_remainder(parts: list[str]):
    """Best-effort QR parse from semicolon-separated OCR lines (single segment only)."""
    for p in reversed(parts):
        qr = _parse_quotient_remainder(p)
        if qr:
            return qr
    joined = " ".join(parts)
    return _parse_quotient_remainder(joined)


def _f9_remainder_is_sign_flip(ur: str, cr: str) -> bool:
    try:
        from sympy import simplify

        su = _as_symbolic_tolerant(ur)
        sc = _as_symbolic_tolerant(cr)
        if su is None or sc is None:
            return False
        return simplify(su + sc) == 0
    except Exception:
        return False


def _f9_default_step_focus(parts: list[str]) -> str:
    n = len(parts)
    if n >= 5:
        return "subtract_row_1"
    if n >= 3:
        return "quotient_term_1"
    return ""


def analyze_polynomial_long_division_layout(
    recognized_expression: object,
    expected_answer: object,
    question_text: object,
) -> dict:
    """
    Rule-based F9 / poly_div_poly_qr layout analysis. Does not call LLMs.
    Returns error_mechanism, main_issue, step_focus for merging into structured_analysis.
    """
    rec = str(recognized_expression or "").strip()
    exp = str(expected_answer or "").strip()
    parts = [p.strip() for p in re.split(r"[;\n\r]+", rec) if p.strip()]

    def pack(mech: str, step: str) -> dict:
        return {
            "error_mechanism": mech,
            "main_issue": F9_ERROR_MAIN_ISSUE.get(mech, ERROR_MECHANISM_FEEDBACK.get(mech, "")),
            "step_focus": step,
        }

    exp_qr = _parse_quotient_remainder(exp)
    st_qr = _f9_find_student_quotient_remainder(parts) if parts else _parse_quotient_remainder(rec)

    # No expected QR: still avoid blanket notation_error when multiline layout exists.
    if not exp_qr:
        if len(parts) >= 3:
            return pack("structure_error", _f9_default_step_focus(parts))
        if len(parts) >= 2:
            return pack("structure_error", "quotient_term_1")
        return pack("notation_error", "")

    cq, cr = exp_qr

    if st_qr:
        uq, ur = st_qr
        q_ok = _symbolic_equal(uq, cq)
        r_ok = _symbolic_equal(ur, cr)
        if q_ok and r_ok:
            return {
                "error_mechanism": "structure_error",
                "main_issue": "長除法演算與最後答案欄位對應不一致，請確認分號後最後一行是否為完整商餘格式。",
                "step_focus": "final_remainder",
            }

        q_step = "quotient_term_2" if len(parts) >= 5 else "quotient_term_1"
        if not q_ok and r_ok:
            return pack("operation_error", q_step)
        if q_ok and not r_ok:
            if _f9_remainder_is_sign_flip(ur, cr):
                return pack("sign_error", "final_remainder")
            return pack("operation_error", "final_remainder")
        # both differ: prefer structure when many rows (OCR layout noise), else operation
        if len(parts) >= 4:
            return pack("structure_error", "subtract_row_1")
        return pack("operation_error", q_step)

    # Multiline work but final answer not in QR — treat as layout / step trace issue first.
    if len(parts) >= 3:
        return pack("structure_error", _f9_default_step_focus(parts))
    if len(parts) == 2:
        return pack("structure_error", "quotient_term_1")

    # Single blob: try labeled divisor row hint
    div_hint = _extract_divisor_from_question(question_text)
    if div_hint and div_hint.replace(" ", "") and parts:
        row0 = parts[0].replace(" ", "")
        if div_hint.replace(" ", "") in row0:
            return pack("structure_error", "quotient_term_1")

    return pack("notation_error", "")


def _f9_tutor_guidance_pick(error_mechanism: str, step_focus: str):
    mech = str(error_mechanism or "").strip()
    step = str(step_focus or "").strip()
    for m, s, h, g, ms in _F9_TUTOR_ROWS:
        if m == mech and s == step:
            return h, g, ms
    for m, s, h, g, ms in _F9_TUTOR_ROWS:
        if m == mech and s == "":
            return h, g, ms
    return None


def _handwriting_has_unflipped_negative_parenthesis(question_text, user_segment):
    """Detect F2-specific mistake: '-(...)' kept original inner signs in student's expansion."""
    q = re.sub(r"\s+", "", str(question_text or "")).lower()
    u = re.sub(r"\s+", "", str(user_segment or "")).lower()
    if not q or not u:
        return False
    inners = re.findall(r"-\(([^()]+)\)", q)
    if not inners:
        return False
    for inner in inners:
        inner_clean = re.sub(r"\s+", "", inner).lower()
        if not inner_clean:
            continue
        # Student still keeps original inner term direction (e.g. -x+1) in work line.
        if inner_clean in u:
            return True
    return False


def _handwriting_infer_error_mechanism(user_segment, expected_answer, family_id, question_text=""):
    fid = str(family_id or "").strip()
    priorities = FAMILY_ERROR_PRIORITY.get(fid, ["sign_error", "combine_error", "unknown"])
    detected = set()

    # F2: highest-value deterministic structure/sign check.
    if fid in ("F2", "poly_add_sub_nested"):
        if _handwriting_has_unflipped_negative_parenthesis(question_text, user_segment):
            detected.add("structure_error")
            detected.add("sign_error")

    try:
        from sympy import Symbol, degree, expand, simplify, Poly

        x = Symbol("x")
        su = _as_symbolic_tolerant(user_segment)
        sc = _as_symbolic_tolerant(expected_answer)
        if su is None or sc is None:
            for mech in priorities:
                if mech in detected:
                    return mech
            return "notation_error"
        eu = expand(su)
        ec = expand(sc)
        diff = simplify(eu - ec)
        if diff == 0:
            return ""

        if ec.has(x):
            deg_c = int(degree(ec, x))
            deg_u = int(degree(eu, x)) if eu != 0 else -1
            if fid in ("F4", "poly_mul_monomial", "F5", "poly_mul_poly"):
                if deg_c > 0 and 0 <= deg_u < deg_c:
                    detected.add("operation_error")
                if deg_c > 0 and deg_u > deg_c:
                    detected.add("structure_error")

            try:
                pc = Poly(ec, x)
                pu = Poly(eu, x)
                exp_coeff = {int(k[0]): v for k, v in pc.as_dict().items()}
                usr_coeff = {int(k[0]): v for k, v in pu.as_dict().items()}
                if set(exp_coeff.keys()) != set(usr_coeff.keys()):
                    detected.add("structure_error")
                else:
                    # same term degrees but coefficients differ -> combine/sign
                    coeff_mismatch = any(exp_coeff[d] != usr_coeff[d] for d in exp_coeff.keys())
                    if coeff_mismatch:
                        detected.add("combine_error")
            except Exception:
                detected.add("notation_error")

        # Simple sign heuristic if expression contains opposite-signed counterpart.
        n_user = re.sub(r"\s+", "", str(user_segment or ""))
        n_exp = re.sub(r"\s+", "", str(expected_answer or ""))
        if ("-" in n_exp or "-(" in n_exp) and ("-" in n_user or "-(" in n_user):
            if n_user.startswith("-") != n_exp.startswith("-"):
                detected.add("sign_error")

        q = str(question_text or "")
        if re.search(r"[a-zA-Z]\s*=", q) and re.search(r"\d", str(user_segment or "")):
            detected.add("substitution_error")

        # F2/F5 additional structure preference when mechanism still ambiguous.
        if fid in ("F2", "poly_add_sub_nested") and "combine_error" in detected and "sign_error" in detected:
            detected.add("structure_error")
        if fid in ("F5", "poly_mul_poly") and "structure_error" in detected:
            detected.add("operation_error")
    except Exception:
        detected.add("unknown")

    for mech in priorities:
        if mech in detected:
            return mech
    return "unknown"


_POLY_REFINE_TARGET_FAMILIES = frozenset(
    {
        "F1",
        "F2",
        "F11",
        "poly_add_sub_flat",
        "poly_add_sub_nested",
        "poly_mixed_simplify",
    }
)


def _poly_refine_poly_in_x(expr: object):
    """Return sympy Poly in x, or None."""
    try:
        from sympy import Poly, Symbol, expand

        x = Symbol("x")
        su = _as_symbolic_tolerant(expr)
        if su is None:
            return None
        return Poly(expand(su), x)
    except Exception:
        return None


def _poly_refine_degree_coeff_dict(poly) -> dict | None:
    if poly is None:
        return None
    try:
        return {int(k[0]): v for k, v in poly.as_dict().items()}
    except Exception:
        return None


def _poly_refine_expr_has_x(expr: object) -> bool:
    try:
        from sympy import Symbol, expand

        x = Symbol("x")
        su = _as_symbolic_tolerant(expr)
        if su is not None:
            return expand(su).has(x)
    except Exception:
        pass
    return "x" in _normalize_math_text(expr)


def _poly_refine_expected_has_no_x(expected_answer: object) -> bool:
    try:
        from sympy import Symbol, expand

        x = Symbol("x")
        se = _as_symbolic_tolerant(expected_answer)
        if se is not None:
            return not expand(se).has(x)
    except Exception:
        pass
    return "x" not in _normalize_math_text(expected_answer)


def _question_has_opposite_linear_x_terms(question_text: object) -> bool:
    """True when question text shows at least one pair of x-terms that can cancel (e.g. 6x and -6x)."""
    t = _normalize_math_text(question_text)
    if "x" not in t:
        return False
    # _normalize_math_text inserts implicit '*' (6x -> 6*x); allow optional * before x
    pairs = re.findall(r"([+-]?)(\d*)\*?x", t)
    coeffs: list[int] = []
    for sign, digs in pairs:
        v = int(digs) if digs else 1
        if sign == "-":
            v = -v
        coeffs.append(v)
    if len(coeffs) < 2:
        return False
    for i in range(len(coeffs)):
        for j in range(i + 1, len(coeffs)):
            if coeffs[i] + coeffs[j] == 0:
                return True
    return False


def _poly_refine_global_sign_flip(user_txt: object, exp_txt: object) -> bool:
    try:
        from sympy import expand, simplify

        su = _as_symbolic_tolerant(user_txt)
        se = _as_symbolic_tolerant(exp_txt)
        if su is None or se is None:
            return False
        return simplify(expand(su) + expand(se)) == 0
    except Exception:
        return False


def _poly_refine_all_coeffs_negated(d_exp: dict, d_usr: dict) -> bool:
    if not d_exp or set(d_exp) != set(d_usr):
        return False
    try:
        from sympy import simplify

        for d in d_exp:
            if simplify(d_usr[d] + d_exp[d]) != 0:
                return False
        return True
    except Exception:
        return False


def _f11_question_suggests_expansion(question_text: object) -> bool:
    qt = str(question_text or "")
    if "(" in qt or ")" in qt:
        return True
    t = _normalize_math_text(qt)
    return "^2" in t or "²" in qt or "**2" in t


def _refine_polynomial_unknown_mechanism(
    family_id,
    recognized_expression,
    final_expression,
    expected_answer,
    question_text,
):
    """
    When generic handwriting inference yields unknown, narrow F1/F2/F11 errors using
    deterministic checks on expressions and question text (no LLM).
    Returns dict with error_mechanism, main_issue, step_focus or None.
    """
    fid = str(family_id or "").strip()
    if fid not in _POLY_REFINE_TARGET_FAMILIES:
        return None

    rec = str(recognized_expression or "").strip()
    fin = str(final_expression or "").strip()
    exp = str(expected_answer or "").strip()
    qt = str(question_text or "").strip()

    if not exp:
        return None

    d_exp = _poly_refine_degree_coeff_dict(_poly_refine_poly_in_x(exp))
    d_fin = _poly_refine_degree_coeff_dict(_poly_refine_poly_in_x(fin))
    d_rec = _poly_refine_degree_coeff_dict(_poly_refine_poly_in_x(rec))

    # Prefer final line for "student answer" structure checks; fall back to full OCR.
    d_usr = d_fin if d_fin is not None else d_rec

    if fid in ("F1", "poly_add_sub_flat"):
        # A1: constant expected but work still shows x, and question has cancellable x-terms
        if (
            _poly_refine_expected_has_no_x(exp)
            and (_poly_refine_expr_has_x(fin) or _poly_refine_expr_has_x(rec))
            and _question_has_opposite_linear_x_terms(qt)
        ):
            return {
                "error_mechanism": "combine_error",
                "step_focus": "like_terms",
                "main_issue": "同類項合併錯誤，請先檢查可互相抵消的項是否已正確消去。",
            }
        # A2: same set of term degrees but wrong coefficients -> combine
        if (
            d_exp is not None
            and d_usr is not None
            and set(d_exp) == set(d_usr)
            and d_exp
            and not _poly_refine_all_coeffs_negated(d_exp, d_usr)
            and any(d_exp[k] != d_usr[k] for k in d_exp)
        ):
            return {
                "error_mechanism": "combine_error",
                "step_focus": "like_terms",
                "main_issue": "同類項合併錯誤，請再檢查可合併項的係數加減。",
            }

    if fid in ("F2", "poly_add_sub_nested"):
        if "(" not in qt and ")" not in qt:
            return None
        # B2: missing term degrees after expansion vs expected
        if (
            d_exp is not None
            and d_usr is not None
            and set(d_usr) < set(d_exp)
            and set(d_exp)
        ):
            return {
                "error_mechanism": "structure_error",
                "step_focus": "bracket_scope",
                "main_issue": "去括號或重寫式子的結構有誤，請先確認每一項是否都有正確保留下來。",
            }
        # B1: sign distribution / global flip
        if _handwriting_has_unflipped_negative_parenthesis(qt, rec) or _handwriting_has_unflipped_negative_parenthesis(
            qt, fin
        ):
            return {
                "error_mechanism": "sign_error",
                "step_focus": "sign_distribution",
                "main_issue": "去括號時的正負號處理有誤，請檢查括號前符號是否正確分配到每一項。",
            }
        chk_u, chk_e = (fin or rec), exp
        if _poly_refine_global_sign_flip(chk_u, chk_e):
            return {
                "error_mechanism": "sign_error",
                "step_focus": "sign_distribution",
                "main_issue": "去括號時的正負號處理有誤，請檢查括號前符號是否正確分配到每一項。",
            }
        if (
            d_exp is not None
            and d_usr is not None
            and set(d_exp) == set(d_usr)
            and d_exp
            and _poly_refine_all_coeffs_negated(d_exp, d_usr)
        ):
            return {
                "error_mechanism": "sign_error",
                "step_focus": "sign_distribution",
                "main_issue": "去括號時的正負號處理有誤，請檢查括號前符號是否正確分配到每一項。",
            }

    if fid in ("F11", "poly_mixed_simplify"):
        # C2: expansion context but student polynomial is missing expected degrees
        if (
            _f11_question_suggests_expansion(qt)
            and d_exp is not None
            and d_usr is not None
            and set(d_usr) < set(d_exp)
            and set(d_exp)
        ):
            return {
                "error_mechanism": "structure_error",
                "step_focus": "expansion_structure",
                "main_issue": "展開或重寫式子的結構有誤，請先確認每個括號中的項是否都有正確處理。",
            }
        # C1: same term structure, coefficient merge wrong
        if (
            d_exp is not None
            and d_usr is not None
            and set(d_exp) == set(d_usr)
            and d_exp
            and not _poly_refine_all_coeffs_negated(d_exp, d_usr)
            and any(d_exp[k] != d_usr[k] for k in d_exp)
        ):
            return {
                "error_mechanism": "combine_error",
                "step_focus": "simplify_combine",
                "main_issue": "展開後的同類項整理有誤，請重新檢查哪些項可以合併。",
            }
        # C3: sign flip on matched terms
        if (
            d_exp is not None
            and d_usr is not None
            and set(d_exp) == set(d_usr)
            and d_exp
            and _poly_refine_all_coeffs_negated(d_exp, d_usr)
        ):
            return {
                "error_mechanism": "sign_error",
                "step_focus": "expansion_sign",
                "main_issue": "展開後的正負號處理有誤，請重新檢查負號或減號是否有正確套用到各項。",
            }
        if _poly_refine_global_sign_flip(fin or rec, exp):
            return {
                "error_mechanism": "sign_error",
                "step_focus": "expansion_sign",
                "main_issue": "展開後的正負號處理有誤，請重新檢查負號或減號是否有正確套用到各項。",
            }

    return None


def _handwriting_structured_analysis(recognized_expression, expected_answer, question_text, family_id):
    exp = (expected_answer or "").strip()
    qt = (question_text or "").strip()
    skill_focus = _handwriting_skill_focus(family_id)
    family_label_zh, family_description_zh = _handwriting_family_meta(family_id)
    final_expr = _handwriting_pick_final_expression(recognized_expression)
    base = {
        "recognized_expression": recognized_expression,
        "final_expression": final_expr,
        "expected_answer": exp,
        "is_correct": False,
        "status": "unknown",
        "main_issue": "",
        "skill_focus": skill_focus,
        "issue_tag": "",
        "error_mechanism": "unknown",
        "family_id": family_id or "",
        "family_label_zh": family_label_zh,
        "family_description_zh": family_description_zh,
        "step_focus": "",
        "analysis_source": "generic_handwriting_analysis",
    }
    if not exp:
        base["main_issue"] = "目前缺少可對照的標準答案，無法完成穩定批改。"
        base["skill_focus"] = skill_focus or "依題目重點進行化簡與整理"
        base["analysis_source"] = "generic_handwriting_analysis"
        return base

    candidates = [final_expr] if final_expr else []
    if not candidates:
        candidates = _handwriting_final_answer_candidates(recognized_expression)
    if not candidates:
        candidates = [str(recognized_expression).strip()]

    for cand in candidates:
        judged = judge_answer_with_feedback(
            cand, exp, question_text=qt, family_id=family_id
        )
        if judged.get("is_correct"):
            base.update(
                {
                    "is_correct": True,
                    "status": "correct",
                    "main_issue": "",
                    "skill_focus": skill_focus or "你已掌握本題重點",
                    "issue_tag": "",
                    "error_mechanism": "unknown",
                    "step_focus": "",
                    "analysis_source": "generic_handwriting_analysis",
                }
            )
            return base

    primary = candidates[0]
    status = "incorrect"
    main_issue = (
        "這題有錯，請先對照題目關鍵步驟再整理一次。"
    )
    if _handwriting_expr_partially_close(primary, exp):
        status = "partially_correct"
        main_issue = (
            "方向正確，但有一個關鍵小錯需要修正。"
        )

    mechanism = ""
    step_focus = ""
    analysis_src = "generic_handwriting_analysis"
    fid = str(family_id or "").strip()
    ua_full = str(recognized_expression or "").strip()
    if status in ("incorrect", "partially_correct"):
        if fid in ("F9", "poly_div_poly_qr") and _f9_long_division_layout_heuristic(ua_full):
            f9_res = analyze_polynomial_long_division_layout(ua_full, exp, qt)
            mechanism = f9_res.get("error_mechanism") or "notation_error"
            main_issue = f9_res.get("main_issue") or ERROR_MECHANISM_FEEDBACK.get(
                mechanism, ERROR_MECHANISM_FEEDBACK["unknown"]
            )
            step_focus = str(f9_res.get("step_focus") or "")
            analysis_src = "f9_layout_heuristic"
        else:
            mechanism = _handwriting_infer_error_mechanism(
                primary, exp, family_id, question_text=qt
            )
            main_issue = ERROR_MECHANISM_FEEDBACK.get(
                mechanism, ERROR_MECHANISM_FEEDBACK["unknown"]
            )

        if str(mechanism or "").strip() == "unknown" and status in (
            "incorrect",
            "partially_correct",
        ):
            refined = _refine_polynomial_unknown_mechanism(
                fid, ua_full, final_expr, exp, qt
            )
            if refined:
                mechanism = refined["error_mechanism"]
                main_issue = refined["main_issue"]
                step_focus = str(refined.get("step_focus") or "")

    base.update(
        {
            "is_correct": False,
            "status": status,
            "main_issue": main_issue,
            "skill_focus": skill_focus or "憭?撘?蝪∟???",
            "issue_tag": mechanism,
            "error_mechanism": mechanism,
            "step_focus": step_focus,
            "analysis_source": analysis_src,
        }
    )
    return base


def _handwriting_family_meta(family_id):
    fid = str(family_id or "").strip()
    alias = {
        "poly_add_sub_basic": "F1",
        "poly_add_sub_nested": "F2",
        "poly_mul_monomial": "F3",
        "poly_mul_poly": "F5",
        "poly_div_monomial": "F11",
        "poly_div_poly_qr": "F9",
    }
    fid = alias.get(fid, fid)
    mapping = {
        "F1": ("多項式加減", "同類項合併與符號整理"),
        "F2": ("巢狀多項式加減", "先處理括號與符號，再合併同類項"),
        "F3": ("多項式乘以單項式", "分配律與係數次方正確分配"),
        "F5": ("多項式乘法展開", "每一項都要完整分配相乘"),
        "F9": ("多項式長除法（商餘）", "長除法對齊、乘回與相減"),
        "F11": ("多項式綜合化簡", "包含展開、乘法公式與同類項合併的混合型化簡"),
    }
    return mapping.get(fid, ("多項式題", "依題意完成整理、化簡與等值轉換"))


def _handwriting_sentence_count(reply):
    parts = re.split(r"[。！？!?]+|\n+", str(reply or ""))
    return len([p.strip() for p in parts if p.strip()])


def _handwriting_reply_is_compliant(reply, status):
    text = str(reply or "").strip()
    if not text:
        return False
    if _handwriting_sentence_count(text) > 3:
        return False

    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    first_line = lines[0] if lines else text
    tail_line = lines[-1] if lines else text
    st = str(status or "unknown").strip()

    if st == "correct":
        if "答案正確" not in first_line:
            return False
        if "進入下一題" not in tail_line:
            return False
    elif st == "partially_correct":
        if "方向正確" not in first_line or "關鍵小錯" not in first_line:
            return False
        if "請再檢查一次" not in tail_line:
            return False
    elif st == "incorrect":
        if "這題有錯" not in first_line:
            return False
        if "想一下再試一次" not in tail_line:
            return False
        banned = (
            "檢查一下",
            "再看看",
            "檢查運算順序",
            "注意運算順序",
            "檢查係數與符號",
            "檢查括號是否正確",
        )
        if any(b in text for b in banned):
            return False
    elif st == "unknown":
        if "無法穩定判斷" not in text:
            return False
    return True


def _handwriting_feedback_second_prompt(
    analysis_result,
    question_text,
    question_context,
    prereq_text,
    family_id,
):
    status = str((analysis_result or {}).get("status") or "unknown")
    question = (question_text or question_context or "").strip()
    student_expression = (analysis_result or {}).get("recognized_expression") or ""
    expected_answer = (analysis_result or {}).get("expected_answer") or ""
    family_description_zh = (analysis_result or {}).get("family_description_zh") or (prereq_text or "")
    main_issue = (analysis_result or {}).get("main_issue") or ""
    error_mechanism = (analysis_result or {}).get("error_mechanism") or ""
    return (
        "你是國中數學評量系統的批改回饋模組，不是解題老師。\n\n"
        "你只根據以下資訊，產生非常短的批改回饋：\n\n"
        f"題目：{question}\n"
        f"學生手寫結果：{student_expression}\n"
        f"正確答案：{expected_answer}\n"
        f"判定狀態：{status}\n"
        f"本題重點：{family_description_zh}\n"
        f"錯誤機制：{error_mechanism}\n"
        f"已知錯誤重點：{main_issue}\n\n"
        "請嚴格遵守：\n"
        "1. 如果 status = correct：\n"
        "- 第一行一定要說「答案正確」\n"
        "- 最後一行一定要說「進入下一題」\n"
        "- 不要解題\n"
        "- 不要長篇說明\n"
        "2. 如果 status = partially_correct：\n"
        "- 第一行說「方向正確，但有一個關鍵小錯」\n"
        "- 只指出一個最重要的錯誤\n"
        "- 最後一行說「請再檢查一次」\n"
        "3. 如果 status = incorrect：\n"
        "- 第一行直接說「這題有錯」\n"
        "- 只指出一個最核心錯誤\n"
        "- 優先使用提供的「已知錯誤重點」\n"
        "- 禁止說：請檢查、再看看、計算方向大致正確、檢查運算順序、檢查係數與符號\n"
        "- 最後一行說「想一下再試一次」\n"
        "4. 回答最多 3 行\n"
        "5. 不要解完整題目\n"
        "6. 不要聊天\n"
        "7. 語氣像老師批改，不像聊天機器人\n\n"
        "只輸出 JSON（不要 markdown、不要多餘文字），格式固定為："
        "{\"reply\":\"...\",\"is_process_correct\":true/false,\"correct\":true/false,"
        "\"next_question\":\"\",\"follow_up_prompts\":[],"
        "\"error_type\":\"handwriting_ok|handwriting_partial|handwriting_wrong|handwriting_unknown\"}。"
    )


def _handwriting_rule_based_reply(analysis_result):
    """Primary short feedback generator for production handwriting flow."""
    st = analysis_result.get("status")
    mech = str(analysis_result.get("error_mechanism") or "").strip()
    issue = ERROR_MECHANISM_FEEDBACK.get(
        mech, str(analysis_result.get("main_issue") or "").strip() or ERROR_MECHANISM_FEEDBACK["unknown"]
    )
    if st == "correct":
        return "✔ 答案正確！\n👉 進入下一題"
    if st == "partially_correct":
        return f"⚠️ 方向正確，但還有一個關鍵小錯\n{issue}\n👉 請再檢查一次"
    if st == "incorrect":
        return f"✘ 這題有錯\n{issue}\n👉 想一下再試一次"
    return "目前我無法穩定判斷你的手寫結果，請確認筆跡清楚或再試一次。"


def _handwriting_issue_is_clear(analysis_result):
    mechanism = str((analysis_result or {}).get("error_mechanism") or "").strip()
    if mechanism in ERROR_MECHANISMS:
        return True
    issue_tag = str((analysis_result or {}).get("issue_tag") or "").strip()
    main_issue = str((analysis_result or {}).get("main_issue") or "").strip()
    if issue_tag:
        return True
    if len(main_issue) < 10:
        return False
    generic = (
        "請檢查",
        "再看看",
        "注意運算順序",
        "檢查係數",
        "檢查符號",
    )
    return not any(g in main_issue for g in generic)


TUTOR_FORBIDDEN_PHRASES = (
    "你錯了", "你對了", "有道理", "不對", "很棒", "沒關係", "再試試",
    "答案是", "我覺得", "我是AI",
)


def _tutor_extract_structured_analysis(data):
    """Prefer explicit structured_analysis; else handwriting_analysis; else flat request fields."""
    if not isinstance(data, dict):
        data = {}
    raw_sa = data.get("structured_analysis")
    raw_ha = data.get("handwriting_analysis")
    if isinstance(raw_sa, dict) and raw_sa:
        src = dict(raw_sa)
    elif isinstance(raw_ha, dict) and raw_ha:
        src = dict(raw_ha)
    else:
        src = {}
    return {
        "status": str(src.get("status") or data.get("status") or "unknown"),
        "main_issue": str(src.get("main_issue") or data.get("main_issue") or ""),
        "issue_tag": str(src.get("issue_tag") or data.get("issue_tag") or ""),
        "expected_answer": str(src.get("expected_answer") or data.get("expected_answer") or ""),
        "error_mechanism": str(src.get("error_mechanism") or data.get("error_mechanism") or "unknown"),
        "step_focus": str(src.get("step_focus") or data.get("step_focus") or ""),
        "family_id": str(src.get("family_id") or data.get("family_id") or ""),
        "analysis_source": str(src.get("analysis_source") or data.get("analysis_source") or ""),
    }


def _tutor_deterministic_fallback(structured_analysis):
    mech = str(structured_analysis.get("error_mechanism") or "unknown")
    issue = str(structured_analysis.get("main_issue") or "")
    fid = str(structured_analysis.get("family_id") or "").strip()
    step = str(structured_analysis.get("step_focus") or "").strip()
    if fid in ("F9", "poly_div_poly_qr"):
        picked = _f9_tutor_guidance_pick(mech, step)
        if picked:
            hint_focus, guided_question, micro_step = picked
            return {
                "hint_focus": hint_focus[:18],
                "guided_question": guided_question[:28],
                "micro_step": micro_step[:22],
                "forbidden": False,
            }
    by_mech = {
        "sign_error": (
            "先看括號前的符號",
            "去括號後每一項符號有變嗎？",
            "先把括號內每項重寫一次",
        ),
        "combine_error": (
            "先找同類項",
            "哪些項的字母和次方完全一樣？",
            "先把可合併的項圈出來",
        ),
        "structure_error": (
            "先確認式子結構",
            "這一步有沒有改變原本括號範圍？",
            "先逐行對照原式重寫",
        ),
        "operation_error": (
            "先確認運算規則",
            "這一步是加減還是分配展開？",
            "先只做一個運算動作",
        ),
        "substitution_error": (
            "先核對代入值",
            "每個代入值放到正確位置了嗎？",
            "先把代入位置標記出來",
        ),
        "notation_error": (
            "先補齊記號格式",
            "括號、變數、次方都寫完整了嗎？",
            "先修正式子書寫格式",
        ),
        "unknown": (
            "先回到題目關鍵條件",
            "哪一步開始與題目條件不一致？",
            "先重寫第一步再往下",
        ),
    }
    hint_focus, guided_question, micro_step = by_mech.get(mech, by_mech["unknown"])
    if issue and mech == "unknown":
        hint_focus = issue[:18]
    return {
        "hint_focus": hint_focus[:18],
        "guided_question": guided_question[:28],
        "micro_step": micro_step[:22],
        "forbidden": False,
    }


def _tutor_guidance_to_reply(g):
    return f"這題的關鍵是：{g['hint_focus']}\n\n想一下：\n{g['guided_question']}\n\n👉 {g['micro_step']}"


def _tutor_has_answer_leak(text):
    t = str(text or "")
    if "答案是" in t:
        return True
    # very simple leak check: direct assignment pattern in tutor text
    return bool(re.search(r"[a-zA-Z]\s*=\s*[-+]?\d", t))


def _tutor_guidance_is_compliant(g, structured_analysis):
    if not isinstance(g, dict):
        return False
    for k in ("hint_focus", "guided_question", "micro_step", "forbidden"):
        if k not in g:
            return False
    if bool(g.get("forbidden")):
        return False
    hint_focus = str(g.get("hint_focus") or "").strip()
    guided_question = str(g.get("guided_question") or "").strip()
    micro_step = str(g.get("micro_step") or "").strip()
    if (not hint_focus) or (not guided_question) or (not micro_step):
        return False
    if len(hint_focus) > 18 or len(guided_question) > 28 or len(micro_step) > 22:
        return False
    merged = f"{hint_focus} {guided_question} {micro_step}"
    if any(p in merged for p in TUTOR_FORBIDDEN_PHRASES):
        return False
    if _tutor_has_answer_leak(merged):
        return False
    status = str(structured_analysis.get("status") or "")
    if status in ("correct", "incorrect", "partially_correct"):
        banned_judge = ("答對", "答錯", "正確", "錯誤")
        if any(p in merged for p in banned_judge):
            return False
    main_issue = str(structured_analysis.get("main_issue") or "").strip()
    if main_issue and (main_issue[:4] not in merged) and (main_issue[:6] not in merged):
        # not strictly required but should stay aligned with truth source
        key_tokens = [w for w in re.findall(r"[\u4e00-\u9fff]{2,}", main_issue) if len(w) >= 2]
        if key_tokens and not any(tok in merged for tok in key_tokens[:2]):
            return False
    return True

def allowed_exam_file(filename):







    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXAM_EXTENSIONS















# ==========================================







# AI Chat & Handwriting (AI ?叟??)







# ==========================================















@practice_bp.route('/chat_ai', methods=['POST'])







def chat_ai():







    """AI chat API."""







    data = request.get_json()







    user_question = data.get('question', '').strip()







    context = data.get('context', '')







    question_text = data.get('question_text', '')







    family_id = (data.get('family_id') or '').strip()







    question_context = (data.get('question_context') or context or '').strip()







    subskill_nodes = data.get('subskill_nodes') or []















    if not user_question:







        return jsonify({"reply": "?ｇ???鈭??選??"}), 400















    current = get_current()







    skill_id = current.get("skill")







    prereq_skills = current.get('prereq_skills', [])







    if not family_id:







        family_id = (current.get('family_id') or current.get('skill') or skill_id or '').strip()







    







    full_question_context = question_text if question_text else (current.get("question") or question_context)
    structured_analysis = _tutor_extract_structured_analysis(data)
    _raw_ha = data.get("handwriting_analysis") if isinstance(data, dict) else None
    _has_handwriting = isinstance(_raw_ha, dict) and bool(_raw_ha)
    _sa_empty = (
        str(structured_analysis.get("status") or "") == "unknown"
        and not str(structured_analysis.get("main_issue") or "").strip()
        and str(structured_analysis.get("error_mechanism") or "") == "unknown"
    )
    if not _has_handwriting and _sa_empty:
        current_app.logger.info("[chat_ai] skipped due to empty structured_analysis")
        return jsonify(
            {
                "reply": "我目前還沒有足夠的分析結果 👉 請先按「AI檢查手寫」或送出答案，我再幫你更精準地找錯誤！",
                "follow_up_prompts": [],
            }
        )
    structured_summary = (
        f"status={structured_analysis.get('status','unknown')}; "
        f"main_issue={structured_analysis.get('main_issue','')}; "
        f"issue_tag={structured_analysis.get('issue_tag','')}; "
        f"error_mechanism={structured_analysis.get('error_mechanism','unknown')}; "
        f"step_focus={structured_analysis.get('step_focus','')}; "
        f"family_id={structured_analysis.get('family_id','')}; "
        f"analysis_source={structured_analysis.get('analysis_source','')}; "
        f"expected_answer={structured_analysis.get('expected_answer','')}"
    )
    if structured_summary:
        full_question_context = f"{full_question_context}\n\n[structured_analysis]\n{structured_summary}"







    







    if not skill_id and context:







        # ?芬謘??質 skill_id (Fallback)







        if '?朱?' in context: skill_id = 'remainder'







        elif '?蹎?' in context: skill_id = 'factor_theorem'















    full_prompt = build_chat_prompt(







        skill_id=skill_id,







        user_question=user_question,







        full_question_context=full_question_context,







        context=context,







        prereq_skills=prereq_skills







    )















    current_app.logger.info(
        "[chat_ai] analysis_source=%s family_id=%s error_mechanism=%s step_focus=%s",
        structured_analysis.get("analysis_source", ""),
        structured_analysis.get("family_id", ""),
        structured_analysis.get("error_mechanism", ""),
        structured_analysis.get("step_focus", ""),
    )
    current_app.logger.info(







        "[chat_ai] received question='%s' context_head='%s'",







        user_question[:120],







        (full_question_context or '')[:120]







    )







    







    result = get_chat_response(







        full_prompt,







        user_question=user_question,







        question_context=full_question_context







    )

    # Tutor compliance gate: bounded language layer only.
    structured_analysis = _tutor_extract_structured_analysis(data)
    guidance = None
    if isinstance(result, dict):
        if all(k in result for k in ("hint_focus", "guided_question", "micro_step", "forbidden")):
            guidance = {
                "hint_focus": result.get("hint_focus"),
                "guided_question": result.get("guided_question"),
                "micro_step": result.get("micro_step"),
                "forbidden": result.get("forbidden"),
            }
        else:
            # Backward compatibility: old tutor may still return only reply.
            guidance = None

    if not _tutor_guidance_is_compliant(guidance, structured_analysis):
        current_app.logger.info("[chat_ai] tutor output non-compliant; fallback to deterministic guidance")
        guidance = _tutor_deterministic_fallback(structured_analysis)

    result = result if isinstance(result, dict) else {}
    result["hint_focus"] = guidance["hint_focus"]
    result["guided_question"] = guidance["guided_question"]
    result["micro_step"] = guidance["micro_step"]
    result["forbidden"] = False
    result["reply"] = _tutor_guidance_to_reply(guidance)















    # ?伍??撖??株????????????圈?鞈?????蹓??迫?堊垮??頛??湛???







    chat_state = session.get('chat_followup_state', {}) if isinstance(session.get('chat_followup_state', {}), dict) else {}







    last_prompts = chat_state.get('last_prompts', [])







    turn_index = int(chat_state.get('turn_index', 0))







    last_context = chat_state.get('last_context', '')















    if last_context != full_question_context:







        last_prompts = []







        turn_index = 0















    # ?漱謓梢??賊??賹???啾冪?閰??嚗??????堊筑???????擏???⊿豲??????????????







    per_turn_prompts = build_dynamic_follow_up_prompts_variant(







        user_question=user_question,







        question_context=full_question_context,







        ai_reply=result.get('reply', ''),







        variant=turn_index







    )







    result['follow_up_prompts'] = diversify_follow_up_prompts(







        per_turn_prompts,







        last_prompts,







        user_question=user_question,







        question_context=full_question_context,







        ai_reply=result.get('reply', ''),







        turn_index=turn_index







    )















    current_app.logger.info(







        "[chat_ai] generated follow_up_prompts=%s",







        result.get('follow_up_prompts', [])







    )















    session['chat_followup_state'] = {







        'last_prompts': result.get('follow_up_prompts', [])[:3],







        'turn_index': turn_index + 1,







        'last_question': user_question[:120],







        'last_context': full_question_context







    }















    subskill_map = {







        'sign_handling': '甇???霈',







        'add_sub': '?湔??',







        'mul_div': '?湔銋',







        'mixed_ops': '??瘛瑕???',







        'absolute_value': '絕對值',







        'parentheses': '?祈???',







        'divide_terms': '???渡?',







        'conjugate_rationalize': '有理化',







    }







    focus_points = []







    for item in subskill_nodes:







        label = subskill_map.get(str(item), str(item).replace('_', ' '))







        if label and label not in focus_points:







            focus_points.append(label)







    if not focus_points:







        focus_points.append('依題目關鍵步驟進行檢查')







    result['subskill_labels'] = focus_points















    result['question_text'] = question_text







    result['family_id'] = family_id







    result['question_context'] = question_context or question_text















    return jsonify(result)















@practice_bp.route('/analyze_handwriting', methods=['POST'])







@login_required







def analyze_handwriting():







    """Student diagnosis page."""







    data = request.get_json(silent=True) or {}







    print("payload keys:", list(data.keys()))
    print("has image:", bool(data.get("image_base64")))
    if data.get("image_base64"):
        print("image prefix:", str(data["image_base64"])[:80])
    img = (
        data.get('image_data_url')
        or data.get('image_base64')
        or data.get('handwriting_image')
        or data.get('scratchpad_image')
    )
    print("has any image field:", bool(img))
    if img:
        print("effective image prefix:", str(img)[:80])







    if not img:
        return _handwriting_not_recognized_response()







    







    state = get_current()







    prereq_skills = state.get('prereq_skills', [])
    question_text = (data.get('question_text') or state.get('question_text') or state.get('question') or "").strip()
    question_context = (data.get('question_context') or state.get('question') or "").strip()
    family_id = (data.get('family_id') or state.get('family_id') or state.get('skill') or "").strip()
    skill_labels = {
        'sign_handling': '?????',
        'add_sub': '????',
        'mul_div': '????',
        'mixed_ops': '??????',
        'absolute_value': '???',
        'parentheses': '????',
        'divide_terms': '????',
        'conjugate_rationalize': '?????',
    }
    prereq_text = ", ".join(
        f"{skill_labels.get(item.get('id'), item.get('name', item.get('id', '')))}"
        for item in prereq_skills
        if isinstance(item, dict)
    )
    b64 = str(img)
    if "," in b64:
        b64 = b64.split(",", 1)[1]
    b64 = b64.strip()
    temp_path = None
    result = None
    try:
        try:
            img_data = base64.b64decode(b64)
        except Exception:
            return _handwriting_not_recognized_response()
        if not img_data:
            return _handwriting_not_recognized_response()
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as f:
            f.write(img_data)
            temp_path = f.name
        print("calling handwriting analyzer (recognition then analysis)")
        print("question_text:", question_text)
        print("image length:", len(b64) if b64 else 0)
        recognition_prompt = (
            "Transcribe all visible handwritten mathematical content from this student whiteboard image. "
            "Return ONLY valid JSON, no markdown, no extra text. "
            "The JSON must be one object with key \"expression\" (string). "
            "Put equations, numbers, and step-by-step work in that string; separate lines with semicolons. "
            "If the image is blank, illegible, or has no mathematical writing, set \"expression\" to \"\". "
            "Do not invent symbols or steps that are not clearly visible."
        )
        rec_response = call_ai(
            role="vision_analyzer",
            prompt=recognition_prompt,
            image_path=temp_path,
            max_retries=2,
            retry_delay=1,
            verbose=False,
        )
        rec_raw = (getattr(rec_response, 'text', '') or '').strip()
        rec_cleaned = re.sub(r'^```json\s*|\s*```$', '', rec_raw, flags=re.MULTILINE)
        rec_parsed = clean_and_parse_json(rec_cleaned)
        expr = _handwriting_expression_from_parsed(rec_parsed)
        if not _handwriting_expression_is_usable(expr):
            current_app.logger.info("analyze_handwriting: no usable expression after recognition pass")
            return _handwriting_not_recognized_response()

        expected_answer = _handwriting_expected_answer(data, state, question_text, question_context)
        print("[HW DEBUG] expected_answer:", expected_answer)
        print("[HW DEBUG] question_text:", question_text)
        analysis_result = _handwriting_structured_analysis(
            expr, expected_answer, question_text, family_id
        )
        current_app.logger.info(
            "analyze_handwriting: analysis_source=%s family_id=%s status=%s",
            analysis_result.get("analysis_source"),
            family_id,
            analysis_result.get("status"),
        )
        _hw_err = {
            "correct": "handwriting_ok",
            "partially_correct": "handwriting_partial",
            "incorrect": "handwriting_wrong",
            "unknown": "handwriting_unknown",
        }

        hw_status = analysis_result.get("status")
        if hw_status in ("unknown", "correct"):
            reply_text = _handwriting_rule_based_reply(analysis_result)
            result = {
                "reply": enforce_strict_mode(reply_text),
                "is_process_correct": hw_status in ("correct", "partially_correct"),
                "correct": hw_status == "correct",
                "next_question": "",
                "follow_up_prompts": [],
                "error_type": _hw_err.get(hw_status, "handwriting_unknown"),
                "success": True,
                "auto_next": hw_status == "correct",
                "handwriting_analysis": analysis_result,
                "handwriting_status": hw_status,
            }
            print("analyzer result:", result)
        elif _handwriting_issue_is_clear(analysis_result):
            reply_text = _handwriting_rule_based_reply(analysis_result)
            result = {
                "reply": enforce_strict_mode(reply_text),
                "is_process_correct": hw_status == "partially_correct",
                "correct": False,
                "next_question": "",
                "follow_up_prompts": [],
                "error_type": _hw_err.get(hw_status, "handwriting_unknown"),
                "success": True,
                "auto_next": False,
                "handwriting_analysis": analysis_result,
                "handwriting_status": hw_status,
            }
            print("analyzer result:", result)
        else:
            prompt = _handwriting_feedback_second_prompt(
                analysis_result, question_text, question_context, prereq_text, family_id
            )
            response = call_ai(
                role="tutor",
                prompt=prompt,
                image_path=None,
                max_retries=2,
                retry_delay=1,
                verbose=False,
            )
            raw_text = (getattr(response, "text", "") or "").strip()
            cleaned = re.sub(r"^```json\s*|\s*```$", "", raw_text, flags=re.MULTILINE)
            parsed = clean_and_parse_json(cleaned)
            reply_stripped = ""
            if isinstance(parsed, dict):
                reply_stripped = str(parsed.get("reply", "") or "").strip()
            if (not reply_stripped) or (not _handwriting_reply_is_compliant(reply_stripped, analysis_result.get("status"))):
                current_app.logger.info(
                    "analyze_handwriting: second-stage reply non-compliant; using rule-based reply"
                )
                mech = str((analysis_result or {}).get("error_mechanism") or "").strip()
                issue = ERROR_MECHANISM_FEEDBACK.get(
                    mech,
                    str((analysis_result or {}).get("main_issue") or "").strip() or ERROR_MECHANISM_FEEDBACK["unknown"],
                )
                st = str((analysis_result or {}).get("status") or "")
                if st == "incorrect" and issue:
                    reply_stripped = f"✘ 這題有錯\n{issue}\n👉 想一下再試一次"
                elif st == "partially_correct" and issue:
                    reply_stripped = f"⚠️ 方向正確，但還有一個關鍵小錯\n{issue}\n👉 請再檢查一次"
                else:
                    reply_stripped = _handwriting_rule_based_reply(analysis_result)
            result = {
                "reply": "目前無法產生穩定批改回饋，請再試一次。",
                "is_process_correct": False,
                "correct": False,
                "next_question": "",
                "follow_up_prompts": [],
                "error_type": "handwriting_analyzer_failed",
            }
            if isinstance(parsed, dict):
                result.update(parsed)
            result["reply"] = enforce_strict_mode(reply_stripped)
            result["handwriting_analysis"] = analysis_result
            result["handwriting_status"] = analysis_result.get("status", "unknown")
            st = analysis_result.get("status")
            result["correct"] = st == "correct"
            result["is_process_correct"] = st in ("correct", "partially_correct")
            result["error_type"] = _hw_err.get(st, "handwriting_unknown")
            result["success"] = True
            result["auto_next"] = False
            if not isinstance(result.get("follow_up_prompts"), list):
                result["follow_up_prompts"] = []
            print("analyzer result:", result)
    except Exception as analyzer_exc:
        current_app.logger.exception("analyze_handwriting analyzer failed: %s", analyzer_exc)
        return _handwriting_not_recognized_response()
    finally:
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)















    # [Start of modification] Diagnosis for handwriting







    if False and result.get("correct") is False and result.get("handwriting_status") == "incorrect":







        try:







            current_app.logger.info(f"[Handwriting Check] Incorrect answer detected, diagnosing...")







            question_text = state.get('question_text', '')







            correct_answer = state.get('correct_answer', '')







            student_answer = f"?????????: {result.get('reply', '')}"







            







            # [Phase 6] Diagnosis







            diagnosis = diagnose_error(







                question_text=question_text,







                correct_answer=correct_answer,







                student_answer=student_answer,







                prerequisite_units=prereq_skills







            )







            







            if diagnosis.get('related_prerequisite_id'):







                prereq_id = diagnosis['related_prerequisite_id']







                # Find name







                prereq_name = "?蝞??獢?"







                if prereq_skills:







                    for p in prereq_skills:







                        # prereq_skills structure: [{'id':..., 'name':...}]







                        if str(p.get('id')) == str(prereq_id) or str(p.get('skill_id')) == str(prereq_id):







                            prereq_name = p.get('name') or p.get('skill_ch_name')







                            break







                







                result['suggested_prerequisite'] = {







                    'id': prereq_id,







                    'name': prereq_name,







                    'reason': diagnosis.get('prerequisite_explanation', '?梁????')







                }







        except Exception as e:







            current_app.logger.error(f"Handwriting diagnosis failed: {e}")







    # [End of modification]







    







    # ?謕???update_progress ??湔?鈭????秋撒???質縐?????helper







    







    return jsonify(result)































# ==========================================







# Mistake Notebook & Diagnosis (????蟡??桃捂謘?







# ==========================================















@core_bp.route('/mistake-notebook')







@login_required







def mistake_notebook():







    return render_template('mistake_notebook.html', username=current_user.username)















@core_bp.route('/api/mistake-notebook', methods=['GET'])







@login_required







def api_mistake_notebook():







    entries = db.session.query(MistakeNotebookEntry).filter_by(student_id=current_user.id).order_by(MistakeNotebookEntry.created_at.desc()).all()







    return jsonify([entry.to_dict() for entry in entries])















@core_bp.route('/mistake-notebook/add', methods=['POST'])







@login_required







def add_mistake_entry():







    try:







        data = request.get_json()







        db.session.add(MistakeNotebookEntry(







            student_id=current_user.id,







            exam_image_path=data.get('exam_image_path'),







            question_data=data.get('question_data'),







            notes=data.get('notes'),







            skill_id=data.get('skill_id')







        ))







        db.session.commit()







        return jsonify({'success': True, 'message': '??'})







    except Exception as e:







        db.session.rollback()







        return jsonify({'success': False, 'message': str(e)}), 500















@core_bp.route('/student/analyze_weakness', methods=['POST'])







@login_required







def analyze_weakness():







    """Analyze student weakness data for radar chart."""







    try:







        force_refresh = request.json.get('force_refresh', False) if request.json else False







        result = perform_weakness_analysis(current_user.id, force_refresh)







        return jsonify(result)







    except Exception as e:







        current_app.logger.error(f"?╰??????芰?: {e}")







        return jsonify({'success': False, 'error': str(e)}), 500















# ==========================================







# [?蝞??乾?] Mistake Notebook Helpers







# ==========================================















@core_bp.route('/add_mistake_page')







@login_required







def add_mistake_page():







    """Render the mistake notebook page."""







    skills = db.session.query(SkillInfo).filter_by(is_active=True).order_by(SkillInfo.skill_ch_name).all()







    return render_template('add_mistake.html', skills=skills, username=current_user.username)















@core_bp.route('/mistake-notebook/upload-image', methods=['POST'])







@login_required







def upload_mistake_image():







    """Upload a mistake notebook image."""







    if 'file' not in request.files: return jsonify({'success': False, 'message': '????澗??'}), 400







    file = request.files['file']







    if file.filename == '' or not allowed_exam_file(file.filename):







        return jsonify({'success': False, 'message': '?澗?????'}), 400















    try:







        upload_dir = os.path.join(current_app.static_folder, 'mistake_uploads', str(current_user.id))







        os.makedirs(upload_dir, exist_ok=True)







        







        filename = secure_filename(file.filename)







        unique_filename = f"{uuid.uuid4().hex}_{filename}"







        path = os.path.join(upload_dir, unique_filename)







        file.save(path)







        







        rel_path = os.path.join('mistake_uploads', str(current_user.id), unique_filename).replace('\\', '/')







        return jsonify({'success': True, 'path': rel_path})







    except Exception as e:







        return jsonify({'success': False, 'message': str(e)}), 500















# ==========================================







# Student Diagnosis (?株???株???桃捂謘?蹓遴?)







# ==========================================















@core_bp.route('/student/diagnosis')







@login_required







def student_diagnosis():







    """







    ?輯??扳鞎??株???桃捂謘?蹓遴?







    """







    return render_template('student_diagnosis.html', username=current_user.username)















# ==========================================







# Naive RAG (RAG ?潘撕??+ LLM ?豯?)







# ==========================================







# RAG??? + ???







# ==========================================















@practice_bp.route('/api/rag_search', methods=['POST'])







def api_rag_search():







    """RAG search API."""







    data = request.get_json(silent=True) or {}







    query = (data.get('query') or '').strip()















    if not query:







        return jsonify({"results": [], "error": "???????"}), 400















    results = rag_search(query, top_k=5)







    return jsonify({"results": results})























@practice_bp.route('/api/rag_chat', methods=['POST'])







def api_rag_chat():







    """RAG + LLM chat API."""







    data = request.get_json(silent=True) or {}







    query = (data.get('query') or '').strip()







    top_skill_id = (data.get('top_skill_id') or '').strip()















    if not query or not top_skill_id:







        return jsonify({"reply": "??????????"}), 400















    result = rag_chat(query, top_skill_id)







    return jsonify(result)









