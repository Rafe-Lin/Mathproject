import random

def generate(level=1):
    """
    生成一道「常用對數定義」的題目。
    log(10^n) = n
    level 1: n 為正整數
    level 2: n 為負整數或分數
    """
    if level == 1:
        n = random.randint(1, 5)
        x = 10**n
        question_text = f"請求出 log({x}) 的值。"
        correct_answer = str(n)
    else: # level 2
        n_type = random.choice(['neg', 'frac'])
        if n_type == 'neg':
            n = random.randint(-4, -1)
            x = f"10^({n})"
            question_text = f"請求出 log({x}) 的值。"
            correct_answer = str(n)
        else: # frac
            n = random.choice([0.5, 1.5, 2.5])
            x = f"10^({n})"
            question_text = f"請求出 log({x}) 的值。"
            correct_answer = str(n)

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}