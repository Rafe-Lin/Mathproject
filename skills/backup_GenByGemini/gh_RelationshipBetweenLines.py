import random
from fractions import Fraction

# --- Helper functions for vector operations and line formatting ---

def _generate_non_zero_vector(min_val=-5, max_val=5):
    """Generates a 3D vector with at least one non-zero component."""
    while True:
        v = [random.randint(min_val, max_val) for _ in range(3)]
        if any(x != 0 for x in v):
            return v

def _are_vectors_parallel(v1, v2):
    """Checks if two 3D vectors are parallel. Assumes v1 and v2 are non-zero."""
    # Cross product is the zero vector if and only if the vectors are parallel.
    cp = _cross_product(v1, v2)
    return all(c == 0 for c in cp)

def _cross_product(v1, v2):
    """Calculates the cross product of two 3D vectors."""
    return [
        v1[1] * v2[2] - v1[2] * v2[1],
        v1[2] * v2[0] - v1[0] * v2[2],
        v1[0] * v2[1] - v1[1] * v2[0]
    ]

def _dot_product(v1, v2):
    """Calculates the dot product of two 3D vectors."""
    return sum(v1[i] * v2[i] for i in range(3))

def _subtract_vectors(v1, v2):
    """Subtracts v2 from v1."""
    return [v1[i] - v2[i] for i in range(3)]

def _add_vectors(v1, v2):
    """Adds two vectors."""
    return [v1[i] + v2[i] for i in range(3)]

def _scalar_multiply_vector(v, k):
    """Multiplies a vector by a scalar."""
    return [x * k for x in v]

def _point_on_line(point_to_check, line_point, line_direction):
    """Checks if a point_to_check lies on the line defined by line_point and line_direction."""
    # A point P is on the line (P0, v) if vector (P - P0) is parallel to v.
    vec_diff = _subtract_vectors(point_to_check, line_point)
    
    # If vec_diff is the zero vector, point_to_check is line_point, so it's on the line.
    if all(d == 0 for d in vec_diff):
        return True
    
    # Otherwise, check parallelism.
    return _are_vectors_parallel(vec_diff, line_direction)

def _generate_offset_not_parallel(v_ref, min_val=-3, max_val=3):
    """Generates a 3D vector that is not parallel to v_ref."""
    while True:
        offset = [random.randint(min_val, max_val) for _ in range(3)]
        # Ensure offset is non-zero and not parallel to v_ref
        if any(x != 0 for x in offset) and not _are_vectors_parallel(offset, v_ref):
            return offset

def _format_line_equation(point, direction):
    """
    Formats a line equation in symmetric form.
    Handles cases where direction vector components are zero.
    Example: P(1,2,3), v(0, -3, 2) -> "x=1, $ \\frac{{y-2}}{{-3}} = \\frac{{z-3}}{{2}} $"
    """
    sym_parts = []
    fixed_coords = []
    
    for i, coord_name in enumerate(['x', 'y', 'z']):
        p_val = point[i]
        d_val = direction[i]
        
        if d_val == 0:
            fixed_coords.append(f"${coord_name}={p_val}$")
        else:
            numerator_val = f"{coord_name}"
            if p_val > 0:
                numerator_val += f"-{p_val}"
            elif p_val < 0:
                numerator_val += f"+{-p_val}" # Example: x - (-2) => x+2
            
            sym_parts.append(r"\\frac{{{}}}{{{}}}".format(numerator_val, d_val))
            
    if not sym_parts:
        # This case should ideally not happen for a valid line (direction vector cannot be all zeros).
        # Fallback to parametric form or raise an error in a robust system.
        # For this problem, _generate_non_zero_vector prevents this.
        return "" 
    
    combined_str = "$ " + " = ".join(sym_parts) + " $"
    if fixed_coords:
        combined_str = ", ".join(fixed_coords) + ", " + combined_str
        
    return combined_str

# --- Main problem generation function ---

def generate_lines_problem():
    relationship_type = random.choice(['coincident', 'parallel', 'intersecting', 'skew'])
    
    # Initialize P1, v1 for L1 and P2, v2 for L2
    P1 = [0,0,0]
    v1 = _generate_non_zero_vector() # Ensure v1 is always a valid non-zero direction vector

    if relationship_type == 'coincident':
        P1 = [random.randint(-10, 10) for _ in range(3)]
        
        # v2 is a non-zero scalar multiple of v1
        k = random.choice([-2, -1, 1, 2])
        v2 = _scalar_multiply_vector(v1, k)
        
        # P2 is also on L1. The simplest way is to set P2 = P1.
        P2 = P1 
        
    elif relationship_type == 'parallel':
        P1 = [random.randint(-10, 10) for _ in range(3)]
        
        # v2 is a non-zero scalar multiple of v1
        k = random.choice([-2, -1, 1, 2])
        v2 = _scalar_multiply_vector(v1, k)
        
        # P2 is NOT on L1.
        # Generate an offset vector that is not parallel to v1.
        offset = _generate_offset_not_parallel(v1)
        P2 = _add_vectors(P1, offset)
    
    elif relationship_type == 'intersecting':
        # Choose an intersection point I
        I = [random.randint(-10, 10) for _ in range(3)]
        P1 = I
        P2 = I # Both lines pass through I
        
        # Generate v1 and v2 that are not parallel
        while True:
            v1 = _generate_non_zero_vector()
            v2 = _generate_non_zero_vector()
            if not _are_vectors_parallel(v1, v2):
                break
                
    elif relationship_type == 'skew':
        # Generate L1 (P1, v1)
        P1 = [random.randint(-10, 10) for _ in range(3)]
        v1 = _generate_non_zero_vector()
        
        # Generate L2 (P2, v2)
        # Ensure v1 and v2 are not parallel AND (P2-P1) is not coplanar with v1, v2
        while True:
            v2 = _generate_non_zero_vector()
            if _are_vectors_parallel(v1, v2):
                continue # v1 and v2 must not be parallel
            
            P2 = [random.randint(-10, 10) for _ in range(3)]
            
            # Check scalar triple product: (P2-P1) . (v1 x v2) != 0
            # If (P2-P1) is coplanar with v1 and v2, scalar triple product is 0.
            # We want them NOT coplanar for skew lines.
            P1P2_vec = _subtract_vectors(P2, P1)
            cross_prod_v1_v2 = _cross_product(v1, v2)
            
            scalar_triple_prod = _dot_product(P1P2_vec, cross_prod_v1_v2)
            
            if scalar_triple_prod != 0:
                break # Found skew lines
    
    line1_str = _format_line_equation(P1, v1)
    line2_str = _format_line_equation(P2, v2)
    
    question_text = f"判斷直線 $L_1$ 與 $L_2$ 的相交情形：<br>$L_1$: {line1_str}<br>$L_2$: {line2_str}"
    
    # Answer should be one of "平行", "重合", "交於一點", "歪斜"
    correct_answer = ""
    if relationship_type == 'coincident':
        correct_answer = "重合"
    elif relationship_type == 'parallel':
        correct_answer = "平行"
    elif relationship_type == 'intersecting':
        correct_answer = "交於一點"
    elif relationship_type == 'skew':
        correct_answer = "歪斜"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def generate(level=1):
    """
    生成「探討空間中兩直線的四種關係」相關題目。
    """
    # Currently, level is not used to vary difficulty, but it could be extended
    # to control number ranges or complexity of equations.
    return generate_lines_problem()

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    # Normalize answers for case-insensitive comparison
    user_answer_normalized = user_answer.strip().lower().replace(" ", "")
    correct_answer_normalized = correct_answer.strip().lower().replace(" ", "")
    
    is_correct = (user_answer_normalized == correct_answer_normalized)
    
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}