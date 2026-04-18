import random

def generate(level=1):
    """
    生成一道「對數與指數互換」的題目。
    log_a(b) = c  <=>  a^c = b
    level 1: 數字較小
    level 2: 數字較大或包含分數
    """
    if level == 1:
        a = random.randint(2, 5)
        c = random.randint(2, 4)
        b = a**c
    else: # level 2
        a = random.choice([4, 8, 9])
        c = random.choice([Fraction(1,2), Fraction(1,3), Fraction(3,2)])
        b = a**c
        b = int(b) if b == int(b) else b

    q_type = random.choice(['log_to_exp', 'exp_to_log'])
    if q_type == 'log_to_exp':
        question_text = f"請將對數式 log_{a}({b}) = {c} 改寫為指數式。"
        correct_answer = f"{a}^{c}={b}"
    else:
        question_text = f"請將指數式 {a}^{c} = {b} 改寫為對數式。"
        correct_answer = f"log_{a}({b})={c}"

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").lower()
    correct = str(correct_answer).strip().replace(" ", "").lower()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}