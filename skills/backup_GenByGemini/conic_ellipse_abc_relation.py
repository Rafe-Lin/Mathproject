# \圓錐曲線\橢圓 (a,b,c 關係)
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「橢圓 (a,b,c 關係)」的觀念題。
    """
    question_text = (
        "在一個橢圓中，a 代表中心到長軸頂點的距離（半長軸長），b 代表中心到短軸頂點的距離（半短軸長），c 代表中心到焦點的距離（焦距）。請問 a, b, c 的關係式為何？\n\n"
        "A) a² = b² + c²\n"
        "B) b² = a² + c²\n"
        "C) c² = a² + b²"
    )
    correct_answer = "A"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    return check_answer(user_answer, correct_answer, check_type='case_insensitive')