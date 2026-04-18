import random

def _format_number(n):
    """Formats a number to a string, removing trailing .0 for integers."""
    if isinstance(n, int):
        return str(n)
    if n == int(n):
        return str(int(n))
    else:
        # Round to a reasonable number of decimal places to avoid float representation errors
        return f"{round(n, 5):.10g}"

def generate_forward_problem():
    """
    Generates a problem for the forward application of the formula.
    e.g., "利用差的平方公式 ... 計算 199^2 的值。"
    """
    # 60% chance for an integer problem, 40% for a decimal problem
    if random.random() < 0.6:
        # Integer case: e.g., (200 - 1)^2
        base = random.choice([100, 200, 300, 400, 500, 1000])
        sub = random.randint(1, 4)
        num_to_square = base - sub
    else:
        # Decimal case: e.g., (20 - 0.1)^2 = 19.9^2
        base = random.randint(2, 10) * 10
        sub = random.randint(1, 4) / 10.0
        num_to_square = base - sub

    question_text = f"利用差的平方公式 $(a-b)^2 = a^2 - 2ab + b^2$，計算 ${_format_number(num_to_square)}^2$ 的值。"
    
    correct_answer_val = num_to_square ** 2
    correct_answer = _format_number(correct_answer_val)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_reverse_problem():
    """
    Generates a problem for the reverse application of the formula.
    e.g., "計算 93^2 - 2*93*3 + 3^2 的值。"
    """
    # 60% chance for an integer problem, 40% for a decimal problem
    if random.random() < 0.6:
        # Integer case: a and b are integers
        # (a-b) will be a round number for easier calculation
        result_base = random.randint(2, 10) * 10 
        b = random.randint(2, 9)
        a = result_base + b
    else:
        # Decimal case: one or both numbers are decimals
        result_base = random.randint(5, 25)
        # b will be a one-decimal-place number like 0.3, 0.7
        b = random.choice([0.1, 0.2, 0.3, 0.4, 0.6, 0.7, 0.8, 0.9])
        a = result_base + b
        
    a_str = _format_number(a)
    b_str = _format_number(b)

    question_text = f"計算 ${a_str}^2 - 2 \\times {a_str} \\times {b_str} + {b_str}^2$ 的值。"
    
    correct_answer_val = result_base ** 2
    correct_answer = _format_number(correct_answer_val)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    生成「差的平方公式」相關題目。
    包含：
    1. 正向應用：計算 (a-b)^2，如 199^2
    2. 反向應用：計算 a^2 - 2ab + b^2
    """
    problem_type = random.choice(['forward', 'reverse'])
    
    if problem_type == 'forward':
        return generate_forward_problem()
    else: # problem_type == 'reverse'
        return generate_reverse_problem()

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    
    is_correct = (user_answer == correct_answer)
    
    if not is_correct:
        try:
            # Allow for floating point comparison, e.g., "100" vs "100.0"
            if float(user_answer) == float(correct_answer):
                is_correct = True
        except ValueError:
            # user_answer might not be a valid number
            pass

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}