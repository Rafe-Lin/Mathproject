# \坐標與函數\平面中點公式
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「平面中點公式」的題目。
    """
    p1 = [random.randint(-10, 10) for _ in range(2)]
    p2 = [random.randint(-10, 10) for _ in range(2)]
    
    # 確保中點為整數
    if (p1[0] + p2[0]) % 2 != 0: p2[0] += 1
    if (p1[1] + p2[1]) % 2 != 0: p2[1] += 1
    
    if level == 1:
        question_text = f"平面上兩點 A({p1[0]},{p1[1]}) 與 B({p2[0]},{p2[1]}) 的中點坐標為何？"
        midpoint = [ (p1[i]+p2[i])//2 for i in range(2) ]
        correct_answer = f"({midpoint[0]},{midpoint[1]})"
    else: # level 2, 逆向提問
        midpoint = [ (p1[i]+p2[i])//2 for i in range(2) ]
        question_text = f"已知線段 AB 的中點為 M({midpoint[0]},{midpoint[1]})，若 A 點坐標為 ({p1[0]},{p1[1]})，請問 B 點坐標為何？"
        correct_answer = f"({p2[0]},{p2[1]})"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user_answer = user_answer.replace(" ", "")
    return check_answer(user_answer, correct_answer)