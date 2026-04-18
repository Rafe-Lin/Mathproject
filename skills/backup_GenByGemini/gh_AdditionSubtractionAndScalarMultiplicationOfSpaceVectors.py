import random
import math
from fractions import Fraction
import re

# --- Helper functions for vector operations ---
def _vec_add(v1, v2):
    """Adds two 3D vectors."""
    return tuple(v1[i] + v2[i] for i in range(3))

def _vec_sub(v1, v2):
    """Subtracts two 3D vectors (v1 - v2)."""
    return tuple(v1[i] - v2[i] for i in range(3))

def _vec_scalar_mult(scalar, vec):
    """Multiplies a 3D vector by a scalar."""
    return tuple(scalar * vec[i] for i in range(3))

def _vec_to_latex(vec):
    """Formats a 3D vector tuple as a LaTeX string."""
    # Double curly braces for f-string, but here only for Python tuple formatting
    return f"({vec[0]}, {vec[1]}, {vec[2]})"

def _simplify_sqrt(n):
    """
    Simplifies sqrt(n). For level 1, returns integer if n is a perfect square,
    otherwise returns '\\sqrt{n}' as a LaTeX string.
    """
    if n < 0:
        raise ValueError("Magnitude cannot be negative.")
    if n == 0:
        return "0"
    
    s = int(math.sqrt(n))
    if s * s == n:
        return str(s)
    else:
        return r"\\sqrt{" + str(n) + r"}"

def _is_parallel(v1, v2):
    """
    Checks if two 3D vectors are parallel.
    Handles zero vectors appropriately.
    """
    is_v1_zero = all(c == 0 for c in v1)
    is_v2_zero = all(c == 0 for c in v2)

    if is_v1_zero and is_v2_zero:
        return True # Both are zero vectors, considered parallel

    if is_v1_zero or is_v2_zero:
        return False # One is zero, the other isn't. Not parallel.
    
    # Find a non-zero component to determine the scalar k
    k = None
    for i in range(3):
        if v1[i] != 0:
            k = Fraction(v2[i], v1[i])
            break
        elif v2[i] != 0: # If v1[i] is 0 but v2[i] is not, they cannot be parallel
            return False 
    
    if k is None: # This case should theoretically be covered by the zero vector checks
        return False

    # Check consistency for all components
    for i in range(3):
        if v1[i] * k != v2[i]:
            return False
            
    return True

# --- Problem Generation Functions ---
def generate_vector_operation_and_magnitude_problem():
    """Generates a problem involving vector addition, subtraction, scalar multiplication, and magnitude."""
    num_vectors = random.choice([2, 3]) # Use 2 or 3 vectors

    vec_a = tuple(random.randint(-5, 5) for _ in range(3))
    vec_b = tuple(random.randint(-5, 5) for _ in range(3))

    coeff_a = random.choice([x for x in range(-3, 4) if x != 0])
    coeff_b = random.choice([x for x in range(-3, 4) if x != 0])
    
    expression_parts = [f"{coeff_a}\\vec{{a}}"]
    calculation_vec = _vec_scalar_mult(coeff_a, vec_a)

    op_b_sign = "+" if coeff_b > 0 else ""
    expression_parts.append(f"{op_b_sign}{coeff_b}\\vec{{b}}")
    calculation_vec = _vec_add(calculation_vec, _vec_scalar_mult(coeff_b, vec_b))

    if num_vectors == 3:
        vec_c = tuple(random.randint(-5, 5) for _ in range(3))
        coeff_c = random.choice([x for x in range(-3, 4) if x != 0])
        op_c_sign = "+" if coeff_c > 0 else ""
        expression_parts.append(f"{op_c_sign}{coeff_c}\\vec{{c}}")
        calculation_vec = _vec_add(calculation_vec, _vec_scalar_mult(coeff_c, vec_c))

    expression_str = "".join(expression_parts)
    
    result_magnitude_sq = sum(c**2 for c in calculation_vec)
    magnitude_str = _simplify_sqrt(result_magnitude_sq)

    question_text = f"已知向量 $\\vec{{a}}={_vec_to_latex(vec_a)}$, $\\vec{{b}}={_vec_to_latex(vec_b)}$"
    if num_vectors == 3:
        question_text += f", $\\vec{{c}}={_vec_to_latex(vec_c)}$"
    
    question_text += f"。求向量 ${expression_str}$ 及其長度 $|{expression_str}|$。"
    question_text += r"<br> (請以 $(x,y,z)$;長度 的格式作答，例如：$(-3,1,2)$;$\\sqrt{14}$ 或 $(3,6,2)$;7)"

    correct_answer_vec = _vec_to_latex(calculation_vec)
    correct_answer = f"{correct_answer_vec};{magnitude_str}"

    return {
        "question_text": question_text,
        "answer": correct_answer, # For internal use in check
        "correct_answer": correct_answer # This is what the user input is compared against
    }

def generate_collinearity_check_problem():
    """Generates a problem to check collinearity of three points."""
    is_collinear = random.choice([True, False])

    # Generate point A
    A = tuple(random.randint(-10, 10) for _ in range(3))

    # Generate point B, ensuring B != A
    while True:
        B = tuple(random.randint(-10, 10) for _ in range(3))
        if B != A:
            break

    vec_AB_base = _vec_sub(B, A)

    if is_collinear:
        # Generate C such that A, B, C are collinear
        # vec_AC = k * vec_AB, k can be any non-zero, non-one scalar to ensure C is distinct from A and B
        k = random.choice([x for x in range(-3, 4) if x != 0 and x != 1])
        vec_AC_base = _vec_scalar_mult(k, vec_AB_base)
        C = _vec_add(A, vec_AC_base)
    else:
        # Generate C such that A, B, C are not collinear
        # Ensure vec_AC is not parallel to vec_AB
        while True:
            C_temp = tuple(random.randint(-10, 10) for _ in range(3))
            if C_temp == A or C_temp == B: # C must be distinct from A and B
                continue
            vec_AC_temp = _vec_sub(C_temp, A)
            if not _is_parallel(vec_AB_base, vec_AC_temp):
                C = C_temp
                break
            # If A,B,C_temp are collinear, try again with a different C_temp

    # Calculate vectors for the question
    vec_AB_calc = _vec_sub(B, A)
    vec_AC_calc = _vec_sub(C, A)

    question_text = f"已知 $A{_vec_to_latex(A)}$, $B{_vec_to_latex(B)}$ 與 $C{_vec_to_latex(C)}$ 為空間中三點。<br>"
    question_text += r"(1) 求向量 $\vec{{AB}}$ 及 $\vec{{AC}}$。<br>"
    question_text += r"(2) 判斷 $A$, $B$, $C$ 三點是否共線？(請填'是'或'否')<br>"
    question_text += r"(請以 $(x_{AB},y_{AB},z_{AB})$;$(x_{AC},y_{AC},z_{AC})$;是/否 的格式作答)"

    # Final check for collinearity based on generated points
    correct_collinear_answer = '是' if _is_parallel(vec_AB_calc, vec_AC_calc) else '否'
    correct_answer = f"{_vec_to_latex(vec_AB_calc)};{_vec_to_latex(vec_AC_calc)};{correct_collinear_answer}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    Generates a problem related to space vector operations or collinearity.
    """
    problem_type = random.choice(['vector_operation_and_magnitude', 'collinearity_check'])
    
    if problem_type == 'vector_operation_and_magnitude':
        return generate_vector_operation_and_magnitude_problem()
    elif problem_type == 'collinearity_check':
        return generate_collinearity_check_problem()

# --- Answer Checking Function ---
def _parse_vector_string(vec_str):
    """Parses a string like '(x,y,z)' into a tuple of integers."""
    vec_str = vec_str.replace('$', '').strip() # Remove any LaTeX dollar signs
    match = re.match(r"\(([-+]?\d+)\s*,\s*([-+]?\d+)\s*,\s*([-+]?\d+)\)", vec_str)
    if match:
        return tuple(int(x) for x in match.groups())
    return None

def _parse_magnitude_string(mag_str):
    """Parses a magnitude string (integer, '\\sqrt{N}', or k'\\sqrt{N}') into a float."""
    mag_str = mag_str.replace('$', '').strip() # Remove any LaTeX dollar signs
    
    # Handle simple integer
    if mag_str.isdigit() or (mag_str.startswith('-') and mag_str[1:].isdigit()):
        return float(mag_str)
    
    # Handle \\sqrt{N}
    match_sqrt = re.match(r"\\sqrt\{(\d+)\}", mag_str)
    if match_sqrt:
        return math.sqrt(int(match_sqrt.group(1)))
    
    # Handle k\\sqrt{N} (not currently generated by _simplify_sqrt, but good for robustness)
    match_ksqrtn = re.match(r"(\d+)\\sqrt\{(\d+)\}", mag_str)
    if match_ksqrtn:
        k = int(match_ksqrtn.group(1))
        n = int(match_ksqrtn.group(2))
        return k * math.sqrt(n)

    return None # Unable to parse

def check(user_answer, correct_answer):
    """
    Checks the user's answer against the correct answer.
    Answers are expected to be semi-colon separated strings.
    """
    user_parts = [p.strip() for p in user_answer.split(';')]
    correct_parts = [p.strip() for p in correct_answer.split(';')]

    is_correct = True
    feedback_messages = []

    if len(user_parts) != len(correct_parts):
        is_correct = False
        feedback_messages.append(f"您的答案格式不正確。應為 {len(correct_parts)} 個部分，但您提供了 {len(user_parts)} 個。")
        
    else:
        # Determine problem type based on number of parts
        if len(correct_parts) == 2: # Vector operation and magnitude problem: Vector;Magnitude
            # Part 1: Vector comparison
            user_vec = _parse_vector_string(user_parts[0])
            correct_vec = _parse_vector_string(correct_parts[0])
            
            if user_vec is None:
                is_correct = False
                feedback_messages.append(f"向量格式不正確，應為 $(x,y,z)$。")
            elif user_vec != correct_vec:
                is_correct = False
                feedback_messages.append(f"向量部分錯誤。您的答案是 ${_vec_to_latex(user_vec)}$，正確應為 ${_vec_to_latex(correct_vec)}$。")
            else:
                feedback_messages.append(f"向量部分正確。")

            # Part 2: Magnitude comparison
            user_mag_val = _parse_magnitude_string(user_parts[1])
            correct_mag_val = _parse_magnitude_string(correct_parts[1])
            
            if user_mag_val is None:
                is_correct = False
                feedback_messages.append(f"長度格式不正確。")
            elif not math.isclose(user_mag_val, correct_mag_val, rel_tol=1e-9):
                is_correct = False
                feedback_messages.append(f"長度部分錯誤。您的答案是 ${user_parts[1].replace('$', '')}$，正確應為 ${correct_parts[1].replace('$', '')}$。")
            else:
                feedback_messages.append(f"長度部分正確。")

        elif len(correct_parts) == 3: # Collinearity check problem: VecAB;VecAC;CollinearDecision
            # Part 1: Vector AB comparison
            user_vec_ab = _parse_vector_string(user_parts[0])
            correct_vec_ab = _parse_vector_string(correct_parts[0])

            if user_vec_ab is None:
                is_correct = False
                feedback_messages.append(f"向量 $\\vec{{AB}}$ 格式不正確。")
            elif user_vec_ab != correct_vec_ab:
                is_correct = False
                feedback_messages.append(f"向量 $\\vec{{AB}}$ 錯誤。您的答案是 ${_vec_to_latex(user_vec_ab)}$，正確應為 ${_vec_to_latex(correct_vec_ab)}$。")
            else:
                feedback_messages.append(f"向量 $\\vec{{AB}}$ 正確。")

            # Part 2: Vector AC comparison
            user_vec_ac = _parse_vector_string(user_parts[1])
            correct_vec_ac = _parse_vector_string(correct_parts[1])

            if user_vec_ac is None:
                is_correct = False
                feedback_messages.append(f"向量 $\\vec{{AC}}$ 格式不正確。")
            elif user_vec_ac != correct_vec_ac:
                is_correct = False
                feedback_messages.append(f"向量 $\\vec{{AC}}$ 錯誤。您的答案是 ${_vec_to_latex(user_vec_ac)}$，正確應為 ${_vec_to_latex(correct_vec_ac)}$。")
            else:
                feedback_messages.append(f"向量 $\\vec{{AC}}$ 正確。")

            # Part 3: Collinearity decision comparison
            user_decision = user_parts[2].upper()
            correct_decision = correct_parts[2].upper()

            if user_decision not in ['是', '否']:
                is_correct = False
                feedback_messages.append(f"判斷是否共線的答案格式不正確，請填寫'是'或'否'。")
            elif user_decision != correct_decision:
                is_correct = False
                feedback_messages.append(f"共線判斷錯誤。您的答案是 '{user_decision}'，正確應為 '{correct_decision}'。")
            else:
                feedback_messages.append(f"共線判斷正確。")
        else:
            is_correct = False
            feedback_messages.append("內部錯誤：無法識別問題類型。")

    result_text = "<br>".join(feedback_messages)
    if is_correct and not feedback_messages: # If all checks passed and no specific feedback was added, give a general correct message
         result_text = "完全正確！"

    return {"correct": is_correct, "result": result_text, "next_question": True}