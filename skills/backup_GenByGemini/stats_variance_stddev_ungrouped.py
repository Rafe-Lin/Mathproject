# \統計\變異數與標準差 (未分組)
import random
import numpy as np
from .utils import check_answer

def generate(level=1):
    """
    生成一道「變異數與標準差 (未分組)」的題目。
    """
    # 為了讓答案漂亮，構造一組平均數為整數的數據
    mean = random.randint(10, 20)
    data = [mean-4, mean-2, mean, mean+2, mean+4]
    random.shuffle(data)
    data_str = ", ".join(map(str, data))
    
    if level == 1:
        question_text = f"請求出數據 {data_str} 的母體變異數 (σ²)。(四捨五入至小數點後兩位)"
        correct_answer = str(round(np.var(data), 2))
    else: # level 2
        question_text = f"請求出數據 {data_str} 的母體標準差 (σ)。(四捨五入至小數點後兩位)"
        correct_answer = str(round(np.std(data), 2))

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    return check_answer(user_answer, correct_answer, check_type='numeric')