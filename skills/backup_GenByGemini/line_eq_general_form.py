import random

def generate(level=1):
    """
    生成一道「一般式」相關的題目。
    level 1: 從一般式求斜率。
    level 2: 從一般式求 x, y 截距。
    """
    a = random.randint(-5, 5)
    b = random.randint(-5, 5)
    while a == 0 or b == 0:
        a = random.randint(-5, 5)
        b = random.randint(-5, 5)
    c = random.randint(-10, 10)
    
    line_eq = f"{a}x + {b}y + {c} = 0".replace("+-", "-")

    if level == 1:
        question_text = f"請問直線 {line_eq} 的斜率是多少？"
        # m = -a/b
        m = Fraction(-a, b)
        correct_answer = str(m.numerator) if m.denominator == 1 else f"{m.numerator}/{m.denominator}"
    else: # level 2
        q_type = random.choice(['x_intercept', 'y_intercept'])
        if q_type == 'x_intercept':
            question_text = f"請問直線 {line_eq} 的 x 截距是多少？"
            # y=0, ax = -c, x = -c/a
            intercept = Fraction(-c, a)
            correct_answer = str(intercept.numerator) if intercept.denominator == 1 else f"{intercept.numerator}/{intercept.denominator}"
        else:
            question_text = f"請問直線 {line_eq} 的 y 截距是多少？"
            # x=0, by = -c, y = -c/b
            intercept = Fraction(-c, b)
            correct_answer = str(intercept.numerator) if intercept.denominator == 1 else f"{intercept.numerator}/{intercept.denominator}"

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}