# skills/factoring_cubes.py
import random

def generate(level=1):
    """
    生成一道「三次式因式分解 (立方公式)」題目
    """
    # level 參數暫時未使用，但保留以符合架構
    is_sum = random.choice([True, False])
    
    # 選擇基數 a 和 b
    a_base = random.randint(1, 3)
    b_base = random.randint(1, 4)
    
    a_cubed = a_base**3
    b_cubed = b_base**3

    if is_sum: # 立方和 a³ + b³
        poly_str = f"{a_cubed if a_cubed > 1 else ''}x³ + {b_cubed}"
        factor1 = f"({a_base if a_base > 1 else ''}x + {b_base})"
        factor2 = f"({a_base**2 if a_base**2 > 1 else ''}x² - {a_base*b_base}x + {b_base**2})"
    else: # 立方差 a³ - b³
        poly_str = f"{a_cubed if a_cubed > 1 else ''}x³ - {b_cubed}"
        factor1 = f"({a_base if a_base > 1 else ''}x - {b_base})"
        factor2 = f"({a_base**2 if a_base**2 > 1 else ''}x² + {a_base*b_base}x + {b_base**2})"

    # 處理 a=1 的情況
    poly_str = poly_str.replace("1x³", "x³").replace("1x²", "x²")
    factor1 = factor1.replace("1x", "x")
    factor2 = factor2.replace("1x²", "x²").replace(" 1x ", " x ")

    correct_answer = f"{factor1}{factor2}"
    
    question_text = f"請利用立方和或立方差公式，將 {poly_str} 因式分解。"
    context_string = f"將 {poly_str} 因式分解"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    """檢查使用者輸入的因式分解是否正確"""
    user_clean = user_answer.replace(" ", "").replace("²", "^2").replace("³", "^3")
    correct_clean = correct_answer.replace(" ", "").replace("²", "^2").replace("³", "^3")
    if user_clean == correct_clean:
        return {"correct": True, "result": f"完全正確！答案是 {correct_answer}。"}
    else:
        return {"correct": False, "result": f"答案不正確。正確答案是：{correct_answer}"}