# \統計\變異數與標準差 (已分組)
import random
import math
from .utils import check_answer

def generate(level=1):
    """
    生成一道「變異數與標準差 (已分組)」的題目。
    """
    groups = ["10-20", "20-30", "30-40"]
    midpoints = [15, 25, 35]
    freqs = [random.randint(2, 8) for _ in range(3)]
    
    table_str = (
        "某班學生成績的次數分配表如下：\n"
        "組距 | 10-20 | 20-30 | 30-40\n"
        "--- | --- | --- | ---\n"
        f"次數 | {freqs[0]} | {freqs[1]} | {freqs[2]}"
    )
    
    question_text = f"{table_str}\n請估算這組數據的標準差。(四捨五入至小數點後一位)"
    n = sum(freqs)
    mean = sum(f * m for f, m in zip(freqs, midpoints)) / n
    variance = sum(f * ((m - mean)**2) for f, m in zip(freqs, midpoints)) / n
    correct_answer = str(round(math.sqrt(variance), 1))
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    return check_answer(user_answer, correct_answer, check_type='numeric')