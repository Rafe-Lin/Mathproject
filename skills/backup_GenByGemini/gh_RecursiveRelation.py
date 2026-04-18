import random
import re
from fractions import Fraction

def generate(level=1):
    """
    生成「遞迴關係」相關題目。
    包含：
    1. 根據首項和公差/公比，寫出遞迴關係式。
    2. 根據給定的遞迴關係式，計算特定項的值。
    3. 根據特殊數列的遞迴關係式，計算特定項的值。
    """
    problem_type = random.choice([
        'rec_arith_relation_formula', # Arithmetic relation string
        'rec_geom_relation_formula',  # Geometric relation string
        'rec_arith_calc_term',        # Calculate term for arithmetic
        'rec_geom_calc_term',         # Calculate term for geometric
        'rec_general_calc_term'       # Calculate term for S_n = S_{n-1} + (2n-1)
    ])

    if problem_type == 'rec_arith_relation_formula':
        return generate_arith_relation_formula(level)
    elif problem_type == 'rec_geom_relation_formula':
        return generate_geom_relation_formula(level)
    elif problem_type == 'rec_arith_calc_term':
        return generate_arith_calc_term(level)
    elif problem_type == 'rec_geom_calc_term':
        return generate_geom_calc_term(level)
    else: # 'rec_general_calc_term'
        return generate_general_calc_term(level)

def generate_arith_relation_formula(level):
    a1 = random.randint(-10, 10)
    d = random.randint(-5, 5)
    while d == 0: # Common difference cannot be 0
        d = random.randint(-5, 5)

    if d > 0:
        d_str = f"+{d}"
    else:
        d_str = str(d) # Already includes '-'

    # Instructions for answer format are crucial for robust checking
    question_text = f"若等差數列 $a_n$ 的首項為 ${a1}$，公差為 ${d}$，則 $a_n$ 的遞迴關係式為何？<br>(請填寫 $a_1=\text{{數字}}, a_n = a_{{n-1}}\text{{符號}}\text{{數字}} (n>=2)$ 的形式)"
    correct_answer = f"a_1={a1}, a_n = a_{{n-1}}{d_str} (n>=2)"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_geom_relation_formula(level):
    a1 = random.randint(1, 5)
    r = random.choice([-2, -1, 2, 3, 4])
    while r == 0 or r == 1 or a1 == 0: # Common ratio cannot be 0 or 1, a1 cannot be 0
        r = random.choice([-2, -1, 2, 3, 4])
        a1 = random.randint(1, 5)

    # Instructions for answer format are crucial for robust checking
    question_text = f"若等比數列 $a_n$ 的首項為 ${a1}$，公比為 ${r}$，則 $a_n$ 的遞迴關係式為何？<br>(請填寫 $a_1=\text{{數字}}, a_n = \text{{數字}}a_{{n-1}} (n>=2)$ 的形式)"
    correct_answer = f"a_1={a1}, a_n = {r}a_{{n-1}} (n>=2)"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_arith_calc_term(level):
    a1 = random.randint(-15, 15)
    d = random.randint(-7, 7)
    while d == 0:
        d = random.randint(-7, 7)

    # Scale k based on level, ensure k is at least 4
    k_min = max(4, 4 + (level-1)*2)
    k_max = max(k_min + 3, 10 + (level-1)*2) # Ensure a range
    k = random.randint(k_min, k_max)

    correct_term = a1 + (k - 1) * d

    if d > 0:
        d_str = f"+{d}"
    else:
        d_str = str(d)

    question_text = f"若數列 $a_n$ 的遞迴關係式為 $a_1={a1}, a_n = a_{{n-1}}{d_str} (n \\ge 2)$，求 $a_{{k}}$ 的值。"
    correct_answer = str(correct_term)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_geom_calc_term(level):
    a1 = random.randint(1, 5)
    r = random.choice([-2, -1, 2, 3]) # Keep r small to avoid huge numbers
    while r == 0 or r == 1 or a1 == 0:
        r = random.choice([-2, -1, 2, 3])
        a1 = random.randint(1, 5)

    # Scale k based on level, ensure k is at least 4
    k_min = max(4, 4 + (level-1)*1)
    k_max = max(k_min + 1, 6 + (level-1)*1) # Powers grow fast, so k should increase slowly
    k = random.randint(k_min, k_max)

    correct_term = a1 * (r**(k - 1))

    question_text = f"若數列 $a_n$ 的遞迴關係式為 $a_1={a1}, a_n = {r}a_{{n-1}} (n \\ge 2)$，求 $a_{{k}}$ 的值。"
    correct_answer = str(correct_term)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_general_calc_term(level):
    # This problem type is based on the "sum of odd numbers" example (魚鱗陣)
    # where S_n = S_{n-1} + (2n-1) and S_k = k^2.
    s1 = 1 # S_1 is always 1 for this specific series
    
    # Scale k based on level, ensure k is at least 4
    k_min = max(4, 4 + (level-1)*2)
    k_max = max(k_min + 3, 10 + (level-1)*2)
    k = random.randint(k_min, k_max)

    correct_term = k * k # S_k = k^2 for sum of first k odd numbers

    question_text = f"若數列 $S_n$ 的遞迴關係式為 $S_1={s1}, S_n = S_{{n-1}}+(2n-1) (n \\ge 2)$，求 $S_{{k}}$ 的值。"
    correct_answer = str(correct_term)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def _normalize_recursive_relation_string_for_check(s):
    """
    Standardizes recursive relation strings for robust comparison.
    It expects strings like "a_1=5, a_n = a_{n-1}-3 (n>=2)"
    or "a_1=5, a_n = 2a_{n-1} (n>=2)".
    """
    s = s.strip()
    s = s.replace(' ', '') # Remove all whitespace
    s = s.replace('\\,', ',') # Handle LaTeX comma spacing
    s = s.lower() # Case insensitive for 'a', 'n', 's'

    # Normalize a_1=X / s_1=X
    s = re.sub(r'(a|s)_1=(-?\d+)', r'\1_1=\2', s)

    # Normalize arithmetic part: a_n=a_{n-1}+(-D) -> a_n=a_{n-1}-D
    s = re.sub(r'\+\(-(\d+)\)', r'-\1', s) # e.g. +(-3) -> -3
    
    # Standardize signs for arithmetic terms
    s = re.sub(r'([as])_{n-1}(\+\d+)', r'\1_{n-1}\2', s) # Ensure + sign is explicit for positive diff
    s = re.sub(r'([as])_{n-1}(\-\d+)', r'\1_{n-1}\2', s) # Ensure - sign is explicit for negative diff

    # Normalize geometric part: a_n=Ra_{n-1}
    # Ensure there's no explicit '+' if it's a positive ratio, e.g., 'a_n=+2a_{n-1}' -> 'a_n=2a_{n-1}'
    s = re.sub(r'([as])_n=\+(\d+)([as])_{n-1}', r'\1_n=\2\3_{n-1}', s)
    s = re.sub(r'([as])_n=(-?\d+)([as])_{n-1}', r'\1_n=\2\3_{n-1}', s) # This is sufficient

    # Normalize general term f(n) for S_n = S_{n-1} + (2n-1)
    s = re.sub(r'([as])_{n-1}\+\(2n-1\)', r'\1_{n-1}+(2n-1)', s)

    # Standardize the (n>=2) part
    # Handle various forms: (n >= 2), (n>=2), (n \\ge 2), (N>=2), (n >= 2)
    # The regex should capture any variation and normalize it to '(n>=2)'
    s = re.sub(r'\(.*[ans]\s*(?:>=|\\ge)\s*2.*\)', r'(n>=2)', s) 
    
    return s

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer_stripped = user_answer.strip()
    correct_answer_stripped = correct_answer.strip()

    is_correct = False
    feedback = ""

    # First, try to check if it's a numerical answer
    try:
        user_num = float(user_answer_stripped)
        correct_num = float(correct_answer_stripped)
        if user_num == correct_num:
            is_correct = True
            feedback = f"完全正確！答案是 ${correct_answer_stripped}$。"
        else:
            feedback = f"答案不正確。正確答案應為：${correct_answer_stripped}$"
    except ValueError:
        # If not a simple number, assume it's a recursive relation string
        # Normalize both user and correct answers for comparison
        user_answer_standardized = _normalize_recursive_relation_string_for_check(user_answer_stripped)
        correct_answer_standardized = _normalize_recursive_relation_string_for_check(correct_answer_stripped)

        if user_answer_standardized == correct_answer_standardized:
            is_correct = True
            feedback = f"完全正確！答案是 ${correct_answer_stripped}$。"
        else:
            feedback = f"答案不正確。正確答案應為：${correct_answer_stripped}$"

    return {"correct": is_correct, "result": feedback, "next_question": True}