# \統計\累積次數
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「累積次數」的題目。
    """
    freqs = [random.randint(2, 8) for _ in range(5)]
    table_str = (
        "某班數學成績的次數分配表如下：\n"
        "分數(分) | 50-60 | 60-70 | 70-80 | 80-90 | 90-100\n"
        "--- | --- | --- | --- | --- | ---\n"
        f"次數(人) | {freqs[0]} | {freqs[1]} | {freqs[2]} | {freqs[3]} | {freqs[4]}"
    )
    
    if level == 1:
        question_text = f"{table_str}\n請問「70分以下」的累積次數是多少人？"
        correct_answer = str(freqs[0] + freqs[1])
    else: # level 2
        question_text = f"{table_str}\n請問「80分以上」的累積次數是多少人？"
        correct_answer = str(freqs[3] + freqs[4])
        
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    return check_answer(user_answer, correct_answer, check_type='numeric')