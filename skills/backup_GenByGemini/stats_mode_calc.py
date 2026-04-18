# \統計\眾數
import random
from collections import Counter
from .utils import check_answer

def generate(level=1):
    """
    生成一道「眾數」的題目。
    """
    if level == 1:
        # 構造單一眾數
        mode = random.randint(1, 10)
        data = [random.randint(1, 10) for _ in range(8)] + [mode, mode, mode]
        random.shuffle(data)
        correct_answer = str(mode)
    else: # level 2, 雙眾數或無眾數
        mode1, mode2 = random.randint(1, 5), random.randint(6, 10)
        data = [1, 2, 3, 4, 5, 6, 7, 8] + [mode1, mode1, mode2, mode2]
        random.shuffle(data)
        correct_answer = f"{mode1},{mode2}"
        
    data_str = ", ".join(map(str, data))
    question_text = f"請求出數據 {data_str} 的眾數。(若有多個，請用逗號分隔)"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user_parts = sorted(user_answer.strip().replace(" ", "").split(','))
    correct_parts = sorted(correct_answer.strip().split(','))
    return check_answer(",".join(user_parts), ",".join(correct_parts))