# \圓錐曲線\橢圓標準式 (中心(0,0))
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「橢圓標準式 (中心(0,0))」的題目。
    """
    c = random.randint(3, 4)
    a = c + random.randint(1, 3)
    b = (a*a - c*c)**0.5
    
    if level == 1:
        question_text = f"一個橢圓的焦點為 (±{c}, 0)，長軸頂點為 (±{a}, 0)，請問此橢圓的方程式為何？"
        correct_answer = f"x²/{a*a} + y²/{int(b*b)} = 1"
    else: # level 2
        question_text = f"橢圓方程式為 x²/{a*a} + y²/{int(b*b)} = 1，請問其焦點坐標為何？"
        correct_answer = f"(±{c},0)"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user_answer = user_answer.replace(" ", "").replace("^2", "²")
    return check_answer(user_answer, correct_answer)