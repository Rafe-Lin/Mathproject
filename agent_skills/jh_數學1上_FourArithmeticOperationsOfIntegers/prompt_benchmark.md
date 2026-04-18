【任務】
實作 `def generate(level=1, **kwargs)`，生成整數四則運算題目。
題目結構必須為：括號內混合運算 + 絕對值 + (Level 3: 高難度多層混和)。
返回 dict: `{'question_text': str, 'answer': '', 'correct_answer': str, 'mode': 1}`

【絕對禁止輸出 thinking 或任何非 code 內容】
- 嚴禁寫任何思考過程、解釋、註解
- 嚴禁寫 "Okay, I need to..." 或 "Let me think..."
- 直接輸出 Python code，沒有任何前言、後語
- 如果違反，直接 0 分

【核心規則】
1. **題目結構**：
   - Level 1: Part 1 + Part 2
   - Level 2: Part 1 - Part 2 + Part 3
   - Level 3: -Part 1 + Part 2 - Part 3 + K
2. **數值範圍**：
   - Level 1: -20 ~ 20
   - Level 2: -50 ~ 50
   - Level 3: -100 ~ 100
3. **格式化要求**：
   - 所有負數必須使用 `IntegerOps.fmt_num(n)` 包裹。
   - 題目中的乘號用 `\times`，除號用 `\div`。

【強烈建議程式碼結構】
```python
import random
import math
# IntegerOps is injected automatically

def generate(level=1, **kwargs):
    # 1. Scaling
    if level == 1:
        r_min, r_max = -20, 20
        div_max = 10
    elif level == 2:
        r_min, r_max = -50, 50
        div_max = 20
    else:
        r_min, r_max = -100, 100
        div_max = 30
        
    def rand_nz(a, b):
        choices = [x for x in range(a, b+1) if x != 0]
        if not choices: return 1
        return random.choice(choices)

    # Part 1: Complex Division [(a*m + b) / divisor]
    divisor = rand_nz(2, div_max)
    quotient = rand_nz(-15, 15)
    dividend = divisor * quotient
    
    m = rand_nz(2, 5)
    a_approx = dividend // m
    if a_approx == 0: a_approx = 5
    a = rand_nz(a_approx - 5, a_approx + 5)
    b = dividend - (a * m)
    
    # 格式化 Part 1
    fmt = IntegerOps.fmt_num
    part1_str = f"[({fmt(a)} \\times {fmt(m)}) + {fmt(b)}] \\div {fmt(divisor)}"
    part1_val = quotient
    
    # Part 2: Absolute Value |d*e - f + g|
    d = rand_nz(-10, 15)
    e = rand_nz(-10, 10)
    f = rand_nz(1, 20)
    g = rand_nz(-10, 10)
    
    if level == 1:
        part2_str = f"|{fmt(d)} \\times {fmt(e)} - {fmt(f)}|"
        part2_val = abs(d * e - f)
    else:
        part2_str = f"|{fmt(d)} \\times {fmt(e)} - {fmt(f)} + {fmt(g)}|"
        part2_val = abs(d * e - f + g)

    # Part 3: Extra Term (h*i - j)
    h = rand_nz(-10, 10)
    i = rand_nz(2, 5)
    j = rand_nz(1, 10)
    part3_str = f"({fmt(h)} \\times {fmt(i)} - {fmt(j)})"
    part3_val = h * i - j
        
    # Final Assembly
    k = rand_nz(-50, 50)
    
    if level == 1:
        question_text = f"計算 ${part1_str} + {part2_str}$ 的值。"
        ans = part1_val + part2_val
    elif level == 2:
        question_text = f"計算 ${part1_str} - {part2_str} + {part3_str}$ 的值。"
        ans = part1_val - part2_val + part3_val
    else:
        question_text = f"計算 $- {part1_str} + {part2_str} - {part3_str} + {fmt(k)}$ 的值。"
        ans = -part1_val + part2_val - part3_val + k
        
    return {
        'question_text': question_text,
        'answer': '',       # 必須為空字串
        'correct_answer': str(int(ans)),
        'mode': 1
    }

def check(user_answer, correct_answer):
    try:
        if str(user_answer).strip() == str(correct_answer).strip():
            return {'correct': True, 'result': '正確'}
        if abs(float(user_answer) - float(correct_answer)) < 1e-6:
            return {'correct': True, 'result': '正確'}
    except:
❌ 輸出 Markdown 代碼塊 → 直接寫 code
⚠️ Output Python code ONLY. No introduction. No comments. No thinking.
/no_think