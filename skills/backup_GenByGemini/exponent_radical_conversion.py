import random

def generate(level=1):
    """
    生成一道「指數與根式互換」的題目。
    level 1: a^(1/n) = n√a
    level 2: a^(m/n) = n√(a^m)
    """
    base = random.randint(2, 7)
    
    if level == 1:
        n = random.choice([2, 3, 4])
        if n == 2:
            question_text = f"請將 {base} 的 1/2 次方表示為根式。"
            correct_answer = f"√{base}"
        else:
            question_text = f"請將 {base} 的 1/{n} 次方表示為根式。"
            correct_answer = f"{n}√{base}" # 假設前端能顯示 n 次方根
    else: # level 2
        m = random.randint(2, 5)
        n = random.randint(2, 4)
        while m == n: m = random.randint(2, 5)
        
        q_type = random.choice(['to_radical', 'to_exponent'])
        if q_type == 'to_radical':
            question_text = f"請將 {base} 的 {m}/{n} 次方表示為根式。"
            correct_answer = f"{n}√({base}^{m})"
        else:
            question_text = f"請將根式 {n}√({base}^{m}) 表示為指數形式。"
            correct_answer = f"{base}^({m}/{n})"

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").replace("sqrt", "√")
    correct = str(correct_answer).strip().replace(" ", "")
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}