import random
import math
from fractions import Fraction
import re

# Helper function to format a Fraction object representing a coefficient of pi into a LaTeX string.
def _format_coeff_to_pi_latex(coeff_fraction):
    """
    Formats a Fraction object representing a coefficient of pi into a LaTeX string for display.
    e.g., Fraction(1,1) -> "\\pi"
          Fraction(4,1) -> "4\\pi"
          Fraction(2,3) -> "\\frac{{2\\pi}}{{3}}"
          Fraction(-1,2) -> "-\\frac{{\\pi}}{{2}}"
    """
    if not isinstance(coeff_fraction, Fraction):
        # Limit denominator to avoid excessively complex fractions from float inputs if any.
        # For this skill, inputs should generally lead to clean fractions.
        coeff_fraction = Fraction(coeff_fraction).limit_denominator(1000)

    if coeff_fraction == 0:
        return "0"
    
    abs_coeff = abs(coeff_fraction)
    sign = "-" if coeff_fraction < 0 else ""
    
    if abs_coeff == 1:
        return fr"{sign}{{\\pi}}"
    elif abs_coeff.denominator == 1:
        return fr"{sign}{abs_coeff.numerator}{{\\pi}}"
    else:
        # Use inner {{}} for LaTeX \\frac arguments, and outer for f-string
        if abs_coeff.numerator == 1: # e.g., pi/3
            return fr"{sign}\\frac{{\\pi}}{{{abs_coeff.denominator}}}"
        else: # e.g., 2pi/3
            return fr"{sign}\\frac{{{abs_coeff.numerator}{{\\pi}}}}{{{abs_coeff.denominator}}}"

# Helper function to parse user input that might involve pi or be a simple number/fraction.
def _parse_user_input_to_float(user_input_string):
    """
    Parses a user input string that might contain 'pi' or be a simple number/fraction.
    Returns its float value.
    """
    s = user_input_string.strip().lower().replace(" ", "")

    # Handle cases like "pi", "-pi"
    if s == 'pi' or s == r'\\pi':
        return math.pi
    if s == '-pi' or s == r'-\\pi':
        return -math.pi

    # Try parsing patterns like "X/Y pi" or "X/Y"
    # This regex is more robust for patterns like "X/Ypi", "X/Y", "pi/Y"
    # It tries to capture a coefficient part, a denominator, and optional 'pi'.
    frac_match_coeff = re.match(r"([+\-]?\s*\d*\.?\d*)\s*/\s*(\d*\.?\d*)\s*(?:pi|\\pi)?", s)
    if frac_match_coeff:
        num_str = frac_match_coeff.group(1).strip()
        den_str = frac_match_coeff.group(2).strip()
        has_pi = frac_match_coeff.group(3) is not None
        
        try:
            numerator = float(num_str) if num_str else 1.0 # If "pi/3", num_str is empty, so it's 1
            denominator = float(den_str)
            if denominator == 0: return None # Avoid division by zero
            
            val = numerator / denominator
            return val * math.pi if has_pi else val
        except ValueError:
            pass # Fall through to other parsing attempts

    # Handle cases like "4pi", "0.5pi", "-2pi"
    match_coeff_pi = re.match(r"([+\-]?\s*\d*\.?\d*)\s*(?:pi|\\pi)", s)
    if match_coeff_pi:
        coeff_str = match_coeff_pi.group(1).strip()
        try:
            if coeff_str == "": return math.pi # Just "pi"
            if coeff_str == "-": return -math.pi # Just "-pi"
            return float(coeff_str) * math.pi
        except ValueError:
            pass # Fall through

    # Handle cases like "pi/X" (e.g. "pi/4")
    match_pi_over_num = re.match(r"(?:pi|\\pi)\s*/\s*(\d*\.?\d*)", s)
    if match_pi_over_num:
        try:
            denominator = float(match_pi_over_num.group(1).strip())
            if denominator != 0:
                return math.pi / denominator
        except ValueError:
            pass # Fall through

    # Finally, try to parse as a simple float (e.g., "10", "3.14")
    try:
        return float(s)
    except ValueError:
        return None # Indicate parsing failure


def generate(level=1):
    problem_type = random.choice([1, 2, 3]) # 1: r, deg -> s, A; 2: r, s -> rad, A; 3: deg, A -> r, s

    if problem_type == 1:
        return _generate_type1_problem(level)
    elif problem_type == 2:
        return _generate_type2_problem(level)
    else: # problem_type == 3
        return _generate_type3_problem(level)

def _generate_type1_problem(level):
    # Given r, θ (degrees), find s and A
    r = random.randint(4, 15)
    
    # For level 1, use common angles that simplify nicely with pi
    if level == 1:
        angle_degrees = random.choice([30, 45, 60, 90, 120, 135, 150, 180, 210, 240, 270, 300, 330])
    else: # Allow a wider range of angles for higher levels
        angle_degrees = random.randint(10, 350) 

    # Convert degrees to radians (as a coefficient of pi, stored as a Fraction)
    angle_radians_coeff = Fraction(angle_degrees, 180).limit_denominator(100)
    
    # Calculate arc length coefficient (s = r*theta)
    s_coeff = r * angle_radians_coeff
    
    # Calculate area coefficient (A = 0.5 * r^2 * theta)
    A_coeff = Fraction(1, 2) * (r**2) * angle_radians_coeff

    question_text = (
        f"已知扇形的半徑為 ${r}$，圓心角為 ${angle_degrees}{{\\degree}}$，"
        f"求扇形的弧長與面積。請依序以$\\pi$表示弧長與面積，並用逗號分隔，例如：$\\text{{4\\pi}}, \\text{{20\\pi}}$。"
    )
    
    correct_s_display = _format_coeff_to_pi_latex(s_coeff)
    correct_A_display = _format_coeff_to_pi_latex(A_coeff)
    
    # Store actual float values for comparison in check function
    correct_s_val = float(s_coeff) * math.pi
    correct_A_val = float(A_coeff) * math.pi
    
    correct_answer_for_check = f"{correct_s_val}, {correct_A_val}"

    return {
        "question_text": question_text,
        "answer": f"{correct_s_display}, {correct_A_display}", # Display answer for user
        "correct_answer": correct_answer_for_check # Actual values for internal check
    }

def _generate_type2_problem(level):
    # Given r, s, find θ (radians) and A
    r = random.randint(4, 15)
    
    # Generate an angle (coefficient of pi)
    theta_num = random.randint(1, 10)
    theta_den = random.choice([2, 3, 4, 5, 6, 8, 9, 10, 12])
    theta_rad_coeff = Fraction(theta_num, theta_den).limit_denominator(100)
    
    # Calculate arc length coefficient (s = r*theta)
    s_coeff = r * theta_rad_coeff
    
    # Calculate area coefficient (A = 0.5 * r * s)
    A_coeff = Fraction(1, 2) * r * s_coeff 

    s_display = _format_coeff_to_pi_latex(s_coeff)
    
    question_text = (
        f"已知扇形的半徑為 ${r}$，弧長為 ${s_display}$，"
        f"求此扇形的圓心角（峳）與其面積。請依序以$\\pi$表示圓心角與面積，並用逗號分隔，例如：$\\text{{\\frac{{\\pi}}{{3}}}}, \\text{{10\\pi}}$。"
    )
    
    correct_theta_display = _format_coeff_to_pi_latex(theta_rad_coeff)
    correct_A_display = _format_coeff_to_pi_latex(A_coeff)
    
    correct_theta_val = float(theta_rad_coeff) * math.pi
    correct_A_val = float(A_coeff) * math.pi

    correct_answer_for_check = f"{correct_theta_val}, {correct_A_val}"

    return {
        "question_text": question_text,
        "answer": f"{correct_theta_display}, {correct_A_display}",
        "correct_answer": correct_answer_for_check
    }

def _generate_type3_problem(level):
    # Given θ (degrees) and A, find r and s
    
    # Generate an angle (coefficient of pi)
    angle_degrees = random.choice([30, 45, 60, 90, 120, 135, 150, 180, 210, 240, 270, 300, 330])
    angle_radians_coeff = Fraction(angle_degrees, 180).limit_denominator(100)
    
    # Generate a radius (integer)
    r_val = random.randint(4, 15)

    # Calculate area coefficient based on r_val and angle (A = 0.5 * r^2 * theta)
    A_coeff = Fraction(1, 2) * (r_val**2) * angle_radians_coeff
    
    # Calculate arc length coefficient (s = r*theta)
    s_coeff = r_val * angle_radians_coeff

    A_display = _format_coeff_to_pi_latex(A_coeff)

    question_text = (
        f"已知扇形的圓心角為 ${angle_degrees}{{\\degree}}$，面積為 ${A_display}$，"
        f"求扇形的半徑與弧長。請依序回答半徑（整數或分數）與弧長（以$\\pi$表示），並用逗號分隔，例如：$\\text{{10}}, \\text{{4\\pi}}$。"
    )

    correct_s_display = _format_coeff_to_pi_latex(s_coeff)
    
    correct_r_val = float(r_val)
    correct_s_val = float(s_coeff) * math.pi
    
    correct_answer_for_check = f"{correct_r_val}, {correct_s_val}"

    return {
        "question_text": question_text,
        "answer": f"{r_val}, {correct_s_display}",
        "correct_answer": correct_answer_for_check
    }


def check(user_answer, correct_answer):
    """
    Checks the user's answer against the correct answer.
    Expects user_answer to be a comma-separated string of numerical values,
    where some values might involve pi (e.g., "4pi", "pi/2").
    The correct_answer stores actual comma-separated float values (e.g., "12.566, 62.831").
    """
    
    user_parts = [p.strip() for p in user_answer.split(',')]
    correct_parts_float_str = [p.strip() for p in correct_answer.split(',')]

    if len(user_parts) != len(correct_parts_float_str):
        return {"correct": False, "result": f"答案格式不正確。請提供 {len(correct_parts_float_str)} 個數值，以逗號分隔。", "next_question": False}

    is_correct_overall = True
    feedback_parts = []
    
    for i in range(len(user_parts)):
        user_val_raw = user_parts[i]
        correct_val_float = float(correct_parts_float_str[i])
        
        parsed_user_val = _parse_user_input_to_float(user_val_raw)

        if parsed_user_val is None:
            is_correct_overall = False
            feedback_parts.append(f"您的答案 '{user_val_raw}' 無法解析為有效數字。請檢查格式，特別是涉及$\\pi$的表達式。")
            continue

        # Compare with a small tolerance for floats
        tolerance = 1e-6
        if abs(parsed_user_val - correct_val_float) > tolerance:
            is_correct_overall = False
            feedback_parts.append(f"您提供的答案 '{user_val_raw}' 不正確。")
            
    if is_correct_overall:
        result_text = f"完全正確！"
    else:
        result_text = f"答案不正確。"
        if feedback_parts:
            result_text += "<br>提示：" + "<br>提示：".join(feedback_parts)
            
    return {"correct": is_correct_overall, "result": result_text, "next_question": True}