# \複數\複數極式乘除
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「複數極式乘除」的題目。
    """
    r1, angle1 = random.randint(2, 5), random.randint(20, 100)
    r2, angle2 = random.randint(2, 5), random.randint(20, 100)
    
    z1_str = f"{r1}(cos{angle1}° + i sin{angle1}°)"
    z2_str = f"{r2}(cos{angle2}° + i sin{angle2}°)"
    
    if level == 1:
        question_text = f"已知 z₁ = {z1_str}，z₂ = {z2_str}，請問 z₁z₂ 的絕對值是多少？"
        correct_answer = str(r1 * r2)
    else: # level 2
        question_text = f"已知 z₁ = {z1_str}，z₂ = {z2_str}，請問 z₁/z₂ 的主輻角是多少度？"
        correct_answer = str((angle1 - angle2 + 360) % 360)
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    return check_answer(user_answer, correct_answer, check_type='numeric')