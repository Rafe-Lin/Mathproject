# \統計\中位數 (已分組)
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「中位數 (已分組)」的題目。
    """
    groups = ["50-60", "60-70", "70-80", "80-90", "90-100"]
    freqs = [random.randint(2, 8) for _ in range(5)]
    total_count = sum(freqs)
    median_pos = total_count / 2
    
    table_str = (
        "某班數學成績的次數分配表如下：\n"
        "分數(分) | 50-60 | 60-70 | 70-80 | 80-90 | 90-100\n"
        "--- | --- | --- | --- | --- | ---\n"
        f"次數(人) | {freqs[0]} | {freqs[1]} | {freqs[2]} | {freqs[3]} | {freqs[4]}"
    )
    
    question_text = f"{table_str}\n請問中位數在哪一個組距中？"
    
    cum_freq = 0
    for i, freq in enumerate(freqs):
        cum_freq += freq
        if cum_freq >= median_pos:
            correct_answer = groups[i]
            break
            
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user_answer = user_answer.replace(" ", "")
    return check_answer(user_answer, correct_answer)