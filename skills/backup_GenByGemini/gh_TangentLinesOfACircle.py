import random
import math
from fractions import Fraction
import re # For parsing in check function

# Helper function to get circle center and radius from standard form
def get_circle_params_standard(h, k, r_squared):
    return (Fraction(h), Fraction(k), math.sqrt(r_squared))

# Helper function to get circle center and radius from general form
def get_circle_params_general(D, E, F):
    h = Fraction(-D, 2)
    k = Fraction(-E, 2)
    radius_squared = h**2 + k**2 - F
    if radius_squared <= 0:
        raise ValueError("Invalid circle equation (radius squared <= 0)")
    return (h, k, math.sqrt(radius_squared))

# Helper function to convert line equation Ax+By+C=0 to canonical form (integers, A positive if possible)
# Target format: Ax + By = C (if C != 0), or Ax + By = 0 (if C = 0), or x = C, or y = C
def canonical_line_equation(A, B, C):
    # Convert to Fraction for precise calculations
    A, B, C = Fraction(A), Fraction(B), Fraction(C)

    # Find a common multiplier to make coefficients integers
    denominators = [f.denominator for f in [A, B, C]]
    lcm_val = 1
    for d in denominators:
        if d != 0: 
            lcm_val = (lcm_val * d) // math.gcd(lcm_val, d)

    A_int = A * lcm_val
    B_int = B * lcm_val
    C_int = C * lcm_val

    # If all coefficients are effectively zero, return "0 = 0"
    if abs(A_int) < 1e-9 and abs(B_int) < 1e-9 and abs(C_int) < 1e-9:
        return "0 = 0"

    # Find GCD to simplify coefficients
    # math.gcd requires integers. Ensure inputs are integers before calling.
    # Note: Using int() on a Fraction should be safe after lcm_val multiplication if it's an integer.
    common_divisor = abs(math.gcd(int(A_int), math.gcd(int(B_int), int(C_int))))
    if common_divisor == 0: 
        common_divisor = 1 

    A_final = int(A_int // common_divisor)
    B_final = int(B_int // common_divisor)
    C_final = int(C_int // common_divisor)
    
    # We want Ax+By=C_rhs, so C_rhs = -C_final
    C_rhs = -C_final 

    if A_final < 0:
        A_final, B_final, C_rhs = -A_final, -B_final, -C_rhs
    elif A_final == 0 and B_final < 0:
        # If A is 0, we want By = C_rhs. If B is negative, flip it.
        B_final, C_rhs = -B_final, -C_rhs
    
    # Handle special cases: vertical or horizontal lines
    if A_final == 0 and B_final != 0: # Line is y = constant
        if C_rhs == 0: return "y = 0"
        return f"y = {Fraction(C_rhs, B_final)}"
    
    if B_final == 0 and A_final != 0: # Line is x = constant
        if C_rhs == 0: return "x = 0"
        return f"x = {Fraction(C_rhs, A_final)}"

    # General form Ax + By = C_rhs
    final_terms_lhs = []
    
    # Handle x term
    if A_final == 1: final_terms_lhs.append("x")
    elif A_final == -1: final_terms_lhs.append("-x")
    elif A_final != 0: final_terms_lhs.append(f"{A_final}x")

    # Handle y term
    if B_final == 1:
        if final_terms_lhs: final_terms_lhs.append("+y")
        else: final_terms_lhs.append("y")
    elif B_final == -1:
        final_terms_lhs.append("-y")
    elif B_final != 0:
        if B_final > 0 and final_terms_lhs: final_terms_lhs.append(f"+{B_final}y")
        else: final_terms_lhs.append(f"{B_final}y")
    
    if not final_terms_lhs: # This might occur if A_final and B_final are both 0 (implies C_rhs is also 0 from original logic)
        return "0 = 0" # Should not happen for a valid line
    
    return "".join(final_terms_lhs) + f" = {C_rhs}"


# Helper to parse user input string into (A, B, C) coefficients for Ax+By=C
def parse_line_equation(line_str):
    line_str = line_str.strip().replace(" ", "")
    A, B, C_rhs = Fraction(0), Fraction(0), Fraction(0)
    
    if not line_str:
        raise ValueError("Empty line string")

    # Handle cases like "x=2", "y=-3", "2x=4", "-y=1"
    match_single_var = re.match(r"([-+]?\d*)x=([-+]?[\d/]+)", line_str)
    if match_single_var:
        coeff_x = match_single_var.group(1)
        A = Fraction(coeff_x if coeff_x not in ['', '-'] else ('1' if coeff_x == '' else '-1'))
        C_rhs = Fraction(match_single_var.group(2))
        return A, B, C_rhs

    match_single_var = re.match(r"([-+]?\d*)y=([-+]?[\d/]+)", line_str)
    if match_single_var:
        coeff_y = match_single_var.group(1)
        B = Fraction(coeff_y if coeff_y not in ['', '-'] else ('1' if coeff_y == '' else '-1'))
        C_rhs = Fraction(match_single_var.group(2))
        return A, B, C_rhs

    # Handle cases like "2=x", "-3=y"
    match_single_var = re.match(r"([-+]?[\d/]+)=([-+]?\d*)x", line_str)
    if match_single_var:
        coeff_x = match_single_var.group(2)
        A = Fraction(coeff_x if coeff_x not in ['', '-'] else ('1' if coeff_x == '' else '-1'))
        C_rhs = Fraction(match_single_var.group(1))
        return A, B, C_rhs

    match_single_var = re.match(r"([-+]?[\d/]+)=([-+]?\d*)y", line_str)
    if match_single_var:
        coeff_y = match_single_var.group(2)
        B = Fraction(coeff_y if coeff_y not in ['', '-'] else ('1' if coeff_y == '' else '-1'))
        C_rhs = Fraction(match_single_var.group(1))
        return A, B, C_rhs

    # Handle general Ax+By=C or Ax+By+C=0 forms
    parts = line_str.split('=')
    lhs_str = parts[0]
    rhs_str = parts[1] if len(parts) > 1 else "0" # If no '=', assume =0

    # Parse LHS (Ax + By + C_temp)
    temp_lhs_A, temp_lhs_B, temp_lhs_C = Fraction(0), Fraction(0), Fraction(0)
    lhs_terms = re.findall(r"([+-]?\d*x)|([+-]?\d*y)|([+-]?[\d/]+)", lhs_str.replace("-", "+-"))
    for term_x, term_y, term_const in lhs_terms:
        if term_x:
            coeff_str = term_x.replace('x', '')
            temp_lhs_A += Fraction(coeff_str if coeff_str not in ['', '-'] else ('1' if coeff_str == '' else '-1'))
        elif term_y:
            coeff_str = term_y.replace('y', '')
            temp_lhs_B += Fraction(coeff_str if coeff_str not in ['', '-'] else ('1' if coeff_str == '' else '-1'))
        elif term_const:
            temp_lhs_C += Fraction(term_const)

    # Parse RHS (Ax + By + C_temp) and move to LHS
    temp_rhs_A, temp_rhs_B, temp_rhs_C = Fraction(0), Fraction(0), Fraction(0)
    rhs_terms = re.findall(r"([+-]?\d*x)|([+-]?\d*y)|([+-]?[\d/]+)", rhs_str.replace("-", "+-"))
    for term_x, term_y, term_const in rhs_terms:
        if term_x:
            coeff_str = term_x.replace('x', '')
            temp_rhs_A += Fraction(coeff_str if coeff_str not in ['', '-'] else ('1' if coeff_str == '' else '-1'))
        elif term_y:
            coeff_str = term_y.replace('y', '')
            temp_rhs_B += Fraction(coeff_str if coeff_str not in ['', '-'] else ('1' if coeff_str == '' else '-1'))
        elif term_const:
            temp_rhs_C += Fraction(term_const)
    
    A = temp_lhs_A - temp_rhs_A
    B = temp_lhs_B - temp_rhs_B
    C_rhs = temp_rhs_C - temp_lhs_C # The constant that remains on the RHS after moving all variable terms to LHS
    
    return A, B, C_rhs # Returns A, B, C for Ax+By=C_rhs


def generate_on_circle_tangent_problem(level):
    h = random.randint(-5, 5)
    k = random.randint(-5, 5)
    r_val = random.randint(2, 6) # Radius
    r_squared = r_val**2

    # Find a point (x0, y0) on the circle with integer coordinates
    found_point = False
    for dx_sq_val in range(r_squared + 1):
        dy_sq_val = r_squared - dx_sq_val
        # Check if dy_sq_val is a perfect square
        if math.isqrt(dy_sq_val)**2 == dy_sq_val: 
            dx = math.isqrt(dx_sq_val)
            dy = math.isqrt(dy_sq_val)
            
            # Use random sign for dx and dy
            x0_options = [h + dx, h - dx] if dx != 0 else [h]
            y0_options = [k + dy, k - dy] if dy != 0 else [k]

            x0 = random.choice(x0_options)
            y0 = random.choice(y0_options)
            
            # Ensure the point is distinct from the center for well-defined slope
            if (x0, y0) != (h, k):
                found_point = True
                break
    
    if not found_point: 
        return generate_on_circle_tangent_problem(level)

    # Determine circle equation form
    use_general_form = random.choice([True, False]) if level > 1 else False # Introduce general form at higher levels

    question_circle_eq_str = ""
    if use_general_form:
        D = -2 * h
        E = -2 * k
        F = h**2 + k**2 - r_squared
        question_circle_eq_str = f"x^{{2}} + y^{{2}}"
        if D != 0:
            question_circle_eq_str += f" + {D}x" if D > 0 else f" {D}x"
        if E != 0:
            question_circle_eq_str += f" + {E}y" if E > 0 else f" {E}y"
        if F != 0:
            question_circle_eq_str += f" + {F}" if F > 0 else f" {F}"
        question_circle_eq_str += " = 0"
    else: # Standard form
        # Proper handling of (x-h)^2, (x+h)^2, x^2
        x_part_str = ""
        if h == 0:
            x_part_str = "x^{{2}}"
        elif h < 0: # (x - abs(h))^2
            x_part_str = f"(x + {abs(h)})^{{2}}"
        else: # (x + h)^2 -> (x - (-h))^2
            x_part_str = f"(x - {h})^{{2}}"
        
        y_part_str = ""
        if k == 0:
            y_part_str = "y^{{2}}"
        elif k < 0: # (y - abs(k))^2
            y_part_str = f"(y + {abs(k)})^{{2}}"
        else: # (y + k)^2
            y_part_str = f"(y - {k})^{{2}}"

        question_circle_eq_str = f"{x_part_str} + {y_part_str} = {r_squared}"


    # Calculate tangent line coefficients using the formula: (x0-h)(x-h) + (y0-k)(y-k) = r^2
    A_coeff = Fraction(x0 - h)
    B_coeff = Fraction(y0 - k)
    # The constant term is -(x0-h)*h - (y0-k)*k - r_squared in Ax+By+C=0 form.
    # We want Ax+By=C_rhs, so C_rhs = (x0-h)*h + (y0-k)*k + r_squared
    C_rhs = Fraction((x0 - h) * h + (y0 - k) * k + r_squared)
    
    correct_answer = canonical_line_equation(A_coeff, B_coeff, -C_rhs) # -C_rhs from my definition in canonical_line_equation
    
    question_text = f"已知圓 $C$: ${question_circle_eq_str}$，求過圓上一點 $P({x0}, {y0})$ 的切線方程式。"
    
    return {
        "question_text": question_text,
        "answer": correct_answer, # Store the canonical form as the answer
        "correct_answer": correct_answer
    }


def generate_outside_circle_tangent_problem(level):
    h = random.randint(-4, 4)
    k = random.randint(-4, 4)
    r_val = random.randint(2, 5)
    r_squared = r_val**2

    # Generate P(x0, y0) outside the circle
    x0, y0 = h, k # Start at center
    # Ensure P is outside by a certain margin to avoid near-tangent numerical issues
    min_dist_sq = r_squared + random.randint(3, 10) # At least 3 units further than r^2
    while (x0 - h)**2 + (y0 - k)**2 <= min_dist_sq: 
        x0 = random.randint(h - r_val - 4, h + r_val + 4)
        y0 = random.randint(k - r_val - 4, k + r_val + 4)
        if (x0, y0) == (h, k): # Ensure point is not the center
            x0 += 1 

    # Determine circle equation form
    use_general_form = random.choice([True, False]) if level > 1 else False

    question_circle_eq_str = ""
    if use_general_form:
        D = -2 * h
        E = -2 * k
        F = h**2 + k**2 - r_squared
        question_circle_eq_str = f"x^{{2}} + y^{{2}}"
        if D != 0:
            question_circle_eq_str += f" + {D}x" if D > 0 else f" {D}x"
        if E != 0:
            question_circle_eq_str += f" + {E}y" if E > 0 else f" {E}y"
        if F != 0:
            question_circle_eq_str += f" + {F}" if F > 0 else f" {F}"
        question_circle_eq_str += " = 0"
    else: # Standard form
        # Proper handling of (x-h)^2, (x+h)^2, x^2
        x_part_str = ""
        if h == 0:
            x_part_str = "x^{{2}}"
        elif h < 0: # (x - abs(h))^2
            x_part_str = f"(x + {abs(h)})^{{2}}"
        else: # (x + h)^2 -> (x - (-h))^2
            x_part_str = f"(x - {h})^{{2}}"
        
        y_part_str = ""
        if k == 0:
            y_part_str = "y^{{2}}"
        elif k < 0: # (y - abs(k))^2
            y_part_str = f"(y + {abs(k)})^{{2}}"
        else: # (y + k)^2
            y_part_str = f"(y - {k})^{{2}}"

        question_circle_eq_str = f"{x_part_str} + {y_part_str} = {r_squared}"


    # Calculate tangent lines
    tangent_lines = []
    
    dx_P = Fraction(x0 - h)
    dy_P = Fraction(y0 - k)
    
    # Quadratic equation for m: A_m*m^2 + B_m*m + C_m = 0
    A_m = dx_P**2 - r_val**2
    B_m = -2 * dx_P * dy_P
    C_m = dy_P**2 - r_val**2

    # Solve for m
    if abs(A_m) < 1e-9: # A_m is close to zero, effectively a linear equation
        # This occurs when |x0 - h| = r_val, meaning one tangent is vertical (x = x0)
        tangent_lines.append(canonical_line_equation(1, 0, -x0)) # x - x0 = 0 -> x = x0

        # Find the second tangent
        if abs(B_m) > 1e-9: # If B_m is not zero (dy_P is not zero)
            m_val = -C_m / B_m
            # Line: y - y0 = m(x - x0) -> m*x - y + (y0 - m*x0) = 0
            # Coefficients for canonical_line_equation are A, B, C for Ax+By+C=0
            # So A=m, B=-1, C=(y0 - m*x0)
            tangent_lines.append(canonical_line_equation(m_val, -1, (y0 - m_val * x0)))
        elif abs(dy_P) < 1e-9: # B_m is also zero, implies dy_P = 0 (and dx_P^2 = r_val^2)
            # This means P is (h +/- r_val, k). The two tangents are x = x0 and y = k.
            tangent_lines.append(canonical_line_equation(0, 1, -k)) # y - k = 0 -> y = k
    else: # A_m is not zero, solve quadratic for two slopes
        discriminant = B_m**2 - 4 * A_m * C_m
        if discriminant < -1e-9: # Should not happen if P is truly outside
            # Fallback for numerical instability or incorrect problem generation
            return generate_outside_circle_tangent_problem(level)
        
        sqrt_discriminant = math.sqrt(max(0, discriminant)) 
        
        m1 = (-B_m + sqrt_discriminant) / (2 * A_m)
        m2 = (-B_m - sqrt_discriminant) / (2 * A_m)

        tangent_lines.append(canonical_line_equation(m1, -1, (y0 - m1 * x0)))
        if abs(m1 - m2) > 1e-9: # Only add second line if distinct slope
            tangent_lines.append(canonical_line_equation(m2, -1, (y0 - m2 * x0)))

    unique_tangents = []
    seen_tangents = set()
    for line in tangent_lines:
        if line not in seen_tangents:
            unique_tangents.append(line)
            seen_tangents.add(line)
    
    unique_tangents.sort()
    correct_answer = "; ".join(unique_tangents)
    
    question_text = f"已知圓 $C$: ${question_circle_eq_str}$，求過圓外一點 $P({x0}, {y0})$ 的切線方程式。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def generate(level=1):
    problem_type_choices = ['on_circle', 'outside_circle']
    if level == 1:
        # Level 1 focuses on standard form and basic cases
        problem_type = random.choice(['on_circle', 'on_circle', 'outside_circle']) # More on_circle for level 1
    else:
        problem_type = random.choice(problem_type_choices)

    if problem_type == 'on_circle':
        return generate_on_circle_tangent_problem(level)
    else: # 'outside_circle'
        return generate_outside_circle_tangent_problem(level)

def check(user_answer, correct_answer):
    # Split multiple lines by semicolon, normalize each, and sort
    user_lines_raw = [line.strip() for line in user_answer.split(';') if line.strip()]
    
    normalized_user_lines = []
    for line_str in user_lines_raw:
        try:
            A, B, C_rhs = parse_line_equation(line_str)
            # Convert A, B, -C_rhs (from Ax+By=C_rhs to Ax+By-C_rhs=0, for canonical_line_equation)
            normalized_user_lines.append(canonical_line_equation(A, B, -C_rhs))
        except (ValueError, ZeroDivisionError):
            # If parsing fails or leads to invalid fractions, this line is incorrect
            continue
    
    # Correct answer is already in canonical form from generation
    correct_lines = [line.strip() for line in correct_answer.split(';')]
    
    # Sort for consistent comparison
    normalized_user_lines.sort()
    correct_lines.sort()

    is_correct = (normalized_user_lines == correct_lines)
    
    result_text = ""
    if is_correct:
        result_text = "完全正確！"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer}$"
    
    return {"correct": is_correct, "result": result_text, "next_question": True}