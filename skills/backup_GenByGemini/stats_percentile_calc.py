# \統計\百分位數
import random
import numpy as np
from .utils import check_answer

def generate(level=1):
    """
    生成一道「百分位數」的題目。
    """
    # 為了方便計算，使用 10 個數據點
    data = sorted([random.randint(50, 100) for _ in range(10)])
    data_str = ", ".join(map(str, data))
    
    if level == 1:
        p = 50 # 第50百分位數即中位數
    else: # level 2
        p = random.choice([25, 75, 80, 90])
        
    question_text = f"請求出數據 {data_str} 的第 {p} 百分位數 (P{p})。"
    correct_answer = str(np.percentile(data, p, method='weibull')) # 使用常見的計算方法
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    return check_answer(user_answer, correct_answer, check_type='numeric')