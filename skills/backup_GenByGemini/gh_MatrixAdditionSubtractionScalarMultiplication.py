import random
from fractions import Fraction
import re

# --- Helper functions for matrix operations and formatting ---

def _convert_to_fraction(s):
    """
    Converts a string (like '1', '-2', '3/4', '1.5') to a Fraction object.
    Robustly handles integers, floats, and 'num/den' fraction formats.
    """
    s = str(s).strip()
    if not s:
        raise ValueError("Cannot convert empty string to Fraction")
    
    # Check for fraction format "num/den"
    if '/' in s:
        parts = s.split('/')
        if len(parts) == 2:
            try:
                num = int(parts[0])
                den = int(parts[1])
                if den == 0:
                    raise ZeroDivisionError("Denominator cannot be zero")
                return Fraction(num, den)
            except ValueError:
                pass # Fall through to integer/float parsing if not a clean fraction
    
    # Try parsing as integer
    try:
        return Fraction(int(s))
    except ValueError:
        pass # Fall through to float parsing
        
    # Try parsing as float (and convert to fraction, limiting denominator)
    try:
        # Use limit_denominator to avoid overly complex fractions from user input like 0.3333333
        return Fraction(float(s)).limit_denominator(1000) 
    except ValueError:
        raise ValueError(f"Could not convert '{s}' to a valid number or fraction.")

def create_random_matrix(rows, cols, min_val, max_val):
    """Generates a matrix with random integer elements."""
    matrix = []
    for _ in range(rows):
        row = [random.randint(min_val, max_val) for _ in range(cols)]
        matrix.append(row)
    return matrix

def matrix_to_latex(matrix):
    """Converts a list-of-lists matrix into its LaTeX bmatrix string representation."""
    if not matrix:
        return r"\begin{bmatrix} \end{bmatrix}"
    
    rows_latex = []
    for row in matrix:
        rows_latex.append(" & ".join([format_fraction_latex(val) for val in row]))
    
    latex_str = r"\begin{bmatrix}" + r" \\ ".join(rows_latex) + r"\end{bmatrix}"
    return latex_str

def format_fraction_latex(val):
    """
    Formats a number as a fraction or integer for LaTeX display.
    Ensures negative fractions are displayed correctly (e.g., -1/2 instead of (-1)/2).
    """
    # Ensure val is a Fraction for consistent handling
    if not isinstance(val, Fraction):
        val = Fraction(val)

    if val.denominator == 1:
        return str(val.numerator)
    else:
        # Handle negative fractions nicely, e.g., -1/2 instead of (-1)/2
        if val.numerator < 0:
            return fr"-\\frac{{{-val.numerator}}}{{{val.denominator}}}"
        return fr"\\frac{{{val.numerator}}}{{{val.denominator}}}"

def add_matrices(matrix1, matrix2):
    """Adds two matrices element-wise."""
    rows = len(matrix1)
    cols = len(matrix1[0])
    result = []
    for r in range(rows):
        row = []
        for c in range(cols):
            # Ensure elements are Fractions for precise arithmetic
            val1 = Fraction(matrix1[r][c])
            val2 = Fraction(matrix2[r][c])
            row.append(val1 + val2)
        result.append(row)
    return result

def subtract_matrices(matrix1, matrix2):
    """Subtracts matrix2 from matrix1 element-wise."""
    rows = len(matrix1)
    cols = len(matrix1[0])
    result = []
    for r in range(rows):
        row = []
        for c in range(cols):
            val1 = Fraction(matrix1[r][c])
            val2 = Fraction(matrix2[r][c])
            row.append(val1 - val2)
        result.append(row)
    return result

def scalar_multiply_matrix(scalar, matrix):
    """Multiplies a matrix by a scalar element-wise."""
    rows = len(matrix)
    cols = len(matrix[0])
    result = []
    scalar_frac = Fraction(scalar) # Ensure scalar is a Fraction
    for r in range(rows):
        row = []
        for c in range(cols):
            val = Fraction(matrix[r][c])
            row.append(scalar_frac * val)
        result.append(row)
    return result

def parse_matrix_string(matrix_str):
    """
    Parses a string representation of a matrix into a list of lists of Fractions.
    Handles formats like '[[1,2],[3,4]]', '1 2; 3 4', '1/2 3/4; 5 6', etc.
    """
    matrix_str = matrix_str.strip()
    if not matrix_str:
        return None

    # Normalize row separators: convert ';' and ',' to newline for robust splitting
    matrix_str = re.sub(r'\s*;\s*|\s*,\s*\n\s*', r'\n', matrix_str)
    # Remove outer brackets if present, to simplify row parsing
    if matrix_str.startswith('[[') and matrix_str.endswith(']]'):
        matrix_str = matrix_str[2:-2]
    elif matrix_str.startswith('[') and matrix_str.endswith(']'):
        matrix_str = matrix_str[1:-1]
    
    rows_str_list = [row.strip() for row in matrix_str.split('\n') if row.strip()]
    
    parsed_matrix = []
    for row_s in rows_str_list:
        # Split elements by comma or space
        elements_s = [s.strip() for s in re.split(r'[, ]+', row_s) if s.strip()]
        if not elements_s:
            continue # Skip empty segments
        
        row_values = []
        for el_s in elements_s:
            try:
                row_values.append(_convert_to_fraction(el_s))
            except (ValueError, ZeroDivisionError):
                # If any element cannot be parsed, the whole matrix is invalid
                return None
        parsed_matrix.append(row_values)
            
    if not parsed_matrix:
        return None # No valid matrix found

    # Ensure all rows have the same number of columns
    num_cols = len(parsed_matrix[0])
    if not all(len(row) == num_cols for row in parsed_matrix):
        return None # Inconsistent column count

    return parsed_matrix

# --- Problem generation functions ---

def generate_add_sub_problem(level):
    rows = random.randint(2, 3)
    cols = random.randint(2, 3)
    min_val = -5 - level # Increase range for higher level
    max_val = 5 + level
    
    matrix_a = create_random_matrix(rows, cols, min_val, max_val)
    matrix_b = create_random_matrix(rows, cols, min_val, max_val)
    
    operation = random.choice(['+', '-'])
    
    if operation == '+':
        result_matrix = add_matrices(matrix_a, matrix_b)
        question_text = f"已知矩陣 $A = {matrix_to_latex(matrix_a)}$，$B = {matrix_to_latex(matrix_b)}$，求 $A+B$。"
    else: # operation == '-'
        result_matrix = subtract_matrices(matrix_a, matrix_b)
        question_text = f"已知矩陣 $A = {matrix_to_latex(matrix_a)}$，$B = {matrix_to_latex(matrix_b)}$，求 $A-B$。"
        
    correct_answer_latex = matrix_to_latex(result_matrix)
    correct_answer_parsed = str(result_matrix) # Store as str(list_of_lists_of_Fraction)
    
    return {
        "question_text": question_text,
        "answer": correct_answer_latex, # Display format (optional, usually "None" for user input)
        "correct_answer": correct_answer_parsed # Internal check format
    }

def generate_scalar_multiply_problem(level):
    rows = random.randint(2, 3)
    cols = random.randint(2, 3)
    min_val_mat = -3 - level // 2
    max_val_mat = 3 + level // 2
    
    matrix_a = create_random_matrix(rows, cols, min_val_mat, max_val_mat)
    
    scalar_k = random.randint(-4, 4)
    while scalar_k == 0: # Avoid scalar of 0 for non-trivial problems
        scalar_k = random.randint(-4, 4)
    
    result_matrix = scalar_multiply_matrix(scalar_k, matrix_a)
    
    question_text = f"已知矩陣 $A = {matrix_to_latex(matrix_a)}$，求 ${scalar_k}A$。"
    correct_answer_latex = matrix_to_latex(result_matrix)
    correct_answer_parsed = str(result_matrix)
    
    return {
        "question_text": question_text,
        "answer": correct_answer_latex,
        "correct_answer": correct_answer_parsed
    }

def generate_linear_combination_problem(level):
    rows = random.randint(2, 3)
    cols = random.randint(2, 3)
    min_val_mat = -2 - level // 2
    max_val_mat = 2 + level // 2
    
    matrix_a = create_random_matrix(rows, cols, min_val_mat, max_val_mat)
    matrix_b = create_random_matrix(rows, cols, min_val_mat, max_val_mat)
    
    scalar_k = random.randint(-3, 3)
    scalar_m = random.randint(-3, 3)
    while scalar_k == 0 and scalar_m == 0: # Ensure at least one scalar is non-zero
        scalar_k = random.randint(-3, 3)
        scalar_m = random.randint(-3, 3)

    op_str = random.choice(['+', '-'])
    
    temp_ka = scalar_multiply_matrix(scalar_k, matrix_a)
    temp_mb = scalar_multiply_matrix(scalar_m, matrix_b)
    
    if op_str == '+':
        result_matrix = add_matrices(temp_ka, temp_mb)
        question_text = f"已知矩陣 $A = {matrix_to_latex(matrix_a)}$，$B = {matrix_to_latex(matrix_b)}$，求 ${scalar_k}A + {scalar_m}B$。"
    else:
        result_matrix = subtract_matrices(temp_ka, temp_mb)
        question_text = f"已知矩陣 $A = {matrix_to_latex(matrix_a)}$，$B = {matrix_to_latex(matrix_b)}$，求 ${scalar_k}A - {scalar_m}B$。"
        
    correct_answer_latex = matrix_to_latex(result_matrix)
    correct_answer_parsed = str(result_matrix)
    
    return {
        "question_text": question_text,
        "answer": correct_answer_latex,
        "correct_answer": correct_answer_parsed
    }

def generate_matrix_equation_simple_problem(level):
    rows = random.randint(2, 2)
    cols = random.randint(2, 2)
    min_val = -5 - level
    max_val = 5 + level
    
    matrix_a = create_random_matrix(rows, cols, min_val, max_val)
    matrix_b = create_random_matrix(rows, cols, min_val, max_val)
    
    # Problem types: X + A = B, A + X = B, X - A = B, A - X = B
    equation_type = random.choice([1, 2, 3, 4])
    
    if equation_type == 1: # X + A = B  => X = B - A
        result_matrix = subtract_matrices(matrix_b, matrix_a)
        question_text = f"已知矩陣 $X$ 滿足 $X + {matrix_to_latex(matrix_a)} = {matrix_to_latex(matrix_b)}$，求 $X$。"
    elif equation_type == 2: # A + X = B  => X = B - A
        result_matrix = subtract_matrices(matrix_b, matrix_a)
        question_text = f"已知矩陣 $X$ 滿足 ${matrix_to_latex(matrix_a)} + X = {matrix_to_latex(matrix_b)}$，求 $X$。"
    elif equation_type == 3: # X - A = B  => X = B + A
        result_matrix = add_matrices(matrix_b, matrix_a)
        question_text = f"已知矩陣 $X$ 滿足 $X - {matrix_to_latex(matrix_a)} = {matrix_to_latex(matrix_b)}$，求 $X$。"
    else: # A - X = B  => X = A - B
        result_matrix = subtract_matrices(matrix_a, matrix_b)
        question_text = f"已知矩陣 $X$ 滿足 ${matrix_to_latex(matrix_a)} - X = {matrix_to_latex(matrix_b)}$，求 $X$。"
        
    correct_answer_latex = matrix_to_latex(result_matrix)
    correct_answer_parsed = str(result_matrix)
    
    return {
        "question_text": question_text,
        "answer": correct_answer_latex,
        "correct_answer": correct_answer_parsed
    }

def generate_matrix_equation_complex_problem(level):
    rows = random.randint(2, 2)
    cols = random.randint(2, 2)
    min_val_mat = -2 - level // 2
    max_val_mat = 2 + level // 2
    
    matrix_a = create_random_matrix(rows, cols, min_val_mat, max_val_mat)
    matrix_b = create_random_matrix(rows, cols, min_val_mat, max_val_mat)
    
    problem_type = random.choice([1, 2])
    
    # Ensure scalars for division are non-zero
    p = random.randint(-3, 3)
    while p == 0: p = random.randint(-3, 3)
    q = random.randint(-3, 3)
    while q == 0: q = random.randint(-3, 3)
    r = random.randint(-3, 3)
    while r == 0: r = random.randint(-3, 3)

    if problem_type == 1: # p(qX + A) = rB  => X = (1/pq) * (rB - pA)
        # pqX + pA = rB
        # pqX = rB - pA
        # X = (1/pq) * (rB - pA)
        
        temp_r_b = scalar_multiply_matrix(r, matrix_b)
        temp_p_a = scalar_multiply_matrix(p, matrix_a)
        
        diff_matrix = subtract_matrices(temp_r_b, temp_p_a)
        
        scalar_factor = Fraction(1, p * q)
        result_matrix = scalar_multiply_matrix(scalar_factor, diff_matrix)
        
        question_text = f"已知矩陣 $A = {matrix_to_latex(matrix_a)}$，$B = {matrix_to_latex(matrix_b)}$ 滿足 ${p}({q}X+A)={r}B$，求 $X$。"
        
    else: # pX + qA = rB  => X = (1/p) * (rB - qA)
        # pX = rB - qA
        # X = (1/p) * (rB - qA)
        
        temp_r_b = scalar_multiply_matrix(r, matrix_b)
        temp_q_a = scalar_multiply_matrix(q, matrix_a)
        
        diff_matrix = subtract_matrices(temp_r_b, temp_q_a)
        
        scalar_factor = Fraction(1, p)
        result_matrix = scalar_multiply_matrix(scalar_factor, diff_matrix)
        
        question_text = f"已知矩陣 $A = {matrix_to_latex(matrix_a)}$，$B = {matrix_to_latex(matrix_b)}$ 滿足 ${p}X+{q}A={r}B$，求 $X$。"

    correct_answer_latex = matrix_to_latex(result_matrix)
    correct_answer_parsed = str(result_matrix) # Stores list of lists of Fraction
    
    return {
        "question_text": question_text,
        "answer": correct_answer_latex,
        "correct_answer": correct_answer_parsed
    }

def generate(level=1):
    """
    生成矩陣加法、減法與實數對矩陣的係數積運算相關題目。
    """
    problem_types = [
        'add_sub',
        'scalar_multiply',
        'linear_combination',
        'matrix_equation_simple',
    ]
    
    if level >= 2: # Introduce more complex equations at higher levels
        problem_types.append('matrix_equation_complex')
        
    # Level can influence range of numbers or matrix dimensions,
    # which is handled implicitly by min_val/max_val arguments.

    problem_type = random.choice(problem_types)
    
    if problem_type == 'add_sub':
        return generate_add_sub_problem(level)
    elif problem_type == 'scalar_multiply':
        return generate_scalar_multiply_problem(level)
    elif problem_type == 'linear_combination':
        return generate_linear_combination_problem(level)
    elif problem_type == 'matrix_equation_simple':
        return generate_matrix_equation_simple_problem(level)
    elif problem_type == 'matrix_equation_complex':
        return generate_matrix_equation_complex_problem(level)
    else:
        # Fallback, should not be reached with random.choice
        return generate_add_sub_problem(level)


def check(user_answer, correct_answer):
    """
    檢查使用者輸入的矩陣答案是否正確。
    user_answer 和 correct_answer 預期為代表矩陣的字串
    例如 '[[1, 2], [3, 4]]', '1 2; 3 4', '1/2 3/4; 5 6'
    """
    # Parse user_answer string into a list of lists of Fractions
    parsed_user_matrix = parse_matrix_string(user_answer)
    if parsed_user_matrix is None:
        return {"correct": False, "result": "您的答案格式不正確。請輸入數字列表，例如 '[[1,2],[3,4]]' 或 '1 2; 3 4'，分數請用 'a/b' 表示。", "next_question": False}

    # The correct_answer is stored as str(list_of_lists_of_Fraction),
    # so we need to use eval with Fraction in the scope to reconstruct it.
    try:
        # Reconstruct the list of Fraction objects from the string.
        # It's crucial that Fraction class is available in the eval context.
        parsed_correct_matrix = eval(correct_answer, {'Fraction': Fraction, '__builtins__': {}})
    except (SyntaxError, ValueError, TypeError, NameError):
        # This should ideally not happen if generate produces correct `correct_answer` strings
        return {"correct": False, "result": "系統內部錯誤：無法解析正確答案。", "next_question": False}

    # Compare dimensions
    if not parsed_user_matrix or not parsed_correct_matrix or \
       len(parsed_user_matrix) != len(parsed_correct_matrix) or \
       len(parsed_user_matrix[0]) != len(parsed_correct_matrix[0]):
        return {"correct": False, "result": "矩陣維度不正確。", "next_question": False}

    # Compare elements (Fraction comparison is exact)
    is_correct = True
    for r in range(len(parsed_correct_matrix)):
        for c in range(len(parsed_correct_matrix[0])):
            if parsed_user_matrix[r][c] != parsed_correct_matrix[r][c]:
                is_correct = False
                break
        if not is_correct:
            break

    result_text = f"完全正確！答案是 ${matrix_to_latex(parsed_correct_matrix)}$。" if is_correct else f"答案不正確。正確答案應為：${matrix_to_latex(parsed_correct_matrix)}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}