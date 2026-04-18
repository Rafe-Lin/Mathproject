import random
import math
from fractions import Fraction
import re

# Helper to format numbers for display in LaTeX
def format_number_latex(num):
    """
    Formats a number as a string suitable for LaTeX display.
    Integers are displayed as integers. Non-integers are displayed as fractions
    using \\frac{}{} if possible, otherwise as decimals.
    """
    if isinstance(num, (int, float)):
        if num == int(num):
            return str(int(num))
        else:
            # Try to convert to fraction. Limit denominator to avoid overly complex fractions.
            frac = Fraction(num).limit_denominator(100)
            if frac.denominator == 1:
                return str(frac.numerator)
            return f"\\frac{{{frac.numerator}}}{{{frac.denominator}}}"
    return str(num)

# Helper to format signed terms for the general form equation (x^2 + y^2 + dx + ey + f = 0)
def format_signed_term_equation(coeff, variable):
    """
    Formats a term like dx or ey for display in the general form equation.
    Handles signs and coefficients (e.g., +2x, -y, -5x).
    """
    if coeff == 0:
        return ""
    elif coeff == 1:
        return f" + {variable}"
    elif coeff == -1:
        return f" - {variable}"
    elif coeff > 0:
        return f" + {format_number_latex(coeff)}{variable}"
    else: # coeff < 0
        return f" - {format_number_latex(abs(coeff))}{variable}"

# Helper to format the constant term 'f'
def format_f_term_equation(f_val):
    """
    Formats the constant term 'f' for display in the general form equation.
    Handles signs (e.g., +5, -3).
    """
    if f_val == 0:
        return ""
    elif f_val > 0:
        return f" + {format_number_latex(f_val)}"
    else: # f_val < 0
        return f" - {format_number_latex(abs(f_val))}"


def generate(level=1):
    """
    Generates a problem related to the general form of a circle.
    Problems include finding center/radius, finding k for a given radius,
    determining the graph type, or finding the range of k for a circle.
    """
    problem_type = random.choice([
        'find_center_radius',
        'find_k_given_radius',
        'determine_graph_type',
        'find_k_range_for_circle',
    ])

    if problem_type == 'find_center_radius':
        return generate_find_center_radius_problem(level)
    elif problem_type == 'find_k_given_radius':
        return generate_find_k_given_radius_problem(level)
    elif problem_type == 'determine_graph_type':
        return generate_determine_graph_type_problem(level)
    elif problem_type == 'find_k_range_for_circle':
        return generate_find_k_range_for_circle_problem(level)

def generate_find_center_radius_problem(level):
    """
    Generates a problem to find the center and radius from the general form.
    """
    # Determine coefficient range based on level. Ensure d, e are even for integer h, k.
    coeff_limit = 3 + level // 2
    # Create a list of even numbers within the range, excluding zero
    even_coeffs = [x for x in range(-coeff_limit * 2, coeff_limit * 2 + 1) if x % 2 == 0 and x != 0]
    
    # Ensure even_coeffs is not empty, though with current logic it won't be for level >= 1
    if not even_coeffs:
        even_coeffs = [-2, 2] # Fallback to ensure there are choices

    d = random.choice(even_coeffs)
    e = random.choice(even_coeffs)

    # Calculate center (h, k)
    h_val = -d / 2
    k_val = -e / 2

    # Choose a positive integer radius R (R=0 would be a point, not a circle)
    R = random.randint(1, 5 + level)
    R_squared = R * R

    # Calculate f_val such that R_squared comes out correctly during completing the square
    # R^2 = (d/2)^2 + (e/2)^2 - f => f = (d/2)^2 + (e/2)^2 - R^2
    f_val = (d*d)/4 + (e*e)/4 - R_squared
    f_val = int(f_val) # Ensure f is an integer

    # Format coefficients for display in the question text
    d_str = format_signed_term_equation(d, 'x')
    e_str = format_signed_term_equation(e, 'y')
    f_str = format_f_term_equation(f_val)

    question_text = f"已知圓 $C:x^{{2}} + y^{{2}}{d_str}{e_str}{f_str} = 0$，求圓 $C$ 的圓心與半徑。"
    
    # Canonical form for checking (h,k),R
    correct_h_str = format_number_latex(h_val)
    correct_k_str = format_number_latex(k_val)
    correct_r_str = format_number_latex(R)
    correct_answer_canonical = f"({correct_h_str},{correct_k_str}),{correct_r_str}"
    
    # Human-readable form for feedback display
    display_answer = f"圓心為 $({correct_h_str},{correct_k_str})$，半徑為 ${correct_r_str}$"

    return {
        "question_text": question_text,
        "answer": display_answer, # This is the full display answer.
        "correct_answer": correct_answer_canonical # This is the canonical form for check.
    }

def generate_find_k_given_radius_problem(level):
    """
    Generates a problem to find the value of k given the radius.
    """
    coeff_limit = 3 + level // 2
    even_coeffs = [x for x in range(-coeff_limit * 2, coeff_limit * 2 + 1) if x % 2 == 0 and x != 0]
    if not even_coeffs: even_coeffs = [-2, 2]

    d = random.choice(even_coeffs)
    e = random.choice(even_coeffs)

    R = random.randint(1, 5 + level)
    R_squared_target = R * R

    # Calculate k_val (which is the constant term 'f')
    # R^2 = (d/2)^2 + (e/2)^2 - k => k = (d/2)^2 + (e/2)^2 - R^2
    k_val = (d*d)/4 + (e*e)/4 - R_squared_target
    k_val = int(k_val) # Ensure k is an integer

    d_str = format_signed_term_equation(d, 'x')
    e_str = format_signed_term_equation(e, 'y')
    
    question_text = f"已知圓 $C:x^{{2}} + y^{{2}}{d_str}{e_str} + k = 0$ 的半徑為 ${R}$，求 $k$ 的值。"
    
    correct_answer_canonical = format_number_latex(k_val) # Canonical form for k value
    display_answer = f"$k = {correct_answer_canonical}$"

    return {
        "question_text": question_text,
        "answer": display_answer,
        "correct_answer": correct_answer_canonical
    }

def generate_determine_graph_type_problem(level):
    """
    Generates a problem to determine if the equation represents a circle, a point, or no graph.
    """
    coeff_limit = 3 + level // 2
    even_coeffs = [x for x in range(-coeff_limit * 2, coeff_limit * 2 + 1) if x % 2 == 0 and x != 0]
    if not even_coeffs: even_coeffs = [-2, 2]

    d = random.choice(even_coeffs)
    e = random.choice(even_coeffs)

    # Randomly choose the graph type
    graph_type = random.choice(['circle', 'point', 'no_graph'])

    if graph_type == 'circle':
        R_squared_val = random.randint(1, 10 + level) # R^2 > 0
        correct_graph_type = "圓"
    elif graph_type == 'point':
        R_squared_val = 0 # R^2 = 0
        correct_graph_type = "點"
    else: # no_graph
        R_squared_val = random.randint(-10, -1) # R^2 < 0
        correct_graph_type = "無圖形"

    # Calculate f_val
    # R^2 = (d/2)^2 + (e/2)^2 - f => f = (d/2)^2 + (e/2)^2 - R^2
    f_val = (d*d)/4 + (e*e)/4 - R_squared_val
    f_val = int(f_val)

    d_str = format_signed_term_equation(d, 'x')
    e_str = format_signed_term_equation(e, 'y')
    f_str = format_f_term_equation(f_val)

    question_text = f"試判斷方程式 $x^{{2}} + y^{{2}}{d_str}{e_str}{f_str} = 0$ 所代表的圖形：(請填寫 '圓', '點' 或 '無圖形')"
    
    correct_answer_canonical = correct_graph_type
    display_answer = correct_graph_type

    return {
        "question_text": question_text,
        "answer": display_answer,
        "correct_answer": correct_answer_canonical
    }

def generate_find_k_range_for_circle_problem(level):
    """
    Generates a problem to find the range of k for the equation to represent a circle.
    """
    coeff_limit = 3 + level // 2
    even_coeffs = [x for x in range(-coeff_limit * 2, coeff_limit * 2 + 1) if x % 2 == 0 and x != 0]
    if not even_coeffs: even_coeffs = [-2, 2]

    d = random.choice(even_coeffs)
    e = random.choice(even_coeffs)

    # For a circle, R^2 must be > 0.
    # R^2 = (d/2)^2 + (e/2)^2 - k > 0
    # k < (d/2)^2 + (e/2)^2
    k_boundary = (d*d)/4 + (e*e)/4
    k_boundary = int(k_boundary)

    d_str = format_signed_term_equation(d, 'x')
    e_str = format_signed_term_equation(e, 'y')

    question_text = f"已知 $x^{{2}} + y^{{2}}{d_str}{e_str} + k = 0$ 的圖形為一圓，求 $k$ 的範圍。"
    
    correct_answer_canonical = f"k<{k_boundary}"
    display_answer = f"$k < {format_number_latex(k_boundary)}$"

    return {
        "question_text": question_text,
        "answer": display_answer,
        "correct_answer": correct_answer_canonical
    }

def check(user_answer, correct_answer):
    """
    Checks the user's answer against the correct answer.
    Handles various input formats for center, radius, k value, and graph type.
    """
    # Normalize user and correct answers for robust comparison
    user_answer_norm = user_answer.strip().lower()
    correct_answer_norm = correct_answer.strip().lower()

    is_correct = False
    feedback_display = correct_answer # Use the display_answer from generate for feedback

    # Regex pattern to parse numbers, including potential LaTeX fractions (e.g., \\frac{3}{2})
    # This pattern supports integers, decimals, and LaTeX fractions.
    # It must be able to convert these into a float for comparison.
    num_parse_pattern = r'([-+]?\d+(?:(?:\.\d+)?|\\frac{\d+}{\d+}?))'
    
    def parse_numeric_string(s):
        """Converts a string (integer, float, or LaTeX fraction) to a float."""
        s = s.strip()
        if '\\frac{' in s:
            # Replace LaTeX frac syntax with a format Fraction can understand, then convert to float.
            s = s.replace('\\frac{', '(').replace('}{', '/').replace('}', ')')
            return float(Fraction(s))
        else:
            return float(s)

    # Case 1: Center and Radius (canonical format: (h,k),R)
    # Example: "(-1,2),5" or "(\\frac{1}{2},-3),4"
    if re.match(rf'\({num_parse_pattern},{num_parse_pattern}\),{num_parse_pattern}', correct_answer_norm):
        match_correct = re.match(rf'\({num_parse_pattern},{num_parse_pattern}\),{num_parse_pattern}', correct_answer_norm)
        if match_correct:
            ch_str, ck_str, cr_str = match_correct.groups()
            correct_h = parse_numeric_string(ch_str)
            correct_k = parse_numeric_string(ck_str)
            correct_r = parse_numeric_string(cr_str)
            
            # Define common user input formats
            user_formats = [
                r'\(([-+]?\d+\.?\d*),([-+]?\d+\.?\d*)\),([-+]?\d+\.?\d*)', # (h,k),R
                r'([-+]?\d+\.?\d*),([-+]?\d+\.?\d*),([-+]?\d+\.?\d*)', # h,k,R
                r'圓心\(([-+]?\d+\.?\d*),([-+]?\d+\.?\d*)\)半徑([-+]?\d+\.?\d*)', # 圓心(h,k)半徑R (Chinese)
                r'center\(([-+]?\d+\.?\d*),([-+]?\d+\.?\d*)\)radius([-+]?\d+\.?\d*)', # center(h,k)radiusR (English)
            ]

            user_input_cleaned = user_answer_norm.replace(' ', '').replace('，', ',')
            for fmt in user_formats:
                match_user = re.search(fmt, user_input_cleaned)
                if match_user and len(match_user.groups()) == 3:
                    try:
                        user_h = float(match_user.group(1))
                        user_k = float(match_user.group(2))
                        user_r = float(match_user.group(3))
                        # Compare floats with a small tolerance
                        if abs(user_h - correct_h) < 1e-6 and \
                           abs(user_k - correct_k) < 1e-6 and \
                           abs(user_r - correct_r) < 1e-6:
                            is_correct = True
                            break
                    except ValueError:
                        continue # Try next format if parsing fails

    # Case 2: k value (canonical format: "number")
    # Example: "5" or "\\frac{3}{2}"
    elif re.match(rf'{num_parse_pattern}$', correct_answer_norm):
        correct_k = parse_numeric_string(correct_answer_norm)
        
        # User answer can be just the number, or "k=number"
        user_val_str = user_answer_norm.replace('k=', '').replace(' ', '')
        try:
            user_k = parse_numeric_string(user_val_str)
            if abs(user_k - correct_k) < 1e-6:
                is_correct = True
        except ValueError:
            pass

    # Case 3: Graph type (canonical format: "圓", "點", "無圖形")
    elif correct_answer_norm in ["圓", "點", "無圖形"]:
        # Standardize common alternative user inputs
        user_input_type = user_answer_norm.replace(' ', '')
        if user_input_type == "圓" or user_input_type == "yuan":
            user_input_type = "圓"
        elif user_input_type == "點" or user_input_type == "dian":
            user_input_type = "點"
        elif user_input_type in ["無圖形", "wu tuxing", "沒有圖形", "no graph"]:
            user_input_type = "無圖形"
        
        if user_input_type == correct_answer_norm:
            is_correct = True

    # Case 4: k range (canonical format: k<k_boundary)
    # Example: "k<5" or "k<\\frac{3}{2}"
    elif re.match(rf'k(<|<=|>|>=|=){num_parse_pattern}', correct_answer_norm):
        correct_op_match = re.match(r'k(<?=?|>?=?|=)', correct_answer_norm)
        correct_operator = correct_op_match.group(1) if correct_op_match else ''
        correct_bound_str = correct_answer_norm.replace(f'k{correct_operator}', '')
        correct_bound = parse_numeric_string(correct_bound_str)

        # User answer can be "k<number", "number>k" etc.
        user_input_cleaned = user_answer_norm.replace(' ', '')
        match_user_k_first = re.match(r'k(<|<=|>|>=|=)\s*([-+]?\d+\.?\d*)', user_input_cleaned)
        match_user_num_first = re.match(r'([-+]?\d+\.?\d*)\s*(<|<=|>|>=|=)k', user_input_cleaned)

        user_operator = None
        user_bound = None

        if match_user_k_first:
            user_operator = match_user_k_first.group(1)
            user_bound = float(match_user_k_first.group(2))
        elif match_user_num_first: # e.g., "5>k"
            user_bound = float(match_user_num_first.group(1))
            op_reversed = match_user_num_first.group(2)
            # Invert the operator if number is first
            if op_reversed == '>': user_operator = '<'
            elif op_reversed == '>=': user_operator = '<='
            elif op_reversed == '<': user_operator = '>'
            elif op_reversed == '<=': user_operator = '>='
            elif op_reversed == '=': user_operator = '='

        if user_operator and user_bound is not None:
            if user_operator == correct_operator and abs(user_bound - correct_bound) < 1e-6:
                is_correct = True
                
    result_text = f"完全正確！答案是 ${feedback_display}$。" if is_correct else f"答案不正確。正確答案應為：${feedback_display}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}