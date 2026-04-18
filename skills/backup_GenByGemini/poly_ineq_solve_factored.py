import random

def generate(level=1):
    """
    生成一道「已因式分解的高次不等式求解」的題目。
    level 1: 兩個一次因式。
    level 2: 包含一個二次因式。
    """
    r1, r2 = random.sample(range(-5, 6), 2)
    op = random.choice(['>', '<', '>=', '<='])

    if level == 1:
        func_str = f"(x - {r1})(x - {r2})".replace("+-", "-")
        roots = sorted([r1, r2])
        # 大於零在兩根之外，小於零在兩根之間
        sol_outside = op in ['>', '>=']
        if sol_outside:
            correct_answer = f"x > {roots[1]} 或 x < {roots[0]}"
        else:
            correct_answer = f"{roots[0]} < x < {roots[1]}"
    else: # level 2
        # (x-r1)(x^2+k) > 0, x^2+k 恆正
        k = random.randint(1, 5)
        func_str = f"(x - {r1})(x² + {k})".replace("+-", "-")
        # 不等式方向只由 (x-r1) 決定
        correct_answer = f"x > {r1}" if op in ['>', '>='] else f"x < {r1}"

    question_text = f"請求解高次不等式：{func_str} {op} 0"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip().replace(" ", "")
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}