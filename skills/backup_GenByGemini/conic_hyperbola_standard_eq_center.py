# \圓錐曲線\雙曲線標準式 (中心(0,0))
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「雙曲線標準式 (中心(0,0))」的題目。
    """
    a = random.randint(2, 4)
    b = random.randint(2, 4)
    c = (a*a + b*b)**0.5
    
    if level == 1:
        question_text = f"一個雙曲線的方程式為 x²/{a*a} - y²/{b*b} = 1，請問其貫軸是 x 軸還是 y 軸？"
        correct_answer = "x軸"
    else: # level 2
        question_text = f"雙曲線方程式為 x²/{a*a} - y²/{b*b} = 1，請問其焦點坐標為何？"
        correct_answer = f"(±{round(c,1)},0)"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user_answer = user_answer.replace(" ", "").replace("^2", "²")
    return check_answer(user_answer, correct_answer)