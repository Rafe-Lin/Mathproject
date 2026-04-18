import random
from fractions import Fraction

def generate(level=1):
    """
    生成一道「有理數指數律」的題目。
    level 1: 底數為完全平方數或立方數，使其可以化簡。
    level 2: 較複雜的運算。
    """
    if level == 1:
        # (a^k)^(m/k) = a^m
        a = random.randint(2, 5)
        k = random.choice([2, 3])
        m = random.randint(1, 3)
        base = a**k
        
        question_text = f"請計算：{base}^({m}/{k})"
        correct_answer = str(a**m)
    else: # level 2
        # a^(m/n) * a^(p/q)
        a = random.randint(2, 4)
        m, n = random.randint(1, 3), random.randint(2, 4)
        p, q = random.randint(1, 3), random.randint(2, 4)
        
        exp1 = Fraction(m, n)
        exp2 = Fraction(p, q)
        total_exp = exp1 + exp2
        
        question_text = f"請計算：{a}^({exp1}) * {a}^({exp2})，並以指數形式表示。"
        correct_answer = f"{a}^({total_exp})"

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip().replace(" ", "")
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}