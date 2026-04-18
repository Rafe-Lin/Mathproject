import random
from fractions import Fraction
import math
import re

# --- Helper functions for polynomial representation and operations ---

def poly_to_string(coeffs, var='x', include_leading_plus=False):
    """
    Converts a list of polynomial coefficients to a LaTeX formatted string.
    coeffs: [c_n, c_{n-1}, ..., c_1, c_0] for c_n x^n + ... + c_0
    """
    if not coeffs or all(c == 0 for c in coeffs):
        return "0"

    parts = []
    degree = len(coeffs) - 1

    for i, coeff in enumerate(coeffs):
        if coeff == 0:
            continue

        power = degree - i
        sign_str = ""
        abs_coeff = abs(coeff)

        if coeff > 0:
            if i > 0 or include_leading_plus:
                sign_str = "+"
        else: # coeff < 0
            sign_str = "-"

        coeff_str = ""
        # Only show coefficient if not 1 or -1, or if it's the constant term (power == 0)
        if abs_coeff != 1 or power == 0:
            coeff_str = str(abs_coeff)
        
        var_str = ""
        if power == 1:
            var_str = var
        elif power > 1:
            var_str = f"{var}^{{ {power} }}"
        # if power == 0, var_str remains empty
        
        # Combine parts for the term
        if power == 0: # Constant term
            parts.append(f"{sign_str}{coeff_str}")
        elif abs_coeff == 1: # x^n or -x^n
            parts.append(f"{sign_str}{var_str}")
        else: # c*x^n
            parts.append(f"{sign_str}{coeff_str}{var_str}")
    
    # Clean up leading plus sign if it's the first term and not forced
    result = "".join(parts)
    if result.startswith('+') and not include_leading_plus:
        result = result[1:]
    
    return result

def diff_poly(coeffs):
    """
    Differentiates a polynomial represented as [c_n, c_{n-1}, ..., c_0].
    Returns coefficients of the derivative.
    e.g., [3, -2, 1] (3x^2 - 2x + 1) -> [6, -2] (6x - 2)
    """
    if len(coeffs) <= 1: # Constant or empty poly
        return [0]

    deriv_coeffs = []
    degree = len(coeffs) - 1
    for i, coeff in enumerate(coeffs[:-1]): # Exclude constant term
        power = degree - i
        deriv_coeffs.append(coeff * power)
    
    # Remove leading zeros if derivative is 0 (e.g. diff [5] -> [0])
    while len(deriv_coeffs) > 1 and deriv_coeffs[0] == 0:
        deriv_coeffs.pop(0)
    
    return deriv_coeffs

def eval_poly(coeffs, x_val):
    """
    Evaluates a polynomial at x_val.
    """
    res = 0
    degree = len(coeffs) - 1
    for i, coeff in enumerate(coeffs):
        power = degree - i
        res += coeff * (x_val ** power)
    return res

def poly_product(poly1_coeffs, poly2_coeffs):
    """
    Multiplies two polynomials.
    """
    deg1 = len(poly1_coeffs) - 1
    deg2 = len(poly2_coeffs) - 1
    result_deg = deg1 + deg2
    
    # Ensure result_coeffs has enough slots; indices match powers when poly_power is used
    # For poly_product, len(result_coeffs) = (deg1+1) + (deg2+1) - 1 = deg1+deg2+1
    result_coeffs = [0] * (result_deg + 1) 

    # Standard convolution for polynomial multiplication
    for i, c1 in enumerate(poly1_coeffs): # c1 is coeff of x^(deg1-i)
        for j, c2 in enumerate(poly2_coeffs): # c2 is coeff of x^(deg2-j)
            # The resulting power is (deg1-i) + (deg2-j)
            # In the result_coeffs array, this power corresponds to index (result_deg - ((deg1-i) + (deg2-j)))
            # This is simpler if both coeffs are stored as [c_0, c_1, ..., c_n]
            # My current convention is [c_n, c_{n-1}, ..., c_0]
            # Let's use the indices directly for simplicity for now as long as it handles the degree correctly
            
            # Simple approach assuming coeff[k] is for x^(degree-k):
            # The power of c1 is deg1 - i
            # The power of c2 is deg2 - j
            # The power of their product is (deg1 - i) + (deg2 - j)
            # The index in result_coeffs for this power is result_deg - ((deg1 - i) + (deg2 - j))
            # This can be simplified to i + j
            
            # Let's reconfirm with example: (x+1)(x+2) = x^2+3x+2
            # [1,1] * [1,2]
            # result_coeffs of size 3 for degree 2
            # i=0, c1=1 (x^1); j=0, c2=1 (x^1) -> power 2. result_coeffs[0] += 1*1 = 1
            # i=0, c1=1 (x^1); j=1, c2=2 (x^0) -> power 1. result_coeffs[1] += 1*2 = 2
            # i=1, c1=1 (x^0); j=0, c2=1 (x^1) -> power 1. result_coeffs[1] += 1*1 = 3
            # i=1, c1=1 (x^0); j=1, c2=2 (x^0) -> power 0. result_coeffs[2] += 1*2 = 2
            # Final: [1,3,2]. Correct.
            result_coeffs[i+j] += c1 * c2
            
    return result_coeffs

def poly_power(coeffs_base, n):
    """
    Calculates (base_poly)^n.
    coeffs_base: coefficients of the base polynomial.
    n: integer power.
    """
    if n == 0:
        return [1] # (anything)^0 = 1
    if n == 1:
        return coeffs_base
    
    current_coeffs = [1] # Start with 1 (as [1])
    
    for _ in range(n):
        current_coeffs = poly_product(current_coeffs, coeffs_base)
    return current_coeffs

# Ensure no empty range for random.randint
def safe_randint(a, b):
    return random.randint(min(a,b), max(a,b)) if a <= b else random.randint(b, a) # ensure a <= b

# Function to solve quadratic equation ax^2 + bx + c = 0
def solve_quadratic(a, b, c):
    if a == 0:
        if b == 0:
            return [] if c != 0 else ['all_real'] # No solution or infinite solutions
        return [-Fraction(c, b)]
    
    delta = b*b - 4*a*c
    if delta < 0:
        return [] # No real solutions
    elif delta == 0:
        return [-Fraction(b, 2*a)]
    else:
        sqrt_delta = math.isqrt(delta) # integer square root
        if sqrt_delta * sqrt_delta != delta: # Check if delta is a perfect square
            # For simplicity, only return rational roots (which means delta must be a perfect square)
            return [] 
        
        x1 = Fraction(-b + sqrt_delta, 2*a)
        x2 = Fraction(-b - sqrt_delta, 2*a)
        
        # Remove duplicates if any (e.g., if one solution is invalid due to constraints not caught by delta check)
        solutions = [x1]
        if x1 != x2:
            solutions.append(x2)
        return solutions

# --- End Helper functions ---


def generate(level=1):
    # Adjust problem distribution based on level
    problem_types_by_level = {
        1: [
            'tangent_point_on_curve', 
            'linear_approx_formula', 
            'kinematics_velocity_acceleration_simple'
        ],
        2: [
            'tangent_point_on_curve', 
            'tangent_given_slope', 
            'linear_approx_estimate', 
            'kinematics_velocity_acceleration_freefall'
        ],
        3: [
            'tangent_point_on_curve', # More complex functions
            'tangent_given_slope',    # More complex functions
            'tangent_external_point', 
            'linear_approx_estimate',
            'kinematics_velocity_acceleration_freefall' # Or more complex scenarios
        ]
    }
    
    problem_choice = random.choice(problem_types_by_level.get(level, problem_types_by_level[1]))

    if problem_choice == 'tangent_point_on_curve':
        return generate_tangent_point_on_curve(level)
    elif problem_choice == 'tangent_given_slope':
        return generate_tangent_given_slope(level)
    elif problem_choice == 'tangent_external_point':
        return generate_tangent_external_point(level)
    elif problem_choice == 'linear_approx_formula':
        return generate_linear_approx_formula(level)
    elif problem_choice == 'linear_approx_estimate':
        return generate_linear_approx_estimate(level)
    elif problem_choice == 'kinematics_velocity_acceleration_simple':
        return generate_kinematics_velocity_acceleration(level, type='simple')
    elif problem_choice == 'kinematics_velocity_acceleration_freefall':
        return generate_kinematics_velocity_acceleration(level, type='freefall')
    else:
        # Fallback for safety
        return generate_tangent_point_on_curve(1) 

def generate_tangent_point_on_curve(level):
    if level == 1:
        degree = random.randint(2, 3)
        x0 = safe_randint(-2, 2)
    elif level == 2:
        degree = random.randint(3, 4)
        x0 = safe_randint(-3, 3)
    else: # level 3
        degree = random.randint(4, 5)
        x0 = safe_randint(-3, 3)

    coeffs = [safe_randint(-5, 5) for _ in range(degree + 1)]
    while coeffs[0] == 0: # Ensure leading coeff is not zero
        coeffs[0] = safe_randint(-5, 5)
        
    f_x_str = poly_to_string(coeffs)
    y0_val = eval_poly(coeffs, x0)
    
    deriv_coeffs = diff_poly(coeffs)
    slope = eval_poly(deriv_coeffs, x0)
    
    # Tangent line equation: y - y0 = m(x - x0)
    # y = mx - mx0 + y0
    intercept_val = y0_val - slope * x0
    
    # Format for display
    x0_display = int(x0) if isinstance(x0, Fraction) and x0.denominator == 1 else x0
    y0_display = int(y0_val) if isinstance(y0_val, Fraction) and y0_val.denominator == 1 else y0_val
    slope_display = int(slope) if isinstance(slope, Fraction) and slope.denominator == 1 else slope
    intercept_display = int(intercept_val) if isinstance(intercept_val, Fraction) and intercept_val.denominator == 1 else intercept_val

    if intercept_display >= 0:
        tangent_equation = f"y = {slope_display}x + {intercept_display}"
    else:
        tangent_equation = f"y = {slope_display}x {intercept_display}"

    question_text = f"在函數 $f(x) = {f_x_str}$ 的圖形上，求以點 $P({x0_display}, {y0_display})$ 為切點的切線方程式。"
    correct_answer = tangent_equation
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_tangent_given_slope(level):
    # Use a quadratic or cubic function where f'(x) is linear or quadratic
    degree = random.randint(2, 3) if level <= 2 else random.randint(3, 4)
    coeffs = [safe_randint(-3, 3) for _ in range(degree + 1)]
    while coeffs[0] == 0 or (len(coeffs) == 2 and coeffs[0] == 0): # Ensure leading coefficient not zero, and not degree 1
        coeffs[0] = safe_randint(-3, 3)
    
    # Pick a random x-value for the tangent point to determine the slope
    x_tangent_choice = safe_randint(-2, 2)
    deriv_coeffs = diff_poly(coeffs)
    target_slope = eval_poly(deriv_coeffs, x_tangent_choice)

    f_x_str = poly_to_string(coeffs)

    question_text = f"在函數 $f(x) = {f_x_str}$ 的圖形上，已知以 $P$ 為切點的切線斜率為 ${target_slope}$，求切點 $P$ 的坐標。"

    # Solve f'(x) = target_slope
    # Adjust deriv_coeffs for the equation: deriv_coeffs_eq = deriv_coeffs - target_slope (constant term)
    eq_coeffs = list(deriv_coeffs)
    eq_coeffs[-1] = Fraction(eq_coeffs[-1]) - Fraction(target_slope) # Use Fraction to ensure precision

    solutions = []
    if len(eq_coeffs) == 1: # Constant derivative, e.g., f(x) = ax+b, f'(x) = a
        # This case should be prevented by ensuring degree >= 2
        if eq_coeffs[0] == 0: # 0 = 0 means infinite solutions, otherwise no solution
            pass # Currently, cannot generate this with valid target_slope
        else: # Non-zero constant, means no solutions if target_slope != that constant
            pass 
    elif len(eq_coeffs) == 2: # Linear equation: Ax + B' = 0
        A = eq_coeffs[0]
        B_prime = eq_coeffs[1]
        if A != 0:
            solutions.append(-B_prime / A)
    elif len(eq_coeffs) == 3: # Quadratic equation: Ax^2 + Bx + C' = 0
        A = eq_coeffs[0]
        B = eq_coeffs[1]
        C_prime = eq_coeffs[2]
        solutions = solve_quadratic(A, B, C_prime)

    points = []
    for sol_x in solutions:
        # Convert Fraction to int if it's a whole number for cleaner display
        sol_x_display = int(sol_x) if isinstance(sol_x, Fraction) and sol_x.denominator == 1 else sol_x
        y_val_calc = eval_poly(coeffs, sol_x)
        y_val_display = int(y_val_calc) if isinstance(y_val_calc, Fraction) and y_val_calc.denominator == 1 else y_val_calc
        points.append(f"({sol_x_display}, {y_val_display})")
            
    correct_answer = " 或 ".join(points) if points else "無解"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_tangent_external_point(level):
    # This is a higher-level problem (Level 3 specific).
    # Use a quadratic function for f(x) = ax^2 + bx + c
    a_coeff = random.choice([1, -1, 2, -2]) # for x^2
    b_coeff = safe_randint(-3, 3) # for x
    c_coeff = safe_randint(-5, 5) # constant
    
    f_coeffs = [a_coeff, b_coeff, c_coeff] # f(x) = ax^2 + bx + c
    f_x_str = poly_to_string(f_coeffs)
    
    # Generate an external point P(xp, yp) that ensures integer tangent point x-coordinates
    # We choose two integer tangent x-coordinates (a_1, a_2) and work backward to find P.
    tangent_x1 = safe_randint(-2, 2)
    tangent_x2 = safe_randint(-3, 3)
    while tangent_x1 == tangent_x2: 
        tangent_x2 = safe_randint(-3, 3)

    # Let the quadratic equation for 'a' (tangency x-coord) be (a - tangent_x1)(a - tangent_x2) = 0
    # i.e., a^2 - (tangent_x1 + tangent_x2)a + (tangent_x1 * tangent_x2) = 0
    # From setting slopes equal: f'(a) = (f(a) - yp) / (a - xp)
    # (2*a_coeff*a + b_coeff)(a - xp) = a_coeff*a^2 + b_coeff*a + c_coeff - yp
    # This simplifies to: a_coeff*a^2 + (2*a_coeff*xp - b_coeff)a + (b_coeff*xp - c_coeff + yp) = 0
    # Note: the example has (c_coeff - b_coeff*xp - yp) for the constant term. My re-arrangement.
    # We multiply by a_coeff to match leading coefficient:
    # a_coeff * [a^2 - (tangent_x1 + tangent_x2)a + (tangent_x1 * tangent_x2)] = 0
    # So,
    # 2*a_coeff*xp - b_coeff = -a_coeff * (tangent_x1 + tangent_x2)
    # b_coeff*xp - c_coeff + yp = a_coeff * (tangent_x1 * tangent_x2)

    # Solve for xp:
    # 2*a_coeff*xp = b_coeff - a_coeff * (tangent_x1 + tangent_x2)
    xp_numerator = b_coeff - a_coeff * (tangent_x1 + tangent_x2)
    xp_denominator = 2 * a_coeff
    
    # Ensure xp is an integer for cleaner problems
    if xp_numerator % xp_denominator != 0:
        return generate_tangent_external_point(level) # Recurse if not integer
    
    xp = xp_numerator // xp_denominator

    # Solve for yp:
    # yp = a_coeff * (tangent_x1 * tangent_x2) - b_coeff*xp + c_coeff
    yp = a_coeff * (tangent_x1 * tangent_x2) - b_coeff * xp + c_coeff
    
    # Check if P(xp, yp) is actually external to the curve
    if eval_poly(f_coeffs, xp) == yp:
        # P is on the curve, not external. Regenerate.
        return generate_tangent_external_point(level)

    question_text = f"已知 $P({xp}, {yp})$ 為二次函數 $f(x) = {f_x_str}$ 圖形外一點，求過 $P$ 點的切線方程式。"
    
    tangent_x_values = [tangent_x1, tangent_x2]
    
    answers = []
    for a_val in tangent_x_values:
        # Calculate slope m = f'(a_val)
        f_prime_coeffs = diff_poly(f_coeffs) # 2ax + b
        m = eval_poly(f_prime_coeffs, a_val)
        
        # Equation: y - yp = m(x - xp)
        # y = m*x - m*xp + yp
        
        line_intercept = m * (-xp) + yp
        
        m_display = int(m) if isinstance(m, Fraction) and m.denominator == 1 else m
        line_intercept_display = int(line_intercept) if isinstance(line_intercept, Fraction) and line_intercept.denominator == 1 else line_intercept

        if line_intercept_display >= 0:
            equation_str = f"y = {m_display}x + {line_intercept_display}"
        else:
            equation_str = f"y = {m_display}x {line_intercept_display}"
        answers.append(equation_str)
        
    correct_answer = " 與 ".join(sorted(answers)) # Sort to ensure consistent answer for checking

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_linear_approx_formula(level):
    # f(x) approx f(a) + f'(a)(x-a)
    degree = random.randint(2, 3) if level == 1 else random.randint(3, 4)
    coeffs = [safe_randint(-5, 5) for _ in range(degree + 1)]
    while coeffs[0] == 0:
        coeffs[0] = safe_randint(-5, 5)

    a_val = safe_randint(-2, 2)
    
    f_x_str = poly_to_string(coeffs)
    
    f_a = eval_poly(coeffs, a_val)
    
    deriv_coeffs = diff_poly(coeffs)
    f_prime_a = eval_poly(deriv_coeffs, a_val)
    
    # Linear approximation formula: L(x) = f(a) + f'(a)(x-a)
    # L(x) = f_prime_a * x + (f_a - f_prime_a * a_val)
    
    intercept = f_a - f_prime_a * a_val
    
    f_prime_a_display = int(f_prime_a) if isinstance(f_prime_a, Fraction) and f_prime_a.denominator == 1 else f_prime_a
    intercept_display = int(intercept) if isinstance(intercept, Fraction) and intercept.denominator == 1 else intercept

    if intercept_display >= 0:
        approx_str = f"{f_prime_a_display}x + {intercept_display}"
    else:
        approx_str = f"{f_prime_a_display}x {intercept_display}"
        
    question_text = f"設函數 $f(x) = {f_x_str}$，求函數 $f(x)$ 在 $x={a_val}$ 附近的一次估計。"
    correct_answer = approx_str

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_linear_approx_estimate(level):
    if level <= 2:
        # General polynomial approximation
        degree = random.randint(2, 3)
        coeffs = [safe_randint(-5, 5) for _ in range(degree + 1)]
        while coeffs[0] == 0:
            coeffs[0] = safe_randint(-5, 5)

        a_val = safe_randint(-2, 2)
        delta_x_exponent = random.choice([-2, -3]) # 0.01 or 0.001
        delta_x = 10**delta_x_exponent
        
        x_target = a_val + delta_x
        
        f_x_str = poly_to_string(coeffs)
        
        f_a = eval_poly(coeffs, a_val)
        deriv_coeffs = diff_poly(coeffs)
        f_prime_a = eval_poly(deriv_coeffs, a_val)
        
        # L(x_target) = f(a) + f'(a)(x_target - a) = f(a) + f'(a) * delta_x
        approx_value = f_a + f_prime_a * delta_x
        
        question_text = f"設函數 $f(x) = {f_x_str}$。使用 $f(x)$ 在 $x={a_val}$ 附近的一次估計，求 $f({x_target})$ 的近似值。"
        
        # Format to appropriate decimal places, accounting for delta_x precision
        correct_answer = f"{approx_value:.{abs(delta_x_exponent * 2)}f}" 
        
    else: # level 3 - specifically (1+x)^n approx 1+nx
        n_val = random.randint(3, 5)
        x_exponent = random.choice([-3, -4])
        x_small = 10**x_exponent
        
        # f(x) = (1+x)^n
        # Approximation: f(x) approx 1 + n*x (around x=0)
        
        approx_value = 1 + n_val * x_small
        
        question_text = f"利用一次估計公式，求 $(1+{x_small})^{n_val}$ 的近似值。"
        
        # Format for precision, e.g., for 10^-4, need at least 5 decimal places.
        correct_answer = f"{approx_value:.{abs(x_exponent) + 2}f}" 
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_kinematics_velocity_acceleration(level, type='simple'):
    if type == 'simple':
        # s(t) = At^2 + Bt + C
        A_val = random.choice([1, 2, 3, 4.9]) # gravitational constant related
        B_val = safe_randint(1, 10)
        C_val = safe_randint(0, 10) # initial position
        
        s_coeffs = [A_val, B_val, C_val] # For At^2 + Bt + C
        t0 = safe_randint(1, 3) # specific time
        
        s_t_str = poly_to_string(s_coeffs, var='t')
        
        v_coeffs = diff_poly(s_coeffs)
        a_coeffs = diff_poly(v_coeffs)
        
        v_t0 = eval_poly(v_coeffs, t0)
        a_t0 = eval_poly(a_coeffs, t0)
        
        v_t0_display = float(v_t0) if isinstance(v_t0, Fraction) else v_t0
        a_t0_display = float(a_t0) if isinstance(a_t0, Fraction) else a_t0

        question_text = (
            f"已知一物體移動的距離函數為 $s(t) = {s_t_str}$（公尺），"
            f"求該物體在 $t={t0}$ 秒時的瞬時速度及瞬時加速度。"
        )
        correct_answer = (
            f"瞬時速度為 {v_t0_display} 公尺/秒，瞬時加速度為 {a_t0_display} 公尺/秒^2"
        )
        
    elif type == 'freefall': # level 2 and 3
        g_val = 9.8 # m/s^2
        
        # To get an integer time for landing, choose t_ground_int first
        t_ground_int = safe_randint(2, 5) 
        # Calculate initial height based on s(t) = 0.5 * g * t^2 being distance fallen
        height_initial = Fraction(g_val, 2) * (t_ground_int**2) 
            
        s_t_str = poly_to_string([Fraction(g_val, 2), 0, 0], var='t') # For 4.9t^2 or 0.5*g*t^2
        
        v_coeffs = diff_poly([Fraction(g_val, 2), 0, 0]) # derivative of 0.5*g*t^2 is g*t
        a_coeffs = diff_poly(v_coeffs) # derivative of g*t is g
        
        v_at_ground = eval_poly(v_coeffs, t_ground_int)
        a_at_ground = eval_poly(a_coeffs, t_ground_int)

        v_at_ground_display = float(v_at_ground) if isinstance(v_at_ground, Fraction) else v_at_ground
        a_at_ground_display = float(a_at_ground) if isinstance(a_at_ground, Fraction) else a_at_ground
        height_initial_display = float(height_initial) if isinstance(height_initial, Fraction) else height_initial

        question_text = (
            f"已知一物體從 ${height_initial_display}$ 公尺的高處自由落下，"
            f"經過 $t$ 秒後落下的距離為 $s(t) = {s_t_str}$（公尺）。<br>"
            f"(1) 該物體著地時的秒數為______秒。<br>"
            f"(2) 求該物體著地時的瞬時速度及瞬時加速度。"
        )
        
        correct_answer = (
            f"(1) {t_ground_int}<br>"
            f"(2) 瞬時速度為 {v_at_ground_display} 公尺/秒，瞬時加速度為 {a_at_ground_display} 公尺/秒^2"
        )
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    考慮多種答案格式，例如浮點數比較、分數比較、或字符串精確匹配。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()

    is_correct = False
    result_text = ""

    # Try exact string match first
    if user_answer == correct_answer:
        is_correct = True
    else:
        # Specific handling for kinematics multipart answer
        if "瞬時速度為" in correct_answer and "瞬時加速度為" in correct_answer:
            is_correct = _check_kinematics_answer(user_answer, correct_answer)
        # For tangent line equations or linear approximation formulas
        elif 'y =' in user_answer or 'y=' in user_answer:
            is_correct = _check_equation_answer(user_answer, correct_answer)
        # For point coordinates (a, b) or (a, b) 或 (c, d)
        elif user_answer.startswith('(') and user_answer.endswith(')'):
            is_correct = _check_coordinates_answer(user_answer, correct_answer)
        else: # For simple numerical answers, try converting to float and comparing
            try:
                user_num = float(user_answer)
                correct_num = float(correct_answer)
                if abs(user_num - correct_num) < 1e-6: # Tolerance for float comparison
                    is_correct = True
            except ValueError:
                pass # Not a simple float, parsing failed

    if is_correct:
        result_text = f"完全正確！答案是 ${correct_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer}$"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}

def _check_kinematics_answer(user_answer, correct_answer):
    correct_parts = correct_answer.split("<br>")
    user_parts = user_answer.split("<br>")

    # Attempt to parse both user and correct answers into structured data
    parsed_correct = _parse_kinematics_answer_string(correct_parts)
    parsed_user = _parse_kinematics_answer_string(user_parts)

    if parsed_correct is None or parsed_user is None:
        return False # Parsing failed for either

    # Compare part (1) time
    if parsed_correct['time'] is not None and parsed_user['time'] is not None:
        if parsed_user['time'] != parsed_correct['time']:
            return False
    elif parsed_correct['time'] is not None and parsed_user['time'] is None:
        # If correct answer has time, but user didn't provide it, check if user provided it implicitly
        try:
            user_time = int(user_answer.strip())
            if user_time == parsed_correct['time']:
                parsed_user['time'] = user_time # Assume user just gave the time for part 1
            else:
                return False
        except ValueError:
            return False # User did not provide valid time

    # Compare part (2) velocity and acceleration
    if parsed_correct['velocity'] is not None and parsed_user['velocity'] is not None and \
       parsed_correct['acceleration'] is not None and parsed_user['acceleration'] is not None:
        
        v_match = abs(float(parsed_user['velocity']) - float(parsed_correct['velocity'])) < 1e-6
        a_match = abs(float(parsed_user['acceleration']) - float(parsed_correct['acceleration'])) < 1e-6
        if not (v_match and a_match):
            return False
    elif parsed_correct['velocity'] is not None and parsed_user['velocity'] is None:
        # Correct answer has velocity/acceleration, but user's parsed answer doesn't
        # This implies user's input might not have been fully structured for part 2
        # Try to parse user_answer as just the velocity/acceleration string
        try:
            user_v_str = user_answer.split("瞬時速度為")[1].split("公尺/秒")[0].strip()
            user_a_str = user_answer.split("瞬時加速度為")[1].split("公尺/秒^2")[0].strip()
            
            user_v = float(user_v_str)
            user_a = float(user_a_str)
            
            v_match = abs(user_v - float(parsed_correct['velocity'])) < 1e-6
            a_match = abs(user_a - float(parsed_correct['acceleration'])) < 1e-6
            if not (v_match and a_match):
                return False
        except (ValueError, IndexError):
            return False

    return True # All checked parts match

def _parse_kinematics_answer_string(parts):
    # Helper to extract numbers from kinematics answer strings
    result = {'time': None, 'velocity': None, 'acceleration': None}
    
    for part in parts:
        part = part.strip()
        if part.startswith("(1)"):
            try:
                result['time'] = int(part.replace("(1)", "").strip())
            except ValueError:
                pass
        elif part.startswith("(2)") or "瞬時速度為" in part:
            try:
                v_str_start_idx = part.find("瞬時速度為") + len("瞬時速度為")
                v_str_end_idx = part.find("公尺/秒")
                v_str = part[v_str_start_idx:v_str_end_idx].strip()
                result['velocity'] = float(v_str)

                a_str_start_idx = part.find("瞬時加速度為") + len("瞬時加速度為")
                a_str_end_idx = part.find("公尺/秒^2")
                a_str = part[a_str_start_idx:a_str_end_idx].strip()
                result['acceleration'] = float(a_str)
            except (ValueError, IndexError):
                pass
    return result

def _check_equation_answer(user_answer, correct_answer):
    user_normalized = _normalize_equation_string(user_answer)
    correct_normalized = _normalize_equation_string(correct_answer)
    
    # Check for multiple solutions
    if isinstance(correct_normalized, list):
        if isinstance(user_normalized, list):
            return sorted(user_normalized) == sorted(correct_normalized)
        else: # User provided single equation
            return user_normalized in correct_normalized
    else: # Single solution
        return user_normalized == correct_normalized

def _normalize_equation_string(equation_str):
    """Normalizes tangent line equations for comparison."""
    # Example: "y = 5x - 11" or "y = -11 + 5x" -> (5, -11)
    # Handles multiple equations separated by " 或 " or " 與 "
    
    # If multiple equations, process each
    if " 或 " in equation_str or " 與 " in equation_str:
        parts = re.split(r'\s*或\s*|\s*與\s*', equation_str)
        return [_normalize_single_equation(p) for p in parts]
    else:
        return _normalize_single_equation(equation_str)

def _normalize_single_equation(equation_str):
    """Normalizes a single equation of the form y = mx + c to a tuple (m, c)."""
    eq = equation_str.replace(" ", "").replace("=", "").replace("y", "")
    
    m = 0
    c = 0
    
    # Regex to find coefficient of x and the x term itself
    match_mx = re.search(r'([+-]?\d*(?:\.\d+)?(?:/\d+)?)x', eq) 
    if match_mx:
        coeff_str = match_mx.group(1)
        if coeff_str == '': # 'x'
            m = 1
        elif coeff_str == '+': # '+x'
            m = 1
        elif coeff_str == '-': # '-x'
            m = -1
        else:
            m = float(Fraction(coeff_str)) # Handles fractions like "1/2"
        eq = eq.replace(match_mx.group(0), '') # Remove 'mx' part

    # Remaining part should be the constant 'c'
    if eq:
        try:
            c = float(Fraction(eq)) # Handles fractions for the constant
        except ValueError:
            pass # No constant or unparseable
    
    return (m, c)

def _check_coordinates_answer(user_answer, correct_answer):
    def parse_coords_string(s):
        points = []
        parts = re.split(r'\s*或\s*|\s*與\s*', s)
        for part in parts:
            try:
                clean_part = part.strip().replace('(', '').replace(')', '')
                x, y = map(lambda val: float(Fraction(val)), clean_part.split(','))
                points.append((x, y))
            except (ValueError, IndexError):
                return None # Parsing failed
        return sorted(points) # Sort points for consistent comparison
    
    user_coords = parse_coords_string(user_answer)
    correct_coords = parse_coords_string(correct_answer)

    if user_coords is None or correct_coords is None or len(user_coords) != len(correct_coords):
        return False
    
    for uc, cc in zip(user_coords, correct_coords):
        if not (abs(uc[0] - cc[0]) < 1e-6 and abs(uc[1] - cc[1]) < 1e-6):
            return False
    return True