import random
from fractions import Fraction

def format_equation_latex(a, h, k, var='x'):
    """Formats a quadratic function into y=a(x-h)^2+k LaTeX string."""

    # --- Part a (coefficient) ---
    a_val = a
    # Convert Fraction to int if denominator is 1
    if isinstance(a, Fraction) and a.denominator == 1:
        a_val = a.numerator

    if isinstance(a_val, Fraction):
        sign = "-" if a_val < 0 else ""
        # Create LaTeX fraction string
        a_str = f"{sign}\\frac{{{abs(a_val.numerator)}}}{{{a_val.denominator}}}"
    else:  # Integer case
        if a_val == 1:
            a_str = ""
        elif a_val == -1:
            a_str = "-"
        else:
            a_str = str(a_val)

    # --- Part h (vertex x-coordinate) ---
    if h == 0:
        h_str = f"{var}^2"
    elif h > 0:
        h_str = f"({var} - {h})^2"
    else:  # h < 0
        h_str = f"({var} + {-h})^2"

    # --- Part k (vertex y-coordinate) ---
    if k == 0:
        k_str = ""
    elif k > 0:
        k_str = f" + {k}"
    else:  # k < 0
        k_str = f" - {-k}"

    return f"y = {a_str}{h_str}{k_str}"


def generate_max_min_value_problem():
    """
    Generates a problem asking for the max/min value or the x-value where it occurs.
    Corresponds to example: "找出下列各二次函數圖形的頂點..."
    """
    # Use fractions for 'a' about 30% of the time for variety
    if random.random() < 0.3:
        num = random.choice([-5, -4, -3, -2, 2, 3, 4, 5])
        den = random.randint(2, 5)
        a = Fraction(num, den)
    else:
        a = random.choice([-5, -4, -3, -2, 2, 3, 4, 5])

    h = random.randint(-9, 9)
    k = random.randint(-9, 9)

    equation_str = format_equation_latex(a, h, k)
    max_or_min_text = "最大值" if a < 0 else "最小值"

    ask_for = random.choice(['value', 'x_coord'])

    if ask_for == 'value':
        question_text = f"請問二次函數 ${equation_str}$ 的{max_or_min_text}為何？"
        correct_answer = str(k)
    else:  # 'x_coord'
        question_text = f"請問當 x 為何值時，二次函數 ${equation_str}$ 會有{max_or_min_text}？"
        correct_answer = str(h)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def generate_intercepts_count_problem():
    """
    Generates a problem asking for the number of x-intercepts.
    Corresponds to example: "判斷下列二次函數圖形與 x 軸的交點個數。"
    """
    if random.random() < 0.3:
        num = random.choice([-5, -4, -3, -2, 2, 3, 4, 5])
        den = random.randint(2, 5)
        a = Fraction(num, den)
    else:
        a = random.choice([-5, -4, -3, -2, 2, 3, 4, 5])

    h = random.randint(-9, 9)
    # Keep k small to have a good mix of cases (0, 1, or 2 intercepts)
    k = random.randint(-5, 5)

    equation_str = format_equation_latex(a, h, k)

    question_text = f"判斷二次函數 ${equation_str}$ 的圖形與 x 軸的交點個數。"

    if k == 0:
        count = 1
    elif (a > 0 and k > 0) or (a < 0 and k < 0):
        count = 0
    else:  # (a > 0 and k < 0) or (a < 0 and k > 0)
        count = 2

    correct_answer = str(count)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def generate_find_equation_problem():
    """
    Generates a problem to find the quadratic equation given the vertex and a point.
    Corresponds to example: "有一個二次函數，其圖形頂點為..."
    'a' is an integer for easier answer input.
    """
    a = random.choice([-3, -2, 2, 3])
    h = random.randint(-5, 5)
    k = random.randint(-5, 5)

    # Generate a point (x_p, y_p) that is not the vertex
    x_p_offset = random.choice([-2, -1, 1, 2])
    x_p = h + x_p_offset

    # 50% chance the point is the y-intercept (if possible)
    if random.random() < 0.5 and h != 0:
        x_p = 0

    y_p = a * (x_p - h)**2 + k

    question_text = f"有一個二次函數，其圖形頂點為 $({h}, {k})$，且通過點 $({x_p}, {y_p})$，求此二次函數。(答案請寫成 $y=a(x-h)^2+k$ 的形式)"
    correct_answer = format_equation_latex(a, h, k)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def generate_find_vertex_problem():
    """
    Generates a problem to find the vertex given properties like translation, axis of symmetry, and a point.
    Corresponds to example: "已知二次函數 y=a(x-h)^2+k 的圖形可由..."
    'a' is an integer for a clearer problem statement.
    """
    a = random.choice([-4, -3, -2, 2, 3, 4])
    h = random.randint(-5, 5)
    k = random.randint(-5, 5)

    # Generate a point (x_p, y_p) that is not the vertex
    x_p_offset = random.choice([-2, -1, 1, 2])
    x_p = h + x_p_offset
    y_p = a * (x_p - h)**2 + k

    # Format the axis of symmetry string with variation
    if h == 0:
        axis_str = "x=0"
    elif h > 0:
        axis_str = random.choice([f"x={h}", f"x-{h}=0"])
    else:  # h < 0
        axis_str = random.choice([f"x={h}", f"x+{-h}=0"])

    # Format the base function string cleanly
    if a == 1: base_func_str = "y = x^2"
    elif a == -1: base_func_str = "y = -x^2"
    else: base_func_str = f"y = {a}x^2"

    question_text = f"已知某二次函數的圖形可由 ${base_func_str}$ 的圖形平移得到，其對稱軸為直線 ${axis_str}$，且圖形通過點 $({x_p}, {y_p})$，則此二次函數圖形的頂點為何？(請以 $(h,k)$ 格式回答)"
    correct_answer = f"({h},{k})"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def generate(level=1):
    """
    Generates a problem related to the maximum and minimum of a quadratic function.
    """
    problem_type = random.choice([
        'max_min_value',
        'intercepts_count',
        'find_equation',
        'find_vertex'
    ])

    if problem_type == 'max_min_value':
        return generate_max_min_value_problem()
    elif problem_type == 'intercepts_count':
        return generate_intercepts_count_problem()
    elif problem_type == 'find_equation':
        return generate_find_equation_problem()
    else:  # 'find_vertex'
        return generate_find_vertex_problem()


def check(user_answer, correct_answer):
    """
    Checks the user's answer against the correct one.
    Handles numerical, coordinate, and equation formats.
    """
    # Normalize both user answer and correct answer for comparison
    norm_user = user_answer.strip().replace(" ", "").lower()
    norm_correct = correct_answer.strip().replace(" ", "").lower()

    # Case 1: Equation
    if norm_correct.startswith('y='):
        norm_user = norm_user.replace('y=', '')
        norm_correct = norm_correct.replace('y=', '')
        # Handle implicit 1: y=1(x-2)^2 -> y=(x-2)^2
        if norm_correct.startswith('(x'):
            norm_user = norm_user.replace('1(x', '(x')
        # Handle implicit -1: y=-1(x-2)^2 -> y=-(x-2)^2
        if norm_correct.startswith('-(x'):
            norm_user = norm_user.replace('-1(x', '-(x')
        # Handle y=x^2 vs y=1x^2
        if norm_correct == "x^2" and norm_user == "1x^2":
            norm_user = "x^2"
        if norm_correct == "-x^2" and norm_user == "-1x^2":
            norm_user = "-x^2"

    # Case 2: Coordinates
    elif norm_correct.startswith('(') and norm_correct.endswith(')'):
        norm_user = norm_user.replace('(', '').replace(')', '')
        norm_correct = norm_correct.replace('(', '').replace(')', '')
        # Also allow for full-width comma
        norm_user = norm_user.replace('，', ',')

    is_correct = (norm_user == norm_correct)

    # Fallback for numerical answers with potential float representations
    if not is_correct:
        try:
            if float(norm_user) == float(norm_correct):
                is_correct = True
        except (ValueError, TypeError):
            pass

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}