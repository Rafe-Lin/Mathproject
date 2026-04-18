# \統計\算術平均數 (未分組)
import random
import numpy as np
from .utils import check_answer

def generate(level=1):
    """
    生成一道「算術平均數 (未分組)」的題目。
    """
    data = [random.randint(1, 20) for _ in range(5)]
    
    if level == 1:
        question_text = f"請求出數據 {data} 的算術平均數。"
        correct_answer = str(np.mean(data))
    else: # level 2, 逆向提問
        mean = int(np.mean(data)) # 確保平均數為整數以簡化題目
        missing_val_index = random.randrange(len(data))
        missing_val = data[missing_val_index]
        data[missing_val_index] = 'x'
        question_text = f"已知一組數據 {str(data).replace("'", '')} 的平均數為 {mean}，請問 x 的值是多少？"
        correct_answer = str(missing_val)
        
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    return check_answer(user_answer, correct_answer, check_type='numeric')