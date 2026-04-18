import random
from fractions import Fraction
import math

def calculate_determinant(matrix):
    """
    Calculates the determinant of a 3x3 matrix using Sarrus' Rule.
    matrix is a list of lists, e.g., [[a,b,c],[d,e,f],[g,h,i]]
    """
    a, b, c = matrix[0]
    d, e, f = matrix[1]
    g, h, i = matrix[2]

    # Sarrus' Rule: (aei + bfg + cdh) - (ceg + afh + bdi)
    det = (a * e * i + b * f * g + c * d * h) - \
          (c * e * g + a * f * h + b * d * i)
    return det

def format_matrix_latex(matrix_elements):
    """
    Formats a 3x3 matrix (list of lists or list of strings for variable 'x')
    into a LaTeX string for display as a determinant.
    """
    return r"\begin{{vmatrix}} {} & {} & {} \\ {} & {} & {} \\ {} & {} & {} \end{{vmatrix}}".format(
        matrix_elements[0][0], matrix_elements[0][1], matrix_elements[0][2],
        matrix_elements[1][0], matrix_elements[1][1], matrix_elements[1][2],
        matrix_elements[2][0], matrix_elements[2][1], matrix_elements[2][2]
    )

def generate_direct_calculation(level):
    """
    Generates a problem asking for the direct calculation of a 3x3 determinant.
    """
    val_range_min = -5 if level == 1 else -10 if level == 2 else -15
    val_range_max = 5 if level == 1 else 10 if level == 2 else 15
    
    matrix = []
    for _ in range(3):
        row = [random.randint(val_range_min, val_range_max) for _ in range(3)]
        matrix.append(row)

    # Occasionally make it a triangular matrix for easier calculation
    if random.random() < 0.2 and level > 1:
        if random.choice([True, False]): # Upper triangular
            matrix[1][0] = 0
            matrix[2][0] = 0
            matrix[2][1] = 0
        else: # Lower triangular
            matrix[0][1] = 0
            matrix[0][2] = 0
            matrix[1][2] = 0
            
    # Occasionally make determinant 0 (e.g., two identical rows)
    if random.random() < 0.1 and level > 1:
        row_idx1 = random.randint(0, 2)
        row_idx2 = (row_idx1 + random.choice([1, 2])) % 3
        matrix[row_idx2] = list(matrix[row_idx1]) # Copy a row

    det_value = calculate_determinant(matrix)
    
    question_text = f"求下列三階行列式的值。<br>${format_matrix_latex(matrix)}$"
    correct_answer = str(det_value)
    
    solution_text = (f"根據三階行列式的展開式（或薩魯斯法則），<br>"
                     f"${format_matrix_latex(matrix)} = {det_value}$。")
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "solution": solution_text
    }

def generate_volume_parallelepiped(level):
    """
    Generates a problem asking for the volume of a parallelepiped formed by three vectors.
    """
    val_range_min = -5 if level == 1 else -8 if level == 2 else -10
    val_range_max = 5 if level == 1 else 8 if level == 2 else 10

    vecs = []
    for _ in range(3):
        vec = [random.randint(val_range_min, val_range_max) for _ in range(3)]
        vecs.append(vec)

    # Occasionally make vectors coplanar for a 0 volume
    if random.random() < 0.2 and level > 1:
        # Make the third vector a linear combination of the first two
        k1 = random.randint(-2, 2)
        k2 = random.randint(-2, 2)
        # Ensure it's not the zero vector unless both k1 and k2 are 0 and vec1, vec2 were also zeros, which is rare.
        if k1 == 0 and k2 == 0:
            k1 = random.choice([-1, 1]) # Ensure non-trivial linear combination

        vecs[2] = [k1 * vecs[0][i] + k2 * vecs[1][i] for i in range(3)]

    matrix = vecs
    det_value = calculate_determinant(matrix)
    volume = abs(det_value)
    
    vec_a_str = f"({vecs[0][0]}, {vecs[0][1]}, {vecs[0][2]})"
    vec_b_str = f"({vecs[1][0]}, {vecs[1][1]}, {vecs[1][2]})"
    vec_c_str = f"({vecs[2][0]}, {vecs[2][1]}, {vecs[2][2]})"

    question_text = (f"求向量 $\\vec{{a}}={vec_a_str}$, $\\vec{{b}}={vec_b_str}$, $\\vec{{c}}={vec_c_str}$ "
                     f"所決定的平行六面體之體積。")
    correct_answer = str(volume)
    
    solution_text = (f"利用三階行列式的幾何意義，由向量 $\\vec{{a}}$, $\\vec{{b}}$, $\\vec{{c}}$ 所決定的平行六面體體積 "
                     f"為其混合積的絕對值，即 $V = |\\det(\\vec{{a}}, \\vec{{b}}, \\vec{{c}})|$。<br>"
                     f"$V = |{format_matrix_latex(matrix)}| = |{det_value}| = {volume}$。")
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "solution": solution_text
    }

def generate_coplanarity(level):
    """
    Generates a problem asking for a missing coordinate for four coplanar points.
    Assumes O(0,0,0) as one point, so vectors OA, OB, OC are used.
    """
    val_range_min = -5 if level == 1 else -8 if level == 2 else -10
    val_range_max = 5 if level == 1 else 8 if level == 2 else 10

    # Loop until two non-collinear vectors are found (to form a plane)
    while True:
        vec1 = [random.randint(val_range_min, val_range_max) for _ in range(3)]
        vec2 = [random.randint(val_range_min, val_range_max) for _ in range(3)]
        
        # Check if vec1 and vec2 are linearly dependent (collinear)
        # Avoid division by zero: if components are 0, handle carefully.
        is_collinear = True
        if all(v == 0 for v in vec1) or all(v == 0 for v in vec2):
            is_collinear = True # If one is zero vector, they are collinear
        else:
            ratios = []
            for i in range(3):
                if vec1[i] != 0 and vec2[i] != 0:
                    ratios.append(Fraction(vec1[i], vec2[i]))
                elif vec1[i] == 0 and vec2[i] != 0:
                    ratios.append(0) # Effectively ratio is 0
                elif vec1[i] != 0 and vec2[i] == 0:
                    ratios.append(float('inf')) # Undefined ratio
            
            if len(ratios) > 0 and all(r == ratios[0] for r in ratios):
                is_collinear = True
            else:
                is_collinear = False
        
        if not is_collinear:
            break

    # Generate a third vector that is a linear combination of vec1 and vec2
    k1 = random.randint(-2, 2)
    k2 = random.randint(-2, 2)
    # Ensure at least one coefficient is non-zero to avoid vec3 being zero vector (unless vec1, vec2 are also zero, which is handled).
    if k1 == 0 and k2 == 0:
        k1 = random.choice([-1, 1])

    vec3_base = [k1 * vec1[i] + k2 * vec2[i] for i in range(3)]

    # Choose a position for the variable 'a' in vec3
    a_idx = random.randint(0, 2)
    correct_a_value = vec3_base[a_idx]
    
    # Construct the matrix for display with 'a'
    matrix_for_display = [list(vec1), list(vec2), list(vec3_base)]
    matrix_for_display[2][a_idx] = 'a' # Placeholder for 'a'

    # Determine the points (assuming O is origin)
    point_O_str = r"$O(0,0,0)$"
    point_A_str = f"$A({vec1[0]}, {vec1[1]}, {vec1[2]})$"
    point_B_str = f"$B({vec2[0]}, {vec2[1]}, {vec2[2]})$"
    point_C_str = f"$C({matrix_for_display[2][0]}, {matrix_for_display[2][1]}, {matrix_for_display[2][2]})$"
    
    variable_name = 'a'
    
    question_text = (f"在空間中，已知四點 {point_O_str}, {point_A_str}, {point_B_str}, {point_C_str} "
                     f"落在同一平面上，求實數 ${variable_name}$ 的值。")
    
    correct_answer = str(correct_a_value)
    
    solution_text = (f"因為 $O, A, B, C$ 四點共平面，所以向量 $\\vec{{OA}}$, $\\vec{{OB}}$, $\\vec{{OC}}$ 共平面。"
                     f"<br>由三個向量共平面的條件，得其行列式值為 $0$。<br>"
                     f"${format_matrix_latex(matrix_for_display)}=0$。"
                     f"<br>展開並解方程式可得 ${variable_name}={correct_a_value}$。")

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "solution": solution_text
    }

def generate_determinant_equation(level):
    """
    Generates a problem where a variable 'x' is inside a determinant and its value is given.
    The problem will be simplified to a linear equation in 'x'.
    """
    val_range_min = -5 if level == 1 else -8 if level == 2 else -10
    val_range_max = 5 if level == 1 else 8 if level == 2 else 10
    
    # Loop until a non-zero cofactor for the 'x' position is found
    while True:
        matrix_base = []
        for _ in range(3):
            row = [random.randint(val_range_min, val_range_max) for _ in range(3)]
            matrix_base.append(row)

        x_row, x_col = random.randint(0, 2), random.randint(0, 2)
        original_val_at_x_pos = matrix_base[x_row][x_col]

        # Calculate the cofactor for the position (x_row, x_col)
        submatrix_rows = [r for r in range(3) if r != x_row]
        submatrix_cols = [c for c in range(3) if c != x_col]
        
        submatrix = [[matrix_base[r][c] for c in submatrix_cols] for r in submatrix_rows]
        
        cofactor_val = submatrix[0][0] * submatrix[1][1] - submatrix[0][1] * submatrix[1][0]
        cofactor_val *= ((-1)**(x_row + x_col))

        if cofactor_val != 0:
            break # Found a suitable cofactor, exit loop
        
    original_det = calculate_determinant(matrix_base)

    matrix_with_x_display = [list(row) for row in matrix_base]
    matrix_with_x_display[x_row][x_col] = 'x'

    correct_x = random.randint(-5, 5) # Set the solution for x to be a simple integer
    
    # Calculate the target determinant value such that the equation yields `correct_x`
    # current_det_contribution = original_val_at_x_pos * cofactor_val
    # new_det_contribution = correct_x * cofactor_val
    # target_det = original_det - current_det_contribution + new_det_contribution
    target_det = original_det - original_val_at_x_pos * cofactor_val + correct_x * cofactor_val

    question_text = (f"已知實數 $x$ 滿足 ${format_matrix_latex(matrix_with_x_display)} = {target_det}$，求 $x$ 的值。")
    correct_answer = str(correct_x)

    solution_text = (f"將行列式依第 ${x_row+1}$ 行（或列）降階展開，可得一個關於 $x$ 的線性方程式。<br>"
                     f"展開式會包含 $x \\cdot ({cofactor_val})$ 這一項。<br>"
                     f"解此方程式，得 $x={correct_x}$。")

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "solution": solution_text
    }

def generate_properties_mcq(level):
    """
    Generates a multiple choice question about determinant properties (True/False).
    """
    
    properties = [
        {"statement": r"將一行(列)所有元素同乘以 $k$，則行列式值變為 $k$ 倍。", "correct": True, "type": "scalar_row_mult"},
        {"statement": r"行列互換 (轉置矩陣) 其值不變，即 $|\\mathbf{{A}}| = |\\mathbf{{A}}^T|$。", "correct": True, "type": "transpose"},
        {"statement": r"兩行(列)對調，則行列式值變號。", "correct": True, "type": "row_swap"},
        {"statement": r"將某一行(列)的 $k$ 倍加到另一行(列)，則行列式值不變。", "correct": True, "type": "row_op"},
        {"statement": r"行列式中有兩行(列)相同，則行列式值為 $0$。", "correct": True, "type": "identical_rows"},
        {"statement": r"行列式中有一行(列)為全 $0$，則行列式值為 $0$。", "correct": True, "type": "zero_row"},
        {"statement": r"若將一個三階行列式所有元素同乘以 $k$，則行列式值變為 $k$ 倍。", "correct": False, "false_version": r"若將一個三階行列式所有元素同乘以 $k$，則行列式值變為 $k^3$ 倍。", "type": "scalar_matrix_mult"},
        {"statement": r"由三個向量 $\vec{{a}}, \vec{{b}}, \vec{{c}}$ 所決定的平行六面體之體積為 $(\vec{{a}} \\times \vec{{b}}) \\cdot \vec{{c}}$。", "correct": False, "false_version": r"由三個向量 $\vec{{a}}, \vec{{b}}, \vec{{c}}$ 所決定的平行六面體之體積為 $|(\vec{{a}} \\times \vec{{b}}) \\cdot \vec{{c}}|$。", "type": "volume_scalar_triple"}
    ]

    selected_prop = random.choice(properties)
    is_statement_correct = selected_prop["correct"]
    
    # Decide if the question asks for 'correct' (O) or 'incorrect' (X) statement
    question_asks_for_correct = random.choice([True, False])
    
    statement_to_ask = selected_prop["statement"]
    
    if question_asks_for_correct: # "下列敘述對的打「○」，錯的打「×」。"
        correct_answer_for_question = "O" if is_statement_correct else "X"
        question_text_prefix = "下列敘述對的打「○」，錯的打「×」。<br>"
    else: # "下列敘述錯誤的打「○」，正確的打「×」。"
        correct_answer_for_question = "O" if not is_statement_correct else "X"
        question_text_prefix = "下列敘述錯誤的打「○」，正確的打「×」。<br>"

    question_text = f"{question_text_prefix}( ) {statement_to_ask}"
    correct_answer = correct_answer_for_question
    
    solution_text = ""
    if is_statement_correct:
        solution_text = f"該敘述是正確的。"
    else:
        solution_text = f"該敘述是錯誤的。正確的說法是：{selected_prop.get('false_version', '請參考行列式基本性質。')}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "solution": solution_text
    }

def generate(level=1):
    """
    Generates a problem related to third-order determinants.
    """
    problem_types = [
        generate_direct_calculation,
        generate_volume_parallelepiped,
        generate_coplanarity,
        generate_determinant_equation,
        generate_properties_mcq
    ]
    
    # Adjust problem distribution based on level
    # Weights for [direct_calc, volume, coplanarity, det_equation, properties_mcq]
    weights = [1] * len(problem_types) 

    if level == 1:
        weights = [4, 2, 1, 1, 2] # Focus on direct calculation and basic properties
    elif level == 2:
        weights = [3, 3, 2, 2, 2] # More balanced, introduce equations and coplanarity more
    else: # level == 3
        weights = [2, 3, 3, 3, 2] # Emphasize geometric problems and equations
        
    chosen_generator = random.choices(problem_types, weights=weights, k=1)[0]
    return chosen_generator(level)

def check(user_answer, correct_answer):
    """
    Checks if the user's answer is correct.
    Handles numerical answers (float/int) and 'O'/'X' for true/false.
    """
    user_answer_cleaned = user_answer.strip().replace(" ", "").upper()
    correct_answer_cleaned = correct_answer.strip().replace(" ", "").upper()
    
    is_correct = False
    result_text = ""

    if user_answer_cleaned == correct_answer_cleaned:
        is_correct = True
    else:
        try:
            # Try converting to float for numerical comparison
            if float(user_answer_cleaned) == float(correct_answer_cleaned):
                is_correct = True
        except ValueError:
            pass # Not a numerical answer, or conversion failed

    if is_correct:
        result_text = f"完全正確！答案是 ${correct_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer}$"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}