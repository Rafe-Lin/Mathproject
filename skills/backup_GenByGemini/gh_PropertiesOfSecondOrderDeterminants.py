import random

def _det2x2(matrix):
    """Calculates the determinant of a 2x2 matrix."""
    return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]

def _format_expr_with_two_vars(coeff_v1, v1_str, coeff_v2, v2_str):
    """
    Helper function to format a linear expression like 'k1*var1 + k2*var2' for LaTeX display.
    Example: (3, 'a', -2, 'b') -> "3a - 2b"
    """
    parts = []

    # Handle first variable (v1_str)
    if coeff_v1 != 0:
        if coeff_v1 == 1:
            parts.append(v1_str)
        elif coeff_v1 == -1:
            parts.append(f"-{v1_str}")
        else:
            parts.append(f"{coeff_v1}{v1_str}")
    
    # Handle second variable (v2_str)
    if coeff_v2 != 0:
        op = ' + ' if coeff_v2 > 0 else ' - '
        val_abs = coeff_v2 if coeff_v2 > 0 else -coeff_v2 # Absolute value for display

        if parts: # If there's already a term, add operator
            parts.append(op)
        elif coeff_v2 < 0: # If it's the first term and negative
            parts.append('-')

        if val_abs == 1:
            parts.append(v2_str)
        else:
            parts.append(f"{val_abs}{v2_str}")
    
    # Return formatted string, default to "0" if all coefficients are zero (shouldn't happen in this generator)
    return "".join(parts) if parts else "0"


def generate_simplify_large_numbers():
    """
    生成利用行列式性質簡化計算的題目，通常涉及倍加運算。
    例如：[[4231, 1000], [4232, 1001]]
    """
    # Generate two base "small" numbers
    val1 = random.randint(-10, 10)
    val2 = random.randint(-10, 10)
    
    # Generate two "large" numbers to make elements seem big, but simplify to small parts
    large_base_1 = random.randint(100, 500) * random.choice([1, -1])
    large_base_2 = random.randint(100, 500) * random.choice([1, -1])
    
    matrix_to_solve = [[0, 0], [0, 0]]
    reduced_matrix = [[0, 0], [0, 0]]
    op_latex = ""
    explanation_hint = ""

    # Choose a type of simplification: R2-R1, R1-R2, C2-C1, C1-C2
    choice = random.choice([1, 2, 3, 4]) 
    
    if choice == 1: # R2 -> R2 - R1: [[L1, L2], [L1+v1, L2+v2]] becomes [[L1, L2], [v1, v2]]
        mat_a, mat_b = large_base_1, large_base_2
        mat_c, mat_d = large_base_1 + val1, large_base_2 + val2
        
        matrix_to_solve = [[mat_a, mat_b], [mat_c, mat_d]]
        reduced_matrix = [[mat_a, mat_b], [val1, val2]]
        op_latex = r"R_2 \to R_2 - R_1"
        explanation_hint = r"將第二列減去第一列"

    elif choice == 2: # R1 -> R1 - R2: [[L1+v1, L2+v2], [L1, L2]] becomes [[v1, v2], [L1, L2]]
        mat_c, mat_d = large_base_1, large_base_2
        mat_a, mat_b = large_base_1 + val1, large_base_2 + val2
        
        matrix_to_solve = [[mat_a, mat_b], [mat_c, mat_d]]
        reduced_matrix = [[val1, val2], [mat_c, mat_d]]
        op_latex = r"R_1 \to R_1 - R_2"
        explanation_hint = r"將第一列減去第二列"
        
    elif choice == 3: # C2 -> C2 - C1: [[L1, L1+v1], [L2, L2+v2]] becomes [[L1, v1], [L2, v2]]
        mat_a, mat_c = large_base_1, large_base_2
        mat_b, mat_d = large_base_1 + val1, large_base_2 + val2
        
        matrix_to_solve = [[mat_a, mat_b], [mat_c, mat_d]]
        reduced_matrix = [[mat_a, val1], [mat_c, val2]]
        op_latex = r"C_2 \to C_2 - C_1"
        explanation_hint = r"將第二行減去第一行"

    else: # choice == 4: # C1 -> C1 - C2: [[L1+v1, L1], [L2+v2, L2]] becomes [[v1, L1], [v2, L2]]
        mat_b, mat_d = large_base_1, large_base_2
        mat_a, mat_c = large_base_1 + val1, large_base_2 + val2
        
        matrix_to_solve = [[mat_a, mat_b], [mat_c, mat_d]]
        reduced_matrix = [[val1, mat_b], [val2, mat_d]]
        op_latex = r"C_1 \to C_1 - C_2"
        explanation_hint = r"將第一行減去第二行"

    correct_answer_value = _det2x2(reduced_matrix) # Determinant is unchanged by these operations

    question_text = (
        r"請利用行列式的性質，計算下列二階行列式的值："
        rf"$\begin{{vmatrix}} {matrix_to_solve[0][0]} & {matrix_to_solve[0][1]} \\ {matrix_to_solve[1][0]} & {matrix_to_solve[1][1]} \end{{vmatrix}}$"
    )
    
    explanation_text = (
        r"詳解：利用行列式的性質計算如下：<br>"
        rf"$\begin{{vmatrix}} {matrix_to_solve[0][0]} & {matrix_to_solve[0][1]} \\ {matrix_to_solve[1][0]} & {matrix_to_solve[1][1]} \end{{vmatrix}}$<br>"
        rf"利用性質（倍加運算）：{explanation_hint} ($ {op_latex} $)，行列式值不變。<br>"
        rf"$= \begin{{vmatrix}} {reduced_matrix[0][0]} & {reduced_matrix[0][1]} \\ {reduced_matrix[1][0]} & {reduced_matrix[1][1]} \end{{vmatrix}}$<br>"
        rf"$= ({reduced_matrix[0][0]}) \\times ({reduced_matrix[1][1]}) - ({reduced_matrix[0][1]}) \\times ({reduced_matrix[1][0]})$<br>"
        rf"$= {reduced_matrix[0][0] * reduced_matrix[1][1]} - {reduced_matrix[0][1] * reduced_matrix[1][0]} = {correct_answer_value}$"
    )

    return {
        "question_text": question_text,
        "answer": str(correct_answer_value),
        "correct_answer": str(correct_answer_value),
        "explanation": explanation_text
    }


def generate_transform_determinant():
    """
    生成給定基本行列式值，求經過變換後行列式值的題目。
    例如：已知 det([[a,b],[c,d]]) = 3，求 det([[3a+2b, 3a-4b], [3c+2d, 3c-4d]])。
    此題目類型設計為可透過一系列列/行運算簡化回原始形式。
    """
    # Coefficients for the transformations
    k1 = random.randint(2, 5) * random.choice([1, -1]) # Multiplier for C1
    k2 = random.randint(1, 3) * random.choice([1, -1]) # Multiplier for C1_new + k2*C2
    k3 = random.randint(2, 5) * random.choice([1, -1]) # Multiplier for C2

    base_det_value = random.randint(2, 10) * random.choice([1, -1])
    correct_answer_value = k1 * k3 * base_det_value

    # Construct the elements for the question matrix: [[k1*a + k2*b, k3*b], [k1*c + k2*d, k3*d]]
    q_m11 = _format_expr_with_two_vars(k1, 'a', k2, 'b')
    q_m12 = _format_expr_with_two_vars(k3, 'b', 0, '') 
    q_m21 = _format_expr_with_two_vars(k1, 'c', k2, 'd')
    q_m22 = _format_expr_with_two_vars(k3, 'd', 0, '') 

    question_text = (
        rf"已知 $\begin{{vmatrix}} a & b \\ c & d \end{{vmatrix}} = {base_det_value}$，"
        r"求下列二階行列式的值："
        rf"$\begin{{vmatrix}} {q_m11} & {q_m12} \\ {q_m21} & {q_m22} \end{{vmatrix}}$"
    )
    
    # Explanation steps
    explanation_parts = []
    explanation_parts.append(
        r"詳解：利用二階行列式的性質計算如下：<br>"
        rf"$\begin{{vmatrix}} {q_m11} & {q_m12} \\ {q_m21} & {q_m22} \end{{vmatrix}}$"
    )
    
    # Step 1: Factor out k3 from C2
    explanation_parts.append(
        rf"(利用性質：將第二行提出公因數 ${k3}$)<br>"
        rf"$= {k3} \begin{{vmatrix}} {_format_expr_with_two_vars(k1, 'a', k2, 'b')} & b \\ {_format_expr_with_two_vars(k1, 'c', k2, 'd')} & d \end{{vmatrix}}$"
    )
    
    # Step 2: C1 -> C1 - k2*C2 (eliminate k2*b and k2*d terms)
    explanation_parts.append(
        rf"(利用性質：將第二行乘以 ${-k2}$ 倍加到第一行 ($C_1 \to C_1 + ({-k2})C_2$)，行列式值不變)<br>"
        rf"$= {k3} \begin{{vmatrix}} {_format_expr_with_two_vars(k1, 'a', 0, '')} & b \\ {_format_expr_with_two_vars(k1, 'c', 0, '')} & d \end{{vmatrix}}$"
    )

    # Step 3: Factor out k1 from C1
    explanation_parts.append(
        rf"(利用性質：將第一行提出公因數 ${k1}$)<br>"
        rf"$= {k3} \\times {k1} \begin{{vmatrix}} a & b \\ c & d \end{{vmatrix}}$"
    )
    
    # Final step: substitute base determinant value
    explanation_parts.append(
        rf"$= {k3 * k1} \\times {base_det_value} = {correct_answer_value}$"
    )

    explanation_text = "<br>".join(explanation_parts)

    return {
        "question_text": question_text,
        "answer": str(correct_answer_value),
        "correct_answer": str(correct_answer_value),
        "explanation": explanation_text
    }


def generate_zero_determinant_problem():
    """
    生成行列式值為零的題目，利用成比例為零的性質。
    例如：[[a,b], [k*a, k*b]] 或 [[a, k*a], [b, k*b]]
    """
    val1 = random.randint(1, 15) * random.choice([1, -1])
    val2 = random.randint(1, 15) * random.choice([1, -1])
    
    # Ensure elements are not all zero, to avoid trivial cases
    while val1 == 0 and val2 == 0:
        val1 = random.randint(1, 15) * random.choice([1, -1])
        val2 = random.randint(1, 15) * random.choice([1, -1])

    k_factor = random.randint(2, 5) * random.choice([1, -1])

    choice = random.choice(['proportional_rows', 'proportional_cols'])

    matrix_to_solve = [[0, 0], [0, 0]]
    intermediate_matrix_elements = [0, 0, 0, 0] # For explanation step

    if choice == 'proportional_rows':
        matrix_to_solve[0][0] = val1
        matrix_to_solve[0][1] = val2
        matrix_to_solve[1][0] = k_factor * val1
        matrix_to_solve[1][1] = k_factor * val2
        reason = rf"因為第二列是第一列的 ${k_factor}$ 倍，即兩列成比例"
        op_to_show_zero = rf"將第一列乘以 ${-k_factor}$ 倍加到第二列 ($R_2 \to R_2 + ({-k_factor})R_1$)"
        intermediate_matrix_elements = [
            matrix_to_solve[0][0], matrix_to_solve[0][1],
            0, 0
        ]
    else: # proportional_cols
        matrix_to_solve[0][0] = val1
        matrix_to_solve[1][0] = val2
        matrix_to_solve[0][1] = k_factor * val1
        matrix_to_solve[1][1] = k_factor * val2
        reason = rf"因為第二行是第一行的 ${k_factor}$ 倍，即兩行成比例"
        op_to_show_zero = rf"將第一行乘以 ${-k_factor}$ 倍加到第二行 ($C_2 \to C_2 + ({-k_factor})C_1$)"
        intermediate_matrix_elements = [
            matrix_to_solve[0][0], 0,
            matrix_to_solve[1][0], 0
        ]

    correct_answer_value = 0 # By property

    question_text = (
        r"請利用行列式的性質，計算下列二階行列式的值："
        rf"$\begin{{vmatrix}} {matrix_to_solve[0][0]} & {matrix_to_solve[0][1]} \\ {matrix_to_solve[1][0]} & {matrix_to_solve[1][1]} \end{{vmatrix}}$"
    )

    explanation_text = (
        r"詳解：利用行列式的性質計算如下：<br>"
        rf"$\begin{{vmatrix}} {matrix_to_solve[0][0]} & {matrix_to_solve[0][1]} \\ {matrix_to_solve[1][0]} & {matrix_to_solve[1][1]} \end{{vmatrix}}$<br>"
        rf"利用性質（成比例為零）：{reason}，所以行列式值為零。<br>"
        r"或者，通過倍加運算證明：<br>"
        rf"({op_to_show_zero})<br>"
        rf"$= \begin{{vmatrix}} {intermediate_matrix_elements[0]} & {intermediate_matrix_elements[1]} \\ {intermediate_matrix_elements[2]} & {intermediate_matrix_elements[3]} \end{{vmatrix}}$<br>"
        rf"由於行列式有一列（或一行）全為零，所以其值為 $0$。"
    )

    return {
        "question_text": question_text,
        "answer": str(correct_answer_value),
        "correct_answer": str(correct_answer_value),
        "explanation": explanation_text
    }


def generate(level=1):
    """
    生成「二階行列式的性質」相關題目。
    包含：
    1. 利用倍加運算簡化計算
    2. 利用多重性質轉換行列式
    3. 利用成比例為零的性質
    """
    problem_type = random.choice([
        'simplify_large_numbers',
        'transform_determinant',
        'zero_determinant'
    ])
    
    if problem_type == 'simplify_large_numbers':
        return generate_simplify_large_numbers()
    elif problem_type == 'transform_determinant':
        return generate_transform_determinant()
    elif problem_type == 'zero_determinant':
        return generate_zero_determinant_problem()


def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    
    is_correct = False
    try:
        # For numerical answers, float comparison
        if float(user_answer) == float(correct_answer):
            is_correct = True
    except ValueError:
        # Fallback for non-numerical, though not expected for this skill
        if user_answer.lower() == correct_answer.lower():
            is_correct = True

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}