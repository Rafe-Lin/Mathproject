import random

def generate(level=1):
    """
    生成一道「整數指數律」的題目。
    level 1: a^m * a^n = a^(m+n) 或 (a^m)^n = a^(mn)
    level 2: (ab)^n = a^n * b^n 或包含負數底數
    """
    base = random.randint(2, 5)
    m = random.randint(2, 5)
    n = random.randint(2, 5)

    if level == 1:
        op_type = random.choice(['multiply', 'power'])
        if op_type == 'multiply':
            # a^m * a^n
            question_text = f"請計算：{base}² * {base}³"
            # 為了讓題目固定，這裡不用變數 m, n
            m, n = 2, 3
            correct_answer = str(base**(m+n))
        else: # power
            # (a^m)^n
            question_text = f"請計算：({base}²)³"
            m, n = 2, 3
            correct_answer = str(base**(m*n))
    else: # level 2
        op_type = random.choice(['product_power', 'negative_base'])
        if op_type == 'product_power':
            # (ab)^n
            base2 = random.randint(2, 5)
            while base == base2: base2 = random.randint(2, 5)
            question_text = f"請計算：({base} * {base2})²"
            n = 2
            correct_answer = str((base*base2)**n)
        else: # negative_base
            base = -random.randint(2, 4)
            m = random.choice([2, 3])
            n = random.choice([2, 3])
            question_text = f"請計算：({base})^{m} * ({base})^{n}"
            correct_answer = str(base**(m+n))

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}