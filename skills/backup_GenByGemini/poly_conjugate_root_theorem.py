# \複數\虛根成對定理
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「虛根成對定理」的觀念題。
    """
    if level == 1:
        question_text = (
            "「虛根成對定理」適用於哪一種類型的多項式方程式？\n\n"
            "A) 任意複係數方程式\n"
            "B) 實係數方程式\n"
            "C) 整係數方程式"
        )
        correct_answer = "B"
    else: # level 2
        root = complex(random.randint(1,5), random.randint(1,5))
        question_text = f"已知一個「實係數」方程式有一根為 {root}，請問下列何者也必為其根？"
        correct_answer = str(root.conjugate()).replace("j","i")
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    if correct_answer in ["A", "B", "C"]:
        return check_answer(user_answer, correct_answer, check_type='case_insensitive')
    else:
        user_answer = user_answer.replace(" ", "")
        return check_answer(user_answer, correct_answer)