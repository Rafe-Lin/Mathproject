import random
from fractions import Fraction
import re

# --- Helper Functions ---

def _format_fraction(f: Fraction) -> str:
    """Formats a Fraction object into a mixed number string for display."""
    if f.denominator == 1:
        return str(f.numerator)
    
    sign = ""
    if f < 0:
        sign = "-"
        f = abs(f)
        
    whole_part = f.numerator // f.denominator
    rem_numerator = f.numerator % f.denominator
    
    if whole_part == 0:
        if rem_numerator == 0: # Should not happen with proper fractions but as a safeguard
            return "0"
        return f"{sign}{rem_numerator}/{f.denominator}"
    else:
        if rem_numerator == 0:
            return f"{sign}{whole_part}"
        else:
            # Using a space for mixed number, e.g., "2 1/3"
            return f"{sign}{whole_part} {rem_numerator}/{f.denominator}"

def _parse_user_answer_to_fraction(s: str) -> Fraction:
    """Parses a user-provided string (integer, decimal, fraction, or mixed fraction) into a Fraction."""
    s = s.strip()
    
    # Handle mixed fractions like "-2 1/3"
    match = re.match(r'(-?)\s*(\d+)\s+(\d+)\s*/\s*(\d+)', s)
    if match:
        sign = -1 if match.group(1) == '-' else 1
        whole = int(match.group(2))
        num = int(match.group(3))
        den = int(match.group(4))
        return sign * (Fraction(whole) + Fraction(num, den))
    
    # Handle simple fractions and integers
    return Fraction(s)

# --- Problem Generation Functions ---

def generate_find_term_problem():
    """
    Generates a problem asking for the n-th term given the first term and common difference.
    Example: 首項為 2，公差為 3，求第 4 項。
    """
    a1 = random.randint(-20, 20)
    d = random.choice(list(range(-10, 0)) + list(range(1, 11)))
    n = random.randint(4, 10)
    
    an = a1 + (n - 1) * d
    
    question_text = f"一個等差數列的首項為 ${a1}$，公差為 ${d}$，請問此數列的第 ${n}$ 項為何？"
    correct_answer = str(an)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_find_sequence_problem():
    """
    Generates a problem asking for the first n terms given the first term and common difference.
    Example: 首項為 2，公差為 3，寫出前 4 項。
    """
    a1 = random.randint(-10, 10)
    d = random.choice(list(range(-5, 0)) + list(range(1, 6)))
    n = random.choice([3, 4, 5])
    
    sequence = [a1 + i * d for i in range(n)]
    sequence_str = ", ".join(map(str, sequence))
    
    question_text = f"一個等差數列的首項為 ${a1}$，公差為 ${d}$，請寫出此數列的前 ${n}$ 項。<br>(請用半形逗號 `,` 分隔)"
    correct_answer = sequence_str
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_fill_blank_integer_problem():
    """
    Generates a problem with an integer arithmetic sequence with one blank to fill.
    Example: 3, 7, __, 15
    """
    a1 = random.randint(-15, 15)
    d = random.choice(list(range(-8, 0)) + list(range(1, 9)))
    length = random.choice([4, 5])
    
    sequence = [a1 + i * d for i in range(length)]
    missing_idx = random.randint(0, length - 1)
    
    display_list = []
    for i, term in enumerate(sequence):
        if i == missing_idx:
            display_list.append("(   )")
        else:
            display_list.append(str(term))
            
    display_str = ", ".join(display_list)
    
    question_text = f"請在下列空格中填入適當的數，使它成為一個等差數列：<br>{display_str}"
    correct_answer = str(sequence[missing_idx])
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_fill_blank_fraction_problem():
    """
    Generates a problem with a fraction arithmetic sequence with one blank to fill.
    Example: -2 1/3, 3 1/3, __, 14 2/3
    """
    d_den = random.choice([2, 3, 4])
    d_num = random.randint(1, d_den * 2)
    d = Fraction(d_num, d_den)
    if random.random() < 0.5:
        d = -d

    a1_den = random.choice([2, 3, 4])
    a1_num = random.randint(-a1_den * 3, a1_den * 3)
    a1 = Fraction(a1_num, a1_den)
    
    length = 4
    sequence = [a1 + i * d for i in range(length)]
    
    # Avoid hiding the first two terms to ensure the common difference is clear
    missing_idx = random.randint(2, length - 1)
    
    display_list = []
    for i, term in enumerate(sequence):
        if i == missing_idx:
            display_list.append("(   )")
        else:
            display_list.append(f"${_format_fraction(term)}$")
            
    display_str = ", ".join(display_list)
    
    question_text = f"請在下列空格中填入適當的數，使它成為一個等差數列：<br>{display_str}<br>(答案請以整數、分數或帶分數表示)"
    
    correct_fraction = sequence[missing_idx]
    correct_answer = _format_fraction(correct_fraction)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_fill_blanks_variable_problem():
    """
    Generates a problem with a variable arithmetic sequence with two blanks.
    Example: __, a, a+5, a+10, __
    """
    var = 'a'
    d = random.choice(list(range(-10, 0)) + list(range(1, 11)))
    
    # Create a sequence centered around the variable `a`
    # Example: a-2d, a-d, a, a+d, a+2d
    mid_term_idx = 2
    length = 5
    sequence_coeffs = [(i - mid_term_idx) * d for i in range(length)]

    def _format_term(variable, coeff):
        if coeff == 0:
            return variable
        elif coeff > 0:
            return f"{variable}+{coeff}"
        else:
            return f"{variable}{coeff}"

    sequence_str = [_format_term(var, c) for c in sequence_coeffs]
    
    display_list = [f"${sequence_str[1]}$", f"${sequence_str[2]}$", f"${sequence_str[3]}$"]
    display_list.insert(0, "(   )")
    display_list.append("(   )")
    
    display_str = ", ".join(display_list)
    
    question_text = f"在下列各空格中填入適當的式子，使數列成為等差數列：<br>{display_str}<br>(請用半形逗號 `,` 分隔兩個答案)"
    
    correct_answer = f"{sequence_str[0]}, {sequence_str[4]}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    Generates a problem related to Arithmetic Sequences.
    """
    problem_type = random.choice([
        'find_term', 
        'find_sequence', 
        'fill_blank_integer',
        'fill_blank_fraction',
        'fill_blanks_variable'
    ])
    
    if problem_type == 'find_term':
        return generate_find_term_problem()
    elif problem_type == 'find_sequence':
        return generate_find_sequence_problem()
    elif problem_type == 'fill_blank_integer':
        return generate_fill_blank_integer_problem()
    elif problem_type == 'fill_blank_fraction':
        return generate_fill_blank_fraction_problem()
    else: # 'fill_blanks_variable'
        return generate_fill_blanks_variable_problem()

def check(user_answer, correct_answer):
    """
    Checks if the user's answer is correct.
    Handles single numbers, fractions, mixed fractions, and sequences.
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    is_correct = False

    # Case 1: Sequence answer (contains a comma)
    if ',' in correct_answer or '，' in correct_answer:
        user_parts = [p.strip() for p in user_answer.replace('，', ',').split(',')]
        correct_parts = [p.strip() for p in correct_answer.split(',')]
        
        # Remove empty strings that might result from trailing commas
        user_parts = [p for p in user_parts if p]
        correct_parts = [p for p in correct_parts if p]

        if len(user_parts) == len(correct_parts):
            # For variable answers, we need case-insensitive and space-insensitive comparison
            user_normalized = [p.replace(" ", "").lower() for p in user_parts]
            correct_normalized = [p.replace(" ", "").lower() for p in correct_parts]
            if user_normalized == correct_normalized:
                is_correct = True

    # Case 2: Single answer (numeric or variable)
    else:
        # First, try direct string comparison (for variable answers like "a-5")
        if user_answer.replace(" ", "").lower() == correct_answer.replace(" ", "").lower():
            is_correct = True
        else:
            # If not a direct match, try numeric comparison (handles integers, fractions)
            try:
                user_frac = _parse_user_answer_to_fraction(user_answer)
                correct_frac = _parse_user_answer_to_fraction(correct_answer)
                if user_frac == correct_frac:
                    is_correct = True
            except (ValueError, ZeroDivisionError):
                # Parsing failed, so the answer is incorrect if it wasn't a string match
                pass
    
    # Format the correct answer for display, adding LaTeX delimiters
    if re.search(r'[a-zA-Z]', correct_answer): # If it's an algebraic expression
        # Handle sequences of algebraic expressions
        parts = [f"${p.strip()}$" for p in correct_answer.split(',')]
        formatted_correct_answer = ", ".join(parts)
    else:
        # Handle numeric answers
        formatted_correct_answer = f"${correct_answer}$"

    if is_correct:
        result_text = f"完全正確！答案是 {formatted_correct_answer}。"
    else:
        result_text = f"答案不正確。正確答案應為：{formatted_correct_answer}"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}