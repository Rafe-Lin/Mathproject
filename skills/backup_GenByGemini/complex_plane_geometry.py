# \複數\複數平面
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「複數平面」的題目。
    """
    z = complex(random.randint(-10, 10), random.randint(-10, 10))
    
    if level == 1:
        question_text = f"複數 z = {z} 在複數平面上對應的點坐標為何？"
        correct_answer = f"({int(z.real)},{int(z.imag)})"
    else: # level 2
        question_text = f"複數平面上，點 P({int(z.real)}, {int(z.imag)}) 所代表的複數為何？ (格式: a+bi)"
        correct_answer = f"{int(z.real)}{'+' if z.imag >= 0 else ''}{int(z.imag)}i".replace("+-","-")
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user_answer = user_answer.replace(" ", "")
    return check_answer(user_answer, correct_answer)