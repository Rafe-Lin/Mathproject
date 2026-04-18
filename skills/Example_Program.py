# ==============================================================================
# ID: skills/Example_Program.py (V15.6 Golden Rule)
# ⚠️ 首席架構師最高指令：
# 1. 嚴禁使用 += 拼接 LaTeX。問句必須「一次性」定義在模板字串中。
# 2. 嚴禁 f-string，嚴禁 {{ }}。在 r"..." 模板中，LaTeX 指令請用單大括號 {cases}。
# 3. 答案必須手動格式化為 x=a, y=b 格式 (禁止回傳字典)。
# ==============================================================================

import random

def generate_linear_system():
    """示範：代入消去法 (100% 鏡射課本三題型)"""
    # 1. 先定解 (x, y)
    vx, vy = random.randint(1, 5), random.randint(1, 5)
    
    # 2. 型態鏡射
    # Type 1: x=2y | Type 2: y=3-9x | Type 3: x+4y=-1 (其中一個係數為1/-1)
    p_type = random.choice([1, 2, 3])
    
    if p_type == 1: # x = ky
        k = random.randint(2, 4)
        vx = k * vy
        eq1 = r"x = {k}y".replace("{k}", str(k))
        eq2 = r"x + y = {s}".replace("{s}", str(vx + vy))
    elif p_type == 2: # y = ax + b
        a, b = random.randint(2, 4), random.randint(1, 10)
        vy = a * vx + b
        eq1 = r"y = {a}x + {b}".replace("{a}", str(a)).replace("{b}", str(b))
        eq2 = r"2x + y = {s}".replace("{s}", str(2 * vx + vy))
    else: # ax + by = c (其中一係數為 1)
        eq1 = r"x + 4y = {s}".replace("{s}", str(vx + 4 * vy))
        eq2 = r"5x - y = {s}".replace("{s}", str(5 * vx - vy))

    # [V15.6 核心修復] 一次性定義，標籤名稱絕不重複，嚴禁 +=
    tpl = r"解聯立方程式：$\begin{cases} {e1} \\ {e2} \end{cases}$"
    q_text = tpl.replace("{e1}", eq1).replace("{e2}", eq2)
    
    # [核心修復] 乾淨的字串答案 (手動格式化)
    ans = r"x={x}, y={y}".replace("{x}", str(vx)).replace("{y}", str(vy))
    
    return {
        "question_text": q_text + r"\n(答案格式：請在手寫區作答)",
        "correct_answer": ans,
        "input_mode": "handwriting"
    }

def generate(level=1):
    return generate_linear_system()
