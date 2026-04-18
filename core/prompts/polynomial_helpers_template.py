# ============================================================================
# 標準多項式工具函數模板 - 供 LLM 參考使用
# [V47.15] Fix syntax error in comments
# ============================================================================

"""
此文件定義了處理多項式相關題目時的標準工具函數。
"""

# 🔴 答案格式鐵律（ANSWER FORMAT RULES）：
# 1. 僅包含數學結果，禁止任何前綴（如 \"f'(x) =\", \"Answer:\", \"Sol:\"）
# 2. 多個答案必須用逗號 \", \" 分隔
# 3. ❌ 禁止使用換行符號分隔 (例如 '\n'.join 是禁止的)

def _coeffs_to_terms(coeffs):
    '''係數列表 [a_n,...,a_0] → terms [(c,e),...]'''
    degree = len(coeffs) - 1
    return [(coeffs[i], degree - i) for i in range(len(coeffs))]

def _poly_to_latex(terms):
    '''terms → LaTeX (不含$)，例: \"3x^{2} - 5\"'''
    if not terms: return '0'
    parts = []
    for i, (c, e) in enumerate(sorted(terms, key=lambda x: x[1], reverse=True)):
        if c == 0: continue
        sign = '' if i == 0 else (' + ' if c > 0 else ' - ')
        abs_c = abs(c)
        if e == 0: val = str(abs_c)
        elif e == 1: val = f\"{abs_c}x\" if abs_c != 1 else \"x\"
        else: val = f\"{abs_c}x^{{{e}}}\" if abs_c != 1 else f\"x^{{{e}}}\"
        parts.append(f\"{sign}{val}\")
    return ''.join(parts).strip()

def _poly_to_plain(terms):
    '''terms → 純文本答案格式 (無空格)，例: \"3x^2-5\"'''
    if not terms: return '0'
    parts = []
    for i, (c, e) in enumerate(sorted(terms, key=lambda x: x[1], reverse=True)):
        if c == 0: continue
        sign = '' if i == 0 else ('+' if c > 0 else '-')
        abs_c = abs(c)
        if e == 0: val = str(abs_c)
        elif e == 1: val = f\"{abs_c}x\" if abs_c != 1 else \"x\"
        else: val = f\"{abs_c}x^{e}\" if abs_c != 1 else f\"x^{e}\"
        parts.append(f\"{sign}{val}\")
    return ''.join(parts).strip()

def _differentiate_poly(terms, order=1):
    '''求導 order 次，返回新 terms'''
    result = list(terms)
    for _ in range(order):
        new_terms = []
        for c, e in result:
            if e > 0:
                new_terms.append((c * e, e - 1))
        result = new_terms
    return result

def _deriv_symbol_latex(order):
    '''導數符號 LaTeX: f'(x), f''(x)'''
    return \"f'(x)\" if order == 1 else \"f''(x)\" if order == 2 else f\"f^{{({order})}}(x)\"
