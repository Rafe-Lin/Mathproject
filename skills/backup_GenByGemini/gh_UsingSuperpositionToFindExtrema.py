import random
import math
from fractions import Fraction

# --- Helper for LaTeX Formatting ---
def _format_coeff(coeff):
    """
    Formats a coefficient (int, float, Fraction, or tuple for sqrt) into a LaTeX string.
    Handles integers, simple fractions, and square roots like sqrt(N) or k*sqrt(N).
    """
    if isinstance(coeff, int):
        return str(coeff)
    elif isinstance(coeff, Fraction):
        if coeff.denominator == 1:
            return str(coeff.numerator)
        return r"\\frac{{{}}}{{{}}}".format(coeff.numerator, coeff.denominator)
    elif isinstance(coeff, tuple) and coeff[0] == 'sqrt':
        if coeff[1] == 1: # sqrt(1) is just 1
            return "1"
        return r"\\sqrt{{{}}}".format(coeff[1])
    elif isinstance(coeff, float):
        # Check if it's an integer after rounding
        if abs(coeff - round(coeff)) < 1e-9:
            return str(int(round(coeff)))
        # Check for sqrt(N) pattern
        for i in range(2, 11): # Check for sqrt(2) to sqrt(10)
            if abs(coeff - math.sqrt(i)) < 1e-9:
                return r"\\sqrt{{{}}}".format(i)
            if abs(coeff - (-math.sqrt(i))) < 1e-9:
                return r"-\\sqrt{{{}}}".format(i)
        # Check for k*sqrt(N) pattern for small k and N
        for k_val in [-3, -2, -1, 1, 2, 3]:
            for n_val in [2, 3]: # Only common sqrt(2), sqrt(3)
                if abs(coeff - k_val * math.sqrt(n_val)) < 1e-9:
                    if k_val == 1:
                        return r"\\sqrt{{{}}}".format(n_val)
                    elif k_val == -1:
                        return r"-\\sqrt{{{}}}".format(n_val)
                    return r"{}\\sqrt{{{}}}".format(k_val, n_val)
        return str(round(coeff, 5)) # Fallback for other floats
    return str(coeff)

def _format_coeff_with_sign(coeff):
    """
    Formats a coefficient into a LaTeX string, including a '+' sign if positive.
    """
    if isinstance(coeff, int):
        if coeff < 0: return str(coeff)
        return "+" + str(coeff)
    elif isinstance(coeff, Fraction):
        if coeff.denominator == 1:
            if coeff.numerator < 0: return str(coeff.numerator)
            return "+" + str(coeff.numerator)
        if coeff < 0:
            return r"-\\frac{{{}}}{{{}}}".format(abs(coeff.numerator), coeff.denominator)
        return r"+\\frac{{{}}}{{{}}}".format(coeff.numerator, coeff.denominator)
    elif isinstance(coeff, tuple) and coeff[0] == 'sqrt':
        if coeff[1] == 1: return "+1"
        return r"+\\sqrt{{{}}}".format(coeff[1])
    elif isinstance(coeff, float):
        if abs(coeff - round(coeff)) < 1e-9: # integer check
            return _format_coeff_with_sign(int(round(coeff)))
        # Check for sqrt(N) pattern
        for i in range(2, 11):
            if abs(coeff - math.sqrt(i)) < 1e-9:
                return r"+\\sqrt{{{}}}".format(i)
            if abs(coeff - (-math.sqrt(i))) < 1e-9:
                return r"-\\sqrt{{{}}}".format(i)
        # Check for k*sqrt(N) pattern
        for k_val in [-3, -2, -1, 1, 2, 3]:
            for n_val in [2, 3]:
                if abs(coeff - k_val * math.sqrt(n_val)) < 1e-9:
                    if k_val == 1: return r"+\\sqrt{{{}}}".format(n_val)
                    if k_val == -1: return r"-\\sqrt{{{}}}".format(n_val)
                    if k_val > 0: return r"+{}\\sqrt{{{}}}".format(k_val, n_val)
                    return r"{}\\sqrt{{{}}}".format(k_val, n_val)
        if coeff < 0:
            return str(round(coeff, 5))
        return "+" + str(round(coeff, 5))
    return str(coeff)

def _get_r_theta_info(a, b):
    """
    Calculates r and theta for a sinx + b cosx = r sin(x + theta).
    Returns (r_val, theta_rad, r_str, theta_str) in LaTeX format.
    """
    a = float(a)
    b = float(b)
    r_val = math.sqrt(a**2 + b**2)
    
    r_str = _format_coeff(r_val)

    theta_rad = math.atan2(b, a) # atan2 gives angle in [-pi, pi]

    # Try to represent theta as a fraction of pi (0, pi/6, pi/4, pi/3, etc.)
    fractions_of_pi = [
        (0, 1), (1, 6), (1, 4), (1, 3), (1, 2), (2, 3), (3, 4), (5, 6), (1, 1),
        (7, 6), (5, 4), (4, 3), (3, 2), (5, 3), (7, 4), (11, 6)
    ]
    
    theta_str = None
    for num, den in fractions_of_pi:
        val = num * math.pi / den
        # Check positive and negative representations for atan2 output
        if abs(theta_rad - val) < 1e-9:
            if num == 0: theta_str = "0"
            elif num == 1 and den == 1: theta_str = r"\\pi"
            elif num == 1: theta_str = r"\\frac{{\\pi}}{{{}}}".format(den)
            else: theta_str = r"\\frac{{{}\\pi}}{{{}}}".format(num, den)
            break
        elif abs(theta_rad - (val - 2*math.pi)) < 1e-9 and (val - 2*math.pi) >= -math.pi: # For negative atan2 outputs that might be like -pi/3 instead of 5pi/3
             if num == 0: theta_str = "0"
             elif num == 1 and den == 1: theta_str = r"-\\pi"
             elif num == 1: theta_str = r"-\\frac{{\\pi}}{{{}}}".format(den)
             else: theta_str = r"-\\frac{{{}\\pi}}{{{}}}".format(num, den)
             break

    if theta_str is None:
        # Fallback if not a simple fraction of pi (should ideally not happen for generated problems)
        theta_str = r"\\theta_0" # Generic symbol

    return r_val, theta_rad, r_str, theta_str

def _format_rad_to_pi_str(rad_val):
    """
    Formats a radian value into a LaTeX string as a fraction of pi.
    Normalizes to [0, 2pi).
    """
    rad_val = rad_val % (2 * math.pi)
    if rad_val < 0: rad_val += 2 * math.pi

    fractions_of_pi = [
        (0, 1), (1, 6), (1, 4), (1, 3), (1, 2), (2, 3), (3, 4), (5, 6), (1, 1),
        (7, 6), (5, 4), (4, 3), (3, 2), (5, 3), (7, 4), (11, 6)
    ]
    
    for num, den in fractions_of_pi:
        val = num * math.pi / den
        if abs(rad_val - val) < 1e-9:
            if num == 0: return "0"
            if num == 1 and den == 1: return r"\\pi"
            if num == 1: return r"\\frac{{\\pi}}{{{}}}".format(den)
            return r"\\frac{{{}\\pi}}{{{}}}".format(num, den)
    return str(round(rad_val, 5)) # Fallback if not a common angle

# --- Problem Generation Functions ---

def generate_basic_extrema_problem():
    """Generates a problem of type y = a sinx + b cosx (find max/min)."""
    
    coeff_pairs = [
        (1, 1), (1, -1), (-1, 1), (-1, -1), # r = sqrt(2)
        (1, math.sqrt(3)), (math.sqrt(3), 1), 
        (1, -math.sqrt(3)), (-math.sqrt(3), 1),
        (math.sqrt(3), -1), (-1, math.sqrt(3)), # r = 2
        (3, 4), (4, 3), (3, -4), (-4, 3), # r = 5
        (5, 12), (12, 5), (-5, 12), (12, -5), # r = 13
        (2, 0), (0, 2), (-2, 0), (0, -2) # r = 2
    ]
    a, b = random.choice(coeff_pairs)

    r_val, _, _, _ = _get_r_theta_info(a, b)

    a_formatted = _format_coeff(a)
    b_formatted = _format_coeff_with_sign(b) # Will be like "+2" or "-3"

    # Construct the question text, handling a=0 or b=0 cases
    if a == 0:
        question_text = f"求函數 $y = {b_formatted} \\cos x$ 的最大值與最小值。"
    elif b == 0:
        question_text = f"求函數 $y = {a_formatted} \\sin x$ 的最大值與最小值。"
    else:
        question_text = f"求函數 $y = {a_formatted} \\sin x {b_formatted} \\cos x$ 的最大值與最小值。"

    max_ans = _format_coeff(r_val)
    min_ans = _format_coeff(-r_val)
    
    correct_answer = f"最大值為 ${max_ans}$，最小值為 ${min_ans}$。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_shifted_extrema_problem():
    """Generates a problem of type y = a sinx + b cosx + c (find max/min)."""
    
    coeff_pairs = [
        (1, 1), (-1, 1), (1, -1), # r = sqrt(2)
        (1, math.sqrt(3)), (math.sqrt(3), 1), 
        (1, -math.sqrt(3)), (-math.sqrt(3), 1),
        (3, 4), (4, 3), (-3, 4), # r = 5
        (2, 0), (0, 2) # r = 2
    ]
    a, b = random.choice(coeff_pairs)
    c = random.randint(-5, 5)
    while c == 0: # Ensure c is not zero for a "shifted" problem
        c = random.randint(-5, 5)

    r_val, _, _, _ = _get_r_theta_info(a, b)

    a_formatted = _format_coeff(a)
    b_formatted = _format_coeff_with_sign(b)
    c_formatted = _format_coeff_with_sign(c)

    if a == 0:
        question_text = f"求函數 $y = {b_formatted} \\cos x {c_formatted}$ 的最大值與最小值。"
    elif b == 0:
        question_text = f"求函數 $y = {a_formatted} \\sin x {c_formatted}$ 的最大值與最小值。"
    else:
        question_text = f"求函數 $y = {a_formatted} \\sin x {b_formatted} \\cos x {c_formatted}$ 的最大值與最小值。"
    
    max_ans = _format_coeff(r_val + c)
    min_ans = _format_coeff(-r_val + c)

    correct_answer = f"最大值為 ${max_ans}$，最小值為 ${min_ans}$。"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_expanded_extrema_problem():
    """
    Generates a problem of type y = A sin(alpha - x) + B cosx + C
    which requires expansion before superposition, guaranteeing a 'nice' r.
    """
    # Choose A, B, alpha and C. Then compute the expanded a, b.
    A = random.choice([-3, -2, -1, 1, 2, 3])
    B = random.choice([-3, -2, -1, 1, 2, 3])
    
    alpha_options_rad = [math.pi/6, math.pi/4, math.pi/3]
    alpha = random.choice(alpha_options_rad)
    alpha_str = _format_rad_to_pi_str(alpha)
    
    C = random.randint(-5, 5)

    # Expanded form: y = (-A cos(alpha))sinx + (A sin(alpha) + B)cosx + C
    a_expanded = -A * math.cos(alpha)
    b_expanded = A * math.sin(alpha) + B
    
    A_formatted = _format_coeff(A)
    B_formatted = _format_coeff_with_sign(B)
    C_formatted = _format_coeff_with_sign(C) if C != 0 else ""

    # Construct the question text
    if B == 0:
        # Simplifies to -A cos(alpha) sinx + A sin(alpha) cosx + C
        question_text = f"求函數 $y = {A_formatted} \\sin({alpha_str} - x) {C_formatted}$ 的最大值與最小值。"
    else:
        question_text = f"求函數 $y = {A_formatted} \\sin({alpha_str} - x) {B_formatted} \\cos x {C_formatted}$ 的最大值與最小值。"

    # Calculate final r_val and min/max
    r_val, _, _, _ = _get_r_theta_info(a_expanded, b_expanded)
    
    max_ans = _format_coeff(r_val + C)
    min_ans = _format_coeff(-r_val + C)

    correct_answer = f"最大值為 ${max_ans}$，最小值為 ${min_ans}$。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def generate_interval_extrema_problem():
    """
    Generates a problem of type y = a sinx + b cosx + c within [x_start, x_end]
    (find max/min and corresponding x values).
    """
    
    coeff_pairs = [
        (1, 1), (-1, 1), (1, -1), # r = sqrt(2)
        (1, math.sqrt(3)), (math.sqrt(3), 1), 
        (1, -math.sqrt(3)), (-math.sqrt(3), 1),
        (3, 4), (-3, 4) # r=5
    ]
    a, b = random.choice(coeff_pairs)
    c = random.randint(-3, 3)
    
    r_val, theta_rad, _, _ = _get_r_theta_info(a, b)
    
    # Choose interval: (0 <= x < 2pi) or (0 <= x <= pi/2)
    interval_type = random.choice(['full', 'quadrant'])

    x_start_rad = 0
    x_start_str = "0"
    
    if interval_type == 'full':
        x_end_rad = 2 * math.pi
        x_end_str = r"2\\pi"
        interval_str = r"$0 \\le x < 2\\pi$"
    else: # quadrant
        x_end_rad = math.pi / 2
        x_end_str = r"\\frac{{\\pi}}{2}"
        interval_str = r"$0 \\le x \\le \\frac{{\\pi}}{2}$"

    # Let z = x + theta. The range for z is [x_start_rad + theta_rad, x_end_rad + theta_rad].
    z_start = x_start_rad + theta_rad
    z_end = x_end_rad + theta_rad
    
    # Determine the max/min values of sin(z) within the interval [z_start, z_end]
    sin_z_at_start = math.sin(z_start)
    sin_z_at_end = math.sin(z_end)
    
    max_sin_z = max(sin_z_at_start, sin_z_at_end)
    min_sin_z = min(sin_z_at_start, sin_z_at_end)

    # Check for sin(z)=1 (at pi/2 + 2k*pi) and sin(z)=-1 (at 3pi/2 + 2k*pi) within [z_start, z_end]
    for k in range(-2, 3): # Check across a few cycles
        critical_z_plus1 = math.pi / 2 + 2 * k * math.pi
        critical_z_minus1 = 3 * math.pi / 2 + 2 * k * math.pi

        if z_start <= critical_z_plus1 <= z_end + 1e-9: # Add tolerance for float comparison
            max_sin_z = 1.0
        if z_start <= critical_z_minus1 <= z_end + 1e-9:
            min_sin_z = -1.0
    
    # Calculate max/min y values
    max_y_actual = r_val * max_sin_z + c
    min_y_actual = r_val * min_sin_z + c

    # Find x values corresponding to max/min y values
    x_for_max = []
    x_for_min = []

    # Target sin(z) values
    target_sin_max = (max_y_actual - c) / r_val
    target_sin_min = (min_y_actual - c) / r_val

    # Find z values that yield target_sin_max/min
    for k in range(-2, 3): # Iterate through cycles
        # Solutions for sin(z) = value are alpha_prime + 2k*pi and pi - alpha_prime + 2k*pi

        # For max y
        # Check for values that result in max_sin_z
        if abs(target_sin_max) <= 1: # Ensure target_sin_max is in valid range [-1, 1]
            alpha_prime_max = math.asin(target_sin_max)
            z_cand1_max = alpha_prime_max + 2 * k * math.pi
            z_cand2_max = math.pi - alpha_prime_max + 2 * k * math.pi
            
            for z_val in [z_cand1_max, z_cand2_max]:
                if z_start - 1e-9 <= z_val <= z_end + 1e-9: # Check if z is in range
                    x_cand = z_val - theta_rad
                    # Normalize x_cand to [0, 2pi) and check against original x interval
                    x_cand_norm = x_cand % (2 * math.pi)
                    if x_cand_norm < 0: x_cand_norm += 2 * math.pi
                    
                    if x_start_rad - 1e-9 <= x_cand_norm <= x_end_rad + 1e-9:
                        x_for_max.append(x_cand_norm)

        # For min y
        # Check for values that result in min_sin_z
        if abs(target_sin_min) <= 1:
            alpha_prime_min = math.asin(target_sin_min)
            z_cand1_min = alpha_prime_min + 2 * k * math.pi
            z_cand2_min = math.pi - alpha_prime_min + 2 * k * math.pi

            for z_val in [z_cand1_min, z_cand2_min]:
                if z_start - 1e-9 <= z_val <= z_end + 1e-9: # Check if z is in range
                    x_cand = z_val - theta_rad
                    x_cand_norm = x_cand % (2 * math.pi)
                    if x_cand_norm < 0: x_cand_norm += 2 * math.pi
                    
                    if x_start_rad - 1e-9 <= x_cand_norm <= x_end_rad + 1e-9:
                        x_for_min.append(x_cand_norm)
    
    # Remove duplicates and format x values to pi fractions, then sort
    formatted_x_for_max = sorted(list(set([_format_rad_to_pi_str(x) for x in x_for_max])))
    formatted_x_for_min = sorted(list(set([_format_rad_to_pi_str(x) for x in x_for_min])))

    # Final string construction
    a_formatted = _format_coeff(a)
    b_formatted = _format_coeff_with_sign(b)
    c_formatted = _format_coeff_with_sign(c) if c != 0 else ""

    if a == 0:
        func_text = f"$y = {b_formatted} \\cos x {c_formatted}$"
    elif b == 0:
        func_text = f"$y = {a_formatted} \\sin x {c_formatted}$"
    else:
        func_text = f"$y = {a_formatted} \\sin x {b_formatted} \\cos x {c_formatted}$"

    question_text = f"在範圍 {interval_str} 內，求函數 {func_text} 的最大值與最小值，並求其對應的 $x$ 值。"
    
    max_val_str = _format_coeff(max_y_actual)
    min_val_str = _format_coeff(min_y_actual)

    max_ans_text = f"最大值為 ${max_val_str}$ (發生在 $x = {{{', '.join(formatted_x_for_max)}}}$ 時)" if formatted_x_for_max else f"最大值為 ${max_val_str}$"
    min_ans_text = f"最小值為 ${min_val_str}$ (發生在 $x = {{{', '.join(formatted_x_for_min)}}}$ 時)" if formatted_x_for_min else f"最小值為 ${min_val_str}$"
    
    correct_answer = f"{max_ans_text}，{min_ans_text}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def generate_equation_solving_problem():
    """
    Generates a problem of type a sinx + b cosx = k in [0, 2pi) (find x values).
    """
    
    coeff_pairs = [
        (1, 1), (1, -1), # r = sqrt(2)
        (1, math.sqrt(3)), (math.sqrt(3), 1), # r = 2
        (1, -math.sqrt(3)), (-math.sqrt(3), 1),
        (3, 4), (-3, 4) # r=5
    ]
    a, b = random.choice(coeff_pairs)
    
    r_val, theta_rad, _, _ = _get_r_theta_info(a, b)
    
    # Choose k such that k/r_val is a common sin value (1, 1/2, sqrt(2)/2, sqrt(3)/2, 0, -1/2, ...)
    common_sin_vals = [0, 0.5, math.sqrt(2)/2, math.sqrt(3)/2, 1, -0.5, -math.sqrt(2)/2, -math.sqrt(3)/2, -1]
    
    target_sin_z = random.choice(common_sin_vals)
    k = target_sin_z * r_val
    
    # Try to make k an integer or simple sqrt multiple for cleaner display
    if abs(k - round(k)) < 1e-9:
        k = int(round(k))
    elif abs(k/math.sqrt(2) - round(k/math.sqrt(2))) < 1e-9:
        k = round(k/math.sqrt(2)) * math.sqrt(2)
    elif abs(k/math.sqrt(3) - round(k/math.sqrt(3))) < 1e-9:
        k = round(k/math.sqrt(3)) * math.sqrt(3)
    
    k_formatted = _format_coeff(k)

    # Solve sin(x + theta) = target_sin_z, where z = x + theta
    # Interval for x is [0, 2pi), so interval for z is [theta_rad, 2pi + theta_rad)
    
    solutions_z = []
    
    # Primary angle for sin(alpha_prime) = target_sin_z
    if abs(target_sin_z) > 1: # No solution if k/r > 1
        formatted_solutions = []
    else:
        alpha_prime = math.asin(target_sin_z)

        # Generate solutions across a few cycles to cover the z interval
        for k_cycle in range(-1, 2): 
            z_cand1 = alpha_prime + 2 * k_cycle * math.pi
            z_cand2 = math.pi - alpha_prime + 2 * k_cycle * math.pi
            
            # Check if z_cand1 is in [theta_rad, 2pi + theta_rad)
            if theta_rad - 1e-9 <= z_cand1 < 2 * math.pi + theta_rad - 1e-9:
                solutions_z.append(z_cand1)
            # Check if z_cand2 is in [theta_rad, 2pi + theta_rad)
            if theta_rad - 1e-9 <= z_cand2 < 2 * math.pi + theta_rad - 1e-9:
                solutions_z.append(z_cand2)
        
        # Convert z solutions to x solutions
        solutions_x = []
        for z_sol in solutions_z:
            x_sol = z_sol - theta_rad
            # Normalize x_sol to [0, 2pi)
            x_sol_norm = x_sol % (2 * math.pi)
            if x_sol_norm < 0: x_sol_norm += 2 * math.pi
            solutions_x.append(x_sol_norm)
            
        # Format x solutions to pi fractions and sort
        formatted_solutions = sorted(list(set([_format_rad_to_pi_str(sol) for sol in solutions_x])))

    a_formatted = _format_coeff(a)
    b_formatted = _format_coeff_with_sign(b)

    if a == 0:
        func_text = f"${b_formatted} \\cos x$"
    elif b == 0:
        func_text = f"${a_formatted} \\sin x$"
    else:
        func_text = f"${a_formatted} \\sin x {b_formatted} \\cos x$"

    question_text = f"在 $0 \\le x < 2\\pi$ 的範圍內，求方程式 {func_text} = ${k_formatted}$ 的解。"
    
    correct_answer = f"$x = {{{', '.join(formatted_solutions)}}}$" if formatted_solutions else "無解"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def generate(level=1):
    """
    生成「應用正餘弦函數疊合後的結果 y = r sin(x + θ)，來求函數在特定或無特定範圍內的最大值與最小值，並能解決相關的方程式與應用問題」相關題目。
    """
    problem_types = [
        'basic_extrema',
        'shifted_extrema',
        'expanded_extrema',
        'interval_extrema',
        'equation_solving'
    ]
    
    # Adjust difficulty for level
    if level == 1:
        problem_type = random.choice(['basic_extrema', 'shifted_extrema'])
    elif level == 2:
        problem_type = random.choice(['expanded_extrema', 'interval_extrema', 'equation_solving'])
    else: # level 3 - all types
        problem_type = random.choice(problem_types)

    if problem_type == 'basic_extrema':
        return generate_basic_extrema_problem()
    elif problem_type == 'shifted_extrema':
        return generate_shifted_extrema_problem()
    elif problem_type == 'expanded_extrema':
        return generate_expanded_extrema_problem()
    elif problem_type == 'interval_extrema':
        return generate_interval_extrema_problem()
    elif problem_type == 'equation_solving':
        return generate_equation_solving_problem()

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    This function performs a robust check by parsing numerical and LaTeX values
    from both user's and correct answers and comparing their floating-point representations.
    """
    user_answer = user_answer.strip().lower().replace(" ", "").replace("\n", "")
    correct_answer = correct_answer.strip().lower().replace(" ", "").replace("\n", "")
    
    def evaluate_math_str(s):
        """Helper to convert string math expressions (including LaTeX) to float."""
        s = s.replace(r"\\sqrt{", "math.sqrt(").replace("}", ")").replace(r"\\pi", "math.pi")
        s = s.replace(r"\\frac{", "Fraction(").replace("}", ")").replace("{", "") # Handle \\frac{num}{den}
        s = s.replace("sqrt", "math.sqrt") # Catch non-LaTeX sqrt
        
        try:
            # Special handling for Fraction objects
            if s.startswith("fraction("):
                parts = s[len("fraction("):-1].split(',')
                num = float(eval(parts[0].strip(), {"math": math, "Fraction": Fraction}))
                den = float(eval(parts[1].strip(), {"math": math, "Fraction": Fraction}))
                return num / den
            return float(eval(s, {"math": math, "Fraction": Fraction}))
        except Exception:
            return s # Return string if evaluation fails

    is_correct = False

    # --- Check for max/min values (with or without corresponding x values) ---
    if "最大值為" in correct_answer and "最小值為" in correct_answer:
        try:
            # Extract max value
            ca_max_val_str = correct_answer.split("最大值為")[1].split("時)")[0].split("，最小值為")[0].strip().replace("$", "")
            if "(發生在" in ca_max_val_str: # Remove "(發生在 x = ...)" part
                ca_max_val_str = ca_max_val_str.split("(發生在")[0].strip()

            # Extract min value
            ca_min_val_str = correct_answer.split("最小值為")[1].split("時)")[0].split("。")[0].strip().replace("$", "")
            if "(發生在" in ca_min_val_str: # Remove "(發生在 x = ...)" part
                ca_min_val_str = ca_min_val_str.split("(發生在")[0].strip()
            
            ua_max_val_str = ""
            ua_min_val_str = ""
            if "最大值為" in user_answer and "最小值為" in user_answer:
                try:
                    ua_max_val_str = user_answer.split("最大值為")[1].split("時)")[0].split("，最小值為")[0].strip().replace("$", "")
                    if "(發生在" in ua_max_val_str:
                        ua_max_val_str = ua_max_val_str.split("(發生在")[0].strip()
                    
                    ua_min_val_str = user_answer.split("最小值為")[1].split("時)")[0].split("。")[0].strip().replace("$", "")
                    if "(發生在" in ua_min_val_str:
                        ua_min_val_str = ua_min_val_str.split("(發生在")[0].strip()
                except IndexError:
                    pass

            ca_max_val = evaluate_math_str(ca_max_val_str)
            ca_min_val = evaluate_math_str(ca_min_val_str)
            ua_max_val = evaluate_math_str(ua_max_val_str)
            ua_min_val = evaluate_math_str(ua_min_val_str)
            
            values_match = False
            if isinstance(ca_max_val, float) and isinstance(ua_max_val, float) and \
               isinstance(ca_min_val, float) and isinstance(ua_min_val, float):
                if abs(ca_max_val - ua_max_val) < 1e-6 and abs(ca_min_val - ua_min_val) < 1e-6:
                    values_match = True
            elif ca_max_val_str == ua_max_val_str and ca_min_val_str == ua_min_val_str: # Fallback to string if not float
                 values_match = True
            
            if values_match:
                is_correct = True # Start with correct based on values, then check x if applicable

                # If x values are also part of the question
                if "(發生在" in correct_answer:
                    x_values_match = False
                    try:
                        ca_x_max_part = correct_answer.split("發生在")[1].split("時)")[0].strip().replace("$", "").replace("x=", "").replace("{", "").replace("}", "")
                        ca_x_min_part = correct_answer.split("發生在")[2].split("時)")[0].strip().replace("$", "").replace("x=", "").replace("{", "").replace("}", "")

                        ua_x_max_part = user_answer.split("發生在")[1].split("時)")[0].strip().replace("$", "").replace("x=", "").replace("{", "").replace("}", "")
                        ua_x_min_part = user_answer.split("發生在")[2].split("時)")[0].strip().replace("$", "").replace("x=", "").replace("{", "").replace("}", "")

                        ca_x_max_list = sorted([evaluate_math_str(x.strip()) for x in ca_x_max_part.split(',') if x.strip()])
                        ca_x_min_list = sorted([evaluate_math_str(x.strip()) for x in ca_x_min_part.split(',') if x.strip()])
                        ua_x_max_list = sorted([evaluate_math_str(x.strip()) for x in ua_x_max_part.split(',') if x.strip()])
                        ua_x_min_list = sorted([evaluate_math_str(x.strip()) for x in ua_x_min_part.split(',') if x.strip()])
                        
                        if len(ca_x_max_list) == len(ua_x_max_list) and len(ca_x_min_list) == len(ua_x_min_list):
                            max_x_match = all(abs(ca_x_max_list[i] - ua_x_max_list[i]) < 1e-6 if isinstance(ca_x_max_list[i], float) and isinstance(ua_x_max_list[i], float) else ca_x_max_list[i] == ua_x_max_list[i] for i in range(len(ca_x_max_list)))
                            min_x_match = all(abs(ca_x_min_list[i] - ua_x_min_list[i]) < 1e-6 if isinstance(ca_x_min_list[i], float) and isinstance(ua_x_min_list[i], float) else ca_x_min_list[i] == ua_x_min_list[i] for i in range(len(ca_x_min_list)))
                            x_values_match = max_x_match and min_x_match
                        
                    except (IndexError, ValueError, AttributeError, TypeError):
                        pass # Parsing x-values failed

                    if not x_values_match:
                        is_correct = False # x values didn't match
            
        except IndexError:
            pass # Basic parsing of max/min values failed, might be a different problem format

    # --- Check for equation solving (list of x values) ---
    elif user_answer.startswith("x=") and correct_answer.startswith("x="):
        ua_solutions_str = user_answer.replace("x=", "").replace("{", "").replace("}", "")
        ca_solutions_str = correct_answer.replace("x=", "").replace("{", "").replace("}", "")

        ua_list = sorted([s.strip() for s in ua_solutions_str.split(',') if s.strip()])
        ca_list = sorted([s.strip() for s in ca_solutions_str.split(',') if s.strip()])

        ua_numeric = [evaluate_math_str(s) for s in ua_list]
        ca_numeric = [evaluate_math_str(s) for s in ca_list]

        if len(ua_numeric) == len(ca_numeric):
            match_count = 0
            for u_val in ua_numeric:
                for c_val in ca_numeric:
                    if isinstance(u_val, float) and isinstance(c_val, float) and abs(u_val - c_val) < 1e-6:
                        match_count += 1
                        break
                    elif u_val == c_val: # String match for non-numeric or exact matches
                        match_count += 1
                        break
            if match_count == len(ca_numeric):
                is_correct = True
            else:
                is_correct = False
        else:
            is_correct = False
    
    # Fallback to direct string comparison if no specific parsing logic applies or initial parsing fails
    if not is_correct and user_answer == correct_answer:
        is_correct = True

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}