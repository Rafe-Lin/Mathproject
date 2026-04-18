import random
from fractions import Fraction

def generate(level=1):
    """
    生成一道「零指數與負整數指數」的題目。
    level 1: a^0 = 1 或 a^(-1) = 1/a
    level 2: a^(-n) = 1/a^n
    """
    base = random.randint(2, 9)

    if level == 1:
        op_type = random.choice(['zero', 'neg_one'])
        if op_type == 'zero':
            # a^0
            question_text = f"請計算：{base}⁰"
            correct_answer = "1"
        else: # neg_one
            # a^(-1)
            question_text = f"請計算：{base}⁻¹"
            correct_answer = f"1/{base}"
    else: # level 2
        # a^(-n)
        n = random.randint(2, 4)
        question_text = f"請計算：{base}⁻{n}"
        correct_answer = f"1/{base**n}"

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}