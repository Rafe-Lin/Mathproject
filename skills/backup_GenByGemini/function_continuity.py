# \極限\連續函數
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「連續函數」的觀念題。
    """
    a = random.randint(1, 5)
    l = random.randint(1, 10)
    
    if level == 1:
        question_text = f"若函數 f(x) 在 x={a} 處連續，且已知 lim (x→{a}) f(x) = {l}，請問 f({a}) 的值是多少？"
        correct_answer = str(l)
    else: # level 2
        question_text = "下列哪個函數在 x=0 處「不連續」？\n\n" \
                        "A) f(x) = x²\nB) f(x) = |x|\nC) f(x) = 1/x"
        correct_answer = "C"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    if correct_answer in ["A", "B", "C"]:
        return check_answer(user_answer, correct_answer, check_type='case_insensitive')
    else:
        return check_answer(user_answer, correct_answer, check_type='numeric')