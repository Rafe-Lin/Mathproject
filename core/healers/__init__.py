# -*- coding: utf-8 -*-
"""
=============================================================================
模組名稱 (Module Name): core/healers/__init__.py
功能說明 (Description): Healers 模組導出接口
執行語法 (Usage): from core.healers import ASTHealer, RegexHealer
版本資訊 (Version): V2.2
更新日期 (Date): 2026-01-30
維護團隊 (Maintainer): Math AI Project Team
=============================================================================
"""

from .ast_healer import ASTHealer
from .regex_healer import (
    RegexHealer, 
    fix_code_syntax,
    clean_redundant_imports,
    remove_forbidden_functions_unified
)
from .live_show_healer import (
    collapse_double_numeric_parentheses,
    enforce_negative_parentheses,
    sanitize_question_text_display,
    infer_fraction_display_mode,
    has_decimal_number,
    format_fraction_mixed_display,
    healer_rule_explain,
    sanitize_rule_explain,
    build_readable_healer_logs,
    force_fraction_answer_text,
    init_healer_trace,
    recompute_regex_totals,
    apply_sanitize_report_to_trace,
    apply_display_report_to_trace,
    add_o1_fix,
    sanitize_result_question,
    format_result_question_display,
    recompute_result_answer,
    maybe_add_o1_fix,
)
from .live_show_iso_guard import (
    evaluate_iso_style_guard,
    append_iso_style_guard_logs,
    append_fallback_switch_log,
)

__all__ = [
    'ASTHealer', 
    'RegexHealer', 
    'fix_code_syntax',
    'clean_redundant_imports',
    'remove_forbidden_functions_unified',
    'collapse_double_numeric_parentheses',
    'enforce_negative_parentheses',
    'sanitize_question_text_display',
    'infer_fraction_display_mode',
    'has_decimal_number',
    'format_fraction_mixed_display',
    'healer_rule_explain',
    'sanitize_rule_explain',
    'build_readable_healer_logs',
    'force_fraction_answer_text',
    'init_healer_trace',
    'recompute_regex_totals',
    'apply_sanitize_report_to_trace',
    'apply_display_report_to_trace',
    'add_o1_fix',
    'sanitize_result_question',
    'format_result_question_display',
    'recompute_result_answer',
    'maybe_add_o1_fix',
    'evaluate_iso_style_guard',
    'append_iso_style_guard_logs',
    'append_fallback_switch_log',
]
