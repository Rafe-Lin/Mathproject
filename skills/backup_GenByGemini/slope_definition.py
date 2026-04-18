# skills/slope_definition.py
import random
import fractions
import re

def generate(level=1):
    """
    生成一道「斜率定義 (兩點式)」題目
    """
    # level 參數暫時未使用，但保留以符合架構
    # 為了讓斜率是漂亮的整數或分數，我們先決定斜率 m = num/den
    num = random.randint(-5, 5)
    den = random.randint(1, 3)
    
    # 簡化分數
    slope = fractions.Fraction(num, den)
    num = slope.numerator
    den = slope.denominator

    # 接著生成點 A(x1, y1)
    x1 = random.randint(-10, 10)
    y1 = random.randint(-10, 10)

    # 根據斜率公式反推點 B(x2, y2)，確保 x2 != x1
    # m = (y2 - y1) / (x2 - x1)  =>  y2 = y1 + m * (x2 - x1)
    # 為了讓 y2 是整數，我們讓 (x2 - x1) 是 den 的倍數
    k = random.choice([-2, -1, 1, 2]) # 確保 x2 != x1
    x2 = x1 + k * den
    y2 = y1 + k * num

    # 組裝題目文字
    question_text = f"設 A({x1}, {y1})、B({x2}, {y2}) 為平面上兩點，求直線 AB 的斜率。"
    
    # 格式化正確答案
    if slope.denominator == 1:
        correct_answer = str(slope.numerator)
    else:
        correct_answer = f"{slope.numerator}/{slope.denominator}"

    context_string = f"計算點 A({x1}, {y1}) 和 B({x2}, {y2}) 的斜率"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    """
    檢查使用者輸入的斜率是否正確。
    能處理整數、小數、分數形式的答案。
    """
    user = user_answer.strip()
    correct = correct_answer.strip()

    try:
        # 將正確答案轉為浮點數
        if "/" in correct:
            num, den = map(int, correct.split('/'))
            correct_val = num / den
        else:
            correct_val = float(correct)

        # 將使用者答案轉為浮點數
        if "/" in user:
            num, den = map(int, user.split('/'))
            user_val = num / den
        else:
            user_val = float(user)

        # 比較浮點數值
        if abs(user_val - correct_val) < 1e-9:
            return {"correct": True, "result": f"完全正確！斜率是 {correct}。"}
        else:
            return {"correct": False, "result": f"答案不正確。正確答案是：{correct}"}
    except (ValueError, ZeroDivisionError):
        return {"correct": False, "result": f"請輸入有效的數字或分數格式。正確答案是：{correct}"}