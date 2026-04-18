# skills/quad_ineq_discriminant.py
import random
import fractions

def generate(level=1):
    """
    生成一道「判別式與二次不等式解」題目 (D <= 0)
    """
    # level 參數暫時未使用，但保留以符合架構
    # 隨機生成 a 和 h (頂點的 x 座標)
    a = random.choice([-4, -3, -2, -1, 1, 2, 3, 4])
    h = random.randint(-5, 5)

    # 隨機決定 D=0 或 D<0
    # D=0: 頂點在 x 軸上 (k=0)
    # D<0: 頂點不在 x 軸上 (k!=0, 且與 a 同號)
    if random.choice([True, False]): # D = 0
        k = 0
    else: # D < 0
        k = random.randint(1, 10) * (1 if a > 0 else -1)

    # 從頂點式 y = a(x-h)² + k 反向展開
    # y = a(x² - 2hx + h²) + k = ax² - 2ahx + ah² + k
    b = -2 * a * h
    c = a * h**2 + k

    # 隨機選擇不等式符號
    sign = random.choice(['>', '<', '>=', '<='])
    
    # 格式化不等式
    poly_str = format_polynomial(a, b, c)
    inequality_str = f"{poly_str} {sign} 0"

    # 判斷解
    if k != 0: # D < 0 (恆正或恆負)
        if (a > 0 and sign in ['>', '>=']) or (a < 0 and sign in ['<', '<=']):
            correct_answer = "所有實數"
        else:
            correct_answer = "無解"
    else: # D = 0 (頂點在 x 軸上)
        root_frac = fractions.Fraction(h)
        if root_frac.denominator == 1:
            root_val = root_frac.numerator
        else:
            # For graph questions, a decimal is more useful for the AI
            root_val = round(root_frac.numerator / root_frac.denominator, 2)
        root_str = str(root_val)

        if sign == '>':
            correct_answer = "所有實數" if a < 0 else f"x != {root_str}"
        elif sign == '<':
            correct_answer = "所有實數" if a > 0 else f"x != {root_str}"
        elif sign == '>=':
            correct_answer = f"x = {root_str}" if a < 0 else "所有實數"
        elif sign == '<=':
            correct_answer = f"x = {root_str}" if a > 0 else "所有實數"

    # 組裝題目
    question_text = (
        f"請解出以下二次不等式的範圍，並在下方的「數位計算紙」上，將解的範圍標示於數線上：\n\n"
        f"{inequality_str}\n\n"
        f"提示：可先計算判別式 D = b²-4ac，並思考二次函數圖形的開口方向與 x 軸的關係。\n"
        f"解的範圍可能是「所有實數」、「無解」、單一一個點、或排除單一一個點。\n"
        f"完成後，請點擊「AI 檢查」按鈕。"
    )

    context_string = f"解二次不等式 {inequality_str}，其解為 {correct_answer}"

    return {
        "question_text": question_text,
        "answer": None,
        "correct_answer": "graph",
        "context_string": context_string,
        "inequality_string": correct_answer,
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