import random
import math
from fractions import Fraction
import re

def format_term(variable, coordinate):
    """
    Formats a single term (e.g., (x-h)^2 or (y-k)^2).
    Ensures correct display for positive, negative, and zero coordinates.
    """
    # Ensure coordinate is an integer if it's a Fraction that simplifies to an integer
    if isinstance(coordinate, Fraction):
        coordinate = int(coordinate) if coordinate.denominator == 1 else coordinate

    if coordinate == 0:
        return f"{variable}^{{2}}"
    elif coordinate > 0:
        return f"({variable}-{coordinate})^{{2}}"
    else: # coordinate < 0
        return f"({variable}+{-coordinate})^{{2}}" # -coordinate makes it positive for display

def generate_equation_string(h, k, r_sq):
    """
    Generates the full circle equation string in standard form (x-h)^2 + (y-k)^2 = r^2.
    """
    x_term = format_term("x", h)
    y_term = format_term("y", k)
    
    # r_sq might be a float (e.g., 25.0). Ensure it's displayed as an integer if it is.
    # Also handle Fraction objects for r_sq
    r_sq_str = ""
    if isinstance(r_sq, Fraction):
        r_sq_str = str(int(r_sq)) if r_sq.denominator == 1 else f"\\frac{{{r_sq.numerator}}}{{{r_sq.denominator}}}"
    elif isinstance(r_sq, float) and r_sq.is_integer():
        r_sq_str = str(int(r_sq))
    else:
        r_sq_str = str(r_sq)

    return f"{x_term} + {y_term} = {r_sq_str}"

def extract_circle_params(eq_str):
    """
    Extracts (h, k, r_sq) from a standard form circle equation string.
    Returns (h, k, r_sq) tuple or None if parsing fails.
    This function handles flexible input for term order.
    """
    eq_str = eq_str.replace(" ", "").replace("+-", "-").replace("--", "+") # Normalize spaces and signs

    # Split into LHS and RHS based on '='
    parts = eq_str.split('=')
    if len(parts) != 2:
        return None # Invalid format

    lhs = parts[0]
    rhs = parts[1]

    # Extract r_sq
    try:
        r_sq = float(rhs)
    except ValueError:
        return None # Invalid r_sq

    h, k = None, None
    
    # Split LHS into potential (x-h)^2 and (y-k)^2 terms
    terms_on_lhs = lhs.split('+')
    if len(terms_on_lhs) != 2:
        return None # Expected exactly two terms joined by '+'

    for term in terms_on_lhs:
        # Try to match x-term
        match_x_term_offset = re.match(r"\(x([+\-]\d+)\)\^{{2}}", term)
        if match_x_term_offset:
            h = -int(match_x_term_offset.group(1))
            continue
        match_x_sq = re.match(r"x\^{{2}}", term)
        if match_x_sq:
            h = 0
            continue
        
        # Try to match y-term
        match_y_term_offset = re.match(r"\(y([+\-]\d+)\)\^{{2}}", term)
        if match_y_term_offset:
            k = -int(match_y_term_offset.group(1))
            continue
        match_y_sq = re.match(r"y\^{{2}}", term)
        if match_y_sq:
            k = 0
            continue
            
    if h is None or k is None:
        return None # Could not parse both h and k components from the two terms

    # Convert r_sq to int if it's a whole number
    r_sq = int(r_sq) if r_sq.is_integer() else r_sq
    
    return (h, k, r_sq)

def generate(level=1):
    problem_type_weights = {
        'center_radius': 0.35,
        'center_point': 0.3,
        'diameter_endpoints': 0.2,
        'find_k_in_equation': 0.15
    }
    
    # Select problem type based on weights
    problem_type = random.choices(
        list(problem_type_weights.keys()), 
        weights=list(problem_type_weights.values()), 
        k=1
    )[0]

    if problem_type == 'center_radius':
        return generate_center_radius_problem(level)
    elif problem_type == 'center_point':
        return generate_center_point_problem(level)
    elif problem_type == 'diameter_endpoints':
        return generate_diameter_endpoints_problem(level)
    elif problem_type == 'find_k_in_equation':
        return generate_find_k_in_equation_problem(level)

def generate_center_radius_problem(level):
    h = random.randint(-5, 5)
    k = random.randint(-5, 5)
    
    # Radius r can be integer or sqrt(N)
    if level == 1:
        r = random.randint(1, 5) # Smaller integer radius
        r_sq = r**2
        r_str = str(r)
    else:
        r_sq_choices = [
            random.randint(1, 8)**2,  # integer radius
            random.randint(2, 20)     # sqrt(N) radius
        ]
        r_sq = random.choice(r_sq_choices)
        r_str = str(int(math.sqrt(r_sq))) if math.sqrt(r_sq).is_integer() else f"\\sqrt{{{r_sq}}}"

    question_text = f"求以點 $({h}, {k})$ 為圓心，半徑為 ${r_str}$ 的圓的方程式。"
    correct_equation = generate_equation_string(h, k, r_sq)
    
    return {
        "question_text": question_text,
        "answer": correct_equation, # The equation itself is the answer for direct comparison
        "correct_answer": correct_equation
    }

def generate_center_point_problem(level):
    h = random.randint(-5, 5)
    k = random.randint(-5, 5)

    # Generate a point (x_p, y_p) that's sufficiently far from the center
    # and results in a 'nice' r_sq (e.g., perfect square or small non-square)
    while True:
        dx = random.randint(-7, 7)
        dy = random.randint(-7, 7)
        if dx == 0 and dy == 0:
            continue
        
        r_sq_candidate = dx**2 + dy**2
        
        # Filter for reasonable r_sq values based on level
        if level == 1:
            if not (1 <= r_sq_candidate <= 50 and (math.sqrt(r_sq_candidate).is_integer() or r_sq_candidate in [2,5,8,10,13,17,18,20,25,26,29,32,34,37,40,41,45,50])):
                continue
        else: # Level 2+
            if not (1 <= r_sq_candidate <= 100):
                continue

        x_p = h + dx
        y_p = k + dy
        r_sq = r_sq_candidate
        break
    
    question_text = f"求以點 $({h}, {k})$ 為圓心，又通過點 $({x_p}, {y_p})$ 的圓的方程式。"
    correct_equation = generate_equation_string(h, k, r_sq)

    return {
        "question_text": question_text,
        "answer": correct_equation,
        "correct_answer": correct_equation
    }

def generate_diameter_endpoints_problem(level):
    # Ensure integer midpoints and r_sq for simplicity
    max_attempts = 100
    for _ in range(max_attempts):
        x_A = random.randint(-8, 8)
        y_A = random.randint(-8, 8)
        
        # Ensure dx and dy are even so midpoint coordinates are integers
        dx = random.randint(-5, 5) * 2
        dy = random.randint(-5, 5) * 2
        
        if dx == 0 and dy == 0: # Diameter cannot be zero length
            continue

        x_B = x_A + dx
        y_B = y_A + dy
        
        h = (x_A + x_B) // 2
        k = (y_A + y_B) // 2
        
        r_sq = (dx**2 + dy**2) // 4 # Must be integer if dx, dy are even
        
        if r_sq > 0: # Ensure non-zero radius
            break
    else: # Fallback if no suitable numbers found after max_attempts
        # If it happens, generate a simpler 'center_radius' problem instead.
        return generate_center_radius_problem(level)

    question_text = f"已知 $A({x_A}, {y_A})$ , $B({x_B}, {y_B})$ ，求以 $AB$ 為直徑的圓方程式。"
    correct_equation = generate_equation_string(h, k, r_sq)
    
    return {
        "question_text": question_text,
        "answer": correct_equation,
        "correct_answer": correct_equation
    }

def generate_find_k_in_equation_problem(level):
    # Determine the value of k (the unknown in the equation)
    actual_k_value = random.randint(-5, 5) 

    # Determine the fixed coordinate for the center
    fixed_coord = random.randint(-5, 5)

    # Determine r_sq. Make it an integer square for simplicity, so R is an integer.
    r = random.randint(2, 6)
    r_sq = r**2

    is_h_unknown = random.choice([True, False]) # Is 'k' in (x-k)^2 or (y-k)^2?
    
    if is_h_unknown:
        h_center = actual_k_value
        k_center = fixed_coord
        equation_str_display = f"(x-k)^{{2}} + {format_term('y', k_center)} = {r_sq}"
    else:
        h_center = fixed_coord
        k_center = actual_k_value
        equation_str_display = f"{format_term('x', h_center)} + (y-k)^{{2}} = {r_sq}"

    # Generate a point (x_p, y_p) that lies on the circle
    # Simple points: (h_center+r, k_center), (h_center-r, k_center), (h_center, k_center+r), (h_center, k_center-r)
    point_choice = random.choice([(h_center + r, k_center), (h_center - r, k_center), (h_center, k_center + r), (h_center, k_center - r)])
    x_p, y_p = point_choice

    question_text = f"已知圓 $C:{equation_str_display}$ 通過 $P({x_p}, {y_p})$，求 $k$ 的值。"
    correct_answer = str(actual_k_value)

    return {
        "question_text": question_text,
        "answer": correct_answer, # The numerical value of k
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    Checks if the user's answer is correct.
    For equation answers, it extracts parameters (h, k, r_sq) from both user and correct answers,
    then compares them.
    For numerical answers (find_k_in_equation type), it performs a numerical comparison.
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()

    # Determine if it's an equation comparison or a numerical comparison
    # If correct_answer contains an '=', it's an equation.
    if '=' in correct_answer:
        # Equation comparison logic
        user_params = extract_circle_params(user_answer)
        correct_params = extract_circle_params(correct_answer) # Correct answer is already in canonical form

        is_correct = (user_params == correct_params)
        
        result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
        return {"correct": is_correct, "result": result_text, "next_question": True}

    else:
        # Numerical comparison logic (for 'find_k_in_equation' type)
        is_correct = False
        try:
            # Check if user_answer can be cast to a float and matches the correct_answer
            if float(user_answer) == float(correct_answer):
                is_correct = True
        except ValueError:
            pass # user_answer is not a valid number or correct_answer is not

        result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
        return {"correct": is_correct, "result": result_text, "next_question": True}