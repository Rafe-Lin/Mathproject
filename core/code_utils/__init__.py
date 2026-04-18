# -*- coding: utf-8 -*-
"""
=============================================================================
模組名稱 (Module Name): core/utils
功能說明 (Description): 工具函數集合，提供數學、LaTeX、檔案處理等通用功能
執行語法 (Usage): from core.utils import safe_choice, to_latex, ...
版本資訊 (Version): V2.0 (Refactored from code_generator.py)
更新日期 (Date): 2026-01-30
維護團隊 (Maintainer): Math AI Project Team
=============================================================================
"""

# 匯出所有工具函數（保持原函數名）
from .math_utils import (
    safe_choice, to_latex, fmt_num, safe_eval, is_prime,
    gcd, lcm, get_factors, clamp_fraction, safe_pow,
    factorial_bounded, nCr, nPr, rational_gauss_solve,
    normalize_angle, fmt_set, fmt_interval, fmt_vec, check,
    build_polynomial_text  # V10.0 新增：防止幻覺函數
)
from .latex_utils import clean_latex_output
from .file_utils import get_base_root, path_in_root, ensure_dir
from .unit_spec_loader import build_unit_pattern_spec, list_patterns_for_unit, make_pattern_skill_id

__all__ = [
    # Math utils
    'safe_choice', 'to_latex', 'fmt_num', 'safe_eval', 'is_prime',
    'gcd', 'lcm', 'get_factors', 'clamp_fraction', 'safe_pow',
    'factorial_bounded', 'nCr', 'nPr', 'rational_gauss_solve',
    'normalize_angle', 'fmt_set', 'fmt_interval', 'fmt_vec', 'check',
    'build_polynomial_text',  # V10.0 新增
    # LaTeX utils
    'clean_latex_output',
    # File utils
    'get_base_root', 'path_in_root', 'ensure_dir',
    # Unit spec loader
    'build_unit_pattern_spec', 'list_patterns_for_unit', 'make_pattern_skill_id',
]
