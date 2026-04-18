# \統計\中位數 (未分組)
import random
import numpy as np
from .utils import check_answer

def generate(level=1):
    """
    生成一道「中位數 (未分組)」的題目。
    """
    if level == 1:
        # 奇數個數據
        data = sorted([random.randint(1, 50) for _ in range(random.choice([5, 7, 9]))])
    else: # level 2
        # 偶數個數據
        data = sorted([random.randint(1, 50) for _ in range(random.choice([6, 8, 10]))])
        
    data_str = ", ".join(map(str, data))
    question_text = f"請求出數據 {data_str} 的中位數。"
    correct_answer = str(np.median(data))
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    return check_answer(user_answer, correct_answer, check_type='numeric')