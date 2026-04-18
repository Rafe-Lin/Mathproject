# \統計\次數分配表
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「次數分配表」的題目。
    """
    data = sorted([random.randint(50, 99) for _ in range(20)])
    data_str = ", ".join(map(str, data))
    
    if level == 1:
        question_text = f"有一組數據如下：{data_str}。\n若第一組為 50~60 分，請問 60~70 分這一組的次數是多少？"
        count = sum(1 for x in data if 60 <= x < 70)
        correct_answer = str(count)
    else: # level 2
        group_start = 60
        group_end = 70
        question_text = f"在製作次數分配表時，對於 60~70 分這一組，其「組中點」是多少？"
        correct_answer = str((group_start + group_end) / 2)
        
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    return check_answer(user_answer, correct_answer, check_type='numeric')