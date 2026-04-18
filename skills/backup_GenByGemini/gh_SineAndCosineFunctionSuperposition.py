import random
import math
import re
from fractions import Fraction # Included for general math utility, though not directly used for output

# Helper function to convert a numerical value (possibly involving sqrt) to its LaTeX string representation.
# Examples: 1 -> "1", math.sqrt(2) -> r"\\sqrt{{2}}", 2*math.sqrt(3) -> r"2\\sqrt{{3}}"
def _num_to_latex_str(num_val):
    if math.isclose(num_val, 0):
        return "0"

    sign = "-" if num_val < 0 else ""
    abs_num_val = abs(num_val)

    # Check for integer values
    if math.isclose(abs_num_val, round(abs_num_val)):
        return f"{sign}{int(round(abs_num_val))}"

    # Check for C * sqrt(N) forms
    # Try to represent as C * sqrt(N) where N is small (2, 3)
    abs_num_squared = abs_num_val * abs_num_val # Should be close to an integer

    for N in [2, 3, 5]: # Test for common sqrt forms (e.g., sqrt(2), sqrt(3), sqrt(5))
        if math.isclose(abs_num_squared % N, 0):
            coeff_squared = abs_num_squared / N
            coeff = math.sqrt(coeff_squared)
            if math.isclose(coeff, round(coeff)):
                int_coeff = int(round(coeff))
                if int_coeff == 1: # sqrt(N) form
                    return f"{sign}{r'\\sqrt{{'}{N}{r'}}'}"
                else: # C*sqrt(N) form
                    return f"{sign}{int_coeff}{r'\\sqrt{{'}{N}{r'}}'}"
    
    # Fallback for other sqrt(N) forms (e.g., sqrt(7)) or if N is large.
    # The num_val itself is already a sqrt of some integer (e.g. sqrt(5))
    if math.isclose(abs_num_val, math.sqrt(round(abs_num_squared))):
        return f"{sign}{r'\\sqrt{{'}{int(round(abs_num_squared))}{r'}}'}"

    # Fallback for general floats - for this skill, we expect "nice" numbers.
    return f"{num_val:.4g}"


# Helper function to convert angle in radians to LaTeX string (e.g., pi/6)
def _rad_to_frac_pi_latex(angle_rad):
    if math.isclose(angle_rad, 0):
        return "0"

    sign = "-" if angle_rad < 0 else ""
    abs_angle_rad = abs(angle_rad)

    pi = math.pi
    # Try to find common fractions of pi
    # Multiplier is the number of 'units' of pi/X, e.g., pi/6 is 1 unit of pi/6, pi/3 is 2 units of pi/6
    for denominator in [6, 4, 3, 2, 1]: # Test common denominators first
        unit_angle = pi / denominator
        if math.isclose(abs_angle_rad % unit_angle, 0):
            numerator = round(abs_angle_rad / unit_angle)
            if numerator == 0: # Should be caught by angle_rad == 0
                continue
            
            if denominator == 1 and numerator == 1: # For pi
                return f"{sign}{r'\\pi'}"
            elif numerator == 1: # For pi/D
                return f"{sign}{r'\\frac{{\\pi}}{{{denominator}}}'}"
            elif denominator == 1: # For N*pi
                 return f"{sign}{numerator}{r'\\pi'}"
            else: # For N*pi/D
                return f"{sign}{r'\\frac{{{numerator}\\pi}}{{{denominator}}}'}"
    
    # Fallback if not a recognized fraction of pi
    return f"{sign}{abs_angle_rad:.4g}" # As a float if not a nice fraction


# Helper to parse LaTeX coefficient string to numerical value
# Handles "C", "\\sqrt{N}", "C\\sqrt{N}", and their negative counterparts.
def _parse_latex_coeff_to_num(latex_coeff_str):
    latex_coeff_str = latex_coeff_str.strip()
    if not latex_coeff_str: # Represents 1 (e.g., for sin x, cos x without explicit 1)
        return 1.0

    # Pattern for C*sqrt(N) or C or sqrt(N)
    # Group 1: sign (-?)
    # Group 2: integer coefficient (\d*)?
    # Group 3: \\sqrt{N} part (?:\\sqrt{{(\d+)}})?
    match = re.match(r"^(-?)(\d*)?(?:\\sqrt{{(\d+)}})?$", latex_coeff_str)
    if not match:
        # If it's just a raw number like "1", "2" that didn't fit the sqrt pattern
        try:
            return float(latex_coeff_str)
        except ValueError:
            return float('nan') # Indicate parsing error

    sign = -1.0 if match.group(1) == "-" else 1.0
    coeff_str = match.group(2)
    sqrt_n_str = match.group(3)

    num_val = 1.0 # Default if only sqrt part or no explicit coefficient (e.g., "\\sqrt{2}")
    if coeff_str: # If there's an explicit integer coefficient (e.g., "2" in "2\\sqrt{3}" or "2")
        num_val = float(coeff_str)
    
    if sqrt_n_str: # If there's a sqrt part
        num_val *= math.sqrt(float(sqrt_n_str))
    
    return sign * num_val


# Helper to parse LaTeX angle string (e.g., "\\frac{\\pi}{6}") to numerical radians
# `op_sign` is "+" or "-" from the main regex to apply the overall sign to the angle.
def _parse_latex_angle_to_rad(latex_angle_str, op_sign):
    latex_angle_str = latex_angle_str.strip()
    if latex_angle_str == "0":
        return 0.0

    # Remove any leading '-' from the string itself, as the `op_sign` parameter will handle the total sign.
    latex_angle_str = latex_angle_str.lstrip('-')

    angle_val = 0.0
    pi = math.pi

    # Case 1: \\frac{N\\pi}{D} or \\frac{\\pi}{D}
    frac_match = re.match(r"^\\frac{{(\d*)\\pi}}{{(\d+)}}$", latex_angle_str)
    if frac_match:
        num_str = frac_match.group(1)
        den_str = frac_match.group(2)
        numerator = float(num_str) if num_str else 1.0 # Handle case where it's just \\pi/D (num_str is empty)
        denominator = float(den_str)
        if denominator == 0: return float('nan') # Avoid division by zero
        angle_val = (numerator * pi) / denominator
    # Case 2: N\\pi or \\pi
    else:
        pi_match = re.match(r"^(?:(\d*)\\pi)$", latex_angle_str)
        if pi_match:
            num_str = pi_match.group(1)
            numerator = float(num_str) if num_str else 1.0 # Handle case where it's just \\pi (num_str is empty)
            angle_val = numerator * pi
        else:
            return float('nan') # Parsing failed

    return angle_val * (1.0 if op_sign == "+" else -1.0)


def generate(level=1):
    # Coefficients for sin(x) and cos(x)
    # To match example style (y = r sin(x +- theta) where theta is acute),
    # 'a' (coefficient of sin(x)) is kept positive to ensure cos(theta) = a/r is positive,
    # leading to an acute positive angle theta when considering theta_abs.
    
    # Define base values for a and b coefficients
    # These are the "naked" values, before any overall scaling or sign application.
    COEF_BASE_VALS = [
        1.0,
        math.sqrt(2),
        math.sqrt(3),
    ]

    # Choose a base for 'a' (coefficient of sin(x)). It is always positive.
    a_base_val = random.choice(COEF_BASE_VALS)
    a_val = a_base_val

    # Choose a base for 'b' (coefficient of cos(x)).
    b_base_val = random.choice(COEF_BASE_VALS + [0.0]) # Include 0 for cases like y = a sin x
    
    # Add a sign for 'b' (if b_base_val is not 0)
    b_sign_multiplier = random.choice([1, -1]) if not math.isclose(b_base_val, 0) else 1
    b_val = b_base_val * b_sign_multiplier

    # Add an overall scaling factor for complexity (level 2+)
    overall_scale = 1
    if level >= 2:
        # For higher levels, use integer multipliers or make problems a bit more complex.
        # Ensure scaling_factor doesn't introduce non-standard angles if possible.
        overall_scale = random.choice([2, 3]) 
    
    # Apply scaling
    a_val_scaled = a_val * overall_scale
    b_val_scaled = b_val * overall_scale

    # --- Construct question_text ---
    # Convert scaled 'a' coefficient to LaTeX string
    a_str_val = _num_to_latex_str(a_val_scaled)
    
    # Convert scaled 'b' coefficient to LaTeX string, handling its sign and "1" for cleaner display
    b_str_abs_val = ""
    if math.isclose(abs(b_val_scaled), 1):
        b_str_abs_val = "" # Omit "1" for "cos x"
    else:
        b_str_abs_val = _num_to_latex_str(abs(b_val_scaled))
    
    b_term_str = ""
    if b_val_scaled > 0:
        b_term_str = f"+ {b_str_abs_val}{r'\\cos x'}"
    elif b_val_scaled < 0:
        b_term_str = f"- {b_str_abs_val}{r'\\cos x'}"
    
    # Build the initial function string for y = A sin(x) + B cos(x)
    question_func = ""
    if math.isclose(a_val_scaled, 1):
        question_func = r"\\sin x"
    else:
        question_func = f"{a_str_val}{r'\\sin x'}"
    
    # Add the cosine term if b_val_scaled is not zero
    if not math.isclose(b_val_scaled, 0):
        question_func += f" {b_term_str}"
    
    question_func = question_func.strip() # Remove any trailing space if b_term_str was empty.

    question_text = f"題目: 將 $y = {question_func}$ 表成正弦函數的形式。"

    # --- Calculate correct_answer ---
    r_val = math.sqrt(a_val_scaled**2 + b_val_scaled**2)
    # atan2(y, x) is used to get the angle in the correct quadrant, where y = b and x = a
    theta_rad = math.atan2(b_val_scaled, a_val_scaled) 

    # Convert r_val to LaTeX string (e.g., "2", r"\\sqrt{{2}}")
    r_str_answer_val = _num_to_latex_str(r_val) 

    # Convert absolute theta to LaTeX string (e.g., r"\\frac{{\\pi}}{{6}}")
    theta_str_answer = _rad_to_frac_pi_latex(abs(theta_rad))
    
    # Determine the operation sign based on the sign of theta_rad
    op_sign = "+" if theta_rad >= 0 else "-"

    # Construct the final correct answer string
    correct_answer = ""
    if math.isclose(theta_rad, 0): # Case: y = r sin x
        if math.isclose(r_val, 1):
            correct_answer = f"$y = {r'\\sin x'}$" # e.g. y = sin x
        else:
            correct_answer = f"$y = {r_str_answer_val}{r'\\sin x'}$" # e.g. y = 2sin x
    else: # Case: y = r sin(x +- theta)
        if math.isclose(r_val, 1):
            correct_answer = f"$y = {r'\\sin(x'}{op_sign}{theta_str_answer}{r')'}$" # e.g. y = sin(x+pi/4)
        else:
            correct_answer = f"$y = {r_str_answer_val}{r'\\sin(x'}{op_sign}{theta_str_answer}{r')'}$" # e.g. y = 2sin(x+pi/6)
    
    return {
        "question_text": question_text,
        "answer": correct_answer, # Store the answer in LaTeX for display/checking
        "correct_answer": correct_answer # For internal consistency
    }


def check(user_answer, correct_answer):
    """
    檢查使用者答案是否正確。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()

    # Regex to extract components from "$y = R \\sin(x \\pm \Theta)$"
    # Group 1: R, Group 2: sign (+ or -), Group 3: Theta
    # Also handle "$y = R \\sin x$" (when Theta is 0)
    pattern_with_angle = r"^\$y = (.+?)\\sin\\(x ([+\-]) (.+?)\\)\$$"
    pattern_without_angle = r"^\$y = (.+?)\\sin x\$$"

    # Try to match the correct answer first
    match_correct_with_angle = re.match(pattern_with_angle, correct_answer)
    match_correct_without_angle = re.match(pattern_without_angle, correct_answer)

    # Extract components from correct_answer
    r_c_str = ""
    theta_c_str = "0"
    op_c = "+"
    if match_correct_with_angle:
        r_c_str = match_correct_with_angle.group(1).strip()
        op_c = match_correct_with_angle.group(2)
        theta_c_str = match_correct_with_angle.group(3).strip()
    elif match_correct_without_angle:
        r_c_str = match_correct_without_angle.group(1).strip()
        # theta_c_str remains "0", op_c remains "+"
    else:
        # Fallback if correct_answer format itself is unexpectedly wrong (shouldn't happen with generate)
        return {"correct": False, "result": "Internal error: Correct answer format invalid.", "next_question": False}

    # Extract components from user_answer
    match_user_with_angle = re.match(pattern_with_angle, user_answer)
    match_user_without_angle = re.match(pattern_without_angle, user_answer)

    r_u_str = ""
    theta_u_str = "0"
    op_u = "+"

    if match_user_with_angle:
        r_u_str = match_user_with_angle.group(1).strip()
        op_u = match_user_with_angle.group(2)
        theta_u_str = match_user_with_angle.group(3).strip()
    elif match_user_without_angle:
        r_u_str = match_user_without_angle.group(1).strip()
        # theta_u_str remains "0", op_u remains "+"
    else:
        # User answer format is incorrect
        return {"correct": False, "result": "答案格式不正確。請確保使用 $y = R \\sin(x \\pm \\theta)$ 或 $y = R \\sin x$ 的形式。", "next_question": False}

    # Handle case where R is omitted for 1
    if not r_u_str and (match_user_with_angle or match_user_without_angle): # If $y = \\sin(x...)$ or $y = \\sin x$
        r_u_str = "1"
    if not r_c_str and (match_correct_with_angle or match_correct_without_angle):
        r_c_str = "1"

    # Convert to numerical values for comparison
    r_c = _parse_latex_coeff_to_num(r_c_str)
    r_u = _parse_latex_coeff_to_num(r_u_str)

    theta_c_rad = _parse_latex_angle_to_rad(theta_c_str, op_c)
    theta_u_rad = _parse_latex_angle_to_rad(theta_u_str, op_u)
    
    # Check for NaN from parsing errors
    if any(math.isnan(val) for val in [r_c, r_u, theta_c_rad, theta_u_rad]):
        return {"correct": False, "result": "無法解析您的答案中的數字或角度，請檢查輸入格式。", "next_question": False}

    # Compare values
    is_r_correct = math.isclose(r_u, r_c, rel_tol=1e-9, abs_tol=1e-9)
    # For angles, compare them modulo 2*pi. Since generate only produces acute angles or 0,
    # direct comparison is often sufficient, but modulo comparison is more robust.
    # Normalize to a common range, e.g., [0, 2pi)
    norm_theta_c = theta_c_rad % (2 * math.pi)
    norm_theta_u = theta_u_rad % (2 * math.pi)
    is_theta_correct = math.isclose(norm_theta_u, norm_theta_c, rel_tol=1e-9, abs_tol=1e-9)

    is_correct = is_r_correct and is_theta_correct

    result_text = ""
    if is_correct:
        result_text = f"完全正確！答案是 ${correct_answer}$。"
    else:
        feedback_parts = []
        if not is_r_correct:
            feedback_parts.append(f"振幅 $R$ 不正確。應為 ${r_c_str}$。")
        if not is_theta_correct:
            feedback_parts.append(f"相位角 $\\theta$ 不正確。應為 ${op_c}{theta_c_str}$。")
        
        if not feedback_parts: # This case should ideally not be reached if is_correct is False
             result_text = "答案不正確。"
        else:
             result_text = "答案不正確。" + " ".join(feedback_parts) + f" 正確答案應為：${correct_answer}$"
    
    return {"correct": is_correct, "result": result_text, "next_question": True}