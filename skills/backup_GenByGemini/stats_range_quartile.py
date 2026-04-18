# \統計\全距與四分位距
import random
import numpy as np
from .utils import check_answer

def generate(level=1):
    """
    生成一道「全距與四分位距」的題目。
    """
    # 為了方便計算四分位數，使用 11 或 15 個數據點
    data = sorted([random.randint(1, 100) for _ in range(random.choice([11, 15]))])
    data_str = ", ".join(map(str, data))
    
    if level == 1:
        question_text = f"請求出數據 {data_str} 的全距 (Range)。"
        correct_answer = str(max(data) - min(data))
    else: # level 2
        question_text = f"請求出數據 {data_str} 的四分位距 (Interquartile Range, Q.D.)。"
        # 使用 numpy 的百分位數計算
        q1 = np.percentile(data, 25)
        q3 = np.percentile(data, 75)
        correct_answer = str(q3 - q1)
        
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    return check_answer(user_answer, correct_answer, check_type='numeric')