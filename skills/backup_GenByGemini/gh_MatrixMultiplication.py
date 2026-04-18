import random
from fractions import Fraction
import re

# --- Helper Functions ---

def _generate_matrix(rows, cols, min_val, max_val):
    """Generates a matrix (list of lists) with specified dimensions and random integer elements."""
    if rows <= 0 or cols <= 0:
        return [] # Return empty matrix for non-positive dimensions
    return [[random.randint(min_val, max_val) for _ in range(cols)] for _ in range(rows)]

def _matrix_to_latex(matrix):
    """Converts a matrix (list of lists) to its LaTeX string representation."""
    if not matrix or not matrix[0]: 
        return r"\begin{bmatrix} \end{bmatrix}"
    
    rows = len(matrix)
    
    latex_str = r"\begin{bmatrix}"
    for i in range(rows):
        latex_str += " & ".join(map(str, matrix[i]))
        if i < rows - 1:
            latex_str += r" \\ "
    latex_str += r"\end{bmatrix}"
    return latex_str

def _multiply_matrices(matrix_a, matrix_b):
    """Performs matrix multiplication. Returns the result matrix or None if not possible."""
    if not matrix_a or not matrix_b:
        return None
        
    rows_a = len(matrix_a)
    cols_a = len(matrix_a[0])
    rows_b = len(matrix_b)
    cols_b = len(matrix_b[0])

    if cols_a != rows_b:
        return None # Multiplication not possible

    result_matrix = [[0 for _ in range(cols_b)] for _ in range(rows_a)]

    for i in range(rows_a):
        for j in range(cols_b):
            for k in range(cols_a): # This also equals rows_b
                result_matrix[i][j] += matrix_a[i][k] * matrix_b[k][j]
    return result_matrix

def _add_matrices(matrix_a, matrix_b):
    """Adds two matrices. Returns the result matrix or None if not possible."""
    if not matrix_a or not matrix_b:
        return None
        
    rows_a = len(matrix_a)
    cols_a = len(matrix_a[0])
    rows_b = len(matrix_b)
    cols_b = len(matrix_b[0])

    if rows_a != rows_b or cols_a != cols_b:
        return None # Addition not possible

    result_matrix = [[0 for _ in range(cols_a)] for _ in range(rows_a)]
    for i in range(rows_a):
        for j in range(cols_a):
            result_matrix[i][j] = matrix_a[i][j] + matrix_b[i][j]
    return result_matrix

def _scalar_multiply_matrix(scalar, matrix):
    """Multiplies a matrix by a scalar."""
    if not matrix:
        return []
    rows = len(matrix)
    cols = len(matrix[0])
    result_matrix = [[0 for _ in range(cols)] for _ in range(rows)]
    for i in range(rows):
        for j in range(cols):
            result_matrix[i][j] = scalar * matrix[i][j]
    return result_matrix

def _are_matrices_equal(mat1, mat2):
    """Checks if two matrices are equal."""
    if mat1 is None and mat2 is None: # Both are "not possible"
        return True
    if mat1 is None or mat2 is None: # One is possible, one is not
        return False
    if not mat1 and not mat2: # Both empty or have 0 rows/cols
        return True
    if not mat1 or not mat2: # One empty, one not
        return False
    
    # Check dimensions
    if len(mat1) != len(mat2) or len(mat1[0]) != len(mat2[0]):
        return False
    
    # Check elements
    for i in range(len(mat1)):
        for j in range(len(mat1[0])):
            if mat1[i][j] != mat2[i][j]:
                return False
    return True

def _parse_matrix_input(input_str):
    """
    Parses a string representing a matrix (e.g., "[[1, 2], [3, 4]]") into a list of lists.
    Includes basic validation.
    """
    try:
        # Normalize spaces and check against a regex pattern for basic validation
        normalized_str = re.sub(r'\s+', '', input_str)
        
        # Regex to validate string format for matrix: [[num,num],[num,num]]
        # Allows integers and fractions for flexibility, though generated problems use integers.
        matrix_pattern = r'\[(\[(-?\d+(?:/\d+)?)(,-?\d+(?:/\d+)?)*\])(,\[(-?\d+(?:/\d+)?)(,-?\d+(?:/\d+)?)*\])*\]'
        if not re.fullmatch(matrix_pattern, normalized_str) and normalized_str != '[]':
            return None # Does not match expected matrix string format
            
        parsed_matrix = eval(normalized_str)
        
        # Further validation: ensure it's a list of lists of numbers
        if not isinstance(parsed_matrix, list):
            return None
        if not parsed_matrix: # Empty matrix
            return []

        rows = len(parsed_matrix)
        cols = len(parsed_matrix[0]) if rows > 0 else 0

        # All rows must be lists and have the same number of columns
        if not all(isinstance(row, list) and len(row) == cols for row in parsed_matrix):
            return None 
            
        for row in parsed_matrix:
            for item in row:
                if not isinstance(item, (int, float, Fraction)):
                    # Check if string representation of fraction
                    if isinstance(item, str) and '/' in item:
                        try:
                            num, den = map(int, item.split('/'))
                            if den == 0: return None # Division by zero
                            Fraction(num, den) # Check if it's a valid fraction
                        except ValueError:
                            return None # Invalid fraction format
                        continue
                    return None
        return parsed_matrix
    except (SyntaxError, NameError, TypeError, ValueError):
        return None # Invalid input format or eval failure

# --- Problem Generation Functions ---

def _generate_basic_multiplication_problem(level):
    """Generates a problem asking to calculate a matrix product AB."""
    if level == 1:
        rows_a = random.randint(2, 3)
        cols_a = random.randint(2, 3)
        rows_b = cols_a
        cols_b = random.randint(2, 3)
        min_val, max_val = -3, 3
    elif level == 2:
        rows_a = random.randint(2, 4)
        cols_a = random.randint(2, 4)
        rows_b = cols_a
        cols_b = random.randint(2, 4)
        min_val, max_val = -5, 5
    else: # level 3
        rows_a = random.randint(3, 5)
        cols_a = random.randint(3, 5)
        rows_b = cols_a
        cols_b = random.randint(3, 5)
        min_val, max_val = -7, 7

    matrix_a = _generate_matrix(rows_a, cols_a, min_val, max_val)
    matrix_b = _generate_matrix(rows_b, cols_b, min_val, max_val)

    product_ab = _multiply_matrices(matrix_a, matrix_b)
    
    question_text = (
        f"給定矩陣 $A = {_matrix_to_latex(matrix_a)}$ 和 $B = {_matrix_to_latex(matrix_b)}$。"
        f" 請計算矩陣乘積 $AB$。"
        f" 若無意義，請回答 '無意義'。"
        f" (請以 Python list of lists 格式回答，例如: [[1, 2], [3, 4]])"
    )
    
    correct_answer_raw = str(product_ab) if product_ab else "無意義"

    return {
        "question_text": question_text,
        "answer": correct_answer_raw,
        "correct_answer": correct_answer_raw
    }

def _generate_compatibility_problem(level):
    """Generates a problem asking to determine if matrix multiplication is possible."""
    rows_a = random.randint(2, 4)
    cols_a = random.randint(2, 4)
    rows_b = random.randint(2, 4)
    cols_b = random.randint(2, 4)

    matrix_a = _generate_matrix(rows_a, cols_a, -2, 2)
    matrix_b = _generate_matrix(rows_b, cols_b, -2, 2)

    op_type = random.choice(['AB', 'BA'])
    
    if op_type == 'AB':
        is_possible = (cols_a == rows_b)
        product_str = "AB"
        dims_a = f"${rows_a} \\times {cols_a}$"
        dims_b = f"${rows_b} \\times {cols_b}$"
        compatibility_check_text = f"$A$ 的行數 ${cols_a}$ 是否等於 $B$ 的列數 ${rows_b}$"
    else: # BA
        is_possible = (cols_b == rows_a)
        product_str = "BA"
        dims_a = f"${rows_a} \\times {cols_a}$"
        dims_b = f"${rows_b} \\times {cols_b}$"
        compatibility_check_text = f"$B$ 的行數 ${cols_b}$ 是否等於 $A$ 的列數 ${rows_a}$"

    question_text = (
        f"給定矩陣 $A = {_matrix_to_latex(matrix_a)}$ (維度 {dims_a}) 和 $B = {_matrix_to_latex(matrix_b)}$ (維度 {dims_b})。"
        f" 判斷矩陣乘積 ${product_str}$ 是否有意義？"
        f" (請回答 '是' 或 '否')"
    )
    
    correct_answer = "是" if is_possible else "否"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def _generate_matrix_power_problem(level):
    """Generates a problem asking to calculate A^n for a given matrix A."""
    size = random.randint(2, 3) # Max 3x3 for A^n
    min_val, max_val = -2, 2
    matrix_a = _generate_matrix(size, size, min_val, max_val)

    power = random.randint(2, 4) # A^2, A^3, A^4

    result = matrix_a
    for _ in range(power - 1):
        result = _multiply_matrices(result, matrix_a)
        if result is None: # Should not happen for square matrices
            break

    question_text = (
        f"給定矩陣 $A = {_matrix_to_latex(matrix_a)}$。"
        f" 請計算 $A^{{{power}}}$。"
        f" (請以 Python list of lists 格式回答，例如: [[1, 2], [3, 4]])"
    )
    
    correct_answer_raw = str(result)
    return {
        "question_text": question_text,
        "answer": correct_answer_raw,
        "correct_answer": correct_answer_raw
    }

def _generate_matrix_properties_problem(level):
    """Generates a problem to verify matrix properties like associativity or distributivity."""
    property_type = random.choice(['associativity', 'distributivity'])

    if property_type == 'associativity':
        # (AB)C = A(BC)
        rows_a = random.randint(2, 3)
        cols_a = random.randint(2, 3)
        rows_b = cols_a
        cols_b = random.randint(2, 3)
        rows_c = cols_b
        cols_c = random.randint(2, 3)
        
        min_val, max_val = -2, 2
        matrix_a = _generate_matrix(rows_a, cols_a, min_val, max_val)
        matrix_b = _generate_matrix(rows_b, cols_b, min_val, max_val)
        matrix_c = _generate_matrix(rows_c, cols_c, min_val, max_val)

        ab = _multiply_matrices(matrix_a, matrix_b)
        abc_left = _multiply_matrices(ab, matrix_c)

        question_text = (
            f"給定矩陣 $A = {_matrix_to_latex(matrix_a)}$，$B = {_matrix_to_latex(matrix_b)}$，$C = {_matrix_to_latex(matrix_c)}$。"
            f" 請計算 $(AB)C$。"
            f" (請以 Python list of lists 格式回答，例如: [[1, 2], [3, 4]])"
        )
        correct_answer_raw = str(abc_left)

    else: # distributivity A(B+C) = AB+AC
        # For distributivity, B and C must have same dimensions, and A must be compatible with B.
        rows_a = random.randint(2, 3)
        cols_a = random.randint(2, 3) # This is B's rows
        rows_b = cols_a
        cols_b = random.randint(2, 3)
        
        matrix_a = _generate_matrix(rows_a, cols_a, -2, 2)
        matrix_b = _generate_matrix(rows_b, cols_b, -2, 2)
        matrix_c = _generate_matrix(rows_b, cols_b, -2, 2) # C has same dimensions as B
        
        b_plus_c = _add_matrices(matrix_b, matrix_c)
        abc_left = _multiply_matrices(matrix_a, b_plus_c)

        question_text = (
            f"給定矩陣 $A = {_matrix_to_latex(matrix_a)}$，$B = {_matrix_to_latex(matrix_b)}$，$C = {_matrix_to_latex(matrix_c)}$。"
            f" 請計算 $A(B+C)$。"
            f" (請以 Python list of lists 格式回答，例如: [[1, 2], [3, 4]])"
        )
        correct_answer_raw = str(abc_left)

    return {
        "question_text": question_text,
        "answer": correct_answer_raw,
        "correct_answer": correct_answer_raw
    }

def _generate_matrix_equation_problem(level):
    """Generates a problem asking to find p, q in A^2 = pA + qI for 2x2 matrices."""
    # This problem type is specifically designed for 2x2 matrices using Cayley-Hamilton Theorem
    size = 2
    min_val, max_val = -2, 2
    matrix_a = _generate_matrix(size, size, min_val, max_val)
    
    # Ensure a non-trivial matrix where p and q are meaningful
    while all(all(x == 0 for x in row) for row in matrix_a) or \
          (matrix_a[0][0] == matrix_a[1][1] and matrix_a[0][1] == 0 and matrix_a[1][0] == 0): # Scalar multiple of identity
        matrix_a = _generate_matrix(size, size, min_val, max_val)

    # For 2x2 matrix [[a, b], [c, d]]:
    # By Cayley-Hamilton Theorem: A^2 - (trace A)A + (det A)I = 0
    # So A^2 = (trace A)A - (det A)I
    # where trace A = a+d and det A = ad-bc
    
    a = matrix_a[0][0]
    b = matrix_a[0][1]
    c = matrix_a[1][0]
    d = matrix_a[1][1]

    p = a + d # Trace
    q = -(a * d - b * c) # Negative of determinant

    identity_matrix = [[1, 0], [0, 1]]

    question_text = (
        f"給定矩陣 $A = {_matrix_to_latex(matrix_a)}$ 和單位方陣 $I = {_matrix_to_latex(identity_matrix)}$。"
        f" 若 $A^{{2}} = pA + qI$，請求出實數 $p, q$ 的值。"
        f" (請以 'p,q' 的格式回答，例如: '5,-3')"
    )
    
    correct_answer_raw = f"{p},{q}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer_raw,
        "correct_answer": correct_answer_raw
    }


def generate(level=1):
    """
    Generates a matrix multiplication problem based on the specified level.
    """
    problem_type_weights = {
        1: {'basic_multiplication': 0.7, 'matrix_power': 0.1, 'check_compatibility': 0.2},
        2: {'basic_multiplication': 0.5, 'matrix_power': 0.2, 'properties': 0.2, 'check_compatibility': 0.1},
        3: {'basic_multiplication': 0.2, 'matrix_power': 0.2, 'properties': 0.4, 'matrix_equation': 0.2}
    }
    
    # Choose problem type based on level
    problem_choices = list(problem_type_weights[level].keys())
    weights = [problem_type_weights[level][pc] for pc in problem_choices]
    problem_type = random.choices(problem_choices, weights=weights, k=1)[0]
    
    if problem_type == 'basic_multiplication':
        return _generate_basic_multiplication_problem(level)
    elif problem_type == 'matrix_power':
        return _generate_matrix_power_problem(level)
    elif problem_type == 'properties':
        return _generate_matrix_properties_problem(level)
    elif problem_type == 'check_compatibility':
        return _generate_compatibility_problem(level)
    elif problem_type == 'matrix_equation':
        return _generate_matrix_equation_problem(level)
    else: # Fallback
        return _generate_basic_multiplication_problem(level)

def check(user_answer, correct_answer):
    """
    Checks if the user's answer is correct for a matrix multiplication problem.
    Handles matrix input (as Python list of lists string), "無意義", "是", "否", and "p,q" formats.
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()

    is_correct = False
    result_text = ""

    if correct_answer == "無意義":
        is_correct = (user_answer.lower() == "無意義")
        result_text = f"完全正確！答案是 '無意義'。" if is_correct else f"答案不正確。正確答案應為：'無意義'"
    elif correct_answer in ["是", "否"]:
        is_correct = (user_answer.lower() == correct_answer.lower())
        result_text = f"完全正確！答案是 '{correct_answer}'。" if is_correct else f"答案不正確。正確答案應為：'{correct_answer}'"
    elif "," in correct_answer and re.match(r"^-?\d+,-?\d+$", correct_answer): # For 'p,q' format
        try:
            user_p, user_q = map(int, user_answer.split(','))
            correct_p, correct_q = map(int, correct_answer.split(','))
            is_correct = (user_p == correct_p and user_q == correct_q)
            result_text = (
                f"完全正確！答案是 $p={correct_p}, q={correct_q}$。" if is_correct 
                else f"答案不正確。正確答案應為：$p={correct_p}, q={correct_q}$"
            )
        except ValueError:
            result_text = f"答案格式不正確。請以 'p,q' 格式回答，例如 '5,-3'。"
    else: # Matrix answer, e.g., "[[1, 2], [3, 4]]"
        user_matrix = _parse_matrix_input(user_answer)
        correct_matrix = _parse_matrix_input(correct_answer)
        
        if user_matrix is None:
            result_text = "您的矩陣輸入格式不正確，請檢查是否符合 Python list of lists 格式 (例如: [[1, 2], [3, 4]])。"
        else:
            is_correct = _are_matrices_equal(user_matrix, correct_matrix)
            correct_latex = _matrix_to_latex(correct_matrix)
            result_text = (
                f"完全正確！答案是 ${correct_latex}$。" if is_correct 
                else f"答案不正確。正確答案應為：${correct_latex}$"
            )

    return {"correct": is_correct, "result": result_text, "next_question": True}