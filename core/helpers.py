# -*- coding: utf-8 -*-
"""
=============================================================================
模組名稱 (Module Name): core/helpers.py
功能說明 (Description): 數學輔助工具模組，提供各種驗證函式 (如答案比對) 與數學表達式格式化工具 (如多項式字串化)。
執行語法 (Usage): 由系統調用
版本資訊 (Version): V2.0
更新日期 (Date): 2026-01-13
維護團隊 (Maintainer): Math AI Project Team
=============================================================================
"""
"""此模組提供各種輔助函式，主要用於驗證使用者答案（如餘數、因式、方程式等）以及格式化數學表達式（如多項式、不等式）。"""

# ==============================================================================
# Helper Functions (Formatting, Checking)
# ==============================================================================

# --- Validation Functions (Referenced by name) ---
def validate_remainder(user_answer, correct_answer):
    # 簡單的字串比較
    return str(user_answer).strip().lower() == str(correct_answer).strip().lower()

def validate_factor(user_answer, correct_answer):
    # 判斷 '是' 或 '否'
    return str(user_answer).strip() == str(correct_answer)

def validate_linear_equation(user_answer, correct_answer):
    # 判斷 x=... 或 y=...
    return str(user_answer).strip().lower() == str(correct_answer).strip().lower()

def validate_check_point(user_answer, correct_answer):
    # 判斷 '是' 或 '否'
    return str(user_answer).strip() == str(correct_answer)

def validate_multiple_choice(user_answer, correct_answer):
    """Validates multiple choice questions by comparing the selected option (e.g., 'A') with the correct answer."""
    return str(user_answer).strip().upper() == str(correct_answer).strip().upper()

# --- Formatting Functions ---
def format_polynomial(coeffs):
    """將係數列表轉換成漂亮的多項式字串"""
    terms = []
    degree = len(coeffs) - 1
    for i, coeff in enumerate(coeffs):
        power = degree - i
        if coeff == 0:
            continue
        term = ""
        if coeff > 0:
            if i > 0:
                term += " + "
        else:
            term += " - "
        abs_coeff = abs(coeff)
        if abs_coeff != 1 or power == 0:
            term += str(abs_coeff)
        if power == 1:
            term += "x"
        elif power > 1:
            term += f"x^{power}"
        terms.append(term)
    if not terms:
        return "0"
    return "".join(terms)

def format_linear_equation_lhs(a, b):
    """將係數 (a, b) 轉換成 "ax + by" 的漂亮字串"""
    terms = []
    if a == 1:
        terms.append("x")
    elif a == -1:
        terms.append("-x")
    elif a != 0:
        terms.append(f"{a}x")
    if b > 0:
        if a != 0:
            terms.append(" + ")
        if b == 1:
            terms.append("y")
        else:
            terms.append(f"{b}y")
    elif b < 0:
        if a != 0:
            terms.append(" - ")
        else:
            terms.append("-")
        if b == -1:
            terms.append("y")
        else:
            terms.append(f"{abs(b)}y")
    if not terms:
        return "0"
    return "".join(terms)

def check_inequality(a, b, c, sign, x, y):
    """檢查點 (x, y) 是否滿足 ax + by [sign] c"""
    lhs = (a * x) + (b * y)
    if sign == '>':
        return lhs > c
    if sign == '>=':
        return lhs >= c
    if sign == '<':
        return lhs < c
    if sign == '<=':
        return lhs <= c
    return False

def format_inequality(a, b, c, sign):
    """將係數 (a, b, c) 和符號轉換成 "ax + by [sign] c" 的字串"""
    lhs_str = format_linear_equation_lhs(a, b)
    return f"{lhs_str} {sign} {c}"
