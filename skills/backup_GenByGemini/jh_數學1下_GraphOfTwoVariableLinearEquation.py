import random
from fractions import Fraction
import math

def _format_equation(a, b, c):
    """Formats ax + by = c into a human-readable string."""
    parts = []
    # X-term
    if a != 0:
        if a == 1:
            parts.append("x")
        elif a == -1:
            parts.append("-x")
        else:
            parts.append(f"{a}x")
    
    # Y-term
    if b != 0:
        sign = " + " if b > 0 else " - "
        val = abs(b)
        
        # If it's the first term, remove the leading sign if it's positive
        if not parts and sign == " + ":
            sign = ""
        # If it's the first term and negative, just use a hyphen
        elif not parts and sign == " - ":
            sign = "-"
            
        if val == 1:
            term = f"{sign}y"
        else:
            term = f"{sign}{val}y"
        parts.append(term)
        
    if not parts:
        lhs = "0"
    else:
        lhs = "".join(parts)
        
    return f"{lhs} = {c}"

def generate_complete_table_problem():
    """
    題型：給定二元一次方程式，完成解的表格。
    """
    # Force one coefficient to be 1 or -1 for easy integer solutions
    a = random.choice([-3, -2, -1, 1, 2, 3])
    b = random.choice([-1, 1])
    
    # Randomly decide which variable gets the easy coefficient
    if random.random() < 0.5:
        a, b = b, a
        
    c = random.randint(-6, 6)
    
    equation_str = _format_equation(a, b, c)
    
    # Generate 3 distinct x-values, sorted for user-friendliness
    x_values = sorted(random.sample(range(-4, 5), 3))
    y_values = []
    
    for x in x_values:
        # ax + by = c => by = c - ax => y = (c - ax) / b
        # Since b is +/-1, y will be an integer.
        y = (c - a * x) // b
        y_values.append(y)

    # Create the table display using a preformatted text block
    header = f"x | {' | '.join(map(str, x_values))}"
    divider = "--|--" + "--|--".join(["-" * len(str(v)) for v in x_values])
    body = f"y | {' | '.join(['?'] * len(x_values))}"
    table = f"{header}\n{divider}\n{body}"
    
    question_text = f"請完成二元一次方程式 ${equation_str}$ 的解的表格，並將 $y$ 的值由左至右依序填入答案欄，以逗號分隔 (不含空格)。<br><pre>{table}</pre>"
    correct_answer = ",".join(map(str, y_values))
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_identify_point_problem():
    """
    題型：給定一個方程式和數個點，判斷哪一個點在圖形上。
    """
    a = random.choice([-3, -2, -1, 1, 2, 3])
    b = random.choice([-1, 1])
    if random.random() < 0.5:
        a, b = b, a
    c = random.randint(-5, 5)
    
    equation_str = _format_equation(a, b, c)
    
    # Generate one correct point
    x_correct = random.randint(-5, 5)
    y_correct = (c - a * x_correct) // b
    correct_point = (x_correct, y_correct)
    
    # Generate three distractor points
    distractors = []
    used_points = {correct_point}
    while len(distractors) < 3:
        x_d = random.randint(-5, 5)
        # Calculate correct y and add a non-zero offset
        y_d_correct = (c - a * x_d) // b
        offset = random.choice([-3, -2, -1, 1, 2, 3])
        y_d = y_d_correct + offset
        
        point_d = (x_d, y_d)
        if point_d not in used_points:
            distractors.append(point_d)
            used_points.add(point_d)
            
    options = [correct_point] + distractors
    random.shuffle(options)
    
    option_strs = []
    correct_label = ''
    labels = ['A', 'B', 'C', 'D']
    for i, p in enumerate(options):
        label = labels[i]
        option_strs.append(f"({label}) $({p[0]}, {p[1]})$")
        if p == correct_point:
            correct_label = label
            
    question_text = f"下列哪一個點在二元一次方程式 ${equation_str}$ 的圖形上？<br>{' '.join(option_strs)}"
    
    return {
        "question_text": question_text,
        "answer": correct_label,
        "correct_answer": correct_label
    }

def generate_identify_equation_problem():
    """
    題型：給定兩點，判斷哪一個方程式的圖形會通過這兩點。
    """
    # Generate the correct equation first in y = mx + k form for simplicity
    m = random.choice([-3, -2, -1, 1, 2, 3])
    k = random.randint(-4, 4)
    # Convert to ax + by = c form: mx - y = -k
    a, b, c = m, -1, -k
    
    # Generate two distinct points on the line
    x1 = random.randint(-4, 4)
    y1 = m * x1 + k
    
    x2 = x1
    while x2 == x1:
        x2 = random.randint(-4, 4)
    y2 = m * x2 + k

    correct_params = (a, b, c)
    all_params = {correct_params}
    distractors_params = []
    
    # Generate 3 distractor equations
    while len(distractors_params) < 3:
        m_d = random.choice([-3, -2, -1, 1, 2, 3])
        k_d = random.randint(-4, 4)
        
        # Ensure distractor is different from the correct one
        if m_d == m and k_d == k:
            continue
            
        ad, bd, cd = m_d, -1, -k_d
        
        # Ensure it's not a duplicate distractor
        if (ad, bd, cd) in all_params:
            continue

        # A distractor is valid if it doesn't pass through *both* given points.
        is_valid_distractor = not (ad*x1 + bd*y1 == cd and ad*x2 + bd*y2 == cd)
        
        if is_valid_distractor:
            distractors_params.append((ad, bd, cd))
            all_params.add((ad, bd, cd))

    option_params = [correct_params] + distractors_params
    random.shuffle(option_params)

    option_strs = []
    correct_label = ''
    labels = ['A', 'B', 'C', 'D']
    for i, params in enumerate(option_params):
        label = labels[i]
        eq_str = _format_equation(*params)
        option_strs.append(f"({label}) ${eq_str}$")
        if params == correct_params:
            correct_label = label
            
    question_text = f"有一圖形為一直線的二元一次方程式，其圖形通過 $({x1}, {y1})$ 和 $({x2}, {y2})$ 兩點。下列何者可能為此方程式？<br>{'<br>'.join(option_strs)}"
    
    return {
        "question_text": question_text,
        "answer": correct_label,
        "correct_answer": correct_label
    }

def generate(level=1):
    """
    生成「二元一次方程式的圖形」相關題目。
    包含：
    1. 查表求值 (complete_table)
    2. 點是否在圖形上 (identify_point)
    3. 由兩點找出方程式 (identify_equation)
    """
    problem_type = random.choice(['complete_table', 'identify_point', 'identify_equation'])
    
    if problem_type == 'complete_table':
        return generate_complete_table_problem()
    elif problem_type == 'identify_point':
        return generate_identify_point_problem()
    else:
        return generate_identify_equation_problem()

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    # Clean up strings for robust comparison
    user_ans_cleaned = "".join(str(user_answer).split()).upper()
    correct_ans_cleaned = "".join(str(correct_answer).split()).upper()
    
    is_correct = (user_ans_cleaned == correct_ans_cleaned)
    
    # Fallback check for single numeric answers
    if not is_correct:
        try:
            if float(user_answer) == float(correct_answer):
                is_correct = True
        except (ValueError, TypeError):
            pass

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}
