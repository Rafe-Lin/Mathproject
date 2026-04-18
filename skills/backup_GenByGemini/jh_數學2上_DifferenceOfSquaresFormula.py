import random
from fractions import Fraction

def generate(level=1):
    """
    生成「平方差公式」相關題目。
    包含：
    1. 正向應用：計算 (a+b)(a-b) 形式的乘積。
    2. 反向應用：計算 a^2 - b^2 形式的減法。
    """
    problem_type = random.choice(['forward', 'reverse'])
    
    if problem_type == 'forward':
        return generate_forward_problem(level)
    else: # 'reverse'
        return generate_reverse_problem(level)

def generate_forward_problem(level=1):
    """
    生成正向應用題目： (a+b)(a-b) = a^2 - b^2
    例如：計算 203 × 197
    """
    if level == 1:
        # 'a' is a nice round number (multiple of 10)
        a = random.randint(2, 10) * 10 
        # 'b' is a small integer
        b = random.randint(1, 5)
    else: # Higher levels can have larger numbers
        a = random.randint(11, 100) * 10
        b = random.randint(1, 9)

    num1 = a + b
    num2 = a - b
    
    # Randomize the order of multiplication
    if random.random() < 0.5:
        num1, num2 = num2, num1

    # The question text reminds the student of the formula.
    question_text = f"利用平方差公式 $(a+b)(a-b) = a^2 - b^2$，計算 ${num1} \\times {num2}$ 的值。"
    
    correct_answer = a**2 - b**2
    
    return {
        "question_text": question_text,
        "answer": str(correct_answer),
        "correct_answer": str(correct_answer)
    }

def generate_reverse_problem(level=1):
    """
    生成反向應用題目： a^2 - b^2 = (a+b)(a-b)
    例如：計算 655^2 - 345^2
    """
    if level == 1:
        # s = a+b, a nice round number
        s = random.choice([100, 500, 1000])
        # d = a-b, a multiple of 10
        d = random.randint(2, 20) * 10
    else: # Higher levels
        s = random.choice([1000, 2000, 5000, 10000])
        d = random.randint(10, 50) * 10

    # Ensure s > d, so b > 0.
    if d >= s:
        d = s // (random.randint(2,5))
        d = (d // 10) * 10 # make it a multiple of 10 again
        if d == 0: d = 10

    # s and d are both multiples of 10, so they are both even.
    # This guarantees that a = (s+d)/2 and b = (s-d)/2 are integers.
    a = (s + d) // 2
    b = (s - d) // 2

    question_text = f"利用平方差公式 $(a+b)(a-b) = a^2 - b^2$，計算 ${a}^2 - {b}^2$ 的值。"
    
    correct_answer = s * d
    
    return {
        "question_text": question_text,
        "answer": str(correct_answer),
        "correct_answer": str(correct_answer)
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    
    is_correct = (user_answer == correct_answer)
    
    # Allow for answers like '123.0' for integer '123'
    if not is_correct:
        try:
            if float(user_answer) == float(correct_answer):
                is_correct = True
        except (ValueError, TypeError):
            pass

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}