# -*- coding: utf-8 -*-
# ==============================================================================
# ID: evaluate_mcri.py
# Version: V1.0.0 (MCRI Heuristic Evaluator)
# Last Updated: 2026-04-15
# Author: *Steve
#
# [Description]:
#   提供 live_show、scaler、agent_tools 等模組共用的 MCRI 風格程式碼評分介面。
#   實作 analyze_code_robustness、evaluate_math_hygiene、evaluate_live_code 等函式，
#   以啟發式規則避免假分數，並產生穩定的數值輸出供 UI 與批次評測使用。
#
# [Scientific Control Strategy]:
#   固定規則評分與分數上下限，避免隨機或未定義的 fallback 分數。
#
# [Database Schema Usage]:
#   無直接資料庫操作。
#
# [Logic Flow]:
#   1. 解析或檢查程式碼結構、題文衛生與執行結果。
#   2. 計算合併分數並回傳給路由或批次評測呼叫端。
# ==============================================================================

from __future__ import annotations

import ast
import math
import re
from typing import Any


def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def _safe_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def _count_pattern(text: str, pattern: str) -> int:
    return len(re.findall(pattern, text, flags=re.MULTILINE))


def analyze_code_robustness(code: str) -> tuple[str, str]:
    code = _safe_text(code)
    if not code.strip():
        return "SYNTAX_ERROR", "empty code"

    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return "SYNTAX_ERROR", f"syntax error: {exc.msg}"

    score = 70
    reasons: list[str] = []

    if any(isinstance(node, ast.Try) for node in ast.walk(tree)):
        score += 8
        reasons.append("has try/except guard")

    if any(isinstance(node, ast.FunctionDef) and node.name == "generate" for node in ast.walk(tree)):
        score += 8
        reasons.append("has generate() entrypoint")

    if "safe_eval" in code:
        score += 8
        reasons.append("uses safe_eval")

    risky_patterns = [
        (r"\beval\s*\(", 18, "uses eval()"),
        (r"\bexec\s*\(", 20, "uses exec()"),
        (r"\bopen\s*\(", 12, "opens files"),
        (r"\bos\.system\s*\(", 25, "uses os.system"),
        (r"\bsubprocess\.", 25, "uses subprocess"),
        (r"\brequests\.", 10, "uses network requests"),
    ]
    for pattern, penalty, label in risky_patterns:
        if re.search(pattern, code):
            score -= penalty
            reasons.append(label)

    if _count_pattern(code, r"\bimport\b") > 12:
        score -= 8
        reasons.append("too many imports")

    score = int(_clamp(score, 0, 100))

    if score >= 85:
        return "ROBUST", "; ".join(reasons) or "clean structured code"
    if score >= 65:
        return "MODERATE", "; ".join(reasons) or "usable with minor risk"
    if score >= 45:
        return "NEUTRAL", "; ".join(reasons) or "mixed signals"
    return "RISKY", "; ".join(reasons) or "multiple risky constructs"


def evaluate_math_hygiene(question_text: str) -> tuple[float, list[str]]:
    question = _safe_text(question_text).strip()
    if not question:
        return 0.0, ["missing question text"]

    score = 15.0
    notes: list[str] = []

    if "$" not in question:
        score -= 4.0
        notes.append("missing inline LaTeX delimiters")

    if "\\\\" in question:
        score -= 2.0
        notes.append("double backslash leakage")

    if "Math input error" in question or "Traceback" in question or "Error" == question.strip():
        score -= 8.0
        notes.append("contains visible error marker")

    if "None" in question or "nan" in question.lower():
        score -= 3.0
        notes.append("contains invalid placeholder")

    if _count_pattern(question, r"\\frac\{[^{}]+\}\{[^{}]+\}") > 0:
        score += 1.0
    if _count_pattern(question, r"\\sqrt\{[^{}]+\}") > 0:
        score += 1.0

    score = round(_clamp(score, 0.0, 15.0), 1)
    return score, notes


def _syntax_score(code: str) -> tuple[float, dict[str, Any]]:
    breakdown: dict[str, Any] = {}
    if not code.strip():
        return 0.0, {"compile_ok": False, "reason": "empty code"}

    score = 100.0
    try:
        ast.parse(code)
        breakdown["compile_ok"] = True
    except SyntaxError as exc:
        return 0.0, {"compile_ok": False, "reason": exc.msg}

    if "def generate" not in code:
        score -= 20.0
        breakdown["missing_generate"] = True

    if re.search(r"\bTODO\b|\bpass\b", code):
        score -= 10.0
        breakdown["contains_placeholder"] = True

    return round(_clamp(score), 1), breakdown


def _logic_score(exec_result: dict[str, Any]) -> tuple[float, dict[str, Any]]:
    breakdown: dict[str, Any] = {}
    if not isinstance(exec_result, dict):
        return 0.0, {"invalid_exec_result": True}

    if exec_result.get("error"):
        return 5.0, {"runtime_error": _safe_text(exec_result.get("error"))[:120]}

    score = 55.0
    q = _safe_text(exec_result.get("question_text")).strip()
    a = _safe_text(exec_result.get("correct_answer")).strip()

    if q:
        score += 20.0
        breakdown["has_question"] = True
    if a:
        score += 15.0
        breakdown["has_answer"] = True

    if q and ("$" in q or "\\frac" in q or "\\sqrt" in q):
        score += 5.0
    if a and ("Math input error" not in a):
        score += 5.0

    if q and a and "Error" not in q:
        score += 5.0

    return round(_clamp(score), 1), breakdown


def _render_score(exec_result: dict[str, Any]) -> tuple[float, dict[str, Any]]:
    q = _safe_text((exec_result or {}).get("question_text")).strip()
    score = 35.0
    breakdown: dict[str, Any] = {}

    if not q:
        return 0.0, {"missing_question_text": True}

    if "$" in q:
        score += 20.0
        breakdown["latex_wrapped"] = True
    if "\\frac" in q:
        score += 18.0
        breakdown["has_fraction"] = True
    if "\\sqrt" in q:
        score += 18.0
        breakdown["has_radical"] = True
    if "Math input error" in q or "Traceback" in q:
        score -= 50.0
        breakdown["render_error"] = True
    if "\\\\" in q:
        score -= 8.0
        breakdown["double_backslash"] = True

    return round(_clamp(score), 1), breakdown


def _stability_score(
    healer_trace: dict[str, Any] | None,
    exec_result: dict[str, Any],
    ablation_mode: bool,
) -> tuple[float, dict[str, Any]]:
    trace = healer_trace if isinstance(healer_trace, dict) else {}
    total_fixes = 0
    for key in ("regex_fixes", "regex_code_fixes", "regex_display_fixes", "ast_fixes", "o1_fixes"):
        value = trace.get(key, 0)
        if isinstance(value, (int, float)):
            total_fixes += int(value)

    score = 78.0 if not ablation_mode else 70.0
    breakdown: dict[str, Any] = {"fix_count": total_fixes}

    if exec_result.get("error"):
        score -= 45.0
        breakdown["runtime_error"] = True

    if total_fixes == 0:
        score += 8.0
        breakdown["clean_pass"] = True
    elif total_fixes <= 2:
        score += 2.0
    elif total_fixes <= 5:
        score -= 8.0
    else:
        score -= min(25.0, float(total_fixes) * 4.0)
        breakdown["heavy_healing"] = True

    return round(_clamp(score), 1), breakdown


def evaluate_live_code(
    code: str,
    exec_result: dict[str, Any],
    healer_trace: dict[str, Any] | None = None,
    ablation_mode: bool = False,
) -> dict[str, Any]:
    code = _safe_text(code)
    exec_result = exec_result if isinstance(exec_result, dict) else {}

    syntax_score, syntax_meta = _syntax_score(code)
    logic_score, logic_meta = _logic_score(exec_result)
    render_score, render_meta = _render_score(exec_result)
    stability_score, stability_meta = _stability_score(healer_trace, exec_result, ablation_mode)

    hygiene_score, hygiene_notes = evaluate_math_hygiene(exec_result.get("question_text", ""))
    hygiene_percent = round((hygiene_score / 15.0) * 100.0, 1)

    # Fold hygiene lightly into render/logic without double-counting too hard.
    logic_score = round(_clamp(logic_score * 0.85 + hygiene_percent * 0.15), 1)
    render_score = round(_clamp(render_score * 0.8 + hygiene_percent * 0.2), 1)

    total_score = round(
        _clamp(
            syntax_score * 0.25
            + logic_score * 0.30
            + render_score * 0.25
            + stability_score * 0.20
        ),
        1,
    )

    breakdown = {
        "l1_syntax": syntax_meta,
        "l2_logic": logic_meta,
        "l3_render": render_meta,
        "l4_stability": stability_meta,
        "l4_3_hygiene": hygiene_score,
        "hygiene_notes": hygiene_notes,
    }

    return {
        "syntax_score": syntax_score,
        "logic_score": logic_score,
        "render_score": render_score,
        "stability_score": stability_score,
        "total_score": total_score,
        "breakdown": breakdown,
    }


__all__ = [
    "analyze_code_robustness",
    "evaluate_math_hygiene",
    "evaluate_live_code",
]
