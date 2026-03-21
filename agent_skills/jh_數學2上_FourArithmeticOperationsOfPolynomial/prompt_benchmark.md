【課本例題風格】
**Level 1**（加減法）：
```
計算 $(3x^{2} - 2x + 1) + (-x^{2} + 5x - 3)$。
答案：2x^2+3x-2
```

**Level 2**（乘法展開）：
```
展開並化簡 $(x + 2)(2x^{2} - 3x + 1)$。
答案：2x^3+x^2-5x+2
```

**Level 3**（求未知多項式）：
```
若 $(3x^{2} - x + 2) + P = 5x^{2} + 4x - 1$，求多項式 $P$。
答案：2x^2+5x-3
```

【完整程式碼（必須照此結構複製）】
```python
import random
# PolynomialOps is injected automatically

def generate(level=1, **kwargs):
    var = 'x'

    if level == 1:
        # 加減法 — 課本例題格式
        deg_a = random.randint(2, 3)
        deg_b = random.randint(2, 3)
        coeffs_a = PolynomialOps.random_poly(deg_a)
        coeffs_b = PolynomialOps.random_poly(deg_b)
        op = random.choice(['+', '-'])
        if op == '+':
            result_coeffs = PolynomialOps.add(coeffs_a, coeffs_b)
        else:
            result_coeffs = PolynomialOps.sub(coeffs_a, coeffs_b)
        a_latex = PolynomialOps.format_latex(coeffs_a, var)
        b_latex = PolynomialOps.format_latex(coeffs_b, var)
        question_text = f'計算 $({a_latex}) {op} ({b_latex})$。'
        correct_answer = PolynomialOps.format_plain(result_coeffs, var)

    elif level == 2:
        # 乘法展開 — 課本例題格式
        coeffs_a = PolynomialOps.random_poly(1)
        coeffs_b = PolynomialOps.random_poly(2)
        result_coeffs = PolynomialOps.mul(coeffs_a, coeffs_b)
        a_latex = PolynomialOps.format_latex(coeffs_a, var)
        b_latex = PolynomialOps.format_latex(coeffs_b, var)
        question_text = f'展開並化簡 $({a_latex})({b_latex})$。'
        correct_answer = PolynomialOps.format_plain(result_coeffs, var)

    else:  # level 3
        # 求未知多項式 P — 課本例題格式
        deg_a = random.randint(1, 2)
        deg_b = random.randint(2, 3)
        coeffs_a = PolynomialOps.random_poly(deg_a)
        coeffs_b = PolynomialOps.random_poly(deg_b)
        a_latex = PolynomialOps.format_latex(coeffs_a, var)
        b_latex = PolynomialOps.format_latex(coeffs_b, var)
        choice = random.choice(['A+P=B', 'P-A=B', 'A-P=B'])
        if choice == 'A+P=B':
            result_coeffs = PolynomialOps.sub(coeffs_b, coeffs_a)
            question_text = f'若 $({a_latex}) + P = {b_latex}$，求多項式 $P$。'
        elif choice == 'P-A=B':
            result_coeffs = PolynomialOps.add(coeffs_b, coeffs_a)
            question_text = f'若 $P - ({a_latex}) = {b_latex}$，求多項式 $P$。'
        else:
            result_coeffs = PolynomialOps.sub(coeffs_a, coeffs_b)
            question_text = f'若 $({a_latex}) - P = {b_latex}$，求多項式 $P$。'
        correct_answer = PolynomialOps.format_plain(result_coeffs, var)

    return {
        'question_text': question_text,
        'answer': '',
        'correct_answer': correct_answer,
        'mode': 1
    }

def check(user_answer, correct_answer):
    correct = str(user_answer).strip().replace(' ', '') == str(correct_answer).strip().replace(' ', '')
    return {'correct': correct, 'result': '正確' if correct else '錯誤'}
```

【檢查清單】
✅ 必須 `import random`
✅ `var = 'x'` — 只能 x
✅ Level 2 題目前綴為 `展開並化簡`（課本格式）
✅ Level 3 未知數用 `$P$`（課本格式）
✅ 答案用 `format_plain`（無空格）
✅ 輸出 Python code only, no thinking, no comments
/no_think