# \函數\對數大小比較
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「對數大小比較」的題目。
    """
    if level == 1: # 同底
        base = random.randint(2, 5)
        val1 = random.randint(10, 20)
        val2 = random.randint(30, 50)
        question_text = f"請比較 A = log_{base}({val1}) 與 B = log_{base}({val2}) 的大小。"
        correct_answer = "A < B"
    else: # level 2, 不同底
        base1 = 2
        base2 = 3
        val = 8
        question_text = f"請比較 A = log_{base1}({val}) 與 B = log_{base2}({val}) 的大小。"
        correct_answer = "A > B" # log2(8)=3, log3(8)<2
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user_answer = user_answer.replace(" ", "")
    return check_answer(user_answer, correct_answer)