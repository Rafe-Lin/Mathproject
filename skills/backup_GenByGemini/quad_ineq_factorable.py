# skills/quad_ineq_factorable.py
import random
from .utils import poly_to_string

def generate(level=1):
    """
    生成一道「可因式分解之二次不等式」題目
    """
    # level 參數暫時未使用，但保留以符合架構
    # 從因式分解 a(x-p)(x-q) 開始，確保題目可因式分解且根為整數
    a_coeff = random.choice([-2, -1, 1, 2])
    p = random.randint(-5, 5)
    q = random.randint(-5, 5)
    
    # 確保兩根不相等
    while p == q:
        q = random.randint(-5, 5)

    # 展開 a(x-p)(x-q) = a(x² - (p+q)x + pq) = ax² - a(p+q)x + apq
    a = a_coeff
    b = -a_coeff * (p + q)
    c = a_coeff * p * q

    # 隨機選擇不等式符號
    sign = random.choice(['>', '<', '>=', '<='])
    
    # 格式化多項式
    poly_str = poly_to_string([a, b, c])
    inequality_str = f"{poly_str} {sign} 0"

    # 決定解的區間
    root1 = min(p, q)
    root2 = max(p, q)
    
    # 判斷解是 "大於兩根" 還是 "介於兩根之間"
    # a > 0, > 0 => x > root2 或 x < root1
    # a > 0, < 0 => root1 < x < root2
    # a < 0, > 0 => root1 < x < root2
    # a < 0, < 0 => x > root2 或 x < root1
    is_outside_roots = (a > 0 and sign in ['>', '>=']) or \
                       (a < 0 and sign in ['<', '<='])

    if is_outside_roots:
        lower_sign = '<=' if sign in ['>=', '<='] else '<'
        upper_sign = '>=' if sign in ['>=', '<='] else '>'
        solution_str = f"x {lower_sign} {root1} 或 x {upper_sign} {root2}"
    else: # 介於兩根之間
        lower_sign = '<=' if sign in ['>=', '<='] else '<'
        upper_sign = '<=' if sign in ['>=', '<='] else '<'
        solution_str = f"{root1} {lower_sign} x {upper_sign} {root2}"

    # 組裝題目
    question_text = (
        f"請解出以下二次不等式的範圍，並在下方的「數位計算紙」上，將解的範圍標示於數線上：\n\n"
        f"{inequality_str}\n\n"
        f"提示：可先用十字交乘法因式分解，找出兩根，再判斷範圍。\n"
        f"完成後，請點擊「AI 檢查」按鈕。"
    )

    context_string = f"解二次不等式 {inequality_str}，其解為 {solution_str}"

    return {
        "question_text": question_text,
        "answer": None,
        "correct_answer": "graph",
        "context_string": context_string,
        "inequality_string": solution_str,
    }

def check(user_answer, correct_answer):
    """
    圖形題不走文字批改，由前端觸發 AI 分析。
    """
    return {
        "correct": False,
        "result": "請在數位計算紙上畫出解的範圍，然後點選「AI 檢查」。",
        "next_question": False
    }