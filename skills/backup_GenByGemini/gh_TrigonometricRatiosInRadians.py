import random
import math
from fractions import Fraction

# Helper function to convert LaTeX-like math strings to float values for comparison.
# This function uses a restricted `eval` environment for safety and to interpret common math expressions.
def _convert_latex_to_float(math_str):
    math_str = math_str.strip().replace(' ', '')
    
    if math_str.lower() == "undefined":
        return "undefined" # Special string for undefined values (e.g., tan(90))

    # Replace common LaTeX math constructs with their Python equivalents for evaluation
    s_eval = math_str
    s_eval = s_eval.replace(r'\\pi', 'math.pi')
    s_eval = s_eval.replace(r'\\sqrt{2}', 'math.sqrt(2)')
    s_eval = s_eval.replace(r'\\sqrt{3}', 'math.sqrt(3)')
    
    # Handle fractions: \\frac{num}{den} -> Fraction(num,den)
    # This replacement assumes simple fractions and might need more sophistication for complex nested LaTeX.
    # The double braces {{ }} in the original LaTeX string ensure Python's f-string works correctly.
    # Here, we remove them to prepare for eval.
    s_eval = s_eval.replace(r'\\frac{{', 'Fraction(').replace('}}{{', ',').replace('}}', ')')
    
    # Define a safe environment for eval to limit available functions and modules.
    safe_dict = {
        'math': math,
        'Fraction': Fraction,
        # Allow `sqrt` function in user input if they type e.g., "sqrt(2)"
        'sqrt': math.sqrt 
    }
    
    try:
        # Evaluate the string using the safe dictionary.
        # `__builtins__": None` disables access to Python's built-in functions.
        result = eval(s_eval, {"__builtins__": None}, safe_dict)
        return float(result) # Convert Fraction objects to float for numerical comparison
    except (SyntaxError, NameError, TypeError, ValueError, ZeroDivisionError):
        # If evaluation fails (e.g., malformed expression, unsupported function),
        # return None to indicate that it couldn't be converted to a float.
        return None 

# Helper function to get simplified string representation of a numerical value.
# This ensures consistent LaTeX formatting for correct answers.
def get_simplified_answer_string(value):
    if value is None: # For undefined trigonometric values
        return "Undefined"
    
    # Using a small tolerance for float comparison to handle precision issues.
    tolerance = 1e-9

    # Directly map float values to their common string representations for special angles
    if abs(value - 0) < tolerance: return "0"
    if abs(value - 1) < tolerance: return "1"
    if abs(value - -1) < tolerance: return "-1"
    if abs(value - 0.5) < tolerance: return r"\\frac{{1}}{{2}}"
    if abs(value - -0.5) < tolerance: return r"-\\frac{{1}}{{2}}"
    if abs(value - (math.sqrt(2)/2)) < tolerance: return r"\\frac{{\\sqrt{{2}}}}{{2}}"
    if abs(value - (-math.sqrt(2)/2)) < tolerance: return r"-\\frac{{\\sqrt{{2}}}}{{2}}"
    if abs(value - (math.sqrt(3)/2)) < tolerance: return r"\\frac{{\\sqrt{{3}}}}{{2}}"
    if abs(value - (-math.sqrt(3)/2)) < tolerance: return r"-\\frac{{\\sqrt{{3}}}}{{2}}"
    if abs(value - math.sqrt(3)) < tolerance: return r"\\sqrt{{3}}"
    if abs(value - -math.sqrt(3)) < tolerance: return r"-\\sqrt{{3}}"
    if abs(value - (1/math.sqrt(3))) < tolerance: return r"\\frac{{\\sqrt{{3}}}}{{3}}" # tan(30) = sqrt(3)/3
    if abs(value - (-1/math.sqrt(3))) < tolerance: return r"-\\frac{{\\sqrt{{3}}}}{{3}}" # tan(150) = -sqrt(3)/3
    
    # Check if the value is a multiple of pi and format it as X*pi/Y
    # This is for values like 2*pi/3, pi, etc.
    if abs(value / math.pi - round(value / math.pi)) < tolerance: 
        pi_multiple = Fraction(value / math.pi).limit_denominator(100) # Simplify as fraction of pi
        if pi_multiple.numerator == 0: return "0"
        if pi_multiple.numerator == 1 and pi_multiple.denominator == 1: return r"\\pi"
        if pi_multiple.numerator == -1 and pi_multiple.denominator == 1: return r"-\\pi"
        
        if pi_multiple.denominator == 1:
            return f"{pi_multiple.numerator}" + r"\\pi"
        elif pi_multiple.numerator == 1:
            return r"\\frac{{\\pi}}{{{}}}".format(pi_multiple.denominator)
        elif pi_multiple.numerator == -1:
            return r"-\\frac{{\\pi}}{{{}}}".format(pi_multiple.denominator)
        else:
            return r"\\frac{{{num}\\pi}}{{{den}}}".format(num=pi_multiple.numerator, den=pi_multiple.denominator)

    # Fallback to general fractional representation for other numerical values
    frac_val = Fraction(value).limit_denominator(100)
    if frac_val.denominator == 1:
        return str(int(frac_val))
    return r"\\frac{{{}}}{{{}}}".format(frac_val.numerator, frac_val.denominator)


# Data for special angles: (radian_value, degree_value, sin_value, cos_value, tan_value)
# tan_value is None for undefined cases (e.g., at pi/2, 3pi/2).
SPECIAL_ANGLES_DATA = [
    (0, 0, 0, 1, 0),
    (math.pi/6, 30, 0.5, math.sqrt(3)/2, 1/math.sqrt(3)),
    (math.pi/4, 45, math.sqrt(2)/2, math.sqrt(2)/2, 1),
    (math.pi/3, 60, math.sqrt(3)/2, 0.5, math.sqrt(3)),
    (math.pi/2, 90, 1, 0, None),
    (2*math.pi/3, 120, math.sqrt(3)/2, -0.5, -math.sqrt(3)),
    (3*math.pi/4, 135, math.sqrt(2)/2, -math.sqrt(2)/2, -1),
    (5*math.pi/6, 150, 0.5, -math.sqrt(3)/2, -1/math.sqrt(3)),
    (math.pi, 180, 0, -1, 0),
    (7*math.pi/6, 210, -0.5, -math.sqrt(3)/2, 1/math.sqrt(3)),
    (5*math.pi/4, 225, -math.sqrt(2)/2, -math.sqrt(2)/2, 1),
    (4*math.pi/3, 240, -math.sqrt(3)/2, -0.5, math.sqrt(3)),
    (3*math.pi/2, 270, -1, 0, None),
    (5*math.pi/3, 300, -math.sqrt(3)/2, 0.5, -math.sqrt(3)),
    (7*math.pi/4, 315, -math.sqrt(2)/2, math.sqrt(2)/2, -1),
    (11*math.pi/6, 330, -0.5, math.sqrt(3)/2, -1/math.sqrt(3)),
    # Add common negative angles
    (-math.pi/6, -30, -0.5, math.sqrt(3)/2, -1/math.sqrt(3)),
    (-math.pi/4, -45, -math.sqrt(2)/2, math.sqrt(2)/2, -1),
    (-math.pi/3, -60, -math.sqrt(3)/2, 0.5, -math.sqrt(3)),
    (-math.pi/2, -90, -1, 0, None),
]

# Helper for string representation of radian angles (e.g., pi/4, 2pi/3).
# This function formats the angle in a standardized LaTeX string.
def get_radian_str(angle_rad):
    frac = Fraction(angle_rad / math.pi).limit_denominator(100) # Represent as a fraction of pi

    if frac.numerator == 0: return "0"
    if frac.numerator == 1 and frac.denominator == 1: return r"\\pi"
    if frac.numerator == -1 and frac.denominator == 1: return r"-\\pi"
    
    if frac.denominator == 1:
        return f"{frac.numerator}" + r"\\pi"
    elif frac.numerator == 1:
        return r"\\frac{{\\pi}}{{{}}}".format(frac.denominator)
    elif frac.numerator == -1:
        return r"-\\frac{{\\pi}}{{{}}}".format(frac.denominator)
    else:
        return r"\\frac{{{num}\\pi}}{{{den}}}".format(num=frac.numerator, den=frac.denominator)


def generate_trig_ratio_problem():
    """
    Generates a problem asking for the trigonometric ratio of a special angle in radians.
    Example: 求下列各式的值：($\\sin \\frac{\\pi}{4}$)
    """
    # Select a random special angle from the pre-defined data.
    angle_data = random.choice(SPECIAL_ANGLES_DATA)
    rad_val, _, sin_val, cos_val, tan_val = angle_data
    
    # Choose a trigonometric function (sin, cos, or tan).
    trig_func_choices = ["sin", "cos", "tan"]
    
    # Remove 'tan' if the angle makes tangent undefined.
    if tan_val is None:
        trig_func_choices.remove("tan")
    
    trig_func = random.choice(trig_func_choices)
    
    # Get the correct numerical value based on the chosen function.
    if trig_func == "sin":
        correct_float_val = sin_val
    elif trig_func == "cos":
        correct_float_val = cos_val
    else: # tan
        correct_float_val = tan_val
        
    # Convert the numerical answer and the radian angle to their standardized LaTeX string formats.
    correct_answer_str = get_simplified_answer_string(correct_float_val)
    radian_str = get_radian_str(rad_val)

    question_text = f"求下列各式的值：<br>(${trig_func} {radian_str}$)"
    
    return {
        "question_text": question_text,
        "answer": correct_answer_str, # This field can be used for internal checking or storing the correct value.
        "correct_answer": correct_answer_str # The explicitly correct answer string for display/comparison.
    }

def generate_polygon_application_problem():
    """
    Generates a problem related to regular polygons inscribed in a circle.
    Asks for central angle, arc length, or side length.
    """
    n = random.choice([3, 4, 6]) # Number of sides: equilateral triangle (3), square (4), regular hexagon (6)
    r = random.randint(1, 5) # Radius of the circumcircle
    
    polygon_names = {
        3: r"正三角形",
        4: r"正方形",
        6: r"正六邊形"
    }
    
    polygon_name = polygon_names[n]
    
    problem_type = random.choice(["central_angle_arc_length", "side_length"])
    
    if problem_type == "central_angle_arc_length":
        # Calculate central angle and arc length.
        central_angle_rad = (2 * math.pi) / n
        arc_length = r * central_angle_rad
        
        # Convert values to standardized LaTeX strings.
        central_angle_str = get_radian_str(central_angle_rad)
        arc_length_str = get_simplified_answer_string(arc_length)
        
        question_text = (
            f"已知圓內接{polygon_name}的外接圓半徑為 ${r}$，求：<br>"
            r"(1) 圓心角$\\angle AOB$的弧度。(請以$\\pi$表示)<br>"
            r"(2) 扇形AOB的弧長。(請以$\\pi$表示)"
        )
        # Store correct answer as a tuple string for multiple parts.
        correct_answer = f"({central_angle_str}, {arc_length_str})" 
        
    else: # "side_length"
        # Calculate side length of the regular polygon.
        central_angle_rad = (2 * math.pi) / n
        half_central_angle = central_angle_rad / 2 # Angle AOD in the example solution
        
        # Side length formula: 2 * r * sin(half_central_angle)
        side_length_float = 2 * r * math.sin(half_central_angle)
        side_length_str = get_simplified_answer_string(side_length_float)
        
        question_text = (
            f"已知圓內接{polygon_name}的外接圓半徑為 ${r}$，求其邊長 $\\overline{{AB}}$ 的長度。"
        )
        correct_answer = side_length_str
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def generate(level=1):
    """
    Generates a trigonometric ratios in radians problem.
    The level parameter can be used to control difficulty, though currently not fully implemented.
    """
    problem_type = random.choice(["trig_ratio", "polygon_app"]) # Randomly choose between problem types
    
    if problem_type == "trig_ratio":
        return generate_trig_ratio_problem()
    else:
        return generate_polygon_application_problem()


# Helper function to compare mathematical values robustly.
# It attempts to convert strings to floats for numerical comparison,
# or falls back to strict string comparison for symbolic/LaTeX forms.
def _compare_math_values(user_val_str, correct_val_str, tolerance=1e-6):
    user_float_val = _convert_latex_to_float(user_val_str)
    correct_float_val = _convert_latex_to_float(correct_val_str)

    # Handle 'undefined' case for both user and correct answers.
    if user_float_val == 'undefined' and correct_float_val == 'undefined':
        return True
    
    # If both could be converted to floats, compare them numerically with a tolerance.
    if isinstance(user_float_val, float) and isinstance(correct_float_val, float):
        return abs(user_float_val - correct_float_val) < tolerance
    
    # If numerical comparison isn't possible (e.g., one failed conversion, or types don't match),
    # fall back to strict string comparison after normalizing whitespace and LaTeX braces.
    normalized_user_str = user_val_str.strip().replace(' ', '').replace('{{', '{').replace('}}', '}')
    normalized_correct_str = correct_val_str.strip().replace(' ', '').replace('{{', '{').replace('}}', '}')

    return normalized_user_str == normalized_correct_str


def check(user_answer, correct_answer):
    """
    Checks the user's answer against the correct answer for trigonometric ratio problems.
    Handles both single value answers and tuple-like answers for multi-part questions.
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()

    is_correct = False
    feedback = ""
    tolerance = 1e-6 # Numerical tolerance for float comparisons

    # Check if the correct_answer expects multiple parts (e.g., "(val1, val2)").
    if correct_answer.startswith('(') and correct_answer.endswith(')'):
        try:
            # Attempt to parse user_answer as a tuple of strings.
            # Example: user_answer "(pi/3, 2pi/3)" -> ["pi/3", "2pi/3"]
            user_parts_raw = user_answer[1:-1].split(',')
            user_parts = [p.strip() for p in user_parts_raw]
            
            # Extract correct_parts from the correct_answer string.
            correct_parts_raw = correct_answer[1:-1].split(',')
            correct_parts = [p.strip() for p in correct_parts_raw]
            
            if len(user_parts) == len(correct_parts):
                all_parts_correct = True
                # Compare each part individually.
                for u_part_str, c_part_str in zip(user_parts, correct_parts):
                    if not _compare_math_values(u_part_str, c_part_str, tolerance):
                        all_parts_correct = False
                        break
                is_correct = all_parts_correct
                if is_correct:
                    feedback = f"完全正確！答案是 ${correct_answer}$。"
                else:
                    feedback = f"答案不正確。正確答案應為：${correct_answer}$。"
            else:
                feedback = "答案格式不正確，請以 '(值1, 值2)' 的形式輸入。"
        except Exception: # Catch any parsing errors during splitting or stripping.
            feedback = "答案格式不正確，請檢查輸入。"
    else: # Single value answer type.
        if _compare_math_values(user_answer, correct_answer, tolerance):
            is_correct = True
            feedback = f"完全正確！答案是 ${correct_answer}$。"
        else:
            feedback = f"答案不正確。正確答案應為：${correct_answer}$。"

    return {"correct": is_correct, "result": feedback, "next_question": True}