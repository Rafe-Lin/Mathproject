import random
import math
from fractions import Fraction
import re

# Helper function to format numbers, especially for square roots
def format_number(num):
    """
    Formats a number for LaTeX output. Handles integers, floats, and square roots.
    e.g., 3 -> "3", 3.0 -> "3", math.sqrt(13) -> "\\sqrt{13}", 3.14159 -> "3.14"
    """
    if isinstance(num, int):
        return str(num)
    if isinstance(num, float):
        if num.is_integer():
            return str(int(num))
        # Check if num is sqrt(X) where X is an integer
        sq_val = num * num
        if abs(sq_val - round(sq_val)) < 1e-9 and round(sq_val) > 0: # Check for floating point precision and positive radicand
            return r"\\sqrt{{{}}}".format(int(round(sq_val)))
        # For decimal numbers, round to 2 places for display
        return str(round(num, 2))
    return str(num) # Fallback

def format_coords(x, y):
    """
    Formats coordinates (x, y) into a string like "(X, Y)".
    """
    return f"({format_number(x)}, {format_number(y)})"

def get_coord_part(var_name, coord_val):
    """
    Generates the (variable - coordinate) part for a standard form equation.
    e.g., 'x', 0 -> "x"
          'x', 3 -> "(x-3)"
          'y', -2 -> "(y+2)"
    """
    if coord_val == 0:
        return var_name
    elif coord_val > 0:
        return f"({var_name}-{coord_val})"
    else: # coord_val < 0
        return f"({var_name}+{abs(coord_val)})"

def generate(level=1):
    """
    Generates a problem related to the standard form of a hyperbola.
    Includes:
    1. Finding the equation given foci and transverse axis length.
    2. Finding vertices, foci, and asymptotes from a general form equation.
    3. True/False questions about hyperbola properties.
    """
    problem_type = random.choice([
        'equation_from_foci_transverse',
        'properties_from_general_form',
        'true_false_properties'
    ])
    
    if problem_type == 'equation_from_foci_transverse':
        return generate_equation_from_foci_transverse(level)
    elif problem_type == 'properties_from_general_form':
        return generate_properties_from_general_form(level)
    else: # true_false_properties
        return generate_true_false_properties(level)

def generate_equation_from_foci_transverse(level):
    """
    Generates a problem to find the hyperbola equation given foci and transverse axis length.
    """
    h = random.randint(-3, 3)
    k = random.randint(-3, 3)

    # Ensure a, b are distinct positive integers to avoid trivial cases
    a_val = random.randint(2, 5)
    b_val = random.randint(2, 5)
    while a_val == b_val:
        b_val = random.randint(2, 5)

    a_sq = a_val**2
    b_sq = b_val**2
    
    c_sq = a_sq + b_sq
    c_val = math.sqrt(c_sq)
    
    # Randomly decide if the transverse axis is parallel to x-axis or y-axis
    x_axis_parallel = random.choice([True, False])

    x_part = get_coord_part('x', h)
    y_part = get_coord_part('y', k)

    if x_axis_parallel:
        f1_coords = (h - c_val, k)
        f2_coords = (h + c_val, k)
        correct_equation = f"\\frac{{{x_part}^2}}{{{a_sq}}} - \\frac{{{y_part}^2}}{{{b_sq}}} = 1"
    else: # y-axis parallel
        f1_coords = (h, k - c_val)
        f2_coords = (h, k + c_val)
        correct_equation = f"\\frac{{{y_part}^2}}{{{a_sq}}} - \\frac{{{x_part}^2}}{{{b_sq}}} = 1"

    f1_str = format_coords(f1_coords[0], f1_coords[1])
    f2_str = format_coords(f2_coords[0], f2_coords[1])
    transverse_len_str = format_number(2 * a_val)

    question_text = f"求兩焦點為 ${f1_str}$, ${f2_str}$，貫軸長為 ${transverse_len_str}$ 的雙曲線方程式。"
    
    return {
        "question_text": question_text,
        "answer": correct_equation, 
        "correct_answer": correct_equation
    }

def generate_properties_from_general_form(level):
    """
    Generates a problem to find vertices, foci, and asymptotes
    from a general form hyperbola equation.
    """
    h = random.randint(-2, 2)
    k = random.randint(-2, 2)
    a_val = random.randint(2, 4)
    b_val = random.randint(2, 4)
    while a_val == b_val: 
        b_val = random.randint(2, 4)
    
    a_sq = a_val**2
    b_sq = b_val**2
    c_sq = a_sq + b_sq
    c_val = math.sqrt(c_sq)

    x_axis_parallel = random.choice([True, False])
    
    # Determine coefficients for Ax^2 + By^2 + Dx + Ey + F = 0
    if x_axis_parallel: # From (x-h)^2/a^2 - (y-k)^2/b^2 = 1 => b^2(x-h)^2 - a^2(y-k)^2 = a^2b^2
        A_coeff = b_sq
        B_coeff = -a_sq
        D_coeff = -2 * b_sq * h
        E_coeff = 2 * a_sq * k
        F_coeff = b_sq * h**2 - a_sq * k**2 - a_sq * b_sq
    else: # From (y-k)^2/a^2 - (x-h)^2/b^2 = 1 => a^2(y-k)^2 - b^2(x-h)^2 = a^2b^2
        A_coeff = -b_sq
        B_coeff = a_sq
        D_coeff = 2 * b_sq * h
        E_coeff = -2 * a_sq * k
        F_coeff = a_sq * k**2 - b_sq * h**2 - a_sq * b_sq

    # Randomly scale coefficients to make the equation appear more "general"
    multiplier = random.choice([1, 2, 3]) 
    A_coeff *= multiplier
    B_coeff *= multiplier
    D_coeff *= multiplier
    E_coeff *= multiplier
    F_coeff *= multiplier
    
    # Construct the general form equation string
    equation_parts = []
    if A_coeff != 0: equation_parts.append(f"{A_coeff}x^2")
    if B_coeff != 0: 
        equation_parts.append(f"{'+' if B_coeff > 0 and equation_parts else ''}{B_coeff}y^2")
    if D_coeff != 0: 
        equation_parts.append(f"{'+' if D_coeff > 0 and equation_parts else ''}{D_coeff}x")
    if E_coeff != 0: 
        equation_parts.append(f"{'+' if E_coeff > 0 and equation_parts else ''}{E_coeff}y")
    if F_coeff != 0: 
        equation_parts.append(f"{'+' if F_coeff > 0 and equation_parts else ''}{F_coeff}")
    
    general_equation_str = "".join(equation_parts)
    if general_equation_str.startswith("+"): general_equation_str = general_equation_str[1:] # Remove leading plus
    
    general_equation_display = f"${general_equation_str} = 0$"

    # Calculate properties for the answer
    if x_axis_parallel: # Transverse axis parallel to x-axis
        v1 = (h - a_val, k)
        v2 = (h + a_val, k)
        f1 = (h - c_val, k)
        f2 = (h + c_val, k)
        # Asymptotes: y-k = +- (b/a)(x-h)  => b(x-h) - a(y-k) = 0  AND b(x-h) + a(y-k) = 0
        asymp_part1_x = f"{b_val}{get_coord_part('x', h)}"
        asymp_part2_y = f"{a_val}{get_coord_part('y', k)}"
        asymptote1_eq = f"${asymp_part1_x} - {asymp_part2_y} = 0$"
        asymptote2_eq = f"${asymp_part1_x} + {asymp_part2_y} = 0$"
    else: # Transverse axis parallel to y-axis
        v1 = (h, k - a_val)
        v2 = (h, k + a_val)
        f1 = (h, k - c_val)
        f2 = (h, k + c_val)
        # Asymptotes: y-k = +- (a/b)(x-h)  => a(x-h) - b(y-k) = 0  AND a(x-h) + b(y-k) = 0
        asymp_part1_x = f"{a_val}{get_coord_part('x', h)}"
        asymp_part2_y = f"{b_val}{get_coord_part('y', k)}"
        asymptote1_eq = f"${asymp_part1_x} - {asymp_part2_y} = 0$"
        asymptote2_eq = f"${asymp_part1_x} + {asymp_part2_y} = 0$"
    
    vertices_str = f"兩頂點分別為 ${format_coords(v1[0], v1[1])}$ 與 ${format_coords(v2[0], v2[1])}$。"
    foci_str = f"兩焦點分別為 ${format_coords(f1[0], f1[1])}$ 與 ${format_coords(f2[0], f2[1])}$。"
    asymptotes_str = f"兩漸近線分別為 {asymptote1_eq} 與 {asymptote2_eq}。"

    question_text = f"求雙曲線 {general_equation_display} 的頂點、焦點坐標與漸近線方程式。"
    
    # Use a structured string for the answer to enable robust checking
    # Store raw strings for asymptotes without $ for internal comparison
    correct_answer_string = (
        f"頂點: {format_coords(v1[0], v1[1])}, {format_coords(v2[0], v2[1])}\n"
        f"焦點: {format_coords(f1[0], f1[1])}, {format_coords(f2[0], f2[1])}\n"
        f"漸近線: {asymptote1_eq.replace('$', '')}, {asymptote2_eq.replace('$', '')}"
    )

    return {
        "question_text": question_text,
        "answer": correct_answer_string, 
        "correct_answer": correct_answer_string
    }

def generate_true_false_properties(level):
    """
    Generates a True/False question about hyperbola properties.
    """
    h = random.randint(-3, 3)
    k = random.randint(-3, 3)
    a_val = random.randint(2, 5)
    b_val = random.randint(2, 5)
    while a_val == b_val:
        b_val = random.randint(2, 5)

    a_sq = a_val**2
    b_sq = b_val**2
    c_sq = a_sq + b_sq
    c_val = math.sqrt(c_sq)

    x_axis_parallel = random.choice([True, False])

    x_part = get_coord_part('x', h)
    y_part = get_coord_part('y', k)

    if x_axis_parallel:
        eq_str = f"\\frac{{{x_part}^2}}{{{a_sq}}} - \\frac{{{y_part}^2}}{{{b_sq}}} = 1"
    else:
        eq_str = f"\\frac{{{y_part}^2}}{{{a_sq}}} - \\frac{{{x_part}^2}}{{{b_sq}}} = 1"
    
    eq_display = f"雙曲線 ${eq_str}$"

    property_type = random.choice([
        'distance_diff',        # Absolute difference of distances to foci is 2a
        'transverse_axis_orientation', # Transverse axis is parallel to x or y-axis
        'asymptotes_intersection' # Asymptotes intersect at (h,k)
    ])

    statement = ""
    correct_bool = None

    if property_type == 'distance_diff':
        true_value = 2 * a_val
        # Randomly generate a displayed value that is sometimes correct, sometimes off
        if random.random() < 0.7: 
            displayed_value = true_value if random.random() < 0.7 else true_value + random.choice([-1, 1]) * random.randint(1, 2)
        else: # Clearly false value
            displayed_value = true_value + random.choice([-1, 1]) * random.randint(3, 5)
        
        statement = f"{eq_display} 上任一點到兩焦點距離差的絕對值為 ${format_number(displayed_value)}$。"
        correct_bool = (displayed_value == true_value)
    
    elif property_type == 'transverse_axis_orientation':
        actual_orientation = "x" if x_axis_parallel else "y"
        # Randomly choose a stated orientation
        stated_orientation = random.choice(["x", "y"])
        statement = f"{eq_display} 的貫軸平行 ${stated_orientation}$ 軸。"
        correct_bool = (stated_orientation == actual_orientation)

    elif property_type == 'asymptotes_intersection':
        # Randomly choose a stated center, sometimes correct, sometimes off
        if random.random() < 0.7:
            stated_h = h if random.random() < 0.7 else h + random.choice([-1, 1])
            stated_k = k if random.random() < 0.7 else k + random.choice([-1, 1])
        else: # Clearly false center
            stated_h = h + random.choice([-1, 1]) * random.randint(2, 3)
            stated_k = k + random.choice([-1, 1]) * random.randint(2, 3)
        stated_center_str = format_coords(stated_h, stated_k)
        
        statement = f"{eq_display} 的兩漸近線交於 ${stated_center_str}$。"
        correct_bool = (stated_h == h and stated_k == k)
    
    question_text = f"下列敘述對的打「○」，錯的打「╳」。<br>□　(1) {statement}"
    correct_answer = "○" if correct_bool else "╳"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

# Helper for normalizing strings for comparison
def normalize_string(s):
    """
    Normalizes a string for comparison by removing whitespace, LaTeX delimiters,
    and standardizing common LaTeX commands and mathematical syntax.
    """
    # Remove all whitespace and LaTeX equation delimiters
    s = s.replace(" ", "").replace("$", "").replace("\\,", "")
    # Standardize common math operators/symbols
    s = s.replace("+-", "-") # e.g., x+-3 => x-3
    s = s.replace("--", "+") # e.g., x--3 => x+3
    s = s.replace("++", "+") # e.g., x++3 => x+3
    # Standardize LaTeX commands
    s = s.replace(r"\\frac", "frac").replace(r"\\sqrt", "sqrt").replace(r"\\pm", "+-") # Convert to plain text forms
    # Standardize (x-h)^2 to (x-h)^2 etc.
    s = s.replace("**", "^") 
    s = s.lower() # Case insensitive comparison
    return s

def check(user_answer, correct_answer):
    """
    Checks if the user's answer is correct against the generated correct answer.
    Handles True/False, equation strings, and structured multi-line answers.
    """
    user_answer_raw = user_answer.strip()
    correct_answer_raw = correct_answer.strip()
    
    is_correct = False
    result_text = ""

    # --- Type 1: True/False questions ---
    if correct_answer_raw in ["○", "╳"]:
        if user_answer_raw.upper() == correct_answer_raw.upper():
            is_correct = True
            result_text = f"完全正確！答案是 {correct_answer_raw}。"
        else:
            result_text = f"答案不正確。正確答案應為：{correct_answer_raw}"
        return {"correct": is_correct, "result": result_text, "next_question": True}

    # --- Type 2: Equation questions (equation_from_foci_transverse) ---
    # Expected: canonical LaTeX equation string
    # Normalize for comparison
    user_norm = normalize_string(user_answer_raw)
    correct_norm = normalize_string(correct_answer_raw)
    
    if user_norm == correct_norm:
        is_correct = True
        result_text = f"完全正確！答案是 ${correct_answer_raw}$。"
        return {"correct": is_correct, "result": result_text, "next_question": True}


    # --- Type 3: Properties from General Form (multi-line structured answer) ---
    # Expected format: "頂點: ..., ...\n焦點: ..., ...\n漸近線: ..., ..."
    
    # Parse user's answer into a dictionary-like structure
    user_parsed_parts = {}
    for line in user_answer_raw.split('\n'):
        if '頂點:' in line:
            user_parsed_parts['vertices'] = line.replace('頂點:', '').strip()
        elif '焦點:' in line:
            user_parsed_parts['foci'] = line.replace('焦點:', '').strip()
        elif '漸近線:' in line:
            user_parsed_parts['asymptotes'] = line.replace('漸近線:', '').strip()
    
    # Parse correct answer into a dictionary-like structure
    correct_parsed_parts = {}
    for line in correct_answer_raw.split('\n'):
        if '頂點:' in line:
            correct_parsed_parts['vertices'] = line.replace('頂點:', '').strip()
        elif '焦點:' in line:
            correct_parsed_parts['foci'] = line.replace('焦點:', '').strip()
        elif '漸近線:' in line:
            correct_parsed_parts['asymptotes'] = line.replace('漸近線:', '').strip()
            
    # If all expected keys are present in both parsed answers, proceed with comparison
    expected_keys = ['vertices', 'foci', 'asymptotes']
    if all(key in user_parsed_parts and key in correct_parsed_parts for key in expected_keys):
        
        # Compare vertices (order might not matter, so normalize and compare as sets/sorted lists)
        user_vertices_norm = sorted([normalize_string(s.strip()) for s in user_parsed_parts['vertices'].split(',')])
        correct_vertices_norm = sorted([normalize_string(s.strip()) for s in correct_parsed_parts['vertices'].split(',')])
        is_correct_vertices = (user_vertices_norm == correct_vertices_norm)

        # Compare foci (similar to vertices)
        user_foci_norm = sorted([normalize_string(s.strip()) for s in user_parsed_parts['foci'].split(',')])
        correct_foci_norm = sorted([normalize_string(s.strip()) for s in correct_parsed_parts['foci'].split(',')])
        is_correct_foci = (user_foci_norm == correct_foci_norm)

        # Compare asymptotes (order might not matter, normalize and compare as sorted lists)
        user_asymp_norm = sorted([normalize_string(s.strip()) for s in user_parsed_parts['asymptotes'].split(',')])
        correct_asymp_norm = sorted([normalize_string(s.strip()) for s in correct_parsed_parts['asymptotes'].split(',')])
        is_correct_asymptotes = (user_asymp_norm == correct_asymp_norm)

        if is_correct_vertices and is_correct_foci and is_correct_asymptotes:
            is_correct = True
            result_text = "完全正確！"
        else:
            feedback_parts = []
            if not is_correct_vertices: feedback_parts.append("頂點坐標不正確。")
            if not is_correct_foci: feedback_parts.append("焦點坐標不正確。")
            if not is_correct_asymptotes: feedback_parts.append("漸近線方程式不正確。")
            result_text = "答案不完全正確。" + " ".join(feedback_parts)
            
        return {"correct": is_correct, "result": result_text, "next_question": True}

    # Fallback for numerical comparison (unlikely for this skill, but good practice)
    try:
        if float(user_answer_raw) == float(correct_answer_raw):
            is_correct = True
    except ValueError:
        pass

    # Default feedback if none of the specific checks passed
    if is_correct:
        if not result_text: result_text = f"完全正確！答案是 ${correct_answer_raw}$。"
    else:
        if not result_text: result_text = f"答案不正確。正確答案應為：${correct_answer_raw}$"

    return {"correct": is_correct, "result": result_text, "next_question": True}