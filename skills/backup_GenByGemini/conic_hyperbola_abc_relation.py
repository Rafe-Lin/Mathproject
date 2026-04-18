# \圓錐曲線\雙曲線 (a,b,c 關係)
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「雙曲線 (a,b,c 關係)」的觀念題。
    """
    question_text = (
        "在一個雙曲線中，a 代表中心到頂點的距離（半貫軸長），c 代表中心到焦點的距離（焦距），b 則與漸近線斜率有關。請問 a, b, c 的關係式為何？\n\n"
        "A) a² = b² + c²\n"
        "B) b² = a² + c²\n"
        "C) c² = a² + b²"
    )
    correct_answer = "C"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    return check_answer(user_answer, correct_answer, check_type='case_insensitive')