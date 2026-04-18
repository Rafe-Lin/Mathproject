import random
from fractions import Fraction

def generate(level=1):
    """
    生成一道「餘事件機率」的題目。
    level 1: 簡單事件。
    level 2: 至少一...事件。
    """
    if level == 1:
        p_A = Fraction(random.randint(1, 4), 10)
        question_text = f"已知事件 A 發生的機率為 {p_A}，請問 A 的餘事件 A' 發生的機率是多少？ (請以最簡分數 a/b 表示)"
        p_A_comp = 1 - p_A
        correct_answer = f"{p_A_comp.numerator}/{p_A_comp.denominator}"
    else: # level 2
        question_text = "同時擲三枚公正的硬幣，至少出現一個正面的機率是多少？ (請以最簡分數 a/b 表示)"
        # 1 - P(全反) = 1 - (1/2)³ = 1 - 1/8
        correct_answer = "7/8"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}