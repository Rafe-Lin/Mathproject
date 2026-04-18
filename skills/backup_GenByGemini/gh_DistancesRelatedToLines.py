import random
import math
from fractions import Fraction

# --- Helper Functions for 3D Vector Operations ---
def make_vector(p1, p2):
    """Calculates vector from p1 to p2."""
    return [p2[i] - p1[i] for i in range(3)]

def dot_product(v1, v2):
    """Calculates the dot product of two 3D vectors."""
    return sum(v1[i] * v2[i] for i in range(3))

def cross_product(v1, v2):
    """Calculates the cross product of two 3D vectors."""
    return [
        v1[1] * v2[2] - v1[2] * v2[1],
        v1[2] * v2[0] - v1[0] * v2[2],
        v1[0] * v2[1] - v1[1] * v2[0]
    ]

def vector_magnitude(v):
    """Calculates the magnitude of a 3D vector."""
    sum_sq = sum(x**2 for x in v)
    return math.sqrt(sum_sq)

def scalar_multiply(v, scalar):
    """Multiplies a vector by a scalar."""
    return [x * scalar for x in v]

def add_vectors(v1, v2):
    """Adds two 3D vectors."""
    return [v1[i] + v2[i] for i in range(3)]

def subtract_vectors(v1, v2):
    """Subtracts v2 from v1."""
    return [v1[i] - v2[i] for i in range(3)]

def are_vectors_parallel(v1, v2):
    """Checks if two vectors are parallel."""
    cp = cross_product(v1, v2)
    # Check if all components of the cross product are close to zero
    return all(abs(x) < 1e-9 for x in cp)

def is_zero_vector(v):
    """Checks if a vector is a zero vector."""
    return all(x == 0 for x in v)

def get_random_vector(min_coord=-3, max_coord=3):
    """Generates a random 3D vector, ensuring it's not a zero vector."""
    while True:
        v = [random.randint(min_coord, max_coord) for _ in range(3)]
        if not is_zero_vector(v):
            return v

def get_random_point(min_coord=-5, max_coord=5):
    """Generates a random 3D point."""
    return [random.randint(min_coord, max_coord) for _ in range(3)]

def format_point_latex(p, label="P"):
    """Formats a point for LaTeX display."""
    return f"{label}({p[0]}, {p[1]}, {p[2]})"

def format_line_symmetric_latex(point, direction_vector, label="L"):
    """Formats a line in symmetric form for LaTeX display. Returns None if a direction component is 0."""
    parts = []
    for i, (p_coord, v_coord, axis) in enumerate(zip(point, direction_vector, ['x', 'y', 'z'])):
        if v_coord == 0:
            return None # Symmetric form not suitable if a direction component is 0
        else:
            numerator_expr = f"{axis}"
            if p_coord != 0:
                # The format is (axis - p_coord)
                if p_coord > 0:
                    numerator_expr = f"{axis}-{p_coord}"
                else: # p_coord < 0
                    numerator_expr = f"{axis}+{abs(p_coord)}"
            
            parts.append(r"\\frac{{{}}}{{{}}}".format(numerator_expr, v_coord))
    return f"${label}: " + " = ".join(parts) + "$"

def format_line_parametric_latex(point, direction_vector, label="L", param_char="t"):
    """Formats a line in parametric form for LaTeX display."""
    # Build expressions for x, y, z
    coords_expr = []
    for i, (p_coord, v_coord, axis) in enumerate(zip(point, direction_vector, ['x', 'y', 'z'])):
        term_p = str(p_coord)
        term_v = ""
        if v_coord != 0:
            sign = "+" if v_coord > 0 else "-"
            term_v = f"{sign}{abs(v_coord)}{param_char}"
        
        if term_p == "0" and term_v != "":
            coords_expr.append(f"{axis} = {term_v.lstrip('+')}") # Remove leading '+' if only v_term
        elif term_p == "0" and term_v == "": # e.g. x=0 and direction for x is 0
             coords_expr.append(f"{axis} = 0")
        else:
            coords_expr.append(f"{axis} = {term_p}{term_v}")
            
    return f"${label}: \\begin{{cases}} {' \\\\ '.join(coords_expr)} \\end{{cases}}$"


def calculate_point_to_line_distance(P, A, v):
    """
    Calculates the distance from point P to the line passing through A with direction vector v.
    Formula: || (AP x v) || / ||v||
    """
    AP = subtract_vectors(P, A)
    cross_prod_AP_v = cross_product(AP, v)
    
    numerator = vector_magnitude(cross_prod_AP_v)
    denominator = vector_magnitude(v)
    
    if denominator == 0:
        return float('inf') # Should not happen with valid line
    
    return numerator / denominator

def calculate_parallel_lines_distance(P1, v1, P2, v2):
    """
    Calculates the distance between two parallel lines.
    P1, P2 are points on L1, L2 respectively. v1, v2 are their direction vectors.
    (v1 and v2 should be parallel, but for calculation, we can just use one of them, say v1).
    This reduces to point P1 to line L2 distance.
    """
    return calculate_point_to_line_distance(P1, P2, v1)

def calculate_skew_lines_distance(P1, v1, P2, v2):
    """
    Calculates the distance between two skew lines using the scalar triple product.
    Formula: | (P2 - P1) . (v1 x v2) | / || v1 x v2 ||
    """
    # Check if lines are actually skew (not parallel)
    if are_vectors_parallel(v1, v2):
        raise ValueError("Vectors are parallel, not skew lines.")

    n = cross_product(v1, v2)
    # n should not be a zero vector if v1 and v2 are not parallel.
    if is_zero_vector(n):
        raise ValueError("Cross product is zero, vectors are unexpectedly parallel.")

    P1P2 = subtract_vectors(P2, P1)
    
    numerator = abs(dot_product(P1P2, n))
    denominator = vector_magnitude(n)
    
    return numerator / denominator


def generate_point_to_line_problem():
    P = get_random_point()
    A = get_random_point() # Point on the line
    v = get_random_vector() # Direction vector of the line

    # Ensure P is not on the line and line is valid
    AP_vec = subtract_vectors(P, A)
    while is_zero_vector(v) or are_vectors_parallel(AP_vec, v):
        v = get_random_vector()
        P = get_random_point()
        A = get_random_point()
        AP_vec = subtract_vectors(P, A)

    distance = calculate_point_to_line_distance(P, A, v)
    
    # Calculate projection point Q
    t = dot_product(AP_vec, v) / dot_product(v, v)
    Q = [A[i] + v[i] * t for i in range(3)]

    # Format Q coordinates, rounding if close to integer
    Q_coords_str = f"({Q[0]:.2f}, {Q[1]:.2f}, {Q[2]:.2f})"
    if all(abs(x - round(x)) < 1e-6 for x in Q):
        Q_coords_str = f"({int(round(Q[0]))}, {int(round(Q[1]))}, {int(round(Q[2]))})"

    # Format distance, rounding if close to integer
    distance_formatted = f"{distance:.2f}"
    if abs(distance - round(distance)) < 1e-6:
        distance_formatted = str(int(round(distance)))

    line_str = None
    if random.choice([True, False]): # Try symmetric form first
        line_str = format_line_symmetric_latex(A, v, 'L')
    if line_str is None: # Fallback to parametric if symmetric form is not suitable (e.g., v has zero components)
        line_str = format_line_parametric_latex(A, v, 'L')

    question_text = (
        f"已知點 ${format_point_latex(P)}$ 為直線 ${line_str}$ 外一點。<br>"
        r"(1) 求 $P$ 點在 $L$ 上的投影點座標。<br>"
        r"(2) 求 $P$ 點到直線 $L$ 的距離。"
    )
    correct_answer = f"Q: {Q_coords_str}, Distance: {distance_formatted}"

    return {
        "question_text": question_text,
        "answer": correct_answer, # Store the precise calculated answer
        "correct_answer": correct_answer # The full combined string
    }

def generate_parallel_lines_problem():
    P1 = get_random_point()
    v = get_random_vector()
    
    # Ensure v is not a zero vector (already handled by get_random_vector, but defensive)
    while is_zero_vector(v):
        v = get_random_vector()

    # Generate P2 such that L1 and L2 are distinct and parallel
    while True:
        P2 = get_random_point()
        P1P2 = subtract_vectors(P2, P1)
        # P1P2 should not be parallel to v (meaning P2 is not on L1)
        # And P1P2 should not be the zero vector (P1 != P2)
        if not is_zero_vector(P1P2) and not are_vectors_parallel(P1P2, v):
            break

    distance = calculate_parallel_lines_distance(P1, v, P2, v)

    distance_formatted = f"{distance:.2f}"
    if abs(distance - round(distance)) < 1e-6:
        distance_formatted = str(int(round(distance)))

    line1_str = None
    if random.choice([True, False]):
        line1_str = format_line_symmetric_latex(P1, v, 'L_1')
    if line1_str is None:
        line1_str = format_line_parametric_latex(P1, v, 'L_1', 't')

    line2_str = None
    if random.choice([True, False]):
        line2_str = format_line_symmetric_latex(P2, v, 'L_2')
    if line2_str is None:
        line2_str = format_line_parametric_latex(P2, v, 'L_2', 's')

    question_text = (
        f"求兩平行線 ${line1_str}$ 與 ${line2_str}$ 的距離。"
    )
    correct_answer = distance_formatted

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_skew_lines_problem():
    P1 = get_random_point()
    v1 = get_random_vector()

    # Ensure v1 is not zero vector (already handled by get_random_vector)
    while is_zero_vector(v1):
        v1 = get_random_vector()

    # Ensure v2 is not parallel to v1 and not a zero vector
    while True:
        v2 = get_random_vector()
        if not is_zero_vector(v2) and not are_vectors_parallel(v1, v2):
            break

    # Generate P2 such that L1 and L2 are skew (not intersecting)
    # They are skew if (P2-P1) . (v1 x v2) != 0
    while True:
        P2 = get_random_point()
        n = cross_product(v1, v2)
        # n should not be a zero vector here because v1, v2 are not parallel
        if is_zero_vector(n): # Defensive check, should rarely happen if v1,v2 are truly non-parallel
             continue
        P1P2 = subtract_vectors(P2, P1)
        
        # Ensure (P2-P1) . n is non-zero for skew lines
        if dot_product(P1P2, n) != 0:
            break
        
    distance = calculate_skew_lines_distance(P1, v1, P2, v2)

    distance_formatted = f"{distance:.2f}"
    if abs(distance - round(distance)) < 1e-6:
        distance_formatted = str(int(round(distance)))

    line1_str = None
    if random.choice([True, False]):
        line1_str = format_line_symmetric_latex(P1, v1, 'L_1')
    if line1_str is None:
        line1_str = format_line_parametric_latex(P1, v1, 'L_1', 't')

    line2_str = None
    if random.choice([True, False]):
        line2_str = format_line_symmetric_latex(P2, v2, 'L_2')
    if line2_str is None:
        line2_str = format_line_parametric_latex(P2, v2, 'L_2', 's')

    question_text = (
        f"已知直線 ${line1_str}$ 與 ${line2_str}$ 互為歪斜線，求兩直線的距離。"
    )
    correct_answer = distance_formatted

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def generate(level=1):
    problem_types = {
        1: ['point_to_line'],
        2: ['point_to_line', 'parallel_lines'],
        3: ['skew_lines'] 
    }
    
    # Randomly select a problem type based on level
    if level not in problem_types or not problem_types[level]:
        level = 1 # Default to level 1 if invalid level or empty list

    chosen_type = random.choice(problem_types[level])

    if chosen_type == 'point_to_line':
        return generate_point_to_line_problem()
    elif chosen_type == 'parallel_lines':
        return generate_parallel_lines_problem()
    elif chosen_type == 'skew_lines':
        return generate_skew_lines_problem()

def check(user_answer, correct_answer_str):
    """
    Checks the user's answer. Handles specific formats for point-to-line problems.
    """
    user_answer = user_answer.strip().replace(' ', '')
    correct_answer_str = correct_answer_str.strip().replace(' ', '')

    is_correct = False
    feedback = ""

    # Check for point_to_line problem format ("Q:(x,y,z),Distance:D")
    if "Q:(" in correct_answer_str and "Distance:" in correct_answer_str:
        try:
            # Parse correct answer
            q_start_idx = correct_answer_str.find("Q:(") + 2
            q_end_idx = correct_answer_str.find(")", q_start_idx) + 1
            dist_start_idx = correct_answer_str.find("Distance:", q_end_idx) + len("Distance:")
            
            correct_q_str = correct_answer_str[q_start_idx:q_end_idx].strip()
            correct_dist_str = correct_answer_str[dist_start_idx:].strip()

            correct_q_coords = tuple(map(float, correct_q_str.strip('()').split(',')))
            correct_distance = float(correct_dist_str)

            # Parse user answer
            user_q_start_idx = user_answer.find("Q:(") + 2
            user_q_end_idx = user_answer.find(")", user_q_start_idx) + 1
            user_dist_start_idx = user_answer.find("Distance:", user_q_end_idx) + len("Distance:")

            user_q_str = user_answer[user_q_start_idx:user_q_end_idx].strip()
            user_dist_str = user_answer[user_dist_start_idx:].strip()

            user_q_coords = tuple(map(float, user_q_str.strip('()').split(',')))
            user_distance = float(user_dist_str)

            # Compare Q coordinates with tolerance
            q_coords_correct = all(abs(u - c) < 1e-4 for u, c in zip(user_q_coords, correct_q_coords))
            # Compare distance with tolerance
            distance_correct = abs(user_distance - correct_distance) < 1e-4
            
            is_correct = q_coords_correct and distance_correct
            if is_correct:
                feedback = r"完全正確！投影點 $Q$ 座標為 " + f"${correct_q_str}$" + r"，距離為 $" + f"{correct_dist_str}$" + r"。"
            else:
                feedback = r"答案不正確。正確答案應為：投影點 $Q$ 座標為 " + f"${correct_q_str}$" + r"，距離為 $" + f"{correct_dist_str}$" + r"。"

        except (ValueError, IndexError):
            # Fallback for unexpected user input format or parsing error
            feedback = r"請檢查您的輸入格式。正確答案格式應為 $Q:(x,y,z), Distance:D$。"
    else: # For parallel lines and skew lines, simple numerical answer
        try:
            user_val = float(user_answer)
            correct_val = float(correct_answer_str)
            
            is_correct = abs(user_val - correct_val) < 1e-4
            if is_correct:
                feedback = r"完全正確！答案是 $" + f"{correct_answer_str}$" + r"。"
            else:
                feedback = r"答案不正確。正確答案應為：$" + f"{correct_answer_str}$" + r"。"
        except ValueError:
            feedback = r"答案不正確，請輸入一個數字。"
    
    return {"correct": is_correct, "result": feedback, "next_question": True}