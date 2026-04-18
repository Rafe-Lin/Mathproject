import random
from fractions import Fraction
import re

def format_fraction_to_latex(f):
    """
    Formats a Fraction object into a proper LaTeX string.
    Handles integers, proper fractions, and mixed fractions.
    e.g., 2 -> "2", 1/3 -> "\\frac{1}{3}", 7/3 -> "2\\frac{1}{3}"
    """
    if not isinstance(f, Fraction):
        f = Fraction(f)

    if f.denominator == 1:
        return str(f.numerator)

    is_negative = f < 0
    if is_negative:
        f = -f

    integer_part = f.numerator // f.denominator
    numerator_part = f.numerator % f.denominator

    if numerator_part == 0:
        result = str(integer_part)
    elif integer_part == 0:
        result = f"\\frac{{{numerator_part}}}{{{f.denominator}}}"
    else:
        result = f"{integer_part}\\frac{{{numerator_part}}}{{{f.denominator}}}"
    
    if is_negative:
        return f"-{result}"
    return result

def _parse_answer(s):
    """
    Parses a string that could be an integer, decimal, fraction, or mixed fraction.
    Returns a Fraction object or None if parsing fails.
    """
    s = s.strip()
    if not s:
        return None
    # Mixed fraction like "1 1/2" or "-2 3/4"
    mixed_match = re.match(r'(-?\d+)\s+(\d+)/(\d+)', s)
    if mixed_match:
        integer_part = int(mixed_match.group(1))
        num = int(mixed_match.group(2))
        den = int(mixed_match.group(3))
        if den == 0: return None
        if integer_part < 0:
            return Fraction(integer_part * den - num, den)
        else:
            return Fraction(integer_part * den + num, den)
    
    # Simple fraction "1/2", decimal "2.5", or integer "3"
    try:
        return Fraction(s)
    except (ValueError, ZeroDivisionError):
        return None

def generate(level=1):
    """
    Generates a problem related to the number line.
    Skill: jh_數學1上_NumberLine
    Problem Types:
    1. Reading integer coordinates from an ASCII number line.
    2. Determining coordinates of points described as fractions/decimals between integers.
    3. Comparing the positions of points (leftmost/rightmost).
    4. Finding a point's coordinate based on its relative position to another.
    """
    problem_type = random.choice([
        'integer_read', 
        'fractional_pos_description', 
        'comparison', 
        'relative_pos'
    ])
    
    if problem_type == 'integer_read':
        return generate_integer_read_problem()
    elif problem_type == 'fractional_pos_description':
        return generate_fractional_pos_problem()
    elif problem_type == 'comparison':
        return generate_comparison_problem()
    else: # 'relative_pos'
        return generate_relative_pos_problem()

def generate_integer_read_problem():
    """
    Generates a problem asking to read an integer coordinate from an ASCII number line.
    """
    start = random.randint(-10, 5)
    step = random.randint(1, 3)
    num_points = 5
    sequence = [start + i * step for i in range(num_points)]
    
    target_idx = random.randint(1, num_points - 2) # Avoid ends
    target_label = random.choice(['A', 'B', 'C', 'P', 'Q'])
    target_value = sequence[target_idx]
    
    line_parts = []
    for i, val in enumerate(sequence):
        if i == target_idx:
            line_parts.append(f"({target_label})")
        else:
            line_parts.append(str(val))
    
    # ASCII representation of the number line
    ascii_line = "---|".join([f"{p.center(5)}" for p in line_parts]) + "---|"
    ascii_line = "|" + ascii_line

    question_text = f"觀察以下數線，請問 ${target_label}$ 點的坐標為何？\n\n{ascii_line}"
    correct_answer = str(target_value)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "input_type": "text"
    }
    
def generate_fractional_pos_problem():
    """
    Generates a problem asking for a coordinate described as a fraction between two integers.
    """
    start_int = random.randint(-5, 5)
    direction = random.choice(['向右', '向左'])
    
    denominator = random.choice([2, 3, 4, 5, 8, 10])
    numerator = random.randint(1, denominator - 1)
    
    if direction == '向右':
        point_value = Fraction(start_int) + Fraction(numerator, denominator)
        start_point_latex = f"${start_int}$"
        end_point_latex = f"${start_int + 1}$"
        start_desc = f"從 ${start_int}$ 開始{direction}"
    else: # 向左
        point_value = Fraction(start_int) - Fraction(numerator, denominator)
        start_point_latex = f"${start_int}$"
        end_point_latex = f"${start_int - 1}$"
        start_desc = f"從 ${start_int}$ 開始{direction}"

    correct_answer = str(float(point_value))
    
    point_label = random.choice(['A', 'B', 'P', 'Q'])
    question_text = (
        f"在數線上，若將 {start_point_latex} 與 {end_point_latex} 之間的線段"
        f"分成 ${denominator}$ 等分，而 ${point_label}$ 點是{start_desc}的第 ${numerator}$ 個等分點，"
        f"請問 ${point_label}$ 點的坐標為何？"
    )
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "input_type": "handwriting"
    }

def generate_comparison_problem():
    """
    Generates a problem asking which of several points is the leftmost or rightmost.
    Points can be integers, decimals, or fractions.
    """
    num_points = random.choice([3, 4])
    labels = random.sample(['A', 'B', 'C', 'D', 'E'], num_points)
    points = {}
    
    values = set()
    while len(values) < num_points:
        val_type = random.choice(['int', 'frac', 'dec'])
        if val_type == 'int':
            v = Fraction(random.randint(-10, 10))
        elif val_type == 'dec':
            den = random.choice([2, 4, 5, 10])
            num = random.randint(-10 * den, 10 * den)
            v = Fraction(num, den)
        else: # frac
            den = random.choice([3, 5, 6, 7])
            num = random.randint(-10 * den, 10 * den)
            v = Fraction(num, den)
        values.add(v)
    
    values = list(values)
    random.shuffle(values)
    
    points_desc = []
    for i in range(num_points):
        label = labels[i]
        value = values[i]
        points[label] = value
        
        if value.denominator == 1:
            display_val = str(value.numerator)
        elif value.denominator in [2, 4, 5, 10] and random.random() > 0.4:
            display_val = str(float(value))
        else:
            display_val = format_fraction_to_latex(value)
        
        points_desc.append(f"{label}(${display_val}$)")
    
    target_pos = random.choice(['最左邊', '最右邊'])
    
    if target_pos == '最右邊':
        correct_label = max(points, key=points.get)
    else:
        correct_label = min(points, key=points.get)
        
    question_text = f"已知數線上數點：{', '.join(points_desc)}，請問哪一點在{target_pos}？ (請填入代號)"
    
    return {
        "question_text": question_text,
        "answer": correct_label,
        "correct_answer": correct_label,
        "input_type": "text"
    }

def generate_relative_pos_problem():
    """
    Generates a problem about finding a coordinate based on relative position.
    """
    val_a = Fraction(random.randint(-20, 20), random.choice([1, 2]))
    val_diff = Fraction(random.randint(1, 20), random.choice([1, 2]))
    direction = random.choice(['左', '右'])
    
    if direction == '右':
        val_b = val_a + val_diff
    else:
        val_b = val_a - val_diff
    
    val_a_str = str(float(val_a)) if random.random() > 0.5 and val_a.denominator != 1 else format_fraction_to_latex(val_a)
    val_diff_str = str(float(val_diff)) if random.random() > 0.5 and val_diff.denominator != 1 else format_fraction_to_latex(val_diff)

    question_text = (
        f"數線上 A 點的坐標為 ${val_a_str}$，"
        f"若 B 點在 A 點的{direction}邊 ${val_diff_str}$ 單位處，"
        f"請問 B 點的坐標為何？"
    )
    
    correct_answer = str(float(val_b))
    input_type = 'handwriting' if val_b.denominator != 1 else 'text'
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "input_type": input_type
    }

def check(user_answer, correct_answer):
    """
    Checks if the user's answer is correct. Handles integers, decimals, fractions,
    mixed fractions, and text labels.
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    
    correct_fraction = _parse_answer(correct_answer)
    
    is_correct = False
    if correct_fraction is not None:
        user_fraction = _parse_answer(user_answer)
        if user_fraction is not None and user_fraction == correct_fraction:
            is_correct = True
    else:
        if user_answer.upper() == correct_answer.upper():
            is_correct = True
            
    display_answer = correct_answer
    if correct_fraction is not None:
        display_answer = f"${format_fraction_to_latex(correct_fraction)}$"

    if is_correct:
        result_text = f"完全正確！答案是 {display_answer}。"
    else:
        result_text = f"答案不正確。正確答案應為：{display_answer}"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}
