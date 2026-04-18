import random
import math
from fractions import Fraction
import re

# Helper function to calculate distance from a point (x0, y0) to a line Ax + By + C = 0
def distance_point_to_line(x0, y0, A, B, C):
    """Calculates the perpendicular distance from a point to a line."""
    numerator = abs(A * x0 + B * y0 + C)
    denominator = math.sqrt(A**2 + B**2)
    return numerator / denominator

# Helper function to format quadratic roots
def format_roots(roots):
    """Formats quadratic roots for display."""
    if not roots:
        return "無實數解"
    if len(roots) == 1:
        # Sort for consistent (x,y) string output, if x-coordinates are equal, compare y
        p_x, p_y = roots[0]
        return f"$({p_x}, {p_y})$"
    else:
        # Sort for consistent output, e.g., based on x-coordinate, then y-coordinate
        roots.sort(key=lambda p: (p[0], p[1]))
        return f"$({roots[0][0]}, {roots[0][1]})$ 和 $({roots[1][0]}, {roots[1][1]})$"

# Helper function to solve a quadratic equation ax^2 + bx + c = 0
# Returns a list of (x, y) tuples if real roots exist, for line y = mx+c or x=ny+c'
def solve_for_intersection_points(a, b, c, line_type, line_param):
    """
    Solves a quadratic equation and returns intersection points.
    line_type: 'y_is_mx_plus_c' or 'x_is_ny_plus_c_prime'
    line_param: (m, c_line) or (n, c_prime_line)
    """
    discriminant = b**2 - 4 * a * c
    points = []

    if discriminant < 0:
        return [] # No real roots
    elif discriminant == 0:
        x_or_y = Fraction(-b, 2 * a)
        if line_type == 'y_is_mx_plus_c':
            m, c_line = line_param
            y_val = m * x_or_y + c_line
            points.append((x_or_y, y_val))
        else: # x_is_ny_plus_c_prime
            n, c_prime_line = line_param
            x_val = n * x_or_y + c_prime_line
            points.append((x_val, x_or_y)) # (x, y)
    else:
        sqrt_discriminant = math.sqrt(discriminant)
        x_or_y1 = Fraction(-b + sqrt_discriminant, 2 * a)
        x_or_y2 = Fraction(-b - sqrt_discriminant, 2 * a)

        if line_type == 'y_is_mx_plus_c':
            m, c_line = line_param
            y1_val = m * x_or_y1 + c_line
            y2_val = m * x_or_y2 + c_line
            points.append((x_or_y1, y1_val))
            points.append((x_or_y2, y2_val))
        else: # x_is_ny_plus_c_prime
            n, c_prime_line = line_param
            x1_val = n * x_or_y1 + c_prime_line
            x2_val = n * x_or_y2 + c_prime_line
            points.append((x1_val, x_or_y1))
            points.append((x2_val, x_or_y2))
            
    # Convert Fractions to simple strings or floats if they are integers or simple decimals
    formatted_points = []
    for p_x, p_y in points:
        fp_x = float(p_x) if p_x.denominator != 1 else int(p_x)
        fp_y = float(p_y) if p_y.denominator != 1 else int(p_y)
        formatted_points.append((fp_x, fp_y))

    return formatted_points


def generate(level=1):
    problem_type = random.choice([
        'ALG_RELATION_POINTS',
        'ALG_FIND_K_TANGENCY',
        'GEO_RELATION',
        'GEO_CHORD_LENGTH',
        'GEO_FIND_K_TANGENCY_RANGE'
    ])

    if problem_type == 'ALG_RELATION_POINTS':
        return generate_alg_relation_points()
    elif problem_type == 'ALG_FIND_K_TANGENCY':
        return generate_alg_find_k_tangency()
    elif problem_type == 'GEO_RELATION':
        return generate_geo_relation()
    elif problem_type == 'GEO_CHORD_LENGTH':
        return generate_geo_chord_length()
    elif problem_type == 'GEO_FIND_K_TANGENCY_RANGE':
        return generate_geo_find_k_tangency_range()
    else:
        # Fallback or default
        return generate_alg_relation_points()


def generate_alg_relation_points():
    # Algebraic method: Determine relationship and intersection points
    # Circle: x^2 + y^2 = r_sq (simplified for easy substitution)
    # Line: y = mx + c_line or x = ny + c_line_prime (m, n = +/-1)

    # Work backward to ensure integer intersection points and simple coefficients
    
    attempts = 0
    while attempts < 20: # Retry mechanism for valid circle and parameters
        x1, x2 = random.sample(range(-5, 6), 2)
        while x1 == x2: # Ensure distinct x-roots initially for variety
            x2 = random.randint(-5, 5)

        if random.choice([True, False]): # Line form y = mx + c_line
            m = random.choice([1, -1])
            # Quadratic form: 2x^2 + (2mc_line)x + (c_line^2 - r_sq) = 0
            # Compare to 2 * (x - x1)(x - x2) = 2x^2 - 2(x1+x2)x + 2x1x2 = 0
            c_line = -m * (x1 + x2)
            r_sq = c_line**2 - 2 * x1 * x2 # This is r_sq, not r.
            
            if r_sq > 0 and r_sq <= 50: # Ensure r_sq is positive and not too large
                circle_eq = f"$x^{{2}} + y^{{2}} = {r_sq}$"
                
                # Format line equation to Ax+By+C=0
                # From y = mx + c_line => mx - y + c_line = 0
                line_eq = f"${m}x - y {'' if c_line == 0 else ('+ ' + str(c_line) if c_line > 0 else '- ' + str(abs(c_line)))} = 0$"
                
                line_param = (m, c_line)
                line_type = 'y_is_mx_plus_c'
                
                # Prepare quadratic coefficients for x
                a_quad = 1 + m**2
                b_quad = 2 * m * c_line
                c_quad = c_line**2 - r_sq
                
                # Calculate intersection points
                intersection_points = solve_for_intersection_points(a_quad, b_quad, c_quad, line_type, line_param)
                break # Parameters found, exit loop
        else: # Line form x = ny + c_line_prime
            n = random.choice([1, -1])
            y1, y2 = random.sample(range(-5, 6), 2)
            while y1 == y2: # Ensure distinct y-roots initially
                y2 = random.randint(-5, 5)

            c_line_prime = -n * (y1 + y2)
            r_sq = c_line_prime**2 - 2 * y1 * y2

            if r_sq > 0 and r_sq <= 50: # Ensure r_sq is positive and not too large
                circle_eq = f"$x^{{2}} + y^{{2}} = {r_sq}$"
                
                # Format line equation to Ax+By+C=0
                # From x = ny + c_line_prime => x - ny - c_line_prime = 0
                line_eq = f"$x {'' if -n == 0 else ('+ ' + str(-n) + 'y' if -n > 0 else '- ' + str(abs(-n)) + 'y')} {'' if -c_line_prime == 0 else ('+ ' + str(-c_line_prime) if -c_line_prime > 0 else '- ' + str(abs(-c_line_prime)))} = 0$"
                
                line_param = (n, c_line_prime)
                line_type = 'x_is_ny_plus_c_prime'

                # Prepare quadratic coefficients for y
                a_quad = 1 + n**2
                b_quad = 2 * n * c_line_prime
                c_quad = c_line_prime**2 - r_sq

                intersection_points = solve_for_intersection_points(a_quad, b_quad, c_quad, line_type, line_param)
                break # Parameters found, exit loop
        attempts += 1
    else: # If loop completes without breaking (couldn't find good parameters)
        # Fallback to a simpler, perhaps less "nice" problem if generation fails
        # or recursively call to try again
        return generate_alg_relation_points()

    # Determine relationship based on intersection_points
    if len(intersection_points) == 2:
        relation = "相割"
        answer_text = f"圓C和直線L交於相異兩點（相割），交點坐標為 {format_roots(intersection_points)}。"
    elif len(intersection_points) == 1:
        relation = "相切"
        answer_text = f"圓C和直線L交於一點（相切），交點坐標為 {format_roots(intersection_points)}。"
    else:
        relation = "相離"
        answer_text = "圓C和直線L沒有交點（相離）。"

    question_text = f"已知圓C和直線L的方程式如下：<br>C: {circle_eq}, L: {line_eq}。<br>判斷圓C和直線L的相交情形（若相交，求出它們的交點）。"
    
    correct_answer = answer_text

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_alg_find_k_tangency():
    # Algebraic method: Find k for tangency
    # Circle: x^2 + y^2 + Dx + Ey + F = 0
    # Line: Ax + By + C = 0
    
    line_choice = random.choice(['y=x', 'y=-x', 'x=0', 'y=0'])
    
    if line_choice == 'y=x':
        # Line: x - y = 0
        E = random.randint(-3, 3)
        F_opts = [2, 8, 18, 32] # To make 8F a perfect square (16, 64, 144, 256)
        F = random.choice(F_opts)
        
        val_sqrt_8F = int(math.sqrt(8*F))
        k_val1 = val_sqrt_8F - E
        k_val2 = -val_sqrt_8F - E
        
        circle_eq = f"$x^{{2}} + y^{{2}} + kx {'' if E == 0 else ('+ ' + str(E) + 'y' if E > 0 else '- ' + str(abs(E)) + 'y')} + {F} = 0$"
        line_eq = f"$x - y = 0$"
        correct_k_values = [k_val1, k_val2]
        
    elif line_choice == 'y=-x':
        # Line: x + y = 0
        E = random.randint(-3, 3)
        F_opts = [2, 8, 18, 32]
        F = random.choice(F_opts)
        
        val_sqrt_8F = int(math.sqrt(8*F))
        k_val1 = val_sqrt_8F + E # D+E = sqrt(8F) => D = sqrt(8F)-E
        k_val2 = -val_sqrt_8F + E # D+E = -sqrt(8F) => D = -sqrt(8F)-E
        
        # In this case (x+y=0, replace y=-x), (D-E) is coefficient for x.
        # So (D-E)^2 = 8F.
        # Let D be k, E be random. (k-E)^2 = 8F. k = E +- sqrt(8F).
        k_val1 = E + val_sqrt_8F
        k_val2 = E - val_sqrt_8F

        circle_eq = f"$x^{{2}} + y^{{2}} + kx {'' if E == 0 else ('+ ' + str(E) + 'y' if E > 0 else '- ' + str(abs(E)) + 'y')} + {F} = 0$"
        line_eq = f"$x + y = 0$"
        correct_k_values = [k_val1, k_val2]

    elif line_choice == 'x=0': # y-axis
        D = random.randint(-3, 3)
        F_opts = [1, 4, 9, 16] # To make 4F a perfect square (4, 16, 36, 64)
        F = random.choice(F_opts)
        
        val_sqrt_4F = int(math.sqrt(4*F))
        k_val1 = val_sqrt_4F
        k_val2 = -val_sqrt_4F

        circle_eq = f"$x^{{2}} + y^{{2}} {'' if D == 0 else ('+ ' + str(D) + 'x' if D > 0 else '- ' + str(abs(D)) + 'x')} + ky + {F} = 0$"
        line_eq = f"$x = 0$"
        correct_k_values = [k_val1, k_val2]
        
    else: # line_choice == 'y=0' (x-axis)
        E = random.randint(-3, 3)
        F_opts = [1, 4, 9, 16]
        F = random.choice(F_opts)

        val_sqrt_4F = int(math.sqrt(4*F))
        k_val1 = val_sqrt_4F
        k_val2 = -val_sqrt_4F

        circle_eq = f"$x^{{2}} + y^{{2}} + kx {'' if E == 0 else ('+ ' + str(E) + 'y' if E > 0 else '- ' + str(abs(E)) + 'y')} + {F} = 0$"
        line_eq = f"$y = 0$"
        correct_k_values = [k_val1, k_val2]

    question_text = f"已知圓C: {circle_eq} 與直線L: {line_eq} 相切，求實數 $k$ 的值。"
    
    correct_answer = f"$k = {min(correct_k_values)}$ 或 $k = {max(correct_k_values)}$"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_geo_relation():
    # Geometric method: Determine relationship (d vs r)
    # Circle: (x-h)^2 + (y-k)^2 = r^2
    # Line: Ax + By + C = 0
    
    h = random.randint(-5, 5)
    k = random.randint(-5, 5)
    r = random.randint(2, 6)
    
    # Choose A, B for integer denominator sqrt(A^2+B^2)
    pyth_triples = [(3, 4, 5), (5, 12, 13)]
    A_val, B_val, denom = random.choice(pyth_triples)
    # Randomly assign sign and swap A, B
    if random.choice([True, False]): A_val *= -1
    if random.choice([True, False]): B_val *= -1
    if random.choice([True, False]): A_val, B_val = B_val, A_val

    # Calculate current value in numerator without C
    val_Ah_plus_Bk = A_val * h + B_val * k
    
    # Determine relationship and choose C accordingly
    rel_type = random.choice(['intersect', 'tangent', 'separate'])
    
    if rel_type == 'intersect': # d < r
        # We need |val_Ah_plus_Bk + C| < r * denom
        max_abs_numerator = r * denom - 1 
        if max_abs_numerator <= 0: # This case should ideally not happen with r >= 2
            return generate_geo_relation()

        target_abs_numerator = random.randint(1, max_abs_numerator) # d is between 0 and r-epsilon
        
        C_candidate1 = target_abs_numerator - val_Ah_plus_Bk
        C_candidate2 = -target_abs_numerator - val_Ah_plus_Bk
        
        C = random.choice([C_candidate1, C_candidate2])
        # Avoid C being 0 if possible, unless it's the only option or intended
        if C == 0 and (max_abs_numerator > 1 or target_abs_numerator > 0):
             C = C_candidate1 if C_candidate2 != 0 else C_candidate2 # Try other candidate

        relationship = "交於相異兩點"
        
    elif rel_type == 'tangent': # d = r
        # We need |val_Ah_plus_Bk + C| = r * denom
        target_abs_numerator = r * denom
        C_plus = target_abs_numerator - val_Ah_plus_Bk
        C_minus = -target_abs_numerator - val_Ah_plus_Bk
        C = random.choice([C_plus, C_minus])
        relationship = "相切"
        
    else: # rel_type == 'separate' (d > r)
        # We need |val_Ah_plus_Bk + C| > r * denom
        min_abs_numerator = r * denom + 1
        C_val_positive = random.randint(min_abs_numerator, min_abs_numerator + 10) # ensure it's sufficiently far
        C = C_val_positive - val_Ah_plus_Bk if random.choice([True, False]) else -C_val_positive - val_Ah_plus_Bk
        relationship = "相離"

    circle_eq = f"$(x {'' if h == 0 else ('- ' + str(h) if h > 0 else '+ ' + str(abs(h)))})^{{2}} + (y {'' if k == 0 else ('- ' + str(k) if k > 0 else '+ ' + str(abs(k)))})^{{2}} = {r**2}$"
    line_eq = f"${A_val}x {'' if B_val == 0 else ('+ ' + str(B_val) + 'y' if B_val > 0 else '- ' + str(abs(B_val)) + 'y')} {'' if C == 0 else ('+ ' + str(C) if C > 0 else '- ' + str(abs(C)))} = 0$"

    question_text = f"判斷圓C: {circle_eq} 與直線L: {line_eq} 的相交情形。"
    correct_answer = relationship

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_geo_chord_length():
    # Geometric method: Find chord length
    # Circle: (x-h)^2 + (y-k)^2 = r^2
    # Line: Ax + By + C = 0
    
    # Work backward for integer chord length by choosing Pythagorean triples (d, h_half_len, r)
    pyth_triples_for_chord = [
        (3, 4, 5), (4, 3, 5), # d, half_chord, r
        (6, 8, 10), (8, 6, 10),
        (5, 12, 13), (12, 5, 13)
    ]
    d_val, h_half_len, r = random.choice(pyth_triples_for_chord) # d_val is distance from center to line

    # Ensure valid configuration for a chord, i.e., d < r
    if d_val >= r: # this shouldn't happen with pyth triples but as a safeguard
        return generate_geo_chord_length()
    
    h_center = random.randint(-5, 5)
    k_center = random.randint(-5, 5)
    
    # Choose A, B for integer denominator sqrt(A^2+B^2)
    pyth_triples_line = [(3, 4, 5), (5, 12, 13)]
    A_val, B_val, denom = random.choice(pyth_triples_line)
    if random.choice([True, False]): A_val *= -1
    if random.choice([True, False]): B_val *= -1
    if random.choice([True, False]): A_val, B_val = B_val, A_val
    
    # We need d_actual = d_val
    # d_actual = |A_val * h_center + B_val * k_center + C| / denom = d_val
    # |A_val * h_center + B_val * k_center + C| = d_val * denom
    
    current_val_in_abs = A_val * h_center + B_val * k_center
    target_abs_val = d_val * denom
    
    C_plus = target_abs_val - current_val_in_abs
    C_minus = -target_abs_val - current_val_in_abs
    C = random.choice([C_plus, C_minus])
    
    chord_length = 2 * h_half_len

    circle_eq = f"$(x {'' if h_center == 0 else ('- ' + str(h_center) if h_center > 0 else '+ ' + str(abs(h_center)))})^{{2}} + (y {'' if k_center == 0 else ('- ' + str(k_center) if k_center > 0 else '+ ' + str(abs(k_center)))})^{{2}} = {r**2}$"
    line_eq = f"${A_val}x {'' if B_val == 0 else ('+ ' + str(B_val) + 'y' if B_val > 0 else '- ' + str(abs(B_val)) + 'y')} {'' if C == 0 else ('+ ' + str(C) if C > 0 else '- ' + str(abs(C)))} = 0$"

    question_text = f"已知圓C: {circle_eq} 與直線L: {line_eq} 交於A, B兩相異點，求 $\\overline{{AB}}$ 的長。"
    correct_answer = str(chord_length)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_geo_find_k_tangency_range():
    # Geometric method: Find k for tangency or range for intersection
    # Circle: (x-h)^2 + (y-k)^2 = r^2
    # Line: Ax + By + k = 0 (k is in the constant term)
    
    h = random.randint(-5, 5)
    k = random.randint(-5, 5)
    r = random.randint(2, 6)

    # Choose A, B for integer denominator sqrt(A^2+B^2)
    pyth_triples = [(3, 4, 5), (5, 12, 13)]
    A_val, B_val, denom = random.choice(pyth_triples)
    if random.choice([True, False]): A_val *= -1
    if random.choice([True, False]): B_val *= -1
    if random.choice([True, False]): A_val, B_val = B_val, A_val

    # Distance formula: d = |A_val*h + B_val*k + k_line| / denom
    # We want d = r or d < r
    
    constant_part = A_val * h + B_val * k
    
    # d = r => |constant_part + k_line| / denom = r
    # |constant_part + k_line| = r * denom
    target_abs_value = r * denom
    
    k_line1 = target_abs_value - constant_part
    k_line2 = -target_abs_value - constant_part
    
    # Ensure k_line1 and k_line2 are distinct. Highly unlikely to be same for r >= 2
    if k_line1 == k_line2: 
        return generate_geo_find_k_tangency_range()

    circle_eq = f"$(x {'' if h == 0 else ('- ' + str(h) if h > 0 else '+ ' + str(abs(h)))})^{{2}} + (y {'' if k == 0 else ('- ' + str(k) if k > 0 else '+ ' + str(abs(k)))})^{{2}} = {r**2}$"
    line_eq_k = f"${A_val}x {'' if B_val == 0 else ('+ ' + str(B_val) + 'y' if B_val > 0 else '- ' + str(abs(B_val)) + 'y')} + k = 0$"

    # Part 1: Tangency
    question_text_1 = f"已知圓C與直線L相切，求 $k$ 的值與直線L的方程式。（有兩解）"
    
    # Sort k values for consistent output
    k_min = min(k_line1, k_line2)
    k_max = max(k_line1, k_line2)
    
    line_eq_1a = f"${A_val}x {'' if B_val == 0 else ('+ ' + str(B_val) + 'y' if B_val > 0 else '- ' + str(abs(B_val)) + 'y')} {'' if k_min == 0 else ('+ ' + str(k_min) if k_min > 0 else '- ' + str(abs(k_min)))} = 0$"
    line_eq_1b = f"${A_val}x {'' if B_val == 0 else ('+ ' + str(B_val) + 'y' if B_val > 0 else '- ' + str(abs(B_val)) + 'y')} {'' if k_max == 0 else ('+ ' + str(k_max) if k_max > 0 else '- ' + str(abs(k_max)))} = 0$"

    answer_tangency = f"$k = {k_min}$ 或 $k = {k_max}$。直線方程式為 {line_eq_1a} 或 {line_eq_1b}。"

    # Part 2: Intersection at distinct points
    question_text_2 = f"已知圓C與直線L交於相異兩點，求 $k$ 的範圍。"
    answer_intersection_range = f"${k_min}$ < $k$ < ${k_max}$"

    question_text = f"設圓C: {circle_eq} 與直線L: {line_eq_k}。<br>(1){question_text_1}<br>(2){question_text_2}"
    correct_answer = f"(1){answer_tangency}<br>(2){answer_intersection_range}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer_normalized = user_answer.strip().replace(" ", "").lower()
    correct_answer_normalized = correct_answer.strip().replace(" ", "").lower()

    is_correct = False
    feedback = ""

    # Specific parsing for multi-part answers (e.g., Type 5: GEO_FIND_K_TANGENCY_RANGE)
    if "(1)" in correct_answer_normalized and "(2)" in correct_answer_normalized:
        parts_correct = correct_answer_normalized.split("<br>")
        parts_user = user_answer_normalized.split("<br>")
        
        if len(parts_correct) == len(parts_user):
            is_part1_correct = False
            is_part2_correct = False
            part1_feedback = ""
            part2_feedback = ""

            # Check Part 1 (Tangency K values and equations)
            correct_part1 = parts_correct[0].replace("(1)", "").strip()
            user_part1 = parts_user[0].replace("(1)", "").strip()

            k_match_user_p1 = re.findall(r"k=(-?\d+)(?:或|or)k?=(-?\d+)", user_part1)
            k_match_correct_p1 = re.findall(r"k=(-?\d+)(?:或|or)k?=(-?\d+)", correct_part1)

            if k_match_user_p1 and k_match_correct_p1:
                user_ks = sorted([int(k) for k in k_match_user_p1[0]])
                correct_ks = sorted([int(k) for k in k_match_correct_p1[0]])
                if user_ks == correct_ks:
                    # Simplified check: if k values match, assume the rest is correct for now.
                    # A robust check would involve parsing line equations, which is outside basic regex scope.
                    is_part1_correct = True
                    # Check for line equations if they are simple exact matches
                    # This check is basic and assumes user formats lines identically
                    user_line_eqs = sorted(re.findall(r"\$([\w\+\-\=\s]+)\$", user_part1))
                    correct_line_eqs = sorted(re.findall(r"\$([\w\+\-\=\s]+)\$", correct_part1))
                    if user_line_eqs != correct_line_eqs:
                        is_part1_correct = False # If line equations don't match, set to false
                    
                    if is_part1_correct:
                        part1_feedback = "第(1)題K值與直線方程式正確。"
                    else:
                        part1_feedback = "第(1)題K值正確但直線方程式可能不符。" # More specific feedback
                else:
                    part1_feedback = "第(1)題K值不正確。"
            else:
                part1_feedback = "第(1)題答案格式不符或K值不正確。"

            # Check Part 2 (K range)
            correct_part2 = parts_correct[1].replace("(2)", "").strip()
            user_part2 = parts_user[1].replace("(2)", "").strip()

            k_range_match_user_p2 = re.match(r"(-?\d+)<k<(-?\d+)", user_part2)
            k_range_match_correct_p2 = re.match(r"(-?\d+)<k<(-?\d+)", correct_part2)
            
            if k_range_match_user_p2 and k_range_match_correct_p2:
                user_min, user_max = int(k_range_match_user_p2.group(1)), int(k_range_match_user_p2.group(2))
                correct_min, correct_max = int(k_range_match_correct_p2.group(1)), int(k_range_match_correct_p2.group(2))
                if user_min == correct_min and user_max == correct_max:
                    is_part2_correct = True
                    part2_feedback = "第(2)題K的範圍正確。"
                else:
                    part2_feedback = "第(2)題K的範圍不正確。"
            else:
                part2_feedback = "第(2)題答案格式不符或K的範圍不正確。"

            if is_part1_correct and is_part2_correct:
                is_correct = True
                feedback = f"完全正確！答案是 {correct_answer}。"
            else:
                feedback = f"答案不完全正確。<br>{part1_feedback}<br>{part2_feedback}<br>正確答案應為：{correct_answer}"
            
            return {"correct": is_correct, "result": feedback, "next_question": True}
    
    # Fallback to direct string comparison for other problem types
    if user_answer_normalized == correct_answer_normalized:
        is_correct = True
        feedback = f"完全正確！答案是 {correct_answer}。"
        return {"correct": is_correct, "result": feedback, "next_question": True}

    # If direct comparison fails, try more flexible parsing for specific answer types

    # 1. k values (for ALG_FIND_K_TANGENCY)
    k_match_user = re.findall(r"k=(-?\d+)(?:或|or)k?=(-?\d+)", user_answer_normalized)
    k_match_correct = re.findall(r"k=(-?\d+)(?:或|or)k?=(-?\d+)", correct_answer_normalized)
    
    if k_match_user and k_match_correct:
        user_ks = sorted([int(k) for k in k_match_user[0]])
        correct_ks = sorted([int(k) for k in k_match_correct[0]])
        if user_ks == correct_ks:
            is_correct = True
            feedback = f"完全正確！答案是 {correct_answer}。"
            return {"correct": is_correct, "result": feedback, "next_question": True}
        
    # 2. Relationship descriptions & points (for ALG_RELATION_POINTS)
    # Check relationship keywords
    relationship_map = {
        "相割": ["相割", "交於相異兩點", "交於兩點"],
        "相切": ["相切", "交於一點"],
        "相離": ["相離", "沒有交點", "無交點"]
    }
    
    user_rel_key = None
    for key, synonyms in relationship_map.items():
        for s in synonyms:
            if s in user_answer.replace(" ", ""):
                user_rel_key = key
                break
        if user_rel_key: break
    
    correct_rel_key = None
    for key, synonyms in relationship_map.items():
        for s in synonyms:
            if s in correct_answer.replace(" ", ""):
                correct_rel_key = key
                break
        if correct_rel_key: break

    if user_rel_key and correct_rel_key and user_rel_key == correct_rel_key:
        if user_rel_key in ["相割", "相切"]:
            # Extract points (x,y)
            user_points_str = re.findall(r"\((-?\d+),(-?\d+)\)", user_answer_normalized)
            correct_points_str = re.findall(r"\((-?\d+),(-?\d+)\)", correct_answer_normalized)

            user_coords = set(tuple(map(int, p)) for p in user_points_str)
            correct_coords = set(tuple(map(int, p)) for p in correct_points_str)

            if user_coords == correct_coords and len(user_coords) == len(correct_points_str):
                 is_correct = True
                 feedback = f"完全正確！答案是 {correct_answer}。"
                 return {"correct": is_correct, "result": feedback, "next_question": True}
        else: # For 相離, just checking the relationship is enough
            is_correct = True
            feedback = f"完全正確！答案是 {correct_answer}。"
            return {"correct": is_correct, "result": feedback, "next_question": True}
            
    # 3. Chord length (for GEO_CHORD_LENGTH)
    # Check if user_answer is just a number.
    try:
        user_num = float(user_answer_normalized)
        # Regex to extract number from correct answer, potentially inside $ $
        correct_num_match = re.search(r"(-?\d+\.?\d*)", correct_answer_normalized.replace("$", ""))
        if correct_num_match:
            correct_num = float(correct_num_match.group(1))
            if user_num == correct_num:
                is_correct = True
                feedback = f"完全正確！答案是 {correct_answer}。"
                return {"correct": is_correct, "result": feedback, "next_question": True}
    except (ValueError, AttributeError):
        pass # Not a simple number answer or regex failed

    feedback = f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": feedback, "next_question": True}