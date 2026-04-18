import random
from fractions import Fraction

def generate(level=1):
    """
    生成「數列」相關題目。
    根據不同的規律類型生成數列，並在其中填入適當的數。
    """
    problem_type = random.choice([
        'arithmetic_sequence',
        'geometric_sequence',
        'square_sequence',
        'alternating_sequence',
        'fibonacci_like_sequence',
        'arithmetic_decimal_sequence'
    ])
    
    if problem_type == 'arithmetic_sequence':
        return _generate_arithmetic_sequence_problem(level)
    elif problem_type == 'geometric_sequence':
        return _generate_geometric_sequence_problem(level)
    elif problem_type == 'square_sequence':
        return _generate_square_sequence_problem(level)
    elif problem_type == 'alternating_sequence':
        return _generate_alternating_sequence_problem(level)
    elif problem_type == 'fibonacci_like_sequence':
        return _generate_fibonacci_like_sequence_problem(level)
    elif problem_type == 'arithmetic_decimal_sequence':
        return _generate_arithmetic_decimal_sequence_problem(level)

def _generate_arithmetic_sequence_problem(level):
    """
    生成等差數列問題。
    """
    start_term = random.randint(-20, 20)
    common_difference = random.choice([x for x in range(-10, 11) if x != 0])
    
    # Adjust difficulty by level
    if level == 1:
        num_terms = random.randint(5, 7)
        common_difference = random.choice([x for x in range(-5, 6) if x != 0]) # Smaller diff for level 1
    elif level == 2:
        num_terms = random.randint(6, 8)
    else: # level 3+
        num_terms = random.randint(7, 9)
        start_term = random.randint(-50, 50)
        common_difference = random.choice([x for x in range(-15, 16) if x != 0])
    
    sequence = [start_term + i * common_difference for i in range(num_terms)]
    
    # Ensure missing index is not the very first or very last term
    missing_idx = random.randint(1, num_terms - 2) if num_terms > 2 else 0 # Handle very short sequences
    
    correct_answer = sequence[missing_idx]
    
    display_sequence = []
    for i, val in enumerate(sequence):
        if i == missing_idx:
            display_sequence.append("__")
        else:
            display_sequence.append(str(val))
            
    question_text = f"觀察下列數列的規律，在空格中填入適當的數。<br>\\({', '.join(display_sequence)}\\)"
    
    return {
        "question_text": question_text,
        "answer": str(correct_answer),
        "correct_answer": str(correct_answer)
    }

def _generate_arithmetic_decimal_sequence_problem(level):
    """
    生成等差數列問題，包含小數。
    """
    start_term = round(random.uniform(-10, 10), 1)
    common_difference = round(random.uniform(-3, 3), 1)
    # Ensure common_difference is not 0
    while common_difference == 0:
        common_difference = round(random.uniform(-3, 3), 1)
    
    num_terms = random.randint(5, 7)
    
    sequence = [round(start_term + i * common_difference, 1) for i in range(num_terms)]
    
    # Ensure missing index is not the very first or very last term
    missing_idx = random.randint(1, num_terms - 2) if num_terms > 2 else 0 # Handle very short sequences
    
    correct_answer = sequence[missing_idx]
    
    display_sequence = []
    for i, val in enumerate(sequence):
        if i == missing_idx:
            display_sequence.append("__")
        else:
            display_sequence.append(str(val))
            
    question_text = f"觀察下列數列的規律，在空格中填入適當的數。<br>\\({', '.join(display_sequence)}\\)"
    
    return {
        "question_text": question_text,
        "answer": str(correct_answer),
        "correct_answer": str(correct_answer)
    }


def _generate_geometric_sequence_problem(level):
    """
    生成等比數列問題。
    """
    start_term = random.choice([x for x in range(1, 10) if x != 0]) # Positive start for simplicity
    common_ratio = random.choice([2, 3, -2]) # Limited ratios to prevent huge numbers
    
    if level >= 2:
        common_ratio = random.choice([2, 3, 4, -2, -3])
    
    num_terms = random.randint(4, 6) # Keep sequence shorter for geometric
    
    sequence = []
    for i in range(num_terms):
        term = start_term * (common_ratio ** i)
        # Avoid extremely large or small numbers
        if abs(term) > 10000 or (abs(term) < 0.001 and term != 0):
            # Re-generate if numbers get too wild, try a few times
            return _generate_geometric_sequence_problem(level)
        sequence.append(term)
    
    missing_idx = random.randint(1, num_terms - 2) if num_terms > 2 else 0
    
    correct_answer = sequence[missing_idx]
    
    display_sequence = []
    for i, val in enumerate(sequence):
        if i == missing_idx:
            display_sequence.append("__")
        else:
            display_sequence.append(str(val))
            
    question_text = f"觀察下列數列的規律，在空格中填入適當的數。<br>\\({', '.join(display_sequence)}\\)"
    
    return {
        "question_text": question_text,
        "answer": str(correct_answer),
        "correct_answer": str(correct_answer)
    }

def _generate_square_sequence_problem(level):
    """
    生成平方數列問題。
    """
    start_n = random.randint(1, 3) # Start with n=1, 2, or 3
    num_terms = random.randint(5, 7)
    
    sequence = [ (start_n + i)**2 for i in range(num_terms) ]
    
    missing_idx = random.randint(1, num_terms - 2) if num_terms > 2 else 0
    
    correct_answer = sequence[missing_idx]
    
    display_sequence = []
    for i, val in enumerate(sequence):
        if i == missing_idx:
            display_sequence.append("__")
        else:
            display_sequence.append(str(val))
            
    question_text = f"觀察下列數列的規律，在空格中填入適當的數。<br>\\({', '.join(display_sequence)}\\)"
    
    return {
        "question_text": question_text,
        "answer": str(correct_answer),
        "correct_answer": str(correct_answer)
    }

def _generate_alternating_sequence_problem(level):
    """
    生成帶有正負交替規律的數列問題。
    參考例題: 1 , －2 , 3 , －4 , 5 , __ , 7 , －8 , 9 , －10
    """
    start_val = random.randint(1, 5)
    common_diff = random.choice([1, 2]) # Simple diff for the absolute values
    num_terms = random.randint(6, 10)
    
    # Determine if positive first or negative first
    pos_first = random.choice([True, False])
    
    sequence = []
    for i in range(num_terms):
        abs_val = start_val + i * common_diff
        if pos_first:
            term = abs_val if (i % 2 == 0) else -abs_val
        else:
            term = -abs_val if (i % 2 == 0) else abs_val
        sequence.append(term)
        
    missing_idx = random.randint(1, num_terms - 2) if num_terms > 2 else 0
    
    correct_answer = sequence[missing_idx]
    
    display_sequence = []
    for i, val in enumerate(sequence):
        if i == missing_idx:
            display_sequence.append("__")
        else:
            display_sequence.append(str(val))
            
    question_text = f"觀察下列數列的規律，在空格中填入適當的數。<br>\\({', '.join(display_sequence)}\\)"
    
    return {
        "question_text": question_text,
        "answer": str(correct_answer),
        "correct_answer": str(correct_answer)
    }

def _generate_fibonacci_like_sequence_problem(level):
    """
    生成費波那契 (Fibonacci) 類數列問題。
    每個數是前兩個數的和。
    """
    # Start terms
    term1 = random.randint(1, 5)
    term2 = random.randint(1, 5)
    
    num_terms = random.randint(6, 8) # Fibonacci grows fast
    
    sequence = [term1, term2]
    for i in range(2, num_terms):
        next_term = sequence[i-1] + sequence[i-2]
        if abs(next_term) > 200: # Limit growth to prevent excessively large numbers
            num_terms = i # Cut short the sequence
            break
        sequence.append(next_term)
    
    # If sequence is too short after cutting, re-generate (rare but possible)
    if len(sequence) < 5:
        return _generate_fibonacci_like_sequence_problem(level)

    # Ensure missing_idx allows previous two terms to be shown
    missing_idx = random.randint(2, len(sequence) - 2) if len(sequence) > 3 else 0
    
    correct_answer = sequence[missing_idx]
    
    display_sequence = []
    for i, val in enumerate(sequence):
        if i == missing_idx:
            display_sequence.append("__")
        else:
            display_sequence.append(str(val))
            
    question_text = f"觀察下列數列的規律，在空格中填入適當的數。<br>\\({', '.join(display_sequence)}\\)"
    
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
    
    is_correct = False
    
    try:
        # For numeric answers, compare floats
        if float(user_answer) == float(correct_answer):
            is_correct = True
    except ValueError:
        # If not a valid number, it's incorrect
        pass

    result_text = f"完全正確！答案是 \\({correct_answer}\\)。" if is_correct else f"答案不正確。正確答案應為：\\({correct_answer}\\)"
    return {"correct": is_correct, "result": result_text, "next_question": True}