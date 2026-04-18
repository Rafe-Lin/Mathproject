# -*- coding: utf-8 -*-
"""
Live Show Healer 回歸測試：
- 驗證 fix count 分帳一致（Code / Display / AST / O1）
- 驗證 DISPLAY_SANITIZE / DISPLAY_REGEX 細項可追溯
- 驗證可讀摘要中文說明完整
- 驗證 ISO/STYLE guard 判斷與日誌
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.healers.live_show_healer import (
    init_healer_trace,
    apply_sanitize_report_to_trace,
    apply_display_report_to_trace,
    build_readable_healer_logs,
)
from core.healers.live_show_iso_guard import (
    evaluate_iso_style_guard,
    append_iso_style_guard_logs,
    append_fallback_switch_log,
)


def test_fix_count_accounting_consistency():
    trace = init_healer_trace({"regex_code_fixes": 2, "ast_fixes": 1, "o1_fixes": 0})
    logs = []

    sanitize_report = {"double_paren_fixes": 1, "negative_wrap_fixes": 2}
    display_report = {
        "regex_fix_count": 3,
        "fix_breakdown": {
            "normalize_sign_sequence": 2,
            "fix_plain_div_token": 1,
        }
    }

    apply_sanitize_report_to_trace(trace, logs, sanitize_report)
    apply_display_report_to_trace(trace, logs, display_report)

    assert trace["regex_code_fixes"] == 2
    assert trace["regex_display_fixes"] == 6
    assert trace["regex_fixes"] == 8
    assert trace["ast_fixes"] == 1

    assert any("[DISPLAY_SANITIZE_HEALER] double_paren_fixes: +1" in s for s in logs)
    assert any("[DISPLAY_SANITIZE_HEALER] negative_wrap_fixes: +2" in s for s in logs)
    assert any("[DISPLAY_REGEX_HEALER] normalize_sign_sequence: +2" in s for s in logs)
    assert any("[DISPLAY_REGEX_HEALER] fix_plain_div_token: +1" in s for s in logs)


def test_readable_summary_contains_explanations():
    trace = {
        "regex_fixes": 8,
        "regex_code_fixes": 2,
        "regex_display_fixes": 6,
        "ast_fixes": 1,
        "o1_fixes": 0,
    }
    detail_logs = [
        "[DISPLAY_SANITIZE_HEALER] double_paren_fixes: +1",
        "[DISPLAY_SANITIZE_HEALER] negative_wrap_fixes: +2",
        "[DISPLAY_REGEX_HEALER] normalize_sign_sequence: +2",
        "[DISPLAY_REGEX_HEALER] fix_plain_div_token: +1",
        "[ISO_GUARD] primary output profile mismatch.",
    ]

    lines = build_readable_healer_logs(trace, detail_logs)
    merged = "\n".join(lines)

    assert "Regex 總修補: 8（Code=2, Display=6）" in merged
    assert "double_paren_fixes: +1（折疊重複數字括號" in merged
    assert "negative_wrap_fixes: +2（將裸負數統一包成括號" in merged
    assert "normalize_sign_sequence: +2（清理連續符號" in merged
    assert "ISO 檢查：主輸出結構與目標不一致。" in merged


def test_iso_style_guard_decision_and_logs():
    expected_fp = {"mock": True}

    def _extract_expr(text):
        return str(text or "")

    def _has_decimal(text):
        return "." in str(text or "")

    def _isomorphic(_expected, generated_expr):
        return generated_expr == "a*b/c"

    def _profile_diff(_expected, _generated):
        return ["operator_sequence: expected times->divide, got drift"]

    # case 1: isomorphic + no decimal mismatch
    meta_ok = evaluate_iso_style_guard(
        expected_fp=expected_fp,
        question_text="a*b/c",
        decimal_style_mode=False,
        extract_expr_fn=_extract_expr,
        has_decimal_fn=_has_decimal,
        isomorphic_fn=_isomorphic,
    )
    assert meta_ok["triggered"] is False
    assert meta_ok["isomorphic"] is True
    assert meta_ok["decimal_mismatch"] is False

    # case 2: non-isomorphic triggers ISO guard logs
    meta_bad = evaluate_iso_style_guard(
        expected_fp=expected_fp,
        question_text="a+b/c",
        decimal_style_mode=False,
        extract_expr_fn=_extract_expr,
        has_decimal_fn=_has_decimal,
        isomorphic_fn=_isomorphic,
    )
    assert meta_bad["triggered"] is True
    logs = []
    append_iso_style_guard_logs(
        detail_logs=logs,
        expected_fp=expected_fp,
        generated_expr=meta_bad["expr"],
        decimal_mismatch=meta_bad["decimal_mismatch"],
        isomorphic_fn=_isomorphic,
        profile_diff_fn=_profile_diff,
    )
    append_fallback_switch_log(logs, meta_bad["decimal_mismatch"])

    assert any("[ISO_GUARD] primary output profile mismatch." in s for s in logs)
    assert any("[ISO_GUARD] operator_sequence:" in s for s in logs)
    assert any("switched to deterministic isomorphic fallback" in s for s in logs)


def run_all():
    tests = [
        ("fix count 一致性", test_fix_count_accounting_consistency),
        ("可讀摘要說明", test_readable_summary_contains_explanations),
        ("ISO/STYLE guard 判斷與日誌", test_iso_style_guard_decision_and_logs),
    ]

    passed = 0
    failed = 0
    print("=" * 70)
    print("Live Show Healer Regression Tests")
    print("=" * 70)

    for idx, (name, fn) in enumerate(tests, start=1):
        try:
            fn()
            passed += 1
            print(f"[{idx}/{len(tests)}] ✅ {name}")
        except AssertionError as e:
            failed += 1
            print(f"[{idx}/{len(tests)}] ❌ {name} | AssertionError: {e}")
        except Exception as e:
            failed += 1
            print(f"[{idx}/{len(tests)}] ❌ {name} | {type(e).__name__}: {e}")

    print("-" * 70)
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print("=" * 70)

    if failed > 0:
        raise SystemExit(1)


if __name__ == "__main__":
    run_all()
