import random
from fractions import Fraction
import math
import re

# Helper to format line equations nicely
def format_line_equation(A, B, C):
    """
    Formats a line equation Ax + By + C = 0 into a string.
    Ensures A, B, C are integers by finding a common multiplier if they are fractions.
    Handles various cases for coefficients.
    Returns: A tuple (str_equation, A_int, B_int, C_int) in canonical form.
    """
    # Convert to fractions for precision
    A_frac = Fraction(A)
    B_frac = Fraction(B)
    C_frac = Fraction(C)

    # Find common denominator
    common_den = 1
    if A_frac.denominator != 1:
        common_den = math.lcm(common_den, A_frac.denominator)
    if B_frac.denominator != 1:
        common_den = math.lcm(common_den, B_frac.denominator)
    if C_frac.denominator != 1:
        common_den = math.lcm(common_den, C_frac.denominator)

    A_int = int(A_frac * common_den)
    B_int = int(B_frac * common_den)
    C_int = int(C_frac * common_den)

    # Simplify by dividing by GCD
    # Ensure at least one coefficient is non-zero for a valid line
    if A_int == 0 and B_int == 0:
        # This implies a degenerate equation like C=0 or 0=0. If C_int is also 0, it's 0=0.
        # If C_int is non-zero, it's a contradiction C=0.
        # For problem generation, we typically ensure valid lines, so this is for safety.
        if C_int == 0:
            return "0=0", 0, 0, 0 # Effectively any point
        else:
            return f"{C_int}=0", 0, 0, C_int # Contradiction, no points
            
    gcd_val = abs(math.gcd(A_int, math.gcd(B_int, C_int)))
    if gcd_val != 0:
        A_int //= gcd_val
        B_int //= gcd_val
        C_int //= gcd_val
    
    # Ensure the first non-zero coefficient is positive for canonical form
    if A_int < 0 or (A_int == 0 and B_int < 0):
        A_int *= -1
        B_int *= -1
        C_int *= -1

    parts = []
    if A_int != 0:
        if A_int == 1:
            parts.append("x")
        elif A_int == -1:
            parts.append("-x")
        else:
            parts.append(f"{A_int}x")
    
    if B_int != 0:
        if B_int == 1:
            parts.append("+y" if parts else "y")
        elif B_int == -1:
            parts.append("-y")
        else:
            parts.append(f"{'+' if parts and B_int > 0 else ''}{B_int}y")

    if C_int != 0:
        parts.append(f"{'+' if parts and C_int > 0 else ''}{C_int}")
    
    if not parts: # Should only happen if A_int, B_int, C_int are all 0 after simplification
        return "0=0", 0, 0, 0
    
    return f"{''.join(parts)}=0", A_int, B_int, C_int

# Helper to get slope from general form Ax+By+C=0
# Returns (slope, 'vertical') or (slope, 'horizontal') or (slope, 'finite')
def get_slope_from_general_form(A, B, C):
    if B == 0: # Vertical line Ax + C = 0
        if A == 0: return None, 'invalid' # Not a line
        return None, 'vertical' # Slope is undefined
    elif A == 0: # Horizontal line By + C = 0
        return Fraction(0), 'horizontal' # Slope is 0
    else:
        return Fraction(-A, B), 'finite' # Finite slope

# Helper to get line equation from point and slope
# Returns (A, B, C) for Ax+By+C=0, using Fractions
def get_general_form_from_point_slope(x0, y0, slope):
    if slope is None: # Vertical line x = x0
        return Fraction(1), Fraction(0), Fraction(-x0)
    else: # y - y0 = m(x - x0)
        m = Fraction(slope)
        # m*x - y + (y0 - m*x0) = 0
        A_frac = m
        B_frac = Fraction(-1)
        C_frac = Fraction(y0) - m * Fraction(x0)
        return A_frac, B_frac, C_frac

def generate_parallel_perpendicular_lines_problem():
    # 題型：Given a point and a line, find parallel/perpendicular line through the point.
    
    # Generate point A(x0, y0)
    x0 = random.randint(-5, 5)
    y0 = random.randint(-5, 5)

    # Generate line L: Ax + By + C = 0
    # Ensure A or B is non-zero for a valid line
    A_L = 0
    B_L = 0
    while A_L == 0 and B_L == 0:
        A_L = random.randint(-3, 3)
        B_L = random.randint(-3, 3)
    C_L = random.randint(-10, 10)

    line_L_str, A_L_int, B_L_int, C_L_int = format_line_equation(A_L, B_L, C_L)

    # Get slope of L
    m_L, slope_type_L = get_slope_from_general_form(A_L_int, B_L_int, C_L_int)

    # Part 1: Parallel line L1
    m_L1 = m_L # Same slope
    A_L1, B_L1, C_L1 = get_general_form_from_point_slope(x0, y0, m_L1)
    line_L1_str, _, _, _ = format_line_equation(A_L1, B_L1, C_L1)

    # Part 2: Perpendicular line L2
    m_L2 = None # Default for vertical (if m_L is 0)
    if slope_type_L == 'finite':
        m_L2 = -1 / m_L if m_L != 0 else None # If m_L = 0 (horizontal), L2 is vertical
    elif slope_type_L == 'horizontal': # L is horizontal (m_L=0), L2 is vertical (m_L2=None)
        m_L2 = None
    elif slope_type_L == 'vertical': # L is vertical (m_L=None), L2 is horizontal (m_L2=0)
        m_L2 = Fraction(0)
    
    A_L2, B_L2, C_L2 = get_general_form_from_point_slope(x0, y0, m_L2)
    line_L2_str, _, _, _ = format_line_equation(A_L2, B_L2, C_L2)

    question_text = f"給定點 $A({x0},{y0})$ 及直線 $L: {line_L_str}$ 。<br>" \
                    f"(1)已知直線 $L_1$ 通過 $A$ 點且與 $L$ 平行，求 $L_1$ 的方程式。<br>" \
                    f"(2)已知直線 $L_2$ 通過 $A$ 點且與 $L$ 垂直，求 $L_2$ 的方程式。"
    
    correct_answers_dict = {
        "L1": line_L1_str,
        "L2": line_L2_str
    }

    return {
        "question_text": question_text,
        "answer": correct_answers_dict,
        "correct_answer": correct_answers_dict
    }

def generate_perpendicular_bisector_circumcenter_problem():
    # 題型：求中垂線方程式及三點等距離點 (外心) 坐標。
    
    # Generate three non-collinear points A, B, C
    # To ensure non-collinearity and distinctness, generate points within a range
    # and check conditions. Max attempts to avoid infinite loops.
    points_coords = []
    max_attempts = 100
    attempts = 0
    while len(points_coords) < 3 and attempts < max_attempts:
        x_val = random.randint(-7, 7)
        y_val = random.randint(-7, 7)
        new_point = (x_val, y_val)
        if new_point not in points_coords: # Ensure distinct points
            points_coords.append(new_point)
        attempts += 1
    
    # Fallback to known non-collinear points if randomization fails
    if len(points_coords) < 3:
        points_coords = [(1,1), (5,1), (3,5)]

    A, B, C = points_coords[0], points_coords[1], points_coords[2]
    
    # Ensure they are not collinear
    # Area of triangle formed by points (x1, y1), (x2, y2), (x3, y3) is 0 if collinear.
    # Area = 0.5 * |x1(y2-y3) + x2(y3-y1) + x3(y1-y2)|
    # Check if x1(y2-y3) + x2(y3-y1) + x3(y1-y2) is zero
    cross_product = A[0]*(B[1]-C[1]) + B[0]*(C[1]-A[1]) + C[0]*(A[1]-B[1])
    if cross_product == 0:
        # If collinear, regenerate or use a guaranteed non-collinear set
        A, B, C = (random.randint(-5,-1), random.randint(-5,-1)), (random.randint(1,5), random.randint(-5,-1)), (random.randint(-3,3), random.randint(1,5))
        cross_product = A[0]*(B[1]-C[1]) + B[0]*(C[1]-A[1]) + C[0]*(A[1]-B[1])
        if cross_product == 0: # Still collinear, use a fixed set
            A, B, C = (1,1), (7,1), (4,5) # Guaranteed non-collinear

    # Calculate properties for AB segment
    M_AB_x = Fraction(A[0] + B[0], 2)
    M_AB_y = Fraction(A[1] + B[1], 2)

    m_AB = None
    if A[0] == B[0]: # Vertical segment AB
        m_AB = None # Slope undefined
        m_perp_AB = Fraction(0) # Perpendicular is horizontal
    elif A[1] == B[1]: # Horizontal segment AB
        m_AB = Fraction(0)
        m_perp_AB = None # Perpendicular is vertical
    else:
        m_AB = Fraction(B[1] - A[1], B[0] - A[0])
        m_perp_AB = -1 / m_AB
    
    A_L_AB, B_L_AB, C_L_AB = get_general_form_from_point_slope(M_AB_x, M_AB_y, m_perp_AB)
    L_AB_str, _, _, _ = format_line_equation(A_L_AB, B_L_AB, C_L_AB)

    # Calculate properties for BC segment
    M_BC_x = Fraction(B[0] + C[0], 2)
    M_BC_y = Fraction(B[1] + C[1], 2)

    m_BC = None
    if B[0] == C[0]: # Vertical segment BC
        m_BC = None
        m_perp_BC = Fraction(0)
    elif B[1] == C[1]: # Horizontal segment BC
        m_BC = Fraction(0)
        m_perp_BC = None
    else:
        m_BC = Fraction(C[1] - B[1], C[0] - B[0])
        m_perp_BC = -1 / m_BC
    
    A_L_BC, B_L_BC, C_L_BC = get_general_form_from_point_slope(M_BC_x, M_BC_y, m_perp_BC)
    L_BC_str, _, _, _ = format_line_equation(A_L_BC, B_L_BC, C_L_BC)

    # Solve for intersection point (circumcenter)
    # Using Cramer's Rule for the system:
    # A_L_AB * x + B_L_AB * y = -C_L_AB
    # A_L_BC * x + B_L_BC * y = -C_L_BC

    denom = A_L_AB * B_L_BC - A_L_BC * B_L_AB
    
    # If denom == 0, the perpendicular bisectors are parallel or coincident,
    # which implies the triangle is degenerate (collinear points).
    # This should be prevented by the non-collinearity check above, but for safety:
    if denom == 0:
        return generate_perpendicular_bisector_circumcenter_problem() # Retry with different points

    circumcenter_x = (B_L_AB * (-C_L_BC) - B_L_BC * (-C_L_AB)) / denom
    circumcenter_y = (A_L_BC * (-C_L_AB) - A_L_AB * (-C_L_BC)) / denom

    circumcenter_x_str = circumcenter_x.numerator if circumcenter_x.denominator == 1 else str(circumcenter_x)
    circumcenter_y_str = circumcenter_y.numerator if circumcenter_y.denominator == 1 else str(circumcenter_y)
    circumcenter_str = f"({circumcenter_x_str},{circumcenter_y_str})"

    question_text = f"已知三個點的坐標分別為 $A({A[0]},{A[1]})$ , $B({B[0]},{B[1]})$ , $C({C[0]},{C[1]})$ 。<br>" \
                    f"回答下列問題：<br>" \
                    f"(1)求 $\\overline{{AB}}$ 的中垂線之方程式。<br>" \
                    f"(2)求 $\\overline{{BC}}$ 的中垂線之方程式。<br>" \
                    f"(3)該等距離點的坐標為何？"
    
    correct_answers_dict = {
        "L_AB": L_AB_str,
        "L_BC": L_BC_str,
        "circumcenter": circumcenter_str
    }

    return {
        "question_text": question_text,
        "answer": correct_answers_dict,
        "correct_answer": correct_answers_dict
    }

def generate_point_reflection_problem():
    # 題型：求點對於直線的對稱點坐標。
    
    # Generate point A(x1, y1)
    x1 = random.randint(-5, 5)
    y1 = random.randint(-5, 5)

    # Generate line L: Ax + By + C = 0
    A_L = 0
    B_L = 0
    while A_L == 0 and B_L == 0:
        A_L = random.randint(-3, 3)
        B_L = random.randint(-3, 3)
    C_L = random.randint(-10, 10)
    
    # Ensure point A is not on line L to make the problem meaningful
    # Check if Ax1 + By1 + C = 0
    if A_L * x1 + B_L * y1 + C_L == 0:
        # Shift C to move line, ensuring it's not on the line
        C_L += random.choice([-1, 1]) * random.randint(1, 3)
        # Re-check and if still on line (highly unlikely), change A
        if A_L * x1 + B_L * y1 + C_L == 0:
            A_L += random.choice([-1, 1])
            if A_L == 0 and B_L == 0: A_L = 1 # Ensure valid line
            C_L = random.randint(-10, 10) # Re-randomize C after changing A

    line_L_str, A_L_int, B_L_int, C_L_int = format_line_equation(A_L, B_L, C_L)

    # 1. Find slope of L
    m_L, slope_type_L = get_slope_from_general_form(A_L_int, B_L_int, C_L_int)

    # 2. Find slope of perpendicular line L_perp (passing through A and symmetric point B)
    m_perp = None
    if slope_type_L == 'finite':
        m_perp = -1 / m_L if m_L != 0 else None
    elif slope_type_L == 'horizontal': # L is horizontal (m_L=0), L_perp is vertical (m_perp=None)
        m_perp = None
    elif slope_type_L == 'vertical': # L is vertical (m_L=None), L_perp is horizontal (m_perp=0)
        m_perp = Fraction(0)
    
    # 3. Equation of L_perp
    A_L_perp, B_L_perp, C_L_perp = get_general_form_from_point_slope(x1, y1, m_perp)

    # 4. Find intersection point M of L and L_perp
    # Solve:
    # A_L_int * x + B_L_int * y = -C_L_int
    # A_L_perp * x + B_L_perp * y = -C_L_perp
    
    # Use the fractional forms for calculation to maintain precision
    denom = Fraction(A_L_int) * B_L_perp - A_L_perp * Fraction(B_L_int)
    
    # If denom == 0, lines are parallel or coincident. This means L and L_perp are parallel,
    # which implies L has an undefined slope (vertical) and L_perp also has an undefined slope,
    # or L has 0 slope (horizontal) and L_perp also has 0 slope. This should not happen
    # unless there's a problem in slope determination or the original line L is invalid.
    # Given the previous checks, this implies a calculation error or a very rare degenerate case.
    if denom == 0:
        return generate_point_reflection_problem() # Regenerate if lines are parallel/coincident

    M_x = (B_L_perp * Fraction(-C_L_int) - Fraction(B_L_int) * (-C_L_perp)) / denom
    M_y = (A_L_perp * Fraction(-C_L_int) - Fraction(A_L_int) * (-C_L_perp)) / denom

    # 5. M is the midpoint of A(x1, y1) and B(x_sym, y_sym)
    # M_x = (x1 + x_sym) / 2  => x_sym = 2 * M_x - x1
    # M_y = (y1 + y_sym) / 2  => y_sym = 2 * M_y - y1
    
    x_sym = Fraction(2) * M_x - Fraction(x1)
    y_sym = Fraction(2) * M_y - Fraction(y1)

    x_sym_str = x_sym.numerator if x_sym.denominator == 1 else str(x_sym)
    y_sym_str = y_sym.numerator if y_sym.denominator == 1 else str(y_sym)
    symmetric_point_str = f"({x_sym_str},{y_sym_str})"

    question_text = f"求點 $A({x1},{y1})$ 對於直線 $L:{line_L_str}$ 的對稱點坐標。"
    
    correct_answer = symmetric_point_str
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def generate(level=1):
    problem_types = [
        'parallel_perpendicular',
        'perpendicular_bisector_circumcenter',
        'point_reflection'
    ]
    
    problem_type = random.choice(problem_types)

    if problem_type == 'parallel_perpendicular':
        return generate_parallel_perpendicular_lines_problem()
    elif problem_type == 'perpendicular_bisector_circumcenter':
        return generate_perpendicular_bisector_circumcenter_problem()
    elif problem_type == 'point_reflection':
        return generate_point_reflection_problem()
    
    # Fallback / default
    return generate_parallel_perpendicular_lines_problem()


def check(user_answer, correct_answer):
    """
    Checks the user's answer against the correct answer.
    Handles single answers (string) and multiple answers (dictionary).
    """
    is_correct = False
    feedback_messages = []

    def normalize_coordinate(coord_str):
        # Remove parentheses and split by comma
        coord_str = coord_str.strip().replace('(', '').replace(')', '')
        parts = coord_str.split(',')
        if len(parts) == 2:
            try:
                x = Fraction(parts[0].strip())
                y = Fraction(parts[1].strip())
                return (x, y)
            except ValueError:
                return None
        return None

    def parse_line_equation_to_coeffs(eq_str):
        """
        Parses a line equation string into (A, B, C) fractional coefficients.
        Returns (A, B, C) tuple of Fractions or (None, error_message).
        """
        eq_str = eq_str.replace(' ', '').lower()

        # Handle simplified forms like 'x=C' or 'y=C'
        if '=' in eq_str:
            left, right = eq_str.split('=', 1)
            # if already in Ax+By+C=0 form but without '=0'
            if right == '0':
                eq_str = left
            else: # Convert y=mx+b or similar to Ax+By+C=0 form
                if left == 'x': # x=C -> x-C=0
                    eq_str = f"x-{right}"
                elif left == 'y': # y=mx+b -> mx-y+b=0
                    eq_str = f"{right}-y" # Move y to the right for consistent parsing below
                else: # Assume complex, not easily converted
                    return None, "無法解析方程式格式。請使用 $Ax+By+C=0$ 或 $x=C$, $y=C$ 等標準格式。"
        
        # Now try to parse `eq_str` (which should represent `Ax+By+C`)
        # Use regex to find x, y, and constant terms.
        # Ensure terms can be negative, fractional, etc.
        
        A_val = Fraction(0)
        B_val = Fraction(0)
        C_val = Fraction(0)
        
        # Pattern to capture coefficient and variable. Handles leading +/- and fractions.
        # e.g., '1/2x', '-x', '+3y', '5'
        term_pattern = r"([-+]?)(?:\s*(\d+\/\d+|\d*\.?\d+))?([xy]?)"
        
        current_str = eq_str
        
        # Iteratively find and remove terms
        while current_str:
            match = re.match(term_pattern, current_str)
            if not match:
                # If we cannot parse the start of the remaining string, it's malformed
                return None, f"無法解析方程式的'{current_str}'部分。"
            
            sign_str = match.group(1)
            coeff_str = match.group(2)
            var_str = match.group(3)
            
            coeff = Fraction(1)
            if coeff_str:
                coeff = Fraction(coeff_str)
            
            if sign_str == '-':
                coeff *= -1
            
            if var_str == 'x':
                A_val += coeff
            elif var_str == 'y':
                B_val += coeff
            elif not var_str: # Must be a constant
                C_val += coeff
            else: # Should not happen if regex is correct, but for safety
                return None, f"無法識別的變數或項: '{match.group(0)}'"

            current_str = current_str[len(match.group(0)):].strip()

        # After parsing, convert to canonical form using format_line_equation
        # This will simplify fractions, find GCD, and ensure leading positive coefficient.
        _, norm_A, norm_B, norm_C = format_line_equation(A_val, B_val, C_val)
        return (norm_A, norm_B, norm_C), None # Return canonical form

    # Check for dictionary answers (multiple parts) or single answer (string)
    if isinstance(correct_answer, dict):
        # User answer might come as a string representation of a dict. Attempt to parse it.
        if not isinstance(user_answer, dict):
            try:
                # Safely evaluate JSON-like string if needed.
                # Use literal_eval for safer parsing of dict/list strings.
                user_answer = eval(user_answer)
            except (SyntaxError, NameError, ValueError):
                feedback_messages.append("您的輸入格式不正確，請確保答案為字典格式，例如 {{'L1': 'x+y-1=0', 'L2': 'x-y+3=0'}} 或 {{'circumcenter': '(1/2, 3/4)'}}。")
                return {"correct": False, "result": "\n".join(feedback_messages), "next_question": False}

        if not isinstance(user_answer, dict):
            feedback_messages.append("您的輸入格式不正確，請確保答案為字典格式。")
            return {"correct": False, "result": "\n".join(feedback_messages), "next_question": False}

        all_parts_correct = True
        part_feedbacks = []

        for key, correct_val in correct_answer.items():
            user_val = user_answer.get(key)
            if user_val is None:
                all_parts_correct = False
                part_feedbacks.append(f"缺少 '{key}' 的答案。正確答案為 ${correct_val}$。")
                continue
            
            # Compare based on key type
            if key in ["L1", "L2", "L_AB", "L_BC"]: # Line equations
                user_parsed_coeffs, err_msg_user = parse_line_equation_to_coeffs(str(user_val))
                correct_parsed_coeffs, err_msg_correct = parse_line_equation_to_coeffs(str(correct_val))
                
                if err_msg_user:
                    part_feedbacks.append(f"'{key}' 的方程式格式錯誤：{err_msg_user}")
                    all_parts_correct = False
                elif user_parsed_coeffs == correct_parsed_coeffs:
                    part_feedbacks.append(f"'{key}'：正確。")
                else:
                    all_parts_correct = False
                    part_feedbacks.append(f"'{key}'：答案不正確。您的答案：${user_val}$，正確答案：${correct_val}$。")
            elif key in ["circumcenter", "symmetric_point"]: # Coordinate points
                user_coord = normalize_coordinate(str(user_val))
                correct_coord = normalize_coordinate(str(correct_val))

                if user_coord and correct_coord and user_coord[0] == correct_coord[0] and user_coord[1] == correct_coord[1]:
                    part_feedbacks.append(f"'{key}'：正確。")
                else:
                    all_parts_correct = False
                    part_feedbacks.append(f"'{key}'：答案不正確。您的答案：${user_val}$，正確答案：${correct_val}$。")
            else: # Generic string comparison for other keys
                if str(user_val).strip() == str(correct_val).strip():
                    part_feedbacks.append(f"'{key}'：正確。")
                else:
                    all_parts_correct = False
                    part_feedbacks.append(f"'{key}'：答案不正確。您的答案：${user_val}$，正確答案：${correct_val}$。")
        
        is_correct = all_parts_correct
        feedback_messages.append("<br>".join(part_feedbacks))

    else: # Single string answer
        # Default string comparison for exact match
        if str(user_answer).strip() == str(correct_answer).strip():
            is_correct = True
            feedback_messages.append(f"完全正確！答案是 ${correct_answer}$。")
        else:
            # Try to parse as coordinates
            user_coord = normalize_coordinate(str(user_answer))
            correct_coord = normalize_coordinate(str(correct_answer))
            
            if user_coord and correct_coord:
                if user_coord[0] == correct_coord[0] and user_coord[1] == correct_coord[1]:
                    is_correct = True
                    feedback_messages.append(f"完全正確！答案是 ${correct_answer}$。")
                else:
                    feedback_messages.append(f"答案不正確。正確答案應為：${correct_answer}$")
            else: # Try as line equation
                user_line_parsed, err_msg_user = parse_line_equation_to_coeffs(str(user_answer))
                correct_line_parsed, err_msg_correct = parse_line_equation_to_coeffs(str(correct_answer))
                
                if user_line_parsed and correct_line_parsed and user_line_parsed == correct_line_parsed:
                    is_correct = True
                    feedback_messages.append(f"完全正確！答案是 ${correct_answer}$。")
                else:
                    feedback_messages.append(f"答案不正確。正確答案應為：${correct_answer}$")
                    if err_msg_user:
                        feedback_messages.append(f"您的答案格式錯誤：{err_msg_user}")
    
    return {"correct": is_correct, "result": "\n".join(feedback_messages), "next_question": True}