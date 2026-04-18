import random
import numpy as np
from .utils import poly_to_string

def generate(level=1):
    """
    生成一道「連續綜合除法」的題目。
    將 f(x) 表示為 a(x-k)³ + b(x-k)² + c(x-k) + d
    """
    f_coeffs = [random.randint(-3, 3) for _ in range(4)]
    f = np.poly1d(f_coeffs)
    k = random.randint(-2, 2)
    
    question_text = f"請將多項式 f(x) = {poly_to_string(f)} 表示為 (x-{k}) 的多項式形式。\n(這是一道觀念/作圖題，請在計算紙上利用連續綜合除法求解)"
    return {"question_text": question_text, "answer": None, "correct_answer": "graph"}

def check(user_answer, correct_answer):
    return {"correct": True, "result": "觀念正確！使用連續綜合除法，由下往上讀取餘數即可得到係數。", "next_question": True}