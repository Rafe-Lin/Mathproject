# \坐標與函數\平面分點公式
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「平面分點公式」的題目。
    """
    A = [random.randint(-5, 5) for _ in range(2)]
    B = [random.randint(-5, 5) for _ in range(2)]
    
    m = random.randint(1, 4)
    n = random.randint(1, 4)
    
    if level == 1: # 內分點
        question_text = f"已知平面上兩點 A{tuple(A)}, B{tuple(B)}，若點 P 在線段 AB 上且 AP:PB = {m}:{n}，利用分點公式求 P 點坐標。"
        P = [(n*A[i] + m*B[i]) / (m+n) for i in range(2)]
    else: # level 2, 外分點
        while m == n: n = random.randint(1, 4)
        question_text = f"已知平面上兩點 A{tuple(A)}, B{tuple(B)}，若點 P 在直線 AB 上且 AP:PB = {m}:{n} (P為外分點)，求 P 點坐標。"
        P = [(-n*A[i] + m*B[i]) / (m-n) for i in range(2)]
        
    P_rounded = [round(c, 1) for c in P]
    correct_answer = str(tuple(P_rounded))
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user_answer = user_answer.replace(" ", "")
    return check_answer(user_answer, correct_answer)