import random
from fractions import Fraction
import math

# Helper for formatting fractions into LaTeX strings
def format_fraction(num):
    if isinstance(num, Fraction):
        if num.denominator == 1:
            return str(num.numerator)
        # Use LaTeX \\frac for proper fraction display
        return f"\\frac{{{num.numerator}}}{{{num.denominator}}}"
    return str(num)

# Helper for formatting points or vectors into LaTeX-like strings
def format_point(x, y):
    return f"({format_fraction(x)}, {format_fraction(y)})"

# Helper for formatting 2x2 matrices into LaTeX strings
def format_matrix(matrix):
    a, b = matrix[0]
    c, d = matrix[1]
    return r"\begin{pmatrix} " \
           + format_fraction(a) + r" & " + format_fraction(b) + r" \\ " \
           + format_fraction(c) + r" & " + format_fraction(d) + r" \end{pmatrix}"

# Helper for matrix-vector multiplication (2x2 matrix by 2x1 vector)
def matrix_vector_multiply(matrix, vector):
    a, b = matrix[0]
    c, d = matrix[1]
    x, y = vector
    res_x = a * x + b * y
    res_y = c * x + d * y
    return [res_x, res_y]

# Helper for 2x2 matrix determinant
def matrix_determinant(matrix):
    a, b = matrix[0]
    c, d = matrix[1]
    return a * d - b * c

# Helper for 2x2 matrix inverse
def matrix_inverse(matrix):
    det = matrix_determinant(matrix)
    if det == 0:
        return None  # Matrix is singular
    a, b = matrix[0]
    c, d = matrix[1]
    inv_det = Fraction(1, det)
    # Inverse of [[a,b],[c,d]] is (1/det) * [[d,-b],[-c,a]]
    return [[d * inv_det, -b * inv_det],
            [-c * inv_det, a * inv_det]]

# Helper for 2x2 matrix by 2x2 matrix multiplication
def matrix_matrix_multiply(mat1, mat2):
    a, b = mat1[0]
    c, d = mat1[1]
    e, f = mat2[0]
    g, h = mat2[1]

    res_a = a * e + b * g
    res_b = a * f + b * h
    res_c = c * e + d * g
    res_d = c * f + d * h
    return [[res_a, res_b], [res_c, res_d]]

# Generates a random 2x2 matrix with Fraction elements
def generate_random_matrix(min_val, max_val, ensure_invertible=False):
    while True:
        a = Fraction(random.randint(min_val, max_val))
        b = Fraction(random.randint(min_val, max_val))
        c = Fraction(random.randint(min_val, max_val))
        d = Fraction(random.randint(min_val, max_val))
        matrix = [[a, b], [c, d]]
        if not ensure_invertible or matrix_determinant(matrix) != 0:
            return matrix

# Generates a random 2x1 vector (point) with Fraction elements
def generate_random_vector(min_val, max_val):
    x = Fraction(random.randint(min_val, max_val))
    y = Fraction(random.randint(min_val, max_val))
    return [x, y]

# Problem Type 1: Given A and P, find P' (A * P = P')
def generate_type1_problem():
    A = generate_random_matrix(-5, 5)
    P = generate_random_vector(-5, 5)
    P_prime = matrix_vector_multiply(A, P)

    question_text = f"設二階方陣 $A = {format_matrix(A)}$。<br>" \
                    f"已知 A 將 $P{format_point(P[0], P[1])}$ 對應到 $P'$ 點，求 $P'$ 點的坐標。"
    
    # Prefix "[POINT]" for the check function to identify the answer type
    correct_answer_str = f"[POINT]{format_point(P_prime[0], P_prime[1])}"

    return {
        "question_text": question_text,
        "answer": correct_answer_str,
        "correct_answer": correct_answer_str
    }

# Problem Type 2: Given A and P', find P (A * P = P' => P = A_inv * P')
def generate_type2_problem():
    A = generate_random_matrix(-5, 5, ensure_invertible=True)
    
    # Generate the original point P first, then compute P' (the given transformed point)
    P_original = generate_random_vector(-5, 5) 
    P_prime_given = matrix_vector_multiply(A, P_original)

    question_text = f"設二階方陣 $A = {format_matrix(A)}$。<br>" \
                    f"已知 A 將 $Q$ 點對應到 $Q'{format_point(P_prime_given[0], P_prime_given[1])}$，求 $Q$ 點的坐標。"
    
    correct_answer_str = f"[POINT]{format_point(P_original[0], P_original[1])}"

    return {
        "question_text": question_text,
        "answer": correct_answer_str,
        "correct_answer": correct_answer_str
    }

# Problem Type 3: Given P1->P1' and P2->P2', find A (A * [P1 P2] = [P1' P2'])
def generate_type3_problem():
    # Generate the correct matrix A first
    A_correct = generate_random_matrix(-3, 3) 
    
    while True:
        P1 = generate_random_vector(-3, 3)
        P2 = generate_random_vector(-3, 3)
        # Ensure P1 and P2 are distinct and form an invertible matrix M = [P1 P2]
        if P1 == P2:
            continue
        
        M = [[P1[0], P2[0]], [P1[1], P2[1]]]
        if matrix_determinant(M) != 0: 
            break

    P1_prime = matrix_vector_multiply(A_correct, P1)
    P2_prime = matrix_vector_multiply(A_correct, P2)

    question_text = f"已知二階方陣 A 分別將 $P{format_point(P1[0], P1[1])}$ 與 $Q{format_point(P2[0], P2[1])}$ " \
                    f"對應到 $P'{format_point(P1_prime[0], P1_prime[1])}$ 與 $Q'{format_point(P2_prime[0], P2_prime[1])}$，求 A。"
    
    # Prefix "[MATRIX]" for the check function
    correct_answer_str = f"[MATRIX]{format_matrix(A_correct)}"

    return {
        "question_text": question_text,
        "answer": correct_answer_str,
        "correct_answer": correct_answer_str
    }

# Problem Type 4: Given A and vector u, find vector v (A * u = v) - similar to Type 1
def generate_type4_problem():
    A = generate_random_matrix(-5, 5)
    u_vec = generate_random_vector(-5, 5)
    v_vec = matrix_vector_multiply(A, u_vec)

    question_text = f"設二階方陣 $A = {format_matrix(A)}$。<br>" \
                    f"已知 A 將向量 $\\vec{{u}} = {format_point(u_vec[0], u_vec[1])}$ 對應到向量 $\\vec{{v}}$，求向量 $\\vec{{v}}$。"
    
    correct_answer_str = f"[POINT]{format_point(v_vec[0], v_vec[1])}"

    return {
        "question_text": question_text,
        "answer": correct_answer_str,
        "correct_answer": correct_answer_str
    }

def generate(level=1):
    """
    生成「線性變換」相關題目。
    """
    problem_type_choice = random.choice(['type1', 'type2', 'type3', 'type4'])
    
    if problem_type_choice == 'type1':
        return generate_type1_problem()
    elif problem_type_choice == 'type2':
        return generate_type2_problem()
    elif problem_type_choice == 'type3':
        return generate_type3_problem()
    elif problem_type_choice == 'type4':
        return generate_type4_problem()

# Helper to parse a string representation of a fraction (e.g., "1/2" or "3")
def parse_fraction_string(s):
    s = s.strip()
    if '/' in s:
        try:
            parts = s.split('/')
            return Fraction(int(parts[0]), int(parts[1]))
        except ValueError:
            return None
    try:
        return Fraction(s) # Fraction can parse integer strings directly
    except ValueError:
        return None

# Helper to parse a string representation of a point/vector (e.g., "(1/2, -3)")
def parse_point_or_vector_string(ans_str):
    ans_str = ans_str.strip()
    if not (ans_str.startswith('(') and ans_str.endswith(')')):
        return None
    
    content = ans_str[1:-1] # Remove parentheses
    parts = content.split(',')
    if len(parts) != 2:
        return None
    
    x = parse_fraction_string(parts[0])
    y = parse_fraction_string(parts[1])
    
    if x is None or y is None:
        return None
    
    return (x, y)

# Helper to parse a string representation of a 2x2 matrix
def parse_matrix_string(ans_str):
    # This parser needs to handle a few common variations:
    # 1. LaTeX format: \begin{pmatrix} a & b \\ c & d \end{pmatrix}
    # 2. Simple comma-separated numbers: "a,b,c,d"
    # 3. Python list of lists: "[[a,b],[c,d]]"

    ans_str = ans_str.strip()
    # Remove LaTeX specific parts
    ans_str = ans_str.replace(r'\begin{pmatrix}', '').replace(r'\end{pmatrix}', '')
    # Remove Python list specific parts
    ans_str = ans_str.replace('[', '').replace(']', '')
    # Replace common separators with comma for consistent splitting
    ans_str = ans_str.replace('&', ',').replace(r'\\', ',').replace(' ', ',').replace(';', ',')

    parts = [p.strip() for p in ans_str.split(',') if p.strip()]
    
    if len(parts) != 4: # A 2x2 matrix has exactly 4 elements
        return None
    
    elements = []
    for p in parts:
        frac = parse_fraction_string(p)
        if frac is None:
            return None
        elements.append(frac)
            
    return [[elements[0], elements[1]], [elements[2], elements[3]]]

def check(user_answer, correct_answer):
    """
    檢查使用者答案是否正確。
    correct_answer 包含一個前綴，指示答案類型 (例如 "[POINT]", "[MATRIX]")。
    """
    user_answer = user_answer.strip()
    correct_answer_str_with_prefix = correct_answer.strip()
    
    is_correct = False
    feedback = ""
    
    # Determine problem type from the correct_answer prefix
    if correct_answer_str_with_prefix.startswith("[POINT]"):
        correct_data_str = correct_answer_str_with_prefix[len("[POINT]"):]
        parsed_correct = parse_point_or_vector_string(correct_data_str)
        parsed_user = parse_point_or_vector_string(user_answer)

        if parsed_user is None:
            feedback = "請確保你的答案格式為 (x, y)，例如 (1/2, -3)。"
        elif parsed_user == parsed_correct:
            is_correct = True
            feedback = f"完全正確！答案是 ${format_point(parsed_correct[0], parsed_correct[1])}$。"
        else:
            feedback = f"答案不正確。正確答案應為：${format_point(parsed_correct[0], parsed_correct[1])}$"

    elif correct_answer_str_with_prefix.startswith("[MATRIX]"):
        correct_data_str = correct_answer_str_with_prefix[len("[MATRIX]"):]
        parsed_correct = parse_matrix_string(correct_data_str)
        parsed_user = parse_matrix_string(user_answer)

        if parsed_user is None:
            feedback = "請確保你的答案格式為四個數字 (例如 1, 2, 3, 4)，或 [[1, 2], [3, 4]]，或使用 LaTeX 矩陣格式。"
        elif parsed_user == parsed_correct:
            is_correct = True
            feedback = f"完全正確！答案是 ${format_matrix(parsed_correct)}$。"
        else:
            feedback = f"答案不正確。正確答案應為：${format_matrix(parsed_correct)}$"
    
    else: 
        # Fallback for unexpected format (should not happen with prefixes)
        is_correct = (user_answer == correct_answer_str_with_prefix)
        feedback = f"完全正確！答案是 ${correct_answer_str_with_prefix}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer_str_with_prefix}$"

    return {"correct": is_correct, "result": feedback, "next_question": True}