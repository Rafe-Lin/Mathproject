# skills/synthetic_division.py
import random
import numpy as np
from .utils import poly_to_string

def generate(level=1):
    """
    生成一道「多項式綜合除法」題目 (圖形題)
    """
    # level 參數暫時未使用，但保留以符合架構
    # 生成一個 2 或 3 次多項式
    coeffs = [random.randint(-5, 5) for _ in range(random.randint(3, 4))]
    while coeffs[0] == 0: coeffs[0] = random.randint(1, 5)
    f = np.poly1d(coeffs)

    # 除式 x - a
    a = random.randint(-4, 4)
    divisor_str = f"x - {a}" if a > 0 else f"x + {abs(a)}" if a < 0 else "x"

    question_text = f"請在下方的「數位計算紙」上，使用綜合除法計算 ({poly_to_string(f)}) ÷ ({divisor_str}) 的商式與餘式。\n\n完成後，請點擊「AI 檢查」按鈕。"
    context_string = f"使用綜合除法計算 ({poly_to_string(f)}) ÷ ({divisor_str})"

    return {
        "question_text": question_text,
        "answer": None,
        "correct_answer": "graph",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    return {"correct": False, "result": "請在數位計算紙上寫下您的計算過程，然後點選「AI 檢查」。"}