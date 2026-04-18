# \複數\共軛複數與絕對值
import random
import math
from .utils import check_answer

def generate(level=1):
    """
    生成一道「共軛複數與絕對值」的題目。
    """
    z = complex(random.randint(-10, 10), random.randint(-10, 10))
    
    if level == 1:
        question_text = f"請求出複數 z = {z} 的共軛複數。(格式: a+bi)"
        ans = z.conjugate()
        correct_answer = f"{int(ans.real)}{'+' if ans.imag >= 0 else ''}{int(ans.imag)}i".replace("+-","-")
    else: # level 2
        question_text = f"請求出複數 z = {z} 的絕對值 |z|。(四捨五入至小數點後一位)"
        ans = abs(z)
        correct_answer = str(round(ans, 1))
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    if 'i' in correct_answer:
        return check_answer(user_answer.replace(" ", ""), correct_answer)
    else:
        return check_answer(user_answer, correct_answer, check_type='numeric')