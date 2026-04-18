import random
from fractions import Fraction

def _get_random_params():
    """Helper function to generate random parameters a, h, k for the quadratic function."""
    # Define possible values for 'a', including integers and fractions
    # Make a=1 and a=-1 more common as they are fundamental cases
    a_coeffs = [-4, -3, -2, 2, 3, 4]
    a_coeffs.extend([Fraction(1, 2), Fraction(1, 3), Fraction(-1, 2), Fraction(-1, 3)])
    a_coeffs.extend([-1, 1] * 3)
    
    a = random.choice(a_coeffs)
    h = random.randint(-9, 9)
    k = random.randint(-9, 9)
    
    return a, h, k

def _format_quadratic(a, h, k):
    """Formats the quadratic function y = a(x-h)^2 + k into a LaTeX string."""
    # Part 1: Handle the coefficient 'a'
    if a == 1:
        a_str = ""
    elif a == -1:
        a_str = "-"
    elif isinstance(a, Fraction):
        sign = ""
        if a < 0:
            sign = "-"
            # work with the absolute value for fraction formatting
            num = -a.numerator
            den = a.denominator
        else:
            num = a.numerator
            den = a.denominator
        
        if den == 1:
            a_str = f"{sign}{num}"
        else:
            a_str = f"{sign}\\frac{{{num}}}{{{den}}}"
    else: # Integer case
        a_str = str(a)

    # Part 2: Handle the (x-h)^2 term
    if h == 0:
        x_term = "x^2"
    elif h > 0:
        x_term = f"(x - {h})^2"
    else:  # h < 0
        x_term = f"(x + {-h})^2"

    # Part 3: Handle the constant 'k'
    if k == 0:
        k_str = ""
    elif k > 0:
        k_str = f" + {k}"
    else:  # k < 0
        k_str = f" - {-k}"

    # Combine all parts into the final equation string
    # When a is 1 or -1, a_str is just "" or "-", which looks better when combined directly.
    if a_str in ["", "-"]:
        full_equation = f"y = {a_str}{x_term}{k_str}"
    else:
        # For other 'a' values, ensure proper spacing if h=0
        if h == 0:
             full_equation = f"y = {a_str}{x_term}{k_str}"
        else:
             full_equation = f"y = {a_str}{x_term}{k_str}"

    return full_equation

def generate_vertex_problem():
    """Generates a question about finding the vertex of a quadratic function."""
    a, h, k = _get_random_params()
    
    equation = _format_quadratic(a, h, k)
    question_text = f"請問二次函數 ${equation}$ 的圖形頂點座標為何？<br>(請以 $(h, k)$ 的形式作答，例如 $(-2, 5)$)"
    
    correct_answer = f"({h}, {k})"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_axis_problem():
    """Generates a question about finding the axis of symmetry."""
    a, h, k = _get_random_params()
    
    equation = _format_quadratic(a, h, k)
    question_text = f"請問二次函數 ${equation}$ 的圖形對稱軸方程式為何？<br>(請以 $x=h$ 的形式作答，例如 $x=3$)"

    correct_answer = f"x={h}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_opening_direction_problem():
    """Generates a question about the opening direction of the parabola."""
    a, h, k = _get_random_params()
    
    equation = _format_quadratic(a, h, k)
    question_text = f"請問二次函數 ${equation}$ 的圖形開口方向為何？<br>(請填「向上」或「向下」)"
    
    correct_answer = "向上" if a > 0 else "向下"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_max_min_problem():
    """Generates a question about finding the maximum or minimum value."""
    a, h, k = _get_random_params()
    
    question_type = "最小值" if a > 0 else "最大值"
    
    equation = _format_quadratic(a, h, k)
    question_text = f"請問當 $x$ 為任意實數時，二次函數 ${equation}$ 的{question_type}為何？"
    
    correct_answer = str(k)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    生成二次函數 y=a(x-h)^2+k 圖形性質的相關題目。
    包含：
    1. 判斷頂點座標
    2. 判斷對稱軸方程式
    3. 判斷開口方向
    4. 判斷最大值或最小值
    """
    problem_type = random.choice(['vertex', 'axis', 'opening_direction', 'max_min'])
    
    if problem_type == 'vertex':
        return generate_vertex_problem()
    elif problem_type == 'axis':
        return generate_axis_problem()
    elif problem_type == 'opening_direction':
        return generate_opening_direction_problem()
    else: # max_min
        return generate_max_min_problem()

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    # Normalize user input by removing whitespace and making it consistent
    user_answer = user_answer.strip()
    
    # Handle specific answer formats
    if correct_answer.startswith('(') and correct_answer.endswith(')'):  # Vertex: (h, k)
        user_answer = user_answer.replace(' ', '').replace('（', '(').replace('）', ')').replace('，', ',')
    elif correct_answer.lower().startswith('x='):  # Axis: x=h
        user_answer = user_answer.replace(' ', '').lower()
        correct_answer = correct_answer.replace(' ', '').lower()
        
    is_correct = (user_answer == correct_answer)
    
    # For answers that are just numbers, try a numeric comparison as a fallback
    if not is_correct:
        try:
            if float(user_answer) == float(correct_answer):
                is_correct = True
        except (ValueError, TypeError):
            pass

    # Format the feedback message
    text_answers = ["向上", "向下"]
    if correct_answer in text_answers:
        feedback_answer = correct_answer
    else:
        # Wrap mathematical answers in LaTeX delimiters
        feedback_answer = f"${correct_answer}$"
        
    if is_correct:
        result_text = f"完全正確！答案是 {feedback_answer}。"
    else:
        result_text = f"答案不正確。正確答案應為：{feedback_answer}"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}