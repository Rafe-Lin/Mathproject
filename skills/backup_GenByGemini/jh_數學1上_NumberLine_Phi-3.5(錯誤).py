import random

from fractions import Fraction

import re


def generate(level=1):
    # [Auto-Fix] 初始化未定義變數以避免 Crash
    iss_correct = 0


    sequence = [0.5 - level, 0.5 + level]

    missing_idx = random.randint(1, len(sequence) - 2)

    correct_answer = str(Fraction(sequence[missing_idx]).limit_denominator() if isinstance(sequence[missing_idx], Fraction) else sequence[missing_idx])

    question_text = f"請塗色表示下列數線上的點位：{','.join([str(val) for val in sequence[:-1]])}, ( ? ) {sequence[-1]}" if level == 1 else None

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": str(correct_answer)}


def check(user_answer, correct_answer):

    user_answer = re.sub('[^0-9\.\,\s]', '', user_answer).strip()  # Remove any non-numeric characters except for digits and spaces

    is_correct = (str(float(user_answer)) == str(float(correct_answer))) if correct_answer != 'None' else False

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else "答案不正確。正確答案應為：${correct_answer}$"

    return {"correct": iss_correct, "result": result_text, "next_question": True}