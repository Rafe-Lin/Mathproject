# \積分應用\旋轉體體積 (墊圈法)
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「旋轉體體積 (墊圈法)」的觀念題。
    """
    question_text = (
        "利用墊圈法計算由 y=R(x) 和 y=r(x) 在 [a,b] 區間所圍區域，對 x 軸旋轉的體積時，其公式為何？ (R(x) ≥ r(x) ≥ 0)\n\n"
        "A) V = π ∫[a,b] (R(x) - r(x)) dx\n"
        "B) V = π ∫[a,b] (R(x) - r(x))² dx\n"
        "C) V = π ∫[a,b] ([R(x)]² - [r(x)]²) dx"
    )
    correct_answer = "C"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    