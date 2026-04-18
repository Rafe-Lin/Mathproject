# \多項式\整係數一次因式檢驗法
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「整係數一次因式檢驗法」的題目。
    """
    if level == 1:
        # 領導係數為 1
        const = random.choice([6, 8, 10, 12])
        question_text = (
            f"根據一次因式檢驗法，多項式 f(x) = x³ + ... + {const} 可能的一次因式 (x-c) 中，c 的可能值為何？\n\n"
            f"A) 只有 {const} 的正因數\n"
            f"B) 只有 {const} 的負因數\n"
            f"C) {const} 的所有正負因數"
        )
        correct_answer = "C"
    else: # level 2
        q = random.choice([2, 3, 5])
        p = random.choice([1, 2, 3, 4])
        while p % q == 0: p = random.choice([1, 2, 3, 4])
        question_text = f"根據牛頓有理根檢驗法，對於整係數多項式 {q}x³ + ... - {p} = 0，下列何者「不可能」是它的有理根？\n\n" \
                        f"A) {p}\nB) {p}/{q}\nC) {q}/{p}"
        correct_answer = "C"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    return check_answer(user_answer, correct_answer, check_type='case_insensitive')