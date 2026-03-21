# -*- coding: utf-8 -*-
"""Live Show 的 ISO/STYLE guard 輔助函式（僅判斷與記錄，不執行 fallback）。"""


def evaluate_iso_style_guard(
    expected_fp,
    question_text,
    decimal_style_mode,
    extract_expr_fn,
    has_decimal_fn,
    isomorphic_fn,
):
    expr = extract_expr_fn(question_text or "")
    isomorphic = bool(isomorphic_fn(expected_fp, expr))
    decimal_mismatch = bool(decimal_style_mode and (not has_decimal_fn(question_text or "")))
    triggered = (not isomorphic) or decimal_mismatch
    return {
        "triggered": triggered,
        "expr": expr,
        "isomorphic": isomorphic,
        "decimal_mismatch": decimal_mismatch,
    }


def append_iso_style_guard_logs(
    detail_logs,
    expected_fp,
    generated_expr,
    decimal_mismatch,
    isomorphic_fn,
    profile_diff_fn,
):
    logs = detail_logs if isinstance(detail_logs, list) else []

    if not isomorphic_fn(expected_fp, generated_expr):
        logs.append("[ISO_GUARD] primary output profile mismatch.")
        for diff_line in profile_diff_fn(expected_fp, generated_expr):
            logs.append(f"[ISO_GUARD] {diff_line}")

    if decimal_mismatch:
        logs.append("[STYLE_GUARD] source contains decimal but generated expression has no decimal.")

    return logs


def append_fallback_switch_log(detail_logs, decimal_mismatch):
    logs = detail_logs if isinstance(detail_logs, list) else []
    if decimal_mismatch:
        logs.append("[STYLE_GUARD] switched to decimal-preserving deterministic fallback.")
    else:
        logs.append("[ISO_GUARD] LLM output drift detected; switched to deterministic isomorphic fallback.")
    return logs
