import random
from fractions import Fraction

def generate(level=1):
    """
    生成一道「機率加法法則」的題目。
    P(A∪B) = P(A) + P(B) - P(A∩B)
    level 1: 互斥事件 P(A∩B)=0
    level 2: 非互斥事件
    """
    if level == 1:
        p_A = Fraction(random.randint(2, 4), 10)
        p_B = Fraction(random.randint(1, 2), 10)
        question_text = f"已知 A, B 為互斥事件，P(A)={p_A}，P(B)={p_B}，請問 P(A∪B) 是多少？ (請以最簡分數 a/b 表示)"
        ans = p_A + p_B
    else: # level 2
        p_A = Fraction(random.randint(4, 6), 10)
        p_B = Fraction(random.randint(3, 5), 10)
        p_AnB = Fraction(random.randint(1, 2), 10)
        question_text = f"已知 P(A)={p_A}，P(B)={p_B}，P(A∩B)={p_AnB}，請問 P(A∪B) 是多少？ (請以最簡分數 a/b 表示)"
        ans = p_A + p_B - p_AnB
    correct_answer = f"{ans.numerator}/{ans.denominator}"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}