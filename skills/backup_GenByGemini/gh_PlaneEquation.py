import random
import math
from fractions import Fraction
import re

# --- Helper Functions ---

def vec_sub(v1, v2):
    """Subtracts vector v2 from v1."""
    return (v1[0] - v2[0], v1[1] - v2[1], v1[2] - v2[2])

def cross_product(v1, v2):
    """Calculates the cross product of two 3D vectors."""
    x = v1[1] * v2[2] - v1[2] * v2[1]
    y = v1[2] * v2[0] - v1[0] * v2[2]
    z = v1[0] * v2[1] - v1[1] * v2[0]
    return (x, y, z)

def get_canonical_form(a, b, c, d):
    """
    Normalizes plane equation coefficients (Ax + By + Cz = D) to a canonical form.
    Canonical form:
    1. Coefficients (a, b, c, d) are integers.
    2. Divided by their greatest common divisor.
    3. The first non-zero coefficient (A, then B, then C) is positive.
    Returns a tuple (A_prime, B_prime, C_prime, D_prime).
    Special cases for degenerate plane equations:
    - (0,0,0,0) for the equation 0=0 (represents the entire space).
    - (0,0,0,1) for 0=D (where D!=0), which is an impossible equation (no solution).
    """
    # If all coefficients of x, y, z are zero
    if a == 0 and b == 0 and c == 0:
        if d == 0:
            return (0, 0, 0, 0) # 0 = 0
        else:
            return (0, 0, 0, 1) # 0 = non-zero (e.g., 0=5)

    # Calculate GCD of absolute values of all coefficients
    common_divisor = abs(a)
    common_divisor = math.gcd(common_divisor, abs(b))
    common_divisor = math.gcd(common_divisor, abs(c))
    common_divisor = math.gcd(common_divisor, abs(d))

    # Divide by GCD (common_divisor should not be 0 here for valid plane equations)
    a, b, c, d = a // common_divisor, b // common_divisor, c // common_divisor, d // common_divisor

    # Ensure the first non-zero coefficient (A, then B, then C) is positive
    if a != 0:
        if a < 0:
            a, b, c, d = -a, -b, -c, -d
    elif b != 0: # a is 0, but b is not
        if b < 0:
            a, b, c, d = -a, -b, -c, -d
    elif c != 0: # a and b are 0, but c is not
        if c < 0:
            a, b, c, d = -a, -b, -c, -d
            
    return (a, b, c, d)

def format_plane_equation(a, b, c, d):
    """
    Formats plane equation coefficients (a, b, c, d) into a LaTeX string of the form Ax + By + Cz = D.
    """
    terms = []
    
    # x-term
    if a == 1:
        terms.append("x")
    elif a == -1:
        terms.append("-x")
    elif a != 0:
        terms.append(f"{a}x")
    
    # y-term
    if b != 0:
        # Add sign if it's not the first term
        sign = "+" if b > 0 and terms else ""
        if b == 1:
            terms.append(f"{sign}y")
        elif b == -1:
            terms.append("-y")
        else:
            terms.append(f"{sign}{b}y")
            
    # z-term
    if c != 0:
        # Add sign if it's not the first term
        sign = "+" if c > 0 and terms else ""
        if c == 1:
            terms.append(f"{sign}z")
        elif c == -1:
            terms.append("-z")
        else:
            terms.append(f"{sign}{c}z")

    if not terms: # This means a, b, c were all zero.
        return f"$0 = {d}$" # e.g. $0=0$ or $0=5$

    left_side = " ".join(terms)
    return f"${left_side} = {d}$"

def parse_plane_equation(equation_str):
    """
    Parses a plane equation string (e.g., "3x - 2y + z = 2") into its canonical coefficients.
    Returns (A, B, C, D) tuple or None if parsing fails due to invalid format.
    """
    # Clean input: remove spaces, convert to lowercase
    equation_str = equation_str.replace(" ", "").lower()
    
    # Regex to split into left and right sides of '='. D must be an integer.
    match = re.match(r"(.+)=([+-]?\d+)$", equation_str)
    if not match:
        return None # Invalid format (e.g., missing '=', or D is not an integer)

    left_side_str = match.group(1)
    d_val = int(match.group(2))

    a, b, c = 0, 0, 0

    # Prepare left side for splitting by terms (e.g., '3x-2y+z' -> '+3x+-2y+z')
    left_side_str = left_side_str.replace("-", "+-")
    # Add a leading plus sign if not already present, for consistent splitting
    if not left_side_str.startswith("+") and not left_side_str.startswith("-"):
        left_side_str = "+" + left_side_str

    # Split into individual terms (e.g., ['+3x', '-2y', '+z'])
    terms = [term for term in left_side_str.split("+") if term]

    for term in terms:
        coeff_str = ""
        var_char = ''
        
        # Determine the variable and extract its coefficient string
        if term.endswith("x"):
            var_char = 'x'
            coeff_str = term[:-1]
        elif term.endswith("y"):
            var_char = 'y'
            coeff_str = term[:-1]
        elif term.endswith("z"):
            var_char = 'z'
            coeff_str = term[:-1]
        else: # Term does not end with x, y, or z (e.g. malformed or a constant on LHS)
            return None

        # Convert coefficient string to integer
        if coeff_str == "+" or coeff_str == "": # e.g. "x" or "+x"
            coeff = 1
        elif coeff_str == "-": # e.g. "-x"
            coeff = -1
        else:
            try:
                coeff = int(coeff_str)
            except ValueError:
                return None # Malformed coefficient (e.g. "2.5x", "abcx")

        # Accumulate coefficients
        if var_char == 'x':
            a += coeff
        elif var_char == 'y':
            b += coeff
        elif var_char == 'z':
            c += coeff
            
    return get_canonical_form(a, b, c, d_val)


# --- Problem Generation Functions ---

def generate_point_normal_problem():
    """Generates a problem: Find plane equation given a point and a normal vector."""
    p = (random.randint(-5, 5), random.randint(-5, 5), random.randint(-5, 5))
    n = (random.randint(-3, 3), random.randint(-3, 3), random.randint(-3, 3))
    
    # Ensure normal vector is not the zero vector
    while n == (0, 0, 0):
        n = (random.randint(-3, 3), random.randint(-3, 3), random.randint(-3, 3))

    a, b, c = n
    x0, y0, z0 = p

    # Using the point-normal form: a(x - x0) + b(y - y0) + c(z - z0) = 0
    # Rearrange to general form: ax + by + cz = ax0 + by0 + cz0
    d = a * x0 + b * y0 + c * z0

    canonical_coeffs = get_canonical_form(a, b, c, d)
    correct_equation_str = format_plane_equation(*canonical_coeffs)

    question_text = (
        f"求通過點 $A({x0}, {y0}, {z0})$ ，"
        f"且以 $\\vec{{n}}=({a}, {b}, {c})$ 為法向量的平面方程式。"
    )

    return {
        "question_text": question_text,
        "answer": correct_equation_str, # Formatted string for user display
        "correct_answer": canonical_coeffs # Canonical coefficients for robust checking
    }

def generate_perpendicular_line_problem():
    """Generates a problem: Find plane equation given a point outside the plane and its perpendicular foot on the plane."""
    # A is a point outside the plane E. H is the foot of the perpendicular from A to E.
    # The vector AH is the normal vector to the plane E. Point H is on the plane.
    a_point = (random.randint(-5, 5), random.randint(-5, 5), random.randint(-5, 5))
    h_point = (random.randint(-5, 5), random.randint(-5, 5), random.randint(-5, 5))

    # Ensure A and H are distinct points to have a valid normal vector
    while a_point == h_point:
        h_point = (random.randint(-5, 5), random.randint(-5, 5), random.randint(-5, 5))

    # Normal vector N = vector AH
    n_vec = vec_sub(a_point, h_point)
    a, b, c = n_vec

    # Point on plane E is H
    x0, y0, z0 = h_point

    # Using the point-normal form: a(x - x0) + b(y - y0) + c(z - z0) = 0
    # Rearrange to general form: ax + by + cz = ax0 + by0 + cz0
    d = a * x0 + b * y0 + c * z0

    canonical_coeffs = get_canonical_form(a, b, c, d)
    correct_equation_str = format_plane_equation(*canonical_coeffs)

    question_text = (
        f"在空間中，自點 $A({a_point[0]}, {a_point[1]}, {a_point[2]})$ "
        f"作平面 $E$ 的垂線。已知垂足為點 $H({h_point[0]}, {h_point[1]}, {h_point[2]})$ ，"
        f"求平面 $E$ 的方程式。"
    )

    return {
        "question_text": question_text,
        "answer": correct_equation_str,
        "correct_answer": canonical_coeffs
    }

def generate_parallel_plane_problem():
    """Generates a problem: Find plane equation given a point on the plane and a parallel plane's equation."""
    # Plane E passes through point A and is parallel to plane E'
    # E': A'x + B'y + C'z = D'
    # E: A'x + B'y + C'z = D (same normal vector, different D)

    p = (random.randint(-5, 5), random.randint(-5, 5), random.randint(-5, 5))
    a_prime = random.randint(-3, 3)
    b_prime = random.randint(-3, 3)
    c_prime = random.randint(-3, 3)
    d_prime = random.randint(-10, 10)

    # Ensure normal vector for E' (and thus E) is not the zero vector
    while (a_prime, b_prime, c_prime) == (0, 0, 0):
        a_prime = random.randint(-3, 3)
        b_prime = random.randint(-3, 3)
        c_prime = random.randint(-3, 3)

    # Format E' equation for the question text
    e_prime_canonical_coeffs = get_canonical_form(a_prime, b_prime, c_prime, d_prime)
    e_prime_equation_str = format_plane_equation(*e_prime_canonical_coeffs)
    
    # Normal vector for E is (a_prime, b_prime, c_prime)
    # Point on E is p(x0, y0, z0)
    # Calculate D for E: D = a_prime * x0 + b_prime * y0 + c_prime * z0
    d = a_prime * p[0] + b_prime * p[1] + c_prime * p[2]

    canonical_coeffs = get_canonical_form(a_prime, b_prime, c_prime, d)
    correct_equation_str = format_plane_equation(*canonical_coeffs)

    question_text = (
        f"已知平面 $E$ 通過點 $A({p[0]}, {p[1]}, {p[2]})$ ，"
        f"且與平面 $E'$ : {e_prime_equation_str} 平行，求 $E$ 的方程式。"
    )

    return {
        "question_text": question_text,
        "answer": correct_equation_str,
        "correct_answer": canonical_coeffs
    }

def generate_three_points_problem():
    """Generates a problem: Find plane equation given three non-collinear points."""
    # Generate 3 points A, B, C. Ensure they are non-collinear.
    while True:
        p1 = (random.randint(-4, 4), random.randint(-4, 4), random.randint(-4, 4))
        p2 = (random.randint(-4, 4), random.randint(-4, 4), random.randint(-4, 4))
        p3 = (random.randint(-4, 4), random.randint(-4, 4), random.randint(-4, 4))

        # Ensure points are distinct
        if p1 == p2 or p1 == p3 or p2 == p3:
            continue

        # Create two vectors on the plane from the three points
        vec_ab = vec_sub(p2, p1)
        vec_ac = vec_sub(p3, p1)
        
        # The cross product of these two vectors gives the normal vector to the plane
        n = cross_product(vec_ab, vec_ac)

        # Ensure normal vector is not zero (implies points are collinear), so cross product is non-zero
        if n != (0, 0, 0):
            break

    a, b, c = n
    x0, y0, z0 = p1 # Use p1 (point A) as the point on the plane

    # Using the point-normal form: a(x - x0) + b(y - y0) + c(z - z0) = 0
    # Rearrange to general form: ax + by + cz = ax0 + by0 + cz0
    d = a * x0 + b * y0 + c * z0

    canonical_coeffs = get_canonical_form(a, b, c, d)
    correct_equation_str = format_plane_equation(*canonical_coeffs)

    question_text = (
        f"已知平面 $E$ 通過 $A({p1[0]}, {p1[1]}, {p1[2]})$、"
        f"$B({p2[0]}, {p2[1]}, {p2[2]})$、$C({p3[0]}, {p3[1]}, {p3[2]})$ 三點，"
        f"求 $E$ 的方程式。"
    )

    return {
        "question_text": question_text,
        "answer": correct_equation_str,
        "correct_answer": canonical_coeffs
    }

def generate_intercept_form_problem():
    """Generates a problem: Find plane equation given three points on the axes (intercept form)."""
    # Generate non-zero intercepts for x, y, z axes
    x_int = random.choice([x for x in range(-5, 6) if x != 0])
    y_int = random.choice([y for y in range(-5, 6) if y != 0])
    z_int = random.choice([z for z in range(-5, 6) if z != 0])

    p1 = (x_int, 0, 0)
    p2 = (0, y_int, 0)
    p3 = (0, 0, z_int)

    # Create two vectors on the plane
    vec_ab = vec_sub(p2, p1) # (-x_int, y_int, 0)
    vec_ac = vec_sub(p3, p1) # (-x_int, 0, z_int)
    
    # The cross product gives the normal vector
    n = cross_product(vec_ab, vec_ac)
    # The result will be (y_int*z_int, x_int*z_int, x_int*y_int)

    a, b, c = n
    x0, y0, z0 = p1 # Use p1 (point A) as the point on the plane

    # Using the point-normal form: a(x - x0) + b(y - y0) + c(z - z0) = 0
    # Rearrange to general form: ax + by + cz = ax0 + by0 + cz0
    d = a * x0 + b * y0 + c * z0 # d = (y_int*z_int)*x_int

    canonical_coeffs = get_canonical_form(a, b, c, d)
    correct_equation_str = format_plane_equation(*canonical_coeffs)

    question_text = (
        f"已知平面 $E$ 通過 $A({p1[0]}, {p1[1]}, {p1[2]})$、"
        f"$B({p2[0]}, {p2[1]}, {p2[2]})$、$C({p3[0]}, {p3[1]}, {p3[2]})$ 三點，"
        f"求 $E$ 的方程式。"
    )

    return {
        "question_text": question_text,
        "answer": correct_equation_str,
        "correct_answer": canonical_coeffs
    }


def generate(level=1):
    """
    生成「平面方程式」相關題目。
    包含：
    1. 點法式 (Point-Normal Form)
    2. 由點與垂足決定平面 (Point and Perpendicular Line)
    3. 平行平面 (Parallel Plane)
    4. 三點決定平面 (Three Non-Collinear Points)
    5. 截距式 (Intercept Form)
    """
    problem_type = random.choice([
        'point_normal',
        'perpendicular_line',
        'parallel_plane',
        'three_points',
        'intercept_form'
    ])

    if problem_type == 'point_normal':
        return generate_point_normal_problem()
    elif problem_type == 'perpendicular_line':
        return generate_perpendicular_line_problem()
    elif problem_type == 'parallel_plane':
        return generate_parallel_plane_problem()
    elif problem_type == 'three_points':
        return generate_three_points_problem()
    elif problem_type == 'intercept_form':
        return generate_intercept_form_problem()

def check(user_answer, correct_answer):
    """
    檢查使用者對平面方程式問題的答案是否正確。
    user_answer: 使用者的答案字符串 (e.g., "3x - 2y + z = 2")
    correct_answer: 正確答案的標準化係數元組 (A, B, C, D)
    """
    user_coeffs = parse_plane_equation(user_answer)
    
    if user_coeffs is None:
        return {"correct": False, "result": "輸入格式錯誤，請確保為 $Ax+By+Cz=D$ 形式。", "next_question": False}

    # Compare the canonical forms
    is_correct = (user_coeffs == correct_answer)

    # Format the correct answer for feedback
    if correct_answer == (0,0,0,0):
        formatted_correct = "$0 = 0$"
    elif correct_answer == (0,0,0,1):
        formatted_correct = "$0 = D$ (where $D \\neq 0$)" # Impossible equation
    else:
        formatted_correct = format_plane_equation(*correct_answer)


    result_text = f"完全正確！答案是 {formatted_correct}。" if is_correct else f"答案不正確。正確答案應為：{formatted_correct}"
    return {"correct": is_correct, "result": result_text, "next_question": True}