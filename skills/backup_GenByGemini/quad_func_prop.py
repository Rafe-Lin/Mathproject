# skills/quad_func_prop.py
# 中文名稱：二次函數圖形特性 (繁體)
# 英文名稱：Quadratic Function Properties (Traditional)
# 內容描述：根據 y=ax²+bx+c 的 a 值判斷開口方向，並識別對稱軸 (x=−b/2a) 與頂點坐標。

import random
import fractions

def generate(level=1):
    """
    生成一道關於二次函數圖形特性的題目。
    """
    # level 參數暫時未使用，但保留以符合架構
    # 隨機生成係數 a, b, c
    a = random.choice([i for i in range(-5, 6) if i != 0])
    b = random.randint(-10, 10)
    c = random.randint(-10, 10)

    # 題目類型：開口方向、對稱軸、頂點坐標
    question_type = random.choice(['opening_direction', 'axis_of_symmetry', 'vertex'])

    func_str = f"y = {a}x²"
    if b > 0:
        func_str += f" + {b}x"
    elif b < 0:
        func_str += f" - {abs(b)}x"
    
    if c > 0:
        func_str += f" + {c}"
    elif c < 0:
        func_str += f" - {abs(c)}"

    if question_type == 'opening_direction':
        question_text = f"請問二次函數 {func_str} 的圖形開口朝向？ (請回答「上」或「下」)"
        correct_answer = "上" if a > 0 else "下"
    
    elif question_type == 'axis_of_symmetry':
        question_text = f"請問二次函數 {func_str} 的對稱軸方程式為何？ (請以 x=h 的格式作答)"
        # 使用分數表示以確保精確
        h = fractions.Fraction(-b, 2 * a)
        if h.denominator == 1:
            correct_answer = f"x={h.numerator}"
        else:
            correct_answer = f"x={h.numerator}/{h.denominator}"

    else: # vertex
        question_text = f"請問二次函數 {func_str} 的頂點坐標為何？ (請以 (h,k) 的格式作答)"
        h = fractions.Fraction(-b, 2 * a)
        # 計算 k = a*h^2 + b*h + c
        k = a * (h**2) + b * h + c
        
        h_str = str(h.numerator) if h.denominator == 1 else f"{h.numerator}/{h.denominator}"
        k_str = str(k.numerator) if k.denominator == 1 else f"{k.numerator}/{k.denominator}"
        correct_answer = f"({h_str},{k_str})"

    return {
        "question_text": question_text,
        "answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查使用者對二次函數特性的答案是否正確。
    """
    user_answer = user_answer.strip().replace(' ', '')
    
    if user_answer == correct_answer:
        return {"correct": True, "result": "完全正確！"}
    else:
        return {"correct": False, "result": f"答案不正確。正確答案是：{correct_answer}"}