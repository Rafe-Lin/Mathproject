【任務】
實作 `def generate(level=1, **kwargs)`，生成「分數四則運算」題目。
題目結構必須為：中括號混合運算 + 除法 + 絕對值；Level 越高層次越深。
回傳 dict: `{'question_text': str, 'answer': '', 'correct_answer': str, 'mode': 1}`

【目標對齊（最高優先）】
1. 必須複製使用者提供題型的結構（同構），只替換數字，不替換運算拓撲。
2. 新題難度必須與原題相近，不可突然放大數值級距。
3. 題目與答案都必須符合七年級初學者可讀、可算、可驗算。

【絕對禁止輸出 thinking 或任何非 code 內容】
- 嚴禁寫任何思考過程、解釋、註解
- 嚴禁寫 "Okay, I need to..." 或 "Let me think..."
- 直接輸出 Python code，沒有任何前言、後語
- 如果違反，直接 0 分

【核心規則】
1. **題目結構**：
   - Level 1: `[Part 1] \div Part 2 + |Part 3|`
   - Level 2: `[Part 1 - Part 2] \div Part 3 + |Part 4|`
   - Level 3: `-[Part 1] + |Part 2| - (Part 3) + Part 4`
2. **分數範圍**：
    - Level 1~3: 分子 `-50 ~ 50`、分母 `-10 ~ 10`（分母不可為 0）
    - 題面分母建議避開 `±1`，降低題目退化成整數四則的機率。
    - 所有分子必須額外滿足硬限制：`-50 <= numerator <= 50`
    - 分子與分母的正負號必須隨機抽樣，不可固定某一位置永遠為正或永遠為負。
3. **格式化要求**：
   - 分數顯示必須使用 `FractionOps.to_latex(...)`
   - 乘號必須用 `\times`，除號必須用 `\div`
   - 中括號用 `\left[ ... \right]`
   - 絕對值用 `\left| ... \right|`
4. **答案要求**：
    - ✅ 答案可以是分數，不必為整數。
   - 結果若為整數，`correct_answer` 輸出整數字串
   - 否則輸出 `a/b` 最簡分數字串
5. **七年級友善限制**：
    - 最終答案建議限制為：`|numerator| <= 40` 且 `denominator <= 12`
    - 若超出範圍，應重新抽樣，避免出現過大數字
6. **題面美觀限制（Ab2 必做）**：
    - 題面禁止出現 `\\frac{n}{1}`，分母為 1 必須直接顯示整數。
    - 題面分數必須先約分（禁止 `2/10`、`10/15` 這類未約分表示）。
    - 題面若出現 `|numerator| > denominator` 的分數，必須以「帶分數」顯示（例如 `17/4` 顯示為 `4\frac{1}{4}`，`-13/5` 顯示為 `-2\frac{3}{5}`）。
    - 題面禁止小數表示分數值（例如 `2.5`、`-1.75`）。
    - 題面中任一單一整數建議 `|n| <= 50`，超過就重抽。
    - 題面分母建議 `|denominator| <= 10` 且分母不可為 0。
    - 最終答案若為分數，建議 `|numerator| <= 120` 且 `denominator <= 30`，超過就重抽。

【強烈建議程式碼結構】
```python
import random
import math
from fractions import Fraction


def generate(level=1, **kwargs):
    fmt = IntegerOps.fmt_num

    if level == 1:
        n_min, n_max = -50, 50
        d_min, d_max = -10, 10
    elif level == 2:
        n_min, n_max = -50, 50
        d_min, d_max = -10, 10
    else:
        n_min, n_max = -50, 50
        d_min, d_max = -10, 10

    def rand_frac():
        num = IntegerOps.random_nonzero(n_min, n_max)
        den = random.randint(d_min, d_max)
        while den == 0 or abs(den) == 1:
            den = random.randint(d_min, d_max)
        return Fraction(num, den)

    def latex_frac_clean(x):
        x = Fraction(x)
        if x.denominator == 1:
            return str(x.numerator)
        return FractionOps.to_latex(x)

    for _ in range(40):
        try:
            a = rand_frac()
            b = rand_frac()
            c = rand_frac()
            d = rand_frac()
            e = rand_frac()
            f = rand_frac()
            g = rand_frac()
            h = rand_frac()

            if c == 0 or f == 0:
                continue

            p1_val = (a + b) * c
            p2_val = d
            p3_val = abs(e * f - g)

            p1_str = f"\\left[{latex_frac_clean(a)} + {latex_frac_clean(b)}\\right] \\times {latex_frac_clean(c)}"
            p2_str = f"\\left({latex_frac_clean(p2_val)}\\right)"
            p3_str = f"\\left|{latex_frac_clean(e)} \\times {latex_frac_clean(f)} - {latex_frac_clean(g)}\\right|"

            if level == 1:
                math_str = f"\\left[{p1_str}\\right] \\div {p2_str} + {p3_str}"
                ans = Fraction(p1_val, 1) / p2_val + p3_val
            elif level == 2:
                p4_val = abs(a - b / c)
                p4_str = f"\\left|{latex_frac_clean(a)} - {latex_frac_clean(b)} \\div {latex_frac_clean(c)}\\right|"
                math_str = f"\\left[{p1_str} - {latex_frac_clean(h)}\\right] \\div {p2_str} + {p4_str}"
                ans = (p1_val - h) / p2_val + p4_val
            else:
                p4_val = h
                p4_str = latex_frac_clean(p4_val)
                math_str = f"-\\left[{p1_str}\\right] + {p3_str} - \\left({latex_frac_clean(d)} \\div {latex_frac_clean(f)}\\right) + {p4_str}"
                ans = -p1_val + p3_val - (d / f) + p4_val

            if ans.denominator == 1:
                correct = str(ans.numerator)
            else:
                correct = f"{ans.numerator}/{ans.denominator}"

            if abs(ans.numerator) > 120 or ans.denominator > 30:
                continue

            if any(abs(x.numerator) > 50 for x in [a, b, c, d, e, f, g, h]):
                continue

            return {
                'question_text': f'計算 $' + math_str + '$ 的值。',
                'answer': '',
                'correct_answer': correct,
                'mode': 1
            }
        except Exception:
            continue

    return {'question_text': 'Error', 'answer': '', 'correct_answer': '0', 'mode': 1}


def check(user_answer, correct_answer):
    try:
        ua = str(user_answer).strip()
        ca = str(correct_answer).strip()
        if ua == ca:
            return {'correct': True, 'result': '正確'}
        if Fraction(ua) == Fraction(ca):
            return {'correct': True, 'result': '正確'}
    except Exception:
        pass
    return {'correct': False, 'result': '錯誤'}
```

❌ 輸出 Markdown 代碼塊 → 直接寫 code
⚠️ Output Python code ONLY. No introduction. No comments. No thinking.
/no_think