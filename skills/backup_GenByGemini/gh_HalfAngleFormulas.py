import random
import math
from fractions import Fraction

# --- Helper Functions ---

def _get_quadrant(angle_degrees):
    """Returns the quadrant (1, 2, 3, 4) for a given angle in degrees (0-360).
    Returns 0 if on an axis.
    """
    angle_norm = angle_degrees % 360
    if angle_norm == 0 or angle_norm == 90 or angle_norm == 180 or angle_norm == 270:
        return 0 # On axis
    elif 0 < angle_norm < 90: return 1
    elif 90 < angle_norm < 180: return 2
    elif 180 < angle_norm < 270: return 3
    elif 270 < angle_norm < 360: return 4
    return 0

def _get_sign_for_quadrant(quadrant, trig_func):
    """Determines the sign (+1 or -1) for a trig function in a given quadrant."""
    if quadrant == 0: return 1 # For angles on axes, usually positive or 0/-1. Assume positive for half-angle formula context.
    if trig_func == 'sin':
        return 1 if quadrant in (1, 2) else -1
    elif trig_func == 'cos':
        return 1 if quadrant in (1, 4) else -1
    elif trig_func == 'tan':
        return 1 if quadrant in (1, 3) else -1
    return 1 # Default

def _format_simple_fraction_latex(frac_val):
    """Formats a Fraction object into a LaTeX fraction string."""
    if frac_val.denominator == 1:
        return str(frac_val.numerator)
    return f"\\frac{{{frac_val.numerator}}}{{{frac_val.denominator}}}"

def _calculate_sqrt_fraction_latex(frac_val, sign):
    """
    Calculates the value of +/- sqrt(frac_val) and returns its LaTeX string representation.
    E.g., sqrt(4/5) -> \\frac{2\\sqrt{5}}{5}
    E.g., sqrt(9/4) -> \\frac{3}{2}
    """
    if frac_val < 0:
        raise ValueError("Cannot take square root of a negative number for real values.")
    
    if frac_val == 0:
        return "0"

    numerator_val = frac_val.numerator
    denominator_val = frac_val.denominator

    # We want sqrt(numerator_val / denominator_val)
    # This is equivalent to sqrt(numerator_val * denominator_val) / denominator_val
    
    val_under_sqrt = numerator_val * denominator_val
    final_denominator = denominator_val

    # Simplify sqrt(val_under_sqrt) by extracting perfect squares
    sqrt_coeff = 1
    temp_sqrt_val = val_under_sqrt
    i = 2
    while i * i <= temp_sqrt_val:
        if temp_sqrt_val % (i * i) == 0:
            sqrt_coeff *= i
            temp_sqrt_val //= (i * i)
        else:
            i += 1
            
    # Now we have (sqrt_coeff * sqrt(temp_sqrt_val)) / final_denominator
    
    # Simplify the fraction (sqrt_coeff / final_denominator)
    common_divisor = math.gcd(sqrt_coeff, final_denominator)
    sqrt_coeff //= common_divisor
    final_denominator //= common_divisor

    sign_str = "-" if sign == -1 else ""

    if final_denominator == 1:
        if temp_sqrt_val == 1:
            return f"{sign_str}{sqrt_coeff}"
        else:
            return f"{sign_str}{sqrt_coeff}\\sqrt{{{temp_sqrt_val}}}"
    else: # final_denominator > 1
        if temp_sqrt_val == 1:
            return f"{sign_str}\\frac{{{sqrt_coeff}}}{{{final_denominator}}}"
        else:
            return f"{sign_str}\\frac{{{sqrt_coeff}\\sqrt{{{temp_sqrt_val}}}}}{{{final_denominator}}}"


# --- Problem Generation Functions ---

def generate_specific_angle_problem():
    """Generates problems asking for sin, cos, tan of specific half-angles (e.g., 22.5°, 15°)."""
    target_angle_options = [15, 22.5, 67.5, 75]
    target_angle = random.choice(target_angle_options)

    question_text_base = f"求 $\\sin {target_angle}°$, $\\cos {target_angle}°$ 與 $\\tan {target_angle}°$ 的值。"
    
    # Hardcoded specific answers for these angles due to complex nested radicals.
    # LaTeX strings use double braces for literal braces in f-strings.
    if target_angle == 22.5:
        sin_val = r"\\frac{{\\sqrt{{2-\\sqrt{{2}}}}}}{{2}}"
        cos_val = r"\\frac{{\\sqrt{{2+\\sqrt{{2}}}}}}{{2}}"
        tan_val = r"\\sqrt{{2}}-1"
    elif target_angle == 15:
        sin_val = r"\\frac{{\\sqrt{{2-\\sqrt{{3}}}}}}{{2}}"
        cos_val = r"\\frac{{\\sqrt{{2+\\sqrt{{3}}}}}}{{2}}"
        tan_val = r"2-\\sqrt{{3}}"
    elif target_angle == 75:
        # sin(75) = cos(15), cos(75) = sin(15), tan(75) = 1/tan(15) = 2+sqrt(3)
        sin_val = r"\\frac{{\\sqrt{{2+\\sqrt{{3}}}}}}{{2}}"
        cos_val = r"\\frac{{\\sqrt{{2-\\sqrt{{3}}}}}}{{2}}"
        tan_val = r"2+\\sqrt{{3}}"
    elif target_angle == 67.5:
        # sin(67.5) = cos(22.5), cos(67.5) = sin(22.5), tan(67.5) = 1/tan(22.5) = sqrt(2)+1
        sin_val = r"\\frac{{\\sqrt{{2+\\sqrt{{2}}}}}}{{2}}"
        cos_val = r"\\frac{{\\sqrt{{2-\\sqrt{{2}}}}}}{{2}}"
        tan_val = r"\\sqrt{{2}}+1"
    else: # Fallback (should not happen with defined options)
        sin_val = "Error"
        cos_val = "Error"
        tan_val = "Error"

    correct_answer = (
        f"$\\sin {target_angle}° = {sin_val}$, "
        f"$\\cos {target_angle}° = {cos_val}$, "
        f"$\\tan {target_angle}° = {tan_val}$"
    )
    
    return {
        "question_text": question_text_base,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_given_trig_ratio_problem():
    """
    Generates problems where sin(theta) or cos(theta) and theta's quadrant are given,
    and the user needs to find sin(theta/2), cos(theta/2), tan(theta/2).
    """
    # Choose a Pythagorean triple
    triples = [(3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25)]
    a, b, c = random.choice(triples)
    
    # Randomly assign a/c or b/c to sin/cos magnitude
    if random.random() < 0.5:
        sin_val_abs_num = a
        cos_val_abs_num = b
    else:
        sin_val_abs_num = b
        cos_val_abs_num = a
    denominator = c

    # Randomly choose a quadrant for theta
    # Quadrant ranges for theta:
    # Q1: 0 < theta < 90
    # Q2: 90 < theta < 180
    # Q3: 180 < theta < 270
    # Q4: 270 < theta < 360
    
    quadrant_theta_choices = [1, 2, 3, 4]
    quadrant_theta = random.choice(quadrant_theta_choices)
    
    # Determine signs for sin(theta) and cos(theta) based on quadrant_theta
    sin_theta_sign = _get_sign_for_quadrant(quadrant_theta, 'sin')
    cos_theta_sign = _get_sign_for_quadrant(quadrant_theta, 'cos')

    sin_theta = Fraction(sin_val_abs_num * sin_theta_sign, denominator)
    cos_theta = Fraction(cos_val_abs_num * cos_theta_sign, denominator)
    
    # Determine the range for theta/2 for sign determination
    angle_ranges = {
        1: (0, 90),   # 0 < theta < 90  => 0 < theta/2 < 45 (Q1)
        2: (90, 180), # 90 < theta < 180 => 45 < theta/2 < 90 (Q1)
        3: (180, 270),# 180 < theta < 270 => 90 < theta/2 < 135 (Q2)
        4: (270, 360) # 270 < theta < 360 => 135 < theta/2 < 180 (Q2)
    }
    
    lower_bound, upper_bound = angle_ranges[quadrant_theta]
    
    # Determine quadrant for theta/2
    quadrant_theta_half = 0
    if lower_bound in (0, 90): quadrant_theta_half = 1 # Q1 (0-90)
    elif lower_bound in (180, 270): quadrant_theta_half = 2 # Q2 (90-180)

    sin_half_sign = _get_sign_for_quadrant(quadrant_theta_half, 'sin')
    cos_half_sign = _get_sign_for_quadrant(quadrant_theta_half, 'cos')
    # tan_half_sign is implicitly determined by sin_half_sign / cos_half_sign
    
    # Calculate values for sin(theta/2), cos(theta/2), tan(theta/2)
    
    # sin(theta/2) = +/- sqrt((1 - cos(theta)) / 2)
    val_in_sqrt_sin_half = (Fraction(1) - cos_theta) / 2
    sin_half_latex = _calculate_sqrt_fraction_latex(val_in_sqrt_sin_half, sin_half_sign)

    # cos(theta/2) = +/- sqrt((1 + cos(theta)) / 2)
    val_in_sqrt_cos_half = (Fraction(1) + cos_theta) / 2
    cos_half_latex = _calculate_sqrt_fraction_latex(val_in_sqrt_cos_half, cos_half_sign)
    
    # tan(theta/2) = (1 - cos(theta)) / sin(theta)
    if sin_theta == 0: # Avoid division by zero, though unlikely with chosen triples/quadrants
        tan_half_latex = "undefined"
    else:
        tan_half_val = (Fraction(1) - cos_theta) / sin_theta
        tan_half_latex = _format_simple_fraction_latex(tan_half_val)
    
    # Randomly choose whether to provide sin(theta) or cos(theta) in the question
    if random.random() < 0.5: # Provide sin(theta)
        given_trig_ratio_latex = f"\\sin \\theta = {_format_simple_fraction_latex(sin_theta)}"
    else: # Provide cos(theta)
        given_trig_ratio_latex = f"\\cos \\theta = {_format_simple_fraction_latex(cos_theta)}"

    question_text = (
        f"已知 ${lower_bound}° < \\theta < {upper_bound}°$，且 ${given_trig_ratio_latex}$，"
        f"求 $\\sin(\\theta/2)$, $\\cos(\\theta/2)$ 與 $\\tan(\\theta/2)$ 的值。"
    )

    correct_answer = (
        f"$\\sin(\\theta/2) = {sin_half_latex}$, "
        f"$\\cos(\\theta/2) = {cos_half_latex}$, "
        f"$\\tan(\\theta/2) = {tan_half_latex}$"
    )

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def generate(level=1):
    """
    生成「半角公式」相關題目。
    """
    problem_type = random.choice(['specific_angle', 'given_trig_ratio'])
    
    if problem_type == 'specific_angle':
        return generate_specific_angle_problem()
    elif problem_type == 'given_trig_ratio':
        return generate_given_trig_ratio_problem()

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    Compares canonicalized LaTeX strings to account for minor formatting differences.
    """
    
    def canonicalize_latex_answer(ans_str):
        # Remove any leading/trailing dollar signs
        if ans_str.startswith('$') and ans_str.endswith('$'):
            ans_str = ans_str[1:-1]
        
        # Remove all whitespace to make comparison robust to spacing
        ans_str = ans_str.replace(' ', '') 
        
        # Standardize brace usage for common LaTeX commands
        ans_str = ans_str.replace(r'\\frac{{', r'\\frac{')
        ans_str = ans_str.replace(r'}}{{', r'}{')
        ans_str = ans_str.replace(r'}}', r'}')
        ans_str = ans_str.replace(r'\\sqrt{{', r'\\sqrt{')
        
        # Remove specific LaTeX spacing commands that might be added randomly but are equivalent
        ans_str = ans_str.replace(r'\mkern-2mu', '')

        return ans_str

    user_canonical = canonicalize_latex_answer(user_answer)
    correct_canonical = canonicalize_latex_answer(correct_answer)
    
    is_correct = (user_canonical == correct_canonical)
    
    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}