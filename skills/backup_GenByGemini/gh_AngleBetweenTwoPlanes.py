import random
import math
from fractions import Fraction

def _format_plane_equation(vec_coeffs, D):
    """
    Formats a normal vector (A, B, C) and constant D into a LaTeX-ready plane equation string.
    Example: (1, 2, -1), 3 -> "x + 2y - z = 3"
    """
    parts = []
    labels = ['x', 'y', 'z']
    
    for i, coeff in enumerate(vec_coeffs):
        if coeff == 0:
            continue
        
        term_str = ""
        if abs(coeff) == 1:
            term_str = labels[i]
        else:
            term_str = f"{abs(coeff)}{labels[i]}"
        
        if coeff < 0:
            parts.append(f"- {term_str}")
        elif parts: # Positive, but not the first term (needs a + sign)
            parts.append(f"+ {term_str}")
        else: # Positive and first term (no + sign needed)
            parts.append(term_str)
            
    # This case should ideally not happen for a valid normal vector (A,B,C not all zero)
    if not parts: 
        return "0 = 0" 
        
    return " ".join(parts) + f" = {D}"

def generate_angle_problem():
    """
    Generates a problem to find the acute angle between two planes.
    The normal vectors are carefully constructed to yield 'nice' angles (45, 60, 90 degrees).
    """
    def _get_random_constant():
        """Generates a random integer for the plane constant D."""
        return random.randint(-10, 10)

    problem_type = random.choice(['45_deg', '60_deg', '90_deg'])
    n1, n2 = None, None
    target_angle_degrees = 0

    if problem_type == '90_deg':
        target_angle_degrees = 90
        # Generate n1=(A,B,C) with A,B,C non-zero for more interesting problems
        A = random.randint(1, 4) * random.choice([-1, 1])
        B = random.randint(1, 4) * random.choice([-1, 1])
        C = random.randint(1, 4) * random.choice([-1, 1])
        n1 = (A, B, C)
        
        # Find an orthogonal vector n2 by setting one component to 0 and swapping/negating others.
        choice = random.randint(0, 2)
        if choice == 0: # n2 = (0, -C, B)
            n2_base = (0, -C, B)
        elif choice == 1: # n2 = (-C, 0, A)
            n2_base = (-C, 0, A)
        else: # choice == 2: # n2 = (-B, A, 0)
            n2_base = (-B, A, 0)
        
        # Apply a random sign flip to the entire n2 vector for more variety
        if random.random() < 0.5:
            n2 = tuple(-x for x in n2_base)
        else:
            n2 = n2_base

    elif problem_type == '45_deg':
        target_angle_degrees = 45
        # Structure (k,0,0) and (k,k,0) after permutation and signs
        k_val = random.randint(1, 4) * random.choice([-1, 1])
        
        # Choose which component is the single non-zero one for n1
        n1_primary_idx = random.randint(0, 2)
        n1_coeffs = [0, 0, 0]
        n1_coeffs[n1_primary_idx] = k_val
        n1 = tuple(n1_coeffs)
        
        # Choose which *other* component is the second non-zero one for n2
        n2_secondary_idx = random.choice([i for i in range(3) if i != n1_primary_idx])
        n2_coeffs = [0, 0, 0]
        n2_coeffs[n1_primary_idx] = k_val # Share one component value
        n2_coeffs[n2_secondary_idx] = k_val # Second component for 1/sqrt(2) ratio
        n2 = tuple(n2_coeffs)
        
        # Apply random sign flips to both vectors independently for more variety
        if random.random() < 0.5: n1 = tuple(-x for x in n1)
        if random.random() < 0.5: n2 = tuple(-x for x in n2)
        
    elif problem_type == '60_deg':
        target_angle_degrees = 60
        # Use the (x,y,z), (x,z,-y) pattern where x^2 = y^2+z^2 (e.g., from Pythagorean triples)
        # Select base (leg1, leg2, hypotenuse) from small Pythagorean triples
        y_base, z_base, x_base = random.choice([(3,4,5), (4,3,5)]) 
        
        # Randomly assign x_base, y_base, z_base to (A,B,C) coordinates for n1
        n1_mapping_indices = list(range(3))
        random.shuffle(n1_mapping_indices) # This determines which (x_base, y_base, z_base) goes to which component index.
        
        n1_coeffs = [0, 0, 0]
        n2_coeffs = [0, 0, 0]
        
        # Assign components to n1 based on shuffled_indices and original (x,y,z) pattern
        n1_coeffs[n1_mapping_indices[0]] = x_base # Corresponds to 'x' in (x,y,z)
        n1_coeffs[n1_mapping_indices[1]] = y_base # Corresponds to 'y' in (x,y,z)
        n1_coeffs[n1_mapping_indices[2]] = z_base # Corresponds to 'z' in (x,y,z)
        
        # For n2, the pattern is (x,z,-y). Use the same mapping for components.
        n2_coeffs[n1_mapping_indices[0]] = x_base  # Corresponds to 'x'
        n2_coeffs[n1_mapping_indices[1]] = z_base  # Corresponds to 'z'
        n2_coeffs[n1_mapping_indices[2]] = -y_base # Corresponds to '-y'
        
        n1 = tuple(n1_coeffs)
        n2 = tuple(n2_coeffs)
        
        # Apply random sign flips to both vectors for variety
        if random.random() < 0.5: n1 = tuple(-c for c in n1)
        if random.random() < 0.5: n2 = tuple(-c for c in n2)

    D1 = _get_random_constant()
    D2 = _get_random_constant()
    
    plane_eq1 = _format_plane_equation(n1, D1)
    plane_eq2 = _format_plane_equation(n2, D2)
    
    question_text = (
        f"求兩平面 $E_1 : {plane_eq1}$ 與 $E_2 : {plane_eq2}$ 的夾角。"
        f"請回答銳角，單位為度。"
    )
    correct_answer = str(target_angle_degrees)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    Main function to generate a problem for the angle between two planes.
    """
    return generate_angle_problem()

def check(user_answer, correct_answer):
    """
    Checks if the user's answer for the angle between planes is correct.
    Answers are expected in integer degrees.
    """
    try:
        user_num = float(user_answer.strip())
        correct_num = float(correct_answer.strip())
        
        # For 'nice' degree answers, an exact match is expected.
        # A small tolerance is included for floating point safety, though it should not be strictly needed here.
        tolerance = 1e-9 
        is_correct = abs(user_num - correct_num) < tolerance
        
        result_text = f"完全正確！答案是 ${correct_answer}^\\circ$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}^\\circ$"
        return {"correct": is_correct, "result": result_text, "next_question": True}
    except ValueError:
        return {"correct": False, "result": "請輸入一個有效的數字。", "next_question": False}