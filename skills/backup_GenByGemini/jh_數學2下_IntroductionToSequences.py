import random

def generate_arithmetic_problem():
    """Generates an arithmetic sequence problem."""
    start = random.randint(-20, 20)
    # Ensure the difference is non-zero
    diff = random.choice(list(range(-10, 0)) + list(range(1, 11)))
    length = random.randint(5, 7)
    
    sequence = [start + i * diff for i in range(length)]
    
    # The missing term will not be the first or the last
    missing_idx = random.randint(1, length - 2)
    correct_answer = str(sequence[missing_idx])
    
    display_seq = [str(term) for term in sequence]
    display_seq[missing_idx] = "__"
    
    question_text = f"觀察下列數列的規律，在空格中填入適當的數。<br>{' , '.join(display_seq)}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_geometric_problem():
    """Generates a geometric sequence problem."""
    start = random.choice([-3, -2, -1, 1, 2, 3])
    ratio = random.choice([-3, -2, 2, 3])
    length = random.randint(4, 5)

    sequence = [start * (ratio ** i) for i in range(length)]

    missing_idx = random.randint(1, length - 2)
    correct_answer = str(sequence[missing_idx])

    display_seq = [str(term) for term in sequence]
    display_seq[missing_idx] = "__"

    question_text = f"觀察下列數列的規律，在空格中填入適當的數。<br>{' , '.join(display_seq)}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_power_problem():
    """Generates a sequence of powers (squares or cubes)."""
    # Squares are more common, so we give them a higher chance
    power = random.choice([2, 2, 3])
    if power == 2: # Squares
        base_start = random.randint(1, 10)
        length = random.randint(5, 7)
    else: # Cubes
        base_start = random.randint(1, 5)
        length = random.randint(4, 5)

    sequence = [(base_start + i) ** power for i in range(length)]

    missing_idx = random.randint(1, length - 2)
    correct_answer = str(sequence[missing_idx])

    display_seq = [str(term) for term in sequence]
    display_seq[missing_idx] = "__"

    question_text = f"觀察下列數列的規律，在空格中填入適當的數。<br>{' , '.join(display_seq)}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_alternating_problem():
    """Generates a sequence with alternating signs based on an arithmetic progression."""
    base_start = random.randint(1, 10)
    diff = random.randint(0, 3) # Can be a sequence of constants like 5, -5, 5, -5...
    length = random.randint(6, 8)
    
    # Two common sign patterns: (+, -, +, ...) or (-, +, -, ...)
    if random.random() < 0.5:
        # Pattern starts with positive
        sign_multiplier = lambda i: (-1)**i
    else:
        # Pattern starts with negative
        sign_multiplier = lambda i: (-1)**(i+1)

    sequence = []
    for i in range(length):
        term = base_start + i * diff
        sequence.append(term * sign_multiplier(i))

    missing_idx = random.randint(1, length - 2)
    correct_answer = str(sequence[missing_idx])

    display_seq = [str(term) for term in sequence]
    display_seq[missing_idx] = "__"

    question_text = f"觀察下列數列的規律，在空格中填入適當的數。<br>{' , '.join(display_seq)}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    生成「數列規律」相關題目。
    包含：
    1. 等差數列
    2. 等比數列
    3. 次方數列 (平方、立方)
    4. 正負交錯數列
    """
    # List of available problem generator functions
    generators = [
        generate_arithmetic_problem,
        generate_geometric_problem,
        generate_power_problem,
        generate_alternating_problem
    ]
    
    # Randomly select one type of problem to generate
    chosen_generator = random.choice(generators)
    return chosen_generator()

def check(user_answer, correct_answer):
    """
    檢查使用者答案是否正確。
    """
    # Clean up the user's answer by removing leading/trailing whitespace
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    
    is_correct = False
    
    # First, try a direct string comparison. This is the most common case.
    if user_answer == correct_answer:
        is_correct = True
    else:
        # If string comparison fails, try comparing as numbers.
        # This handles cases where the user enters "25.0" for an answer of "25".
        try:
            if float(user_answer) == float(correct_answer):
                is_correct = True
        except ValueError:
            # If the user's answer cannot be converted to a number, it is incorrect.
            pass

    # Provide feedback to the user.
    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$。"
    
    return {"correct": is_correct, "result": result_text, "next_question": True}