import random
import math # For math.isclose in check function

# Helper functions for vector operations
def _dot_product(v1, v2):
    """Calculates the dot product of two 3D vectors."""
    return v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2]

def _cross_product(v1, v2):
    """Calculates the cross product of two 3D vectors."""
    x = v1[1]*v2[2] - v1[2]*v2[1]
    y = v1[2]*v2[0] - v1[0]*v2[2]
    z = v1[0]*v2[1] - v1[1]*v2[0]
    return (x, y, z)

def _scalar_triple_product(a, b, c):
    """Calculates the scalar triple product (a x b) . c."""
    return _dot_product(_cross_product(a, b), c)

def _vec_to_str(v):
    """Formats a 3D vector into a string like (x,y,z). Handles 'k' as a component."""
    return f"({v[0]},{v[1]},{v[2]})"

def _generate_vector(min_coord=-5, max_coord=5, allow_zero_vector=False):
    """Generates a 3D vector with integer coordinates within the specified range."""
    while True:
        vec = (random.randint(min_coord, max_coord),
               random.randint(min_coord, max_coord),
               random.randint(min_coord, max_coord))
        if allow_zero_vector or any(x != 0 for x in vec):
            return vec

def generate(level=1):
    """
    Generates a problem related to the volume of a parallelepiped.
    """
    problem_types = ['type_A', 'type_B']
    if level >= 2:
        problem_types.append('type_C')
    
    problem_type = random.choice(problem_types)

    if problem_type == 'type_A':
        return _generate_type_A_problem(level)
    elif problem_type == 'type_B':
        return _generate_type_B_problem(level)
    else: # type_C
        return _generate_type_C_problem(level)

def _generate_type_A_problem(level):
    """
    Generates a problem where vec_a and vec_b x vec_c are given, find volume.
    """
    # Adjust coordinate range based on level for complexity
    min_c, max_c = (-5, 5) if level == 1 else (-8, 8)

    vec_a = _generate_vector(min_c, max_c)
    vec_b_cross_c = _generate_vector(min_c, max_c)

    # Volume V = |a . (b x c)|
    volume = abs(_dot_product(vec_a, vec_b_cross_c))

    question_text = (
        f"求由向量 $\\vec{{a}}={_vec_to_str(vec_a)}$ 與 $\\vec{{b}} \\times \\vec{{c}} = {_vec_to_str(vec_b_cross_c)}$ "
        f"所決定的平行六面體之體積。"
    )
    correct_answer = str(volume)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def _generate_type_B_problem(level):
    """
    Generates a problem where vec_a, vec_b, vec_c are given, find volume.
    """
    # Adjust coordinate range based on level for complexity
    min_c, max_c = (-3, 3) if level == 1 else (-5, 5)

    while True:
        vec_a = _generate_vector(min_c, max_c)
        vec_b = _generate_vector(min_c, max_c)
        vec_c = _generate_vector(min_c, max_c)
        
        # Calculate scalar triple product to get the signed volume
        stp_val = _scalar_triple_product(vec_a, vec_b, vec_c)
        
        # Ensure that for higher levels, the volume is not often zero,
        # unless specifically designed for that edge case.
        # If all vectors are (0,0,0) it's zero. If two are parallel, it's zero. If coplanar, it's zero.
        # Random generation typically avoids these frequently, but a quick check helps.
        # Allow zero volume occasionally for level 1 for completeness
        if level <= 1 or abs(stp_val) > 0 or random.random() < 0.1: 
            break

    volume = abs(stp_val)

    question_text = (
        f"求由向量 $\\vec{{a}}={_vec_to_str(vec_a)}$, $\\vec{{b}}={_vec_to_str(vec_b)}$, $\\vec{{c}}={_vec_to_str(vec_c)}$ "
        f"所決定的平行六面體之體積。"
    )
    correct_answer = str(volume)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def _generate_type_C_problem(level):
    """
    Generates a problem where vec_a, vec_b, vec_c (one component is 'k'), and volume are given, find k.
    """
    min_coord, max_coord = (-2, 2) if level == 2 else (-3, 3) # Keep coefficients small for simpler algebra

    while True:
        # Generate three base vectors, ensuring they are distinct enough
        v1_base = _generate_vector(min_coord, max_coord)
        v2_base = _generate_vector(min_coord, max_coord)
        v3_base = _generate_vector(min_coord, max_coord)
        
        # Avoid all-zero vectors or trivial cases leading to A_coeff = 0 (k disappears)
        if all(x == 0 for x in v1_base) or all(x == 0 for x in v2_base) or all(x == 0 for x in v3_base):
            continue

        # Randomly choose one vector (vec_a, vec_b, or vec_c) to insert 'k'
        vec_k_idx = random.randint(0, 2) 
        # Randomly choose which component (x, y, or z) gets 'k'
        comp_k_idx = random.randint(0, 2) 

        # Temporarily use lists to modify components, then convert to tuples for _scalar_triple_product
        # We model det(M) = A*k + B, where A is the coefficient of k, B is the constant part.
        
        # Calculate A_coeff (coefficient of k)
        # This corresponds to the minor of the element where 'k' is placed, with appropriate sign.
        A_coeff = 0
        if vec_k_idx == 0: # k is in vec_a
            if comp_k_idx == 0: A_coeff = v2_base[1]*v3_base[2] - v2_base[2]*v3_base[1]
            elif comp_k_idx == 1: A_coeff = -(v2_base[0]*v3_base[2] - v2_base[2]*v3_base[0])
            else: A_coeff = v2_base[0]*v3_base[1] - v2_base[1]*v3_base[0]
        elif vec_k_idx == 1: # k is in vec_b
            if comp_k_idx == 0: A_coeff = -(v1_base[1]*v3_base[2] - v1_base[2]*v3_base[1])
            elif comp_k_idx == 1: A_coeff = v1_base[0]*v3_base[2] - v1_base[2]*v3_base[0]
            else: A_coeff = -(v1_base[0]*v3_base[1] - v1_base[1]*v3_base[0])
        else: # k is in vec_c
            if comp_k_idx == 0: A_coeff = v1_base[1]*v2_base[2] - v1_base[2]*v2_base[1]
            elif comp_k_idx == 1: A_coeff = -(v1_base[0]*v2_base[2] - v1_base[2]*v2_base[0])
            else: A_coeff = v1_base[0]*v2_base[1] - v1_base[1]*v2_base[0]

        if A_coeff == 0: # If A_coeff is 0, k has no effect on the determinant, leading to non-unique or no solution.
            continue 

        # Calculate B_const (the constant part of the determinant, when k=0)
        temp_v1 = list(v1_base)
        temp_v2 = list(v2_base)
        temp_v3 = list(v3_base)
        
        # Set the k-component to 0 for B_const calculation
        if vec_k_idx == 0: temp_v1[comp_k_idx] = 0
        elif vec_k_idx == 1: temp_v2[comp_k_idx] = 0
        else: temp_v3[comp_k_idx] = 0
        
        B_const = _scalar_triple_product(tuple(temp_v1), tuple(temp_v2), tuple(temp_v3))

        # Generate a "nice" integer value for k that will be the actual solution
        # This helps ensure the problem has a clean integer answer.
        k_solution = random.randint(-5, 5)
        if k_solution == 0: # Avoid k=0 too frequently or for very simple determinants
            k_solution = random.choice([-1, 1, 2, -2])

        # Calculate the target volume based on this k_solution
        target_det_val = A_coeff * k_solution + B_const
        target_volume = abs(target_det_val)

        if target_volume == 0: # Ensure non-zero volume for a meaningful 'find k' problem
            continue
        
        # Now, prepare the vectors for display, with 'k' inserted
        display_a = list(v1_base)
        display_b = list(v2_base)
        display_c = list(v3_base)

        if vec_k_idx == 0:
            display_a[comp_k_idx] = 'k'
            vec_a_str = _vec_to_str(tuple(display_a))
            vec_b_str = _vec_to_str(v2_base)
            vec_c_str = _vec_to_str(v3_base)
        elif vec_k_idx == 1:
            display_b[comp_k_idx] = 'k'
            vec_a_str = _vec_to_str(v1_base)
            vec_b_str = _vec_to_str(tuple(display_b))
            vec_c_str = _vec_to_str(v3_base)
        else: # vec_k_idx == 2
            display_c[comp_k_idx] = 'k'
            vec_a_str = _vec_to_str(v1_base)
            vec_b_str = _vec_to_str(v2_base)
            vec_c_str = _vec_to_str(tuple(display_c))

        # Calculate all possible values of k
        # |A_coeff * k + B_const| = target_volume
        # Case 1: A_coeff * k + B_const = target_volume
        # Case 2: A_coeff * k + B_const = -target_volume
        
        k1_num = target_volume - B_const
        k1_den = A_coeff
        k2_num = -target_volume - B_const
        k2_den = A_coeff

        # Check for integer solutions
        if k1_num % k1_den != 0 or k2_num % k2_den != 0:
            continue # If solutions are not integers, regenerate to keep problems simpler for now.

        k1_sol = k1_num // k1_den
        k2_sol = k2_num // k2_den
        
        # Store unique integer solutions, comma-separated
        solutions = sorted(list(set([k1_sol, k2_sol])))
        correct_answer_str = ", ".join(map(str, solutions))

        question_text = (
            f"已知向量 $\\vec{{a}}={vec_a_str}$, $\\vec{{b}}={vec_b_str}$, $\\vec{{c}}={vec_c_str}$ "
            f"所決定的平行六面體之體積為 ${target_volume}$，求實數 $k$ 的值。"
        )

        # The 'answer' field can store one of the correct solutions.
        # The 'correct_answer' field should store all acceptable solutions for the checker.
        return {
            "question_text": question_text,
            "answer": str(k_solution), # One valid solution for problem generation
            "correct_answer": correct_answer_str # All valid solutions for checking
        }

def check(user_answer, correct_answer):
    """
    Checks if the user's answer for the parallelepiped volume problem is correct.
    Handles multiple correct answers (e.g., for finding 'k').
    """
    user_answer_str = user_answer.strip()
    correct_answers_str_list = [ans.strip() for ans in correct_answer.split(',')]

    is_correct = False
    
    try:
        user_val = float(user_answer_str)
        
        for ans_str in correct_answers_str_list:
            correct_val = float(ans_str)
            # Use math.isclose for float comparison to handle potential precision issues
            if math.isclose(user_val, correct_val, rel_tol=1e-9, abs_tol=1e-9):
                is_correct = True
                break
        
        if is_correct:
            # If there's only one correct answer, display it simply.
            # If multiple, display the example format.
            if len(correct_answers_str_list) == 1:
                feedback_msg = f"完全正確！答案是 ${correct_answers_str_list[0]}$。"
            else:
                feedback_msg = f"完全正確！一個可能的答案是 ${user_answer_str}$。所有可能答案為 ${correct_answer}$。"
        else:
            feedback_msg = f"答案不正確。正確答案應為：${correct_answer}$"

    except ValueError:
        feedback_msg = f"輸入格式不正確，請輸入數字。正確答案應為：${correct_answer}$"

    return {"correct": is_correct, "result": feedback_msg, "next_question": True}