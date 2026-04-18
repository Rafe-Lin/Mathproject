import random
from fractions import Fraction
import math
import re

# Helper functions for vector operations
def dot_product(v1, v2):
    return sum(c1 * c2 for c1, c2 in zip(v1, v2))

def magnitude_squared(v):
    return sum(c * c for c in v)

def scalar_multiply(k, v):
    return tuple(k * c for c in v)

def vector_subtract(v1, v2):
    return tuple(c1 - c2 for c1, c2 in zip(v1, v2))

def vector_magnitude(v):
    return math.sqrt(float(magnitude_squared(v))) # Convert Fraction to float for math.sqrt

def format_vector(v):
    # Formats a vector for LaTeX display, handling fractions
    formatted_components = []
    for c in v:
        if isinstance(c, Fraction):
            if c.denominator == 1:
                formatted_components.append(str(c.numerator))
            else:
                formatted_components.append(r"\\frac{{{}}}{{{}}}".format(c.numerator, c.denominator))
        else:
            formatted_components.append(str(c))
    return f"({', '.join(formatted_components)})"

def _simplify_sqrt(n):
    # Helper to simplify sqrt(n) into A*sqrt(B) string format for LaTeX
    # Assumes n is a non-negative integer.
    if n < 0:
        raise ValueError("Cannot simplify sqrt of negative number for real numbers")
    if n == 0:
        return "0"
    
    coeff = 1
    remainder = n
    for i in range(2, int(n**0.5) + 2): # Add 2 to upper bound for range to ensure square roots are checked fully
        while remainder % (i*i) == 0:
            coeff *= i
            remainder //= (i*i)
            
    if remainder == 1: # Perfect square, or no radical left (e.g., sqrt(1)=1, sqrt(4)=2)
        return str(coeff)
    elif coeff == 1: # Only radical part (e.g., sqrt(2))
        return r"\\sqrt{{{}}}".format(remainder)
    else: # Both coefficient and radical part (e.g., 2*sqrt(3))
        return f"{coeff}{r'\\sqrt{{{}}}'.format(remainder)}"

def _format_number_or_sqrt_fraction(frac_val):
    # This function takes a Fraction (representing a value *under* the sqrt, e.g., P/Q)
    # and returns its LaTeX simplified sqrt string (e.g., r"\\frac{2\\sqrt{5}}{5}" for sqrt(20/25)).
    
    if frac_val == 0:
        return "0"

    num_u = frac_val.numerator
    den_u = frac_val.denominator

    # We represent sqrt(num_u / den_u) as sqrt(num_u * den_u) / den_u for rationalization
    numerator_for_sqrt = num_u * den_u
    denominator_outside_sqrt = den_u

    simplified_radical_part = _simplify_sqrt(numerator_for_sqrt)

    if simplified_radical_part == "0": # Should be covered by initial frac_val check
        return "0"
    elif simplified_radical_part.isdigit(): # It's a plain integer (A), e.g., sqrt(4) = 2
        final_frac = Fraction(int(simplified_radical_part), denominator_outside_sqrt)
        if final_frac.denominator == 1:
            return str(final_frac.numerator)
        else:
            return r"\\frac{{{}}}{{{}}}".format(final_frac.numerator, final_frac.denominator)
    else: # It's like A\\sqrt{B} or \\sqrt{B}
        # Parse "A\\sqrt{B}" or "\\sqrt{B}"
        match_sqrt_pattern = re.match(r"(\d+)?\\sqrt{(\d+)}", simplified_radical_part)
        
        if match_sqrt_pattern:
            coeff_str = match_sqrt_pattern.group(1) # 'A' or None
            radical_val = match_sqrt_pattern.group(2) # 'B'
            
            coeff_num = int(coeff_str) if coeff_str else 1
            
            final_coeff_frac = Fraction(coeff_num, denominator_outside_sqrt)
            
            # Simplify final_coeff_frac
            final_coeff_frac = Fraction(final_coeff_frac.numerator, final_coeff_frac.denominator)

            if final_coeff_frac.numerator == 1 and final_coeff_frac.denominator == 1: # e.g. sqrt(B)
                return r"\\sqrt{{{}}}".format(radical_val)
            elif final_coeff_frac.denominator == 1: # e.g. A*sqrt(B)
                return f"{final_coeff_frac.numerator}{r'\\sqrt{{{}}}'.format(radical_val)}"
            else: # e.g. A*sqrt(B)/C
                return r"\\frac{{{}}}{{{}}}".format(f"{final_coeff_frac.numerator}{r'\\sqrt{{{}}}'.format(radical_val)}", final_coeff_frac.denominator)
        else:
            # Fallback for unexpected _simplify_sqrt output
            return f"ErrorFormattingSqrt({frac_val})" # This should not be reached with robust _simplify_sqrt


def generate(level=1):
    problem_type_weights = [
        ('projection_2d', 4),
        ('projection_3d', 3 if level > 1 else 0), # 3D only for higher levels
        ('decomposition_2d', 3),
        ('decomposition_3d', 2 if level > 1 else 0) # 3D only for higher levels
    ]
    
    # Filter out 3D problems if level is 1
    if level == 1:
        problem_type_weights = [(pt, weight) for pt, weight in problem_type_weights if '3d' not in pt]

    problem_types = [pt for pt, weight in problem_type_weights for _ in range(weight)]
    if not problem_types: # Fallback if all weights are zero
        problem_types = ['projection_2d']
        
    problem_type = random.choice(problem_types)

    num_dims = 3 if '3d' in problem_type else 2

    # Generate vector components
    min_val = -8 if level == 1 else -12
    max_val = 8 if level == 1 else 12
    
    vec_a = None
    vec_b = None

    # Ensure vectors are not zero vectors and have some non-trivial components
    def get_non_zero_vector(dims, min_v, max_v):
        while True:
            vec = tuple(random.randint(min_v, max_v) for _ in range(dims))
            if any(c != 0 for c in vec):
                return vec
            
    # For decomposition problems, `vec_a` is the vector to be decomposed (vec_c in examples)
    # and `vec_b` is the vector parallel to `v1` (vec_a in examples)
    if 'decomposition' in problem_type:
        vec_c_raw = get_non_zero_vector(num_dims, min_val, max_val)
        vec_a_raw = get_non_zero_vector(num_dims, min_val, max_val)
        vec_a_frac = tuple(Fraction(c) for c in vec_c_raw) # This is `vec_c` from example
        vec_b_frac = tuple(Fraction(c) for c in vec_a_raw) # This is `vec_a` from example
    else: # projection problems
        vec_a_raw = get_non_zero_vector(num_dims, min_val, max_val)
        vec_b_raw = get_non_zero_vector(num_dims, min_val, max_val)
        vec_a_frac = tuple(Fraction(c) for c in vec_a_raw)
        vec_b_frac = tuple(Fraction(c) for c in vec_b_raw)

    question_text = ""
    correct_answer = ""
    answer_display = ""
    
    # Calculate projection
    dot_prod = dot_product(vec_a_frac, vec_b_frac)
    mag_b_sq = magnitude_squared(vec_b_frac)
    
    # Avoid division by zero, though get_non_zero_vector should prevent mag_b_sq from being 0.
    if mag_b_sq == 0:
        projection_scalar = Fraction(0)
    else:
        projection_scalar = Fraction(dot_prod, mag_b_sq)
    
    proj_vec = scalar_multiply(projection_scalar, vec_b_frac)
    
    if 'projection' in problem_type:
        proj_length = vector_magnitude(proj_vec) # This is a float
        
        # Determine what to ask for
        ask_for_vec = random.choice([True, False]) # Ask for vector or length
        if random.random() < 0.3 and proj_length > 0: # Sometimes ask for both
            ask_for_vec = True
            ask_for_length = True
        else:
            ask_for_length = not ask_for_vec # If not vector, ask for length, and vice versa

        question_parts = []
        answer_parts = []

        question_text = f"已知 $\\vec{{a}}={format_vector(vec_a_raw)}$， $\\vec{{b}}={format_vector(vec_b_raw)}$。"

        if ask_for_vec:
            question_parts.append(f"求 $\\vec{{a}}$ 在 $\\vec{{b}}$ 上的正射影")
            answer_parts.append(f"$\\text{{proj}}_{{\\vec{{b}}}}\\vec{{a}} = {format_vector(proj_vec)}$")
        
        if ask_for_length:
            if ask_for_vec:
                question_parts.append("及正射影的長")
            else:
                question_parts.append(f"求 $\\vec{{a}}$ 在 $\\vec{{b}}$ 上的正射影的長")
            
            mag_sq_frac = magnitude_squared(proj_vec) # This is the value under the sqrt, as a Fraction
            proj_length_str = _format_number_or_sqrt_fraction(mag_sq_frac)
            
            answer_parts.append(f"$|\\text{{proj}}_{{\\vec{{b}}}}\\vec{{a}}| = {proj_length_str}$")
            
        question_text += f"{'，' if len(question_parts) > 1 else ''} {question_parts[0]}{question_parts[1] if len(question_parts) > 1 else ''}。"
        answer_display = " ".join(answer_parts)
        correct_answer = f"proj_vec={format_vector(proj_vec)}, proj_len={float(proj_length)}" # For check function

    elif 'decomposition' in problem_type:
        question_text = f"將向量 $\\vec{{c}}={format_vector(vec_a_raw)}$ 分解成兩個向量的和，其中一個向量與 $\\vec{{a}}={format_vector(vec_b_raw)}$ 平行，另一個向量與 $\\vec{{a}}$ 垂直。"
        
        v1_vec = proj_vec # This is proj_c_on_a
        v2_vec = vector_subtract(vec_a_frac, v1_vec) # This is c - proj_c_on_a
        
        answer_display = f"$\\vec{{c}} = {format_vector(v1_vec)} + {format_vector(v2_vec)}$"
        correct_answer = f"v1_vec={format_vector(v1_vec)}, v2_vec={format_vector(v2_vec)}"

    return {
        "question_text": question_text,
        "answer": answer_display, # For display only
        "correct_answer": correct_answer # For the check function
    }


def check(user_answer, correct_answer):
    user_answer = user_answer.strip().replace(' ', '')
    correct_answer_dict = {}
    
    # Parse correct_answer string
    parts = correct_answer.split(',')
    for part in parts:
        key, value = part.split('=', 1) # Split only on first '='
        if key.endswith("vec"):
            # Vector parsing: (x,y) or (x,y,z)
            coords_str = value[1:-1].split(',') # Remove parentheses
            correct_answer_dict[key] = tuple(Fraction(c) for c in coords_str)
        elif key == "proj_len":
            correct_answer_dict[key] = float(value)
    
    is_overall_correct = True
    feedback = []

    # Regex for parsing a single vector from the user's input
    # Handles integers, fractions, and decimals
    vec_component_pattern = r"-?\d+(?:/\d+)?(?:\.\d+)?"
    single_vec_pattern = rf"\(\s*({vec_component_pattern})\s*,\s*({vec_component_pattern})\s*(?:,\s*({vec_component_pattern})\s*)?\)"

    # --- Check for Decomposition (v1_vec, v2_vec) ---
    if "v1_vec" in correct_answer_dict and "v2_vec" in correct_answer_dict:
        # Try to find two vectors in the user's answer, potentially separated by '+'
        user_vectors = re.findall(single_vec_pattern, user_answer)
        
        parsed_v1 = None
        parsed_v2 = None

        if len(user_vectors) >= 2:
            parsed_v1_str_components = [c for c in user_vectors[0] if c] # Remove empty strings for 2D vec
            parsed_v2_str_components = [c for c in user_vectors[1] if c]

            if len(parsed_v1_str_components) == len(correct_answer_dict["v1_vec"]) and \
               len(parsed_v2_str_components) == len(correct_answer_dict["v2_vec"]):
                parsed_v1 = tuple(Fraction(c) for c in parsed_v1_str_components)
                parsed_v2 = tuple(Fraction(c) for c in parsed_v2_str_components)
        
        if parsed_v1 == correct_answer_dict["v1_vec"] and parsed_v2 == correct_answer_dict["v2_vec"]:
            feedback.append(f"向量分解正確。")
        else:
            is_overall_correct = False
            feedback.append(f"向量分解不正確。正確答案為 $\\vec{{c}} = {format_vector(correct_answer_dict['v1_vec'])} + {format_vector(correct_answer_dict['v2_vec'])}$。")
        
        # Remove these vectors from user_answer to avoid re-parsing for other parts
        # This is a bit tricky with `re.sub` for exact matches, so let's simplify by just replacing found vector patterns.
        user_answer = re.sub(single_vec_pattern, "", user_answer, count=2)


    # --- Check for Projection Vector (proj_vec) ---
    if "proj_vec" in correct_answer_dict:
        # If not already handled as part of decomposition, look for it.
        remaining_vectors = re.findall(single_vec_pattern, user_answer)
        
        parsed_proj_vec = None
        if len(remaining_vectors) >= 1:
            parsed_proj_vec_str_components = [c for c in remaining_vectors[0] if c]
            if len(parsed_proj_vec_str_components) == len(correct_answer_dict["proj_vec"]):
                parsed_proj_vec = tuple(Fraction(c) for c in parsed_proj_vec_str_components)
        
        if parsed_proj_vec == correct_answer_dict["proj_vec"]:
            feedback.append(f"正射影向量正確。")
        else:
            is_overall_correct = False
            feedback.append(f"正射影向量不正確。正確答案為 $\\text{{proj}}_{{\\vec{{b}}}}\\vec{{a}} = {format_vector(correct_answer_dict['proj_vec'])}$。")
        
        # Remove this vector from user_answer
        user_answer = re.sub(single_vec_pattern, "", user_answer, count=1)


    # --- Check for Projection Length (proj_len) ---
    if "proj_len" in correct_answer_dict:
        num_pattern = r"-?\d+(?:/\d+)?(?:\.\d+)?"
        
        # Try to find a number in the remaining user_answer
        len_match = re.search(num_pattern, user_answer)
        
        parsed_len = None
        if len_match:
            user_len_str = len_match.group(0) # The full matched number string
            try:
                parsed_len = float(Fraction(user_len_str))
            except ValueError:
                pass # parsed_len remains None

        if parsed_len is not None and math.isclose(parsed_len, correct_answer_dict["proj_len"], rel_tol=1e-9, abs_tol=1e-9):
            feedback.append(f"正射影的長度正確。")
        else:
            is_overall_correct = False
            feedback.append(f"正射影的長度不正確。正確答案是約 ${correct_answer_dict['proj_len']:.4f}$。")

    if not feedback: # If no correct answer type was found in user input
        is_overall_correct = False
        feedback.append("無法解析你的答案，請確保使用正確的格式。例如：\"(x,y), 長度=z\" 或 \"(v1_x,v1_y) + (v2_x,v2_y)\"")
    
    result_text = " ".join(feedback)
    if is_overall_correct:
        result_text = f"完全正確！{result_text}"
    else:
        result_text = f"答案不完全正確。{result_text}"

    return {"correct": is_overall_correct, "result": result_text, "next_question": True}