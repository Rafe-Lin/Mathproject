[[MODE:BENCHMARK]]
【說明】本檔為實驗／大量出題用程式碼結構。Pattern Catalogue 與辨識規則由憲法 (SKILL.md) 提供，scaler 組裝時會一併注入。**不得使用 sympy**；根式運算僅透過 **RadicalOps** 與整數／`Fraction` 運算。

【MCRI 在生成程式中的體現】
- **語法 (M)**：`generate`／`check` 可執行；字串內 LaTeX 使用 `\\` 跳脫。
- **邏輯 (C)**：`correct_answer` 必須由 `RadicalOps.add_term` → `RadicalOps.format_expression`（及必要時 `mul_terms`／`simplify`）推導，與題幹數值自洽。
- **渲染 (R)**：輸出之 LaTeX 片段可被常見數學渲染器顯示。
- **同構 (I)**：變數僅為 int、`Fraction`、或規定之元組／列表，**禁止**以運算式字串當資料。

【RadicalOps LaTeX 偽代碼】
- **`format_term_unsimplified(c, r, is_leading)`**：`c==1,r≠1` → `\\sqrt{r}`；`c==-1,r≠1` → 首項 `-\\sqrt{r}`／中項 ` - \\sqrt{r}`；`r==1` → `str(c)`；**禁止** `*`、`sqrt(`。
- **`format_expression({r: c, ...})`**：radicand **升序**；首項負號緊貼；後續 ` + `／` - ` + 係數絕對值。例 `{3: -4, 5: 2}` → `-4\\sqrt{3} + 2\\sqrt{5}`。

【強烈建議程式碼結構】
```python
import random
import math
from fractions import Fraction
# RadicalOps、FractionOps 由 scaler 自動注入；禁止 import sympy

def generate(level=1, **kwargs):
    if level == 1:
        # Level 1：單項化簡 — 先 (c,r) 分解，再 simplify，最後併入容器並 format_expression
        c = random.choice([-3, -2, 1, 2, 3])
        r = random.choice([8, 12, 18, 20, 24, 27, 32, 45, 48, 50, 72, 75])

        question_text = f"化簡 ${RadicalOps.format_term_unsimplified(c, r, True)}$"

        sc, sr = RadicalOps.simplify(c, r)
        final_terms = {}
        RadicalOps.add_term(final_terms, sc, sr)
        correct_answer = RadicalOps.format_expression(final_terms)

        return {
            'question_text': question_text,
            'answer': '',
            'correct_answer': correct_answer,
            'mode': 1
        }

    elif level == 2:
        # Level 2：加減合併 — 以空 dict 起頭，迴圈 add_term 完成同類項 healing
        base_r = random.choice([2, 3, 5, 7])
        candidates = [base_r * (i**2) for i in range(2, 6)]

        terms = []
        for _ in range(random.randint(3, 4)):
            c = random.choice([-5, -4, -3, -2, 2, 3, 4, 5])
            r = random.choice(candidates)
            terms.append((c, r))

        part_strs = []
        for i, (c, r) in enumerate(terms):
            part_strs.append(RadicalOps.format_term_unsimplified(c, r, i == 0))

        question_text = f"化簡 ${''.join(part_strs)}$"

        final_terms = {}
        for c, r in terms:
            RadicalOps.add_term(final_terms, c, r)

        correct_answer = RadicalOps.format_expression(final_terms)

        return {
            'question_text': question_text,
            'answer': '',
            'correct_answer': correct_answer,
            'mode': 1
        }

    else:
        # Level 3：乘法／分配律 — mul_terms 得新項後再 add_term 併入
        c1 = random.choice([-3, -2, 2, 3])
        r1 = random.choice([2, 3, 5])

        c2 = random.choice([1, 2, 3])
        r2 = random.choice([6, 10, 15])

        c3 = random.choice([-3, -2, 2, 3])
        r3 = random.choice([2, 3, 5])

        t1 = RadicalOps.format_term_unsimplified(c1, r1, True)
        t2 = RadicalOps.format_term_unsimplified(c2, r2, True)
        t3 = RadicalOps.format_term_unsimplified(c3, r3, False)

        question_text = f"化簡 $({t1}) \\times ({t2}{t3})$"

        final_terms = {}
        new_c1, new_r1 = RadicalOps.mul_terms(c1, r1, c2, r2)
        RadicalOps.add_term(final_terms, new_c1, new_r1)

        new_c2, new_r2 = RadicalOps.mul_terms(c1, r1, c3, r3)
        RadicalOps.add_term(final_terms, new_c2, new_r2)

        correct_answer = RadicalOps.format_expression(final_terms)

        return {
            'question_text': question_text,
            'answer': '',
            'correct_answer': correct_answer,
            'mode': 1
        }

def check(user_answer, correct_answer):
    correct = str(user_answer).strip() == str(correct_answer).strip()
    return {'correct': correct, 'result': '正確' if correct else '錯誤'}
```

【檢查清單】
- [ ] **是否完全排除 sympy？**（無 `sympy`／`sp.`）
- [ ] **變數命名與結構是否符合 SKILL.md 的 vars 規範？**（純數值參數，無運算式字串）
- [ ] 必須 `import random`、`import math`、`from fractions import Fraction`
- [ ] 根式狀態以 `(coeff, radicand)` 或合併後 `dict` 表示，不得依賴未化簡字串做運算
- [ ] 嚴禁 `int(str.split(...))` 這類脆弱解析
- [ ] `format_expression` 輸入必須為合併後之 `dict`
- [ ] 輸出 Python code only, no comments
[[END_MODE:BENCHMARK]]
