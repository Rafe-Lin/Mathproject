import random
from fractions import Fraction
import math
import re

# Helper function to find the greatest common divisor of multiple integers,
# handling zero values appropriately.
def calculate_gcd(*args):
    non_zero_args = [abs(arg) for arg in args if arg != 0]
    if not non_zero_args:
        return 1 # Or any convention for all zeros, 1 is safe for division
    
    result_gcd = non_zero_args[0]
    for i in range(1, len(non_zero_args)):
        result_gcd = math.gcd(result_gcd, non_zero_args[i])
    return result_gcd

# Helper function to normalize the equation Ax + By + C = 0
def normalize_equation(a, b, c):
    # Ensure all coefficients are integers
    # (Assuming a, b, c are already integers from generate functions or after Fraction conversion)

    # Handle edge case where it's not a valid line equation (e.g., 0x + 0y + 5 = 0)
    if a == 0 and b == 0:
        return 0, 0, c # Not a line, but keep C for consistency in check if C=0

    # Find the greatest common divisor of the absolute values of A, B, C
    common_divisor = calculate_gcd(a, b, c)
    
    a = a // common_divisor
    b = b // common_divisor
    c = c // common_divisor

    # Ensure leading coefficient is positive based on convention:
    # If A is non-zero, make A positive.
    # If A is zero (horizontal line), make B positive.
    if a < 0:
        a, b, c = -a, -b, -c
    elif a == 0 and b < 0: # Only if A is 0, check B
        a, b, c = -a, -b, -c
    
    return a, b, c

# Helper function to parse a string equation into (A, B, C) for Ax + By + C = 0
def parse_equation_to_abc(equation_str):
    equation_str = equation_str.strip().replace(" ", "").lower()
    
    # Handle forms like x=k or y=k
    match_x_k = re.match(r"x=(-?\d+)$", equation_str)
    if match_x_k:
        k = int(match_x_k.group(1))
        return 1, 0, -k
    
    match_y_k = re.match(r"y=(-?\d+)$", equation_str)
    if match_y_k:
        k = int(match_y_k.group(1))
        return 0, 1, -k

    # Process generic Ax+By+C=0 or y=mx+b forms
    a_val, b_val, c_val = Fraction(0), Fraction(0), Fraction(0)
    
    # Move all terms to the left side if an equals sign is present
    if '=' in equation_str:
        left_side, right_side = equation_str.split('=', 1)
        # Convert 'right_side' to negative terms for moving to left
        processed_right = []
        # Find all number/variable parts
        terms_on_right = re.findall(r"([+\-]?)([^+\-]+)", right_side)
        for sign, term in terms_on_right:
            if sign == '-': processed_right.append(f"+{term}")
            else: processed_right.append(f"-{term}")
        equation_str = left_side + "".join(processed_right)
    
    # Parse the (now single-sided) expression
    # Regex to capture sign, coefficient, and variable (or just constant)
    # e.g., '+3x', '-2y', '+5', 'x', '-y'
    terms = re.findall(r"([+\-]?)(\d*(\.\d+)?(?:/\d+)?)([xy]?)", equation_str)
    
    for sign, coeff_str_raw, _, var in terms:
        if not coeff_str_raw and var: # Handles 'x' or 'y' (coefficient is 1)
            coeff = Fraction(1)
        elif not coeff_str_raw and not var: # Empty string, skip
            continue
        else:
            coeff = Fraction(coeff_str_raw)
        
        if sign == '-':
            coeff *= -1
        
        if var == 'x':
            a_val += coeff
        elif var == 'y':
            b_val += coeff
        elif not var: # It's a constant term
            c_val += coeff
            
    # Convert fractions to integers by finding LCM of denominators
    lcm_den = 1
    if isinstance(a_val, Fraction): lcm_den = math.lcm(lcm_den, a_val.denominator)
    if isinstance(b_val, Fraction): lcm_den = math.lcm(lcm_den, b_val.denominator)
    if isinstance(c_val, Fraction): lcm_den = math.lcm(lcm_den, c_val.denominator)

    return int(a_val * lcm_den), int(b_val * lcm_den), int(c_val * lcm_den)

def generate(level=1):
    """
    生成「直線方程式」相關題目。
    """
    problem_choice = random.choice([
        'point_slope',
        'two_points',
        'slope_y_intercept',
        'two_intercepts',
        'vertical_horizontal',
        'find_slope'
    ])
    
    question_text = ""
    correct_a, correct_b, correct_c = 0, 0, 0
    correct_slope_str = None # For 'find_slope' type

    # Adjust ranges based on level for complexity
    coord_range = (-10, 10)
    slope_num_range = (-5, 5)
    slope_den_range = (1, 5) # Denominator always positive
    intercept_range = (-8, 8)

    if level >= 2:
        coord_range = (-15, 15)
        slope_num_range = (-7, 7)
        slope_den_range = (1, 7)
        intercept_range = (-10, 10)
    
    if problem_choice == 'point_slope':
        x1 = random.randint(*coord_range)
        y1 = random.randint(*coord_range)
        
        # Generate slope: integer or fraction
        slope_type = random.choice(['integer', 'fraction'])
        if slope_type == 'integer':
            m_num = random.randint(*slope_num_range)
            # Avoid m=0 too frequently unless it's a specific simple problem
            if m_num == 0 and level > 1: m_num = random.choice([-2, -1, 1, 2])
            m_frac = Fraction(m_num)
            slope_latex = str(m_num)
        else: # Fraction
            m_num = random.randint(*slope_num_range)
            m_den = random.randint(*slope_den_range)
            while m_num == 0: # Ensure non-zero slope for a general fraction problem
                 m_num = random.randint(*slope_num_range)
            m_frac = Fraction(m_num, m_den)
            slope_latex = f"\\frac{{{m_frac.numerator}}}{{{m_frac.denominator}}}"

        # Equation: y - y1 = m(x - x1)
        # If m = p/q, then q(y - y1) = p(x - x1) => px - qy + (qy1 - px1) = 0
        a = m_frac.numerator
        b = -m_frac.denominator
        c = m_frac.denominator * y1 - m_frac.numerator * x1
        
        correct_a, correct_b, correct_c = normalize_equation(a, b, c)
        
        question_text = f"求通過點 $({x1}, {y1})$ 且斜率為 ${slope_latex}$ 的直線方程式。"

    elif problem_choice == 'two_points':
        x1 = random.randint(*coord_range)
        y1 = random.randint(*coord_range)
        x2 = random.randint(*coord_range)
        y2 = random.randint(*coord_range)

        # Ensure distinct points
        while x1 == x2 and y1 == y2:
            x2 = random.randint(*coord_range)
            y2 = random.randint(*coord_range)
        
        # Handle vertical/horizontal lines explicitly
        if x1 == x2: # Vertical line: x = x1
            a, b, c = 1, 0, -x1
        elif y1 == y2: # Horizontal line: y = y1
            a, b, c = 0, 1, -y1
        else:
            m_frac = Fraction(y2 - y1, x2 - x1)
            # Use point-slope form with (x1, y1) and m_frac
            # px - qy + (qy1 - px1) = 0
            a = m_frac.numerator
            b = -m_frac.denominator
            c = m_frac.denominator * y1 - m_frac.numerator * x1
            
        correct_a, correct_b, correct_c = normalize_equation(a, b, c)
        question_text = f"求通過 $A({x1}, {y1})$ 與 $B({x2}, {y2})$ 兩點的直線方程式。"
    
    elif problem_choice == 'slope_y_intercept':
        # Generate slope: integer or fraction
        slope_type = random.choice(['integer', 'fraction'])
        if slope_type == 'integer':
            m_num = random.randint(*slope_num_range)
            if m_num == 0 and level > 1: m_num = random.choice([-2, -1, 1, 2])
            m_frac = Fraction(m_num)
            slope_latex = str(m_num)
        else: # Fraction
            m_num = random.randint(*slope_num_range)
            m_den = random.randint(*slope_den_range)
            while m_num == 0:
                 m_num = random.randint(*slope_num_range)
            m_frac = Fraction(m_num, m_den)
            slope_latex = f"\\frac{{{m_frac.numerator}}}{{{m_frac.denominator}}}"

        y_intercept = random.randint(*intercept_range)

        # Equation: y = mx + b  => mx - y + b = 0
        # If m = p/q, then qy = px + qb => px - qy + qb = 0
        a = m_frac.numerator
        b = -m_frac.denominator
        c = m_frac.denominator * y_intercept
        
        correct_a, correct_b, correct_c = normalize_equation(a, b, c)
        question_text = f"求斜率為 ${slope_latex}$ 且y截距為 ${y_intercept}$ 的直線方程式。"

    elif problem_choice == 'two_intercepts':
        x_intercept = random.randint(*intercept_range)
        y_intercept = random.randint(*intercept_range)
        
        # Ensure non-zero intercepts for the general form x/a + y/b = 1
        while x_intercept == 0 or y_intercept == 0:
            x_intercept = random.randint(*intercept_range)
            y_intercept = random.randint(*intercept_range)
        
        # Points are (x_intercept, 0) and (0, y_intercept)
        # Slope m = (y_intercept - 0) / (0 - x_intercept) = -y_intercept / x_intercept
        m_frac = Fraction(-y_intercept, x_intercept)
        
        # Use point-slope form with (x_intercept, 0) and m_frac
        # px - qy + (qy1 - px1) = 0, where y1=0
        # px - qy - px1 = 0
        a = m_frac.numerator
        b = -m_frac.denominator
        c = -m_frac.numerator * x_intercept
        
        correct_a, correct_b, correct_c = normalize_equation(a, b, c)
        question_text = f"求x截距為 ${x_intercept}$ 且y截距為 ${y_intercept}$ 的直線方程式。"

    elif problem_choice == 'vertical_horizontal':
        line_type = random.choice(['vertical', 'horizontal'])
        k = random.randint(*coord_range)
        
        # Generate another coordinate just for the point
        other_coord = random.randint(*coord_range)

        if line_type == 'vertical': # x = k
            a, b, c = 1, 0, -k
            question_text = f"求通過點 $({k}, {other_coord})$ 且沒有斜率的直線方程式。"
        else: # y = k
            a, b, c = 0, 1, -k
            question_text = f"求通過點 $({other_coord}, {k})$ 且斜率為 $0$ 的直線方程式。"
        
        correct_a, correct_b, correct_c = normalize_equation(a, b, c)

    elif problem_choice == 'find_slope':
        # Generate A, B, C for Ax + By + C = 0
        a_coeff = random.randint(-5, 5)
        b_coeff = random.randint(-5, 5)
        c_coeff = random.randint(-10, 10)

        # Ensure B is not 0 for slope to be defined for 'find slope' problem type
        # Also ensure not all A, B, C are zero
        while b_coeff == 0 or (a_coeff == 0 and b_coeff == 0 and c_coeff == 0):
            a_coeff = random.randint(-5, 5)
            b_coeff = random.randint(-5, 5)
            c_coeff = random.randint(-10, 10)
        
        # Normalize for display in question text
        display_a, display_b, display_c = normalize_equation(a_coeff, b_coeff, c_coeff)
        
        # Construct equation string for display
        parts = []
        if display_a != 0:
            if display_a == 1: parts.append("x")
            elif display_a == -1: parts.append("-x")
            else: parts.append(f"{display_a}x")
        
        if display_b != 0:
            if display_b == 1: parts.append("+y") if parts else parts.append("y")
            elif display_b == -1: parts.append("-y")
            elif display_b > 0: parts.append(f"+{display_b}y")
            else: parts.append(f"{display_b}y")

        if display_c != 0:
            if display_c > 0: parts.append(f"+{display_c}")
            else: parts.append(str(display_c))
        
        equation_display = "".join(parts) + "=0"
        if equation_display.startswith("+"):
            equation_display = equation_display[1:] # Remove leading '+' if any

        # Calculate slope: m = -A/B
        # This branch already guarantees B != 0
        m_frac = Fraction(-a_coeff, b_coeff)
        if m_frac.denominator == 1:
            correct_slope_str = str(m_frac.numerator)
        else:
            correct_slope_str = f"\\frac{{{m_frac.numerator}}}{{{m_frac.denominator}}}"

        question_text = f"求直線 $L: {equation_display}$ 的斜率。"
        
        return {
            "question_text": question_text,
            "answer": correct_slope_str, # For this type, the answer is the slope string
            "correct_answer": correct_slope_str
        }

    # Format the correct equation Ax + By + C = 0 for other problem types
    ans_parts = []
    
    # Handle A term
    if correct_a != 0:
        if correct_a == 1:
            ans_parts.append("x")
        elif correct_a == -1:
            ans_parts.append("-x")
        else:
            ans_parts.append(f"{correct_a}x")

    # Handle B term
    if correct_b != 0:
        if correct_b == 1:
            ans_parts.append("+y") if ans_parts else ans_parts.append("y") # Add '+' only if not first term
        elif correct_b == -1:
            ans_parts.append("-y")
        elif correct_b > 0:
            ans_parts.append(f"+{correct_b}y")
        else: # correct_b < 0
            ans_parts.append(f"{correct_b}y")
    
    # Handle C term
    if correct_c != 0:
        if correct_c > 0:
            ans_parts.append(f"+{correct_c}")
        else: # correct_c < 0
            ans_parts.append(str(correct_c))

    # Construct the final answer string
    if not ans_parts: # This case should ideally not be reached for a valid line
        final_answer = "0=0" 
    else:
        final_answer = "".join(ans_parts) + "=0"
        # Remove leading '+' if it exists (e.g., "+x+3y-1=0" -> "x+3y-1=0")
        if final_answer.startswith("+"):
            final_answer = final_answer[1:]

    return {
        "question_text": question_text,
        "answer": final_answer, # The equation string is the answer
        "correct_answer": final_answer
    }


def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip().replace(" ", "").lower()
    correct_answer = correct_answer.strip().replace(" ", "").lower()

    # Check if the problem was asking for a slope
    # Heuristic: if correct_answer contains a fraction or is just a number/ "undefined"
    if "/" in correct_answer or re.match(r"^-?\d+$", correct_answer) or correct_answer == "undefined":
        is_correct = False
        try:
            # Try to compare as fractions first
            user_m = Fraction(user_answer)
            correct_m = Fraction(correct_answer)
            is_correct = (user_m == correct_m)
        except ValueError:
            # If not a valid fraction, compare as strings
            is_correct = (user_answer == correct_answer)
        
        result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
        return {"correct": is_correct, "result": result_text, "next_question": True}

    # Otherwise, it's an equation problem
    try:
        user_a, user_b, user_c = parse_equation_to_abc(user_answer)
        correct_a, correct_b, correct_c = parse_equation_to_abc(correct_answer)
        
        normalized_user = normalize_equation(user_a, user_b, user_c)
        normalized_correct = normalize_equation(correct_a, correct_b, correct_c)
        
        is_correct = (normalized_user == normalized_correct)
        
        if is_correct:
            result_text = f"完全正確！您的答案 ${user_answer}$ 經整理後與標準答案一致。"
        else:
            # Format the normalized correct answer for feedback
            correct_display_parts = []
            if normalized_correct[0] != 0:
                if normalized_correct[0] == 1: correct_display_parts.append("x")
                elif normalized_correct[0] == -1: correct_display_parts.append("-x")
                else: correct_display_parts.append(f"{normalized_correct[0]}x")
            
            if normalized_correct[1] != 0:
                if normalized_correct[1] == 1: correct_display_parts.append("+y") if correct_display_parts else correct_display_parts.append("y")
                elif normalized_correct[1] == -1: correct_display_parts.append("-y")
                elif normalized_correct[1] > 0: correct_display_parts.append(f"+{normalized_correct[1]}y")
                else: correct_display_parts.append(f"{normalized_correct[1]}y")

            if normalized_correct[2] != 0:
                if normalized_correct[2] > 0: correct_display_parts.append(f"+{normalized_correct[2]}")
                else: correct_display_parts.append(str(normalized_correct[2]))
            
            if not correct_display_parts:
                correct_display = "0=0"
            else:
                correct_display = "".join(correct_display_parts) + "=0"
                if correct_display.startswith("+"): correct_display = correct_display[1:]
            
            result_text = f"答案不正確。正確答案的標準形式為：${correct_display}$"

    except Exception as e:
        is_correct = False
        result_text = f"您的輸入格式無法解析。請確保輸入的是有效的直線方程式，例如 $Ax+By+C=0$, $y=mx+b$, $x=k$ 或 $y=k$。<br>錯誤訊息: {e}"

    return {"correct": is_correct, "result": result_text, "next_question": True}