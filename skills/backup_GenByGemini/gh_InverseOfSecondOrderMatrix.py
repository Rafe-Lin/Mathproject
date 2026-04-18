import random
from fractions import Fraction
import re

# --- Helper Functions ---

# Helper function to generate a random 2x2 matrix with integer elements
def _generate_random_matrix_2x2(min_val=-5, max_val=5, ensure_invertible=False, det_min_abs=1):
    """
    Generates a random 2x2 matrix with elements as Fractions.
    Can ensure the matrix is invertible with a minimum absolute determinant.
    """
    while True:
        a = random.randint(min_val, max_val)
        b = random.randint(min_val, max_val)
        c = random.randint(min_val, max_val)
        d = random.randint(min_val, max_val)
        matrix = [[Fraction(a), Fraction(b)], [Fraction(c), Fraction(d)]]
        
        det = _calculate_determinant(matrix)
        
        if ensure_invertible:
            # Ensure determinant is not zero and meets minimum absolute value
            if det != 0 and abs(det) >= det_min_abs:
                return matrix, det
        else:
            return matrix, det

# Helper function to calculate the determinant of a 2x2 matrix
def _calculate_determinant(matrix):
    """Calculates the determinant of a 2x2 matrix [[a, b], [c, d]]."""
    return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]

# Helper function to calculate the inverse of a 2x2 matrix
def _calculate_inverse_2x2(matrix):
    """
    Calculates the inverse of a 2x2 matrix.
    Returns the inverse matrix (list of lists of Fractions) or None if determinant is zero.
    """
    det = _calculate_determinant(matrix)
    if det == 0:
        return None  # Inverse does not exist
    
    # Adjugate matrix of [[a, b], [c, d]] is [[d, -b], [-c, a]]
    # Inverse is (1/det) * adjugate
    a, b = matrix[0]
    c, d = matrix[1]
    
    inv_det = Fraction(1, det)
    
    return [
        [d * inv_det, -b * inv_det],
        [-c * inv_det, a * inv_det]
    ]

# Helper function to multiply two 2x2 matrices
def _multiply_matrices_2x2(m1, m2):
    """
    Multiplies two 2x2 matrices.
    m1 = [[a, b], [c, d]]
    m2 = [[e, f], [g, h]]
    Result = [[ae+bg, af+bh], [ce+dg, cf+dh]]
    """
    a, b = m1[0]
    c, d = m1[1]
    
    e, f = m2[0]
    g, h = m2[1]
    
    return [
        [a*e + b*g, a*f + b*h],
        [c*e + d*g, c*f + d*h]
    ]

# Helper to format matrix for LaTeX display
def _format_matrix_latex(matrix):
    """
    Formats a 2x2 matrix (list of lists of Fractions) into a LaTeX bmatrix string.
    Simplifies fractions for display.
    """
    rows_latex = []
    for row in matrix:
        # Ensure all fractions are simplified before display
        row_str = " & ".join([str(val.limit_denominator()) for val in row])
        rows_latex.append(row_str)
    return r"\begin{{bmatrix}} " + r" \\ ".join(rows_latex) + r" \end{{bmatrix}}"

# Constants for identity matrix
IDENTITY_MATRIX_2X2 = [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(1)]]

# --- Problem Generation Functions ---

def _generate_verify_inverse_problem(level):
    """
    Generates a problem asking to verify if matrix B is the inverse of matrix A.
    """
    ensure_invertible = True
    min_val = -3 if level == 1 else -5
    max_val = 3 if level == 1 else 5

    A_data, det_A = _generate_random_matrix_2x2(min_val=min_val, max_val=max_val, ensure_invertible=ensure_invertible, det_min_abs=1)
    A_inv_data = _calculate_inverse_2x2(A_data)

    is_correct_inverse = random.choice([True, False])

    if is_correct_inverse:
        B_data = A_inv_data
        correct_answer_value = "是"
    else:
        B_modified_data = [row[:] for row in A_inv_data] # Deep copy
        row_idx = random.randint(0, 1)
        col_idx = random.randint(0, 1)
        original_val = B_modified_data[row_idx][col_idx]
        
        # Ensure modification makes it clearly not the inverse
        if level == 1:
            change_val = Fraction(random.choice([-1, 1]) * random.randint(1, 2))
        else:
            change_val = Fraction(random.choice([-1, 1]) * random.randint(1, 2), random.randint(1, 3))
        
        new_val = original_val + change_val
        if new_val == original_val: # Avoid accidental no-change
             new_val = original_val + Fraction(1) if original_val != Fraction(0) else Fraction(1) # Force change
        B_modified_data[row_idx][col_idx] = new_val
        B_data = B_modified_data
        correct_answer_value = "否"
        
        # Double check to prevent accidental correct inverse after modification
        if _multiply_matrices_2x2(A_data, B_data) == IDENTITY_MATRIX_2X2:
             B_modified_data[row_idx][col_idx] = original_val + Fraction(random.choice([-3,3]), random.randint(1,3) if level > 1 else 1)
             B_data = B_modified_data

    question_text = f"驗證矩陣 $B = {_format_matrix_latex(B_data)}$ 為 $A = {_format_matrix_latex(A_data)}$ 的反方陣。請回答 '是' 或 '否'。"
    
    return {
        "question_text": question_text,
        "answer": correct_answer_value, # Store simple string answer for comparison
        "correct_answer": correct_answer_value # Store for display in feedback
    }

def _generate_find_inverse_problem(level):
    """
    Generates a problem asking to find the inverse of a 2x2 matrix, or to state if it doesn't exist.
    """
    min_val = -5 if level == 1 else -7
    max_val = 5 if level == 1 else 7
    det_min_abs = 1 if level == 1 else random.randint(1,3)

    # Probability of having no inverse (higher for higher levels)
    has_inverse = random.random() > (0.1 if level == 1 else 0.3)

    if has_inverse:
        A_data, det_A = _generate_random_matrix_2x2(min_val=min_val, max_val=max_val, ensure_invertible=True, det_min_abs=det_min_abs)
        A_inv_data = _calculate_inverse_2x2(A_data)
        
        question_text = f"求二階方陣 $A = {_format_matrix_latex(A_data)}$ 的反方陣 $A^{{-1}}$。"
        correct_answer_value = A_inv_data # Store actual matrix data
        correct_answer_display = _format_matrix_latex(A_inv_data) # Store formatted string for display
    else:
        while True:
            k = random.randint(min_val, max_val)
            a_val = random.randint(min_val, max_val)
            b_val = random.randint(min_val, max_val)
            # Ensure not all zeros, and not trivial like [1,0; 0,0]
            if a_val == 0 and b_val == 0:
                a_val = 1 
            # Create a matrix with linearly dependent rows/columns to ensure det=0
            A_data = [[Fraction(a_val), Fraction(b_val)], [Fraction(a_val*k), Fraction(b_val*k)]]
            if _calculate_determinant(A_data) == 0 and not all(x==0 for row in A_data for x in row):
                break
        
        question_text = f"判斷二階方陣 $A = {_format_matrix_latex(A_data)}$ 是否有反方陣；若有，求其反方陣。"
        correct_answer_value = "沒有反方陣" # Store simple string answer
        correct_answer_display = "沒有反方陣"

    return {
        "question_text": question_text,
        "answer": correct_answer_value, 
        "correct_answer": correct_answer_display
    }

def _generate_solve_AX_B_problem(level):
    """
    Generates a problem to solve the matrix equation AX=B for X.
    """
    min_val = -3 if level == 1 else -5
    max_val = 3 if level == 1 else 5
    det_min_abs = 1 if level == 1 else random.randint(1,2)

    A_data, det_A = _generate_random_matrix_2x2(min_val=min_val, max_val=max_val, ensure_invertible=True, det_min_abs=det_min_abs)
    # A_inv = _calculate_inverse_2x2(A_data) # The inverse is used internally but not explicitly generated for problem text

    X_data, _ = _generate_random_matrix_2x2(min_val=min_val, max_val=max_val, ensure_invertible=False)

    B_data = _multiply_matrices_2x2(A_data, X_data)

    question_text = f"設矩陣 $A = {_format_matrix_latex(A_data)}$ 及 $B = {_format_matrix_latex(B_data)}$ 滿足 $AX=B$。求 $X$。"
    correct_answer_value = X_data # Store actual matrix data
    correct_answer_display = _format_matrix_latex(X_data)

    return {
        "question_text": question_text,
        "answer": correct_answer_value,
        "correct_answer": correct_answer_display
    }

def _generate_no_inverse_condition_problem(level):
    """
    Generates a problem to find a variable 'a' such that a given matrix has no inverse.
    The matrix will be of the form [[a-C1, C2], [C3, a-C4]].
    """
    min_k_val = -3 if level == 1 else -5
    max_k_val = 3 if level == 1 else 5
    k_target = random.randint(min_k_val, max_k_val) # One of the 'a' values to be solved for.

    r1 = k_target
    r2 = k_target # Simplest case: repeated root
    if random.random() < 0.5 and level > 1: # Allow distinct roots for higher levels
        r2 = random.randint(min_k_val, max_k_val)
        while r2 == r1:
            r2 = random.randint(min_k_val, max_k_val)
            
    sum_roots = r1 + r2
    prod_roots = r1 * r2

    # Need C1, C4, C2, C3 such that:
    # C1 + C4 = sum_roots
    # C1 * C4 - C2 * C3 = prod_roots
    
    # Pick C1 randomly, then C4 is determined
    C1 = random.randint(1, 5) * random.choice([-1, 1])
    C4 = sum_roots - C1
    
    # Calculate required product for C2 * C3
    target_product = C1 * C4 - prod_roots
    
    # Find factors for target_product to get C2 and C3
    factors_for_product = []
    # Include 0 if target_product is 0, to allow for C2 or C3 to be 0
    if target_product == 0:
        factors_for_product.extend([0]) 
    for i in range(1, int(abs(target_product)**0.5) + 1):
        if target_product % i == 0:
            factors_for_product.append(i)
            factors_for_product.append(target_product // i)
    factors_for_product = list(set([f * sign for f in factors_for_product for sign in [-1, 1]])) # Unique factors, positive/negative
    if not factors_for_product: # Should not happen if target_product is non-zero, but as fallback
        factors_for_product = [1, -1] if target_product != 0 else [0]
            
    C2 = random.choice(factors_for_product)
    if C2 == 0:
        # If C2 is 0, then target_product must be 0 for a solution. C3 can be any non-zero value.
        C3 = random.randint(1,5) * random.choice([-1,1]) 
    else:
        C3 = target_product // C2
    
    # Construct the matrix string for display
    display_matrix_str = r"\begin{{bmatrix}} "
    
    # Handle the 'a - C' parts (e.g., a-2 becomes a-2, a-(-3) becomes a+3)
    term1 = f"a{'+' if -C1 > 0 else ''}{str(-C1)}" if -C1 != 0 else "a"
    term4 = f"a{'+' if -C4 > 0 else ''}{str(-C4)}" if -C4 != 0 else "a"
    
    display_matrix_str += f"{term1} & {C2} \\\\ {C3} & {term4}"
    display_matrix_str += r" \end{{bmatrix}}"
    
    question_text = f"已知矩陣 ${display_matrix_str}$ 沒有反方陣，求 $a$ 的值。若有多個解，請以半形逗號 ',' 分隔，例如 '2,3'。"
    
    # The correct answer should be a string of roots
    solutions = sorted(list(set([r1, r2]))) # Remove duplicates and sort for consistent answer string
    correct_answer_value = ",".join(map(str, solutions))
    
    return {
        "question_text": question_text,
        "answer": correct_answer_value,
        "correct_answer": correct_answer_value
    }


def generate(level=1):
    """
    Generates a problem related to the inverse of a second-order matrix.
    Problem types include verification, finding inverse, solving matrix equations,
    and finding conditions for no inverse.
    """
    problem_types = [
        _generate_verify_inverse_problem,
        _generate_find_inverse_problem,
        _generate_solve_AX_B_problem,
        _generate_no_inverse_condition_problem
    ]
    
    # Adjust problem distribution by level
    if level == 1:
        # Level 1 focuses on basic inverse calculation and verification
        chosen_type = random.choice(problem_types[:3]) 
    elif level == 2:
        # Level 2 introduces all types, potentially more complex numbers
        chosen_type = random.choice(problem_types)
    else: # level 3 and higher, all types with potentially larger/fractional values
        chosen_type = random.choice(problem_types)

    return chosen_type(level)

# --- Check Function ---

def _parse_matrix_string(matrix_str):
    """
    Parses a string representation of a 2x2 matrix into [[Fraction, Fraction], [Fraction, Fraction]].
    Handles various formats like "[[a,b],[c,d]]", "a b; c d", LaTeX format without \begin \end,
    or just 4 numbers separated by space/comma/semicolon for 2x2.
    Returns None if parsing fails.
    """
    matrix_str = matrix_str.strip()
    
    # Remove common matrix delimiters (e.g., [[ ]], { }, \begin{bmatrix}, \end{bmatrix})
    matrix_str = re.sub(r'(\\[lb]egin\{bmatrix\}|\\[re]nd\{bmatrix\}|\[\[|\]\]|\{\{|\}\}|\[|\]|\(|\))', '', matrix_str)
    
    # Standardize row separators: replace \\ or ; with a common internal marker (e.g., '|')
    matrix_str = matrix_str.replace(r'\\', '|').replace(';', '|').replace('\n', '|')

    # Split into rows
    rows_str_list = matrix_str.split('|')
    
    # Filter out empty row strings
    rows_str_list = [row_s.strip() for row_s in rows_str_list if row_s.strip()]
    
    if not rows_str_list:
        # If no explicit row separators, assume it's a flat list of 4 elements for a 2x2 matrix.
        # Try splitting by comma, space, or both.
        elements_flat = re.findall(r"[-]?\d+(?:/\d+)?|\d+", matrix_str) # Regex for numbers and fractions
        if len(elements_flat) == 4:
            rows_str_list = [f"{elements_flat[0]} {elements_flat[1]}", f"{elements_flat[2]} {elements_flat[3]}"]
        else:
            return None # Cannot parse
            
    if len(rows_str_list) != 2:
        return None # Not a 2x2 matrix

    parsed_matrix = []
    for row_s in rows_str_list:
        # Extract elements from each row using a regex that handles integers and fractions
        elements_str = re.findall(r"[-]?\d+(?:/\d+)?|\d+", row_s)
        
        if len(elements_str) != 2:
            return None # Row does not have 2 elements
        
        row_data = []
        for elem_s in elements_str:
            try:
                row_data.append(Fraction(elem_s))
            except ValueError:
                return None # Failed to parse element
        parsed_matrix.append(row_data)
        
    return parsed_matrix

def check(user_answer, correct_answer):
    """
    Checks the user's answer against the correct answer for matrix problems.
    Handles string answers ("是", "否", "沒有反方陣", "a,b") and matrix answers.
    """
    user_answer = user_answer.strip()

    is_correct = False
    result_text = ""

    if isinstance(correct_answer, str):
        # Case 1: Correct answer is a simple string (e.g., "是", "否", "沒有反方陣", "1,2")
        
        # Handle "是" / "否" type answers
        if correct_answer in ["是", "否"]:
            if user_answer.lower() in ["是", "yes", "true"] and correct_answer == "是":
                is_correct = True
            elif user_answer.lower() in ["否", "no", "false"] and correct_answer == "否":
                is_correct = True
            
            feedback_correct_ans = f"'{correct_answer}'"
            if not is_correct:
                result_text = f"答案不正確。正確答案應為：{feedback_correct_ans}"
            else:
                result_text = f"完全正確！答案是 {feedback_correct_ans}。"
                
        elif correct_answer == "沒有反方陣":
            if user_answer.lower() in ["沒有反方陣", "no inverse", "none"]:
                is_correct = True

            feedback_correct_ans = f"'{correct_answer}'"
            if not is_correct:
                result_text = f"答案不正確。正確答案應為：{feedback_correct_ans}"
            else:
                result_text = f"完全正確！答案是 {feedback_correct_ans}。"
        
        else: # Assume it's a numeric string like "1,2" for roots of a quadratic.
            try:
                user_parts = sorted([Fraction(p.strip()) for p in user_answer.split(',') if p.strip()])
                correct_parts = sorted([Fraction(p.strip()) for p in correct_answer.split(',') if p.strip()])
                
                is_correct = (user_parts == correct_parts)
                
                # Format the correct answer display for the feedback
                feedback_correct_ans = f"${correct_answer}$"
                if not is_correct:
                    result_text = f"答案不正確。正確答案應為：{feedback_correct_ans}"
                else:
                    result_text = f"完全正確！答案是 {feedback_correct_ans}。"
            except ValueError:
                result_text = f"您的答案格式不正確，請檢查是否輸入為數字或以逗號分隔的數字。正確答案應為：${correct_answer}$"


    else: # Case 2: Correct answer is a matrix (list of lists of Fractions)
        # Try to parse user input as a matrix
        user_matrix_parsed = _parse_matrix_string(user_answer)
        
        if user_matrix_parsed is None:
            is_correct = False
            result_text = f"您的答案格式不正確，請檢查是否輸入為二階方陣。正確答案應為：${_format_matrix_latex(correct_answer)}$"
        else:
            # Compare parsed user matrix with the correct_answer matrix
            # Fraction objects already simplify themselves, so direct comparison is safe.
            normalized_correct_matrix = [[val for val in row] for row in correct_answer]
            normalized_user_matrix = [[val for val in row] for row in user_matrix_parsed]

            if normalized_user_matrix == normalized_correct_matrix:
                is_correct = True
                result_text = f"完全正確！答案是 ${_format_matrix_latex(correct_answer)}$。"
            else:
                is_correct = False
                result_text = f"答案不正確。正確答案應為：${_format_matrix_latex(correct_answer)}$"
    
    return {"correct": is_correct, "result": result_text, "next_question": True}