# \圓錐曲線\拋物線定義
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「拋物線定義」的觀念題。
    """
    question_text = (
        "在平面上，到一個「定點 F」與一條「定直線 L」距離相等的點，其所形成的軌跡圖形稱為什麼？\n\n"
        "A) 圓\n"
        "B) 橢圓\n"
        "C) 拋物線"
    )
    correct_answer = "C"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    # 對於選擇題，使用不區分大小寫的比對
    return check_answer(user_answer, correct_answer, check_type='case_insensitive')