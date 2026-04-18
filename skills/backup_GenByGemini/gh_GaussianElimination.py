import random
from fractions import Fraction

def _matrix_to_latex(matrix):
    """
    Converts a matrix (list of lists of Fractions/ints) to a LaTeX string
    for an augmented matrix.
    Example: [[1, 2, 3, 4], [5, 6, 7, 8]] -> \begin{bmatrix} 1 & 2 & | & 3 \\ 5 & 6 & | & 7 \end{bmatrix}
    Assumes the last column is the RHS.
    """
    rows = []
    for r_idx, row in enumerate(matrix):
        formatted_row = []
        for c_idx, val in enumerate(row):
            if c_idx == len(row) - 1: # Vertical bar before the last element
                formatted_row.append(r"|")
            
            # Convert Fraction to string. If it's an integer, display as int.
            if isinstance(val, Fraction) and val.denominator == 1:
                formatted_row.append(str(int(val)))
            elif isinstance(val, Fraction):
                formatted_row.append(str(val))
            else: # Should already be Fraction, but as a safeguard
                formatted_row.append(str(val))
        rows.append(" & ".join(formatted_row))
    return r"\begin{bmatrix} " + r" \\ ".join(rows) + r" \end{bmatrix}"

def _system_to_latex(matrix, var_names):
    """
    Converts an augmented matrix (list of lists of Fractions/ints) to a LaTeX string
    for a system of linear equations.
    Example: [[1, 1, 1, 1], [-1, 3, 0, 0]] with var_names ['x', 'y', 'z']
    -> \begin{cases} x+y+z=1 \\ -x+3y=0 \end{cases}
    """
    equations = []
    num_vars = len(var_names)
    for row in matrix:
        lhs_parts = []
        for i in range(num_vars):
            coeff = row[i]
            if coeff == 0:
                continue
            var = var_names[i]
            
            coeff_str = ""
            if coeff == 1:
                coeff_str = ""
            elif coeff == -1:
                coeff_str = "-"
            elif isinstance(coeff, Fraction) and coeff.denominator == 1:
                coeff_str = str(int(coeff))
            else:
                coeff_str = str(coeff)
            
            # Add '+' for positive coefficients if not the first term
            if lhs_parts and coeff > 0:
                lhs_parts.append("+")
            # If coeff < 0, the '-' is already part of coeff_str
            
            if coeff_str == "-":
                lhs_parts.append(coeff_str + var)
            elif coeff_str == "":
                lhs_parts.append(var)
            else:
                lhs_parts.append(coeff_str + var)
                
        rhs = row[num_vars]
        
        # If all coefficients on LHS are zero
        if not lhs_parts: 
            lhs_str = "0"
        else:
            lhs_str = " ".join(lhs_parts).replace("+ -", "-") # Clean up "+ -" to "-"
            
        rhs_str = str(int(rhs) if isinstance(rhs, Fraction) and rhs.denominator == 1 else rhs)
        equations.append(f"{lhs_str} = {rhs_str}")
        
    return r"\begin{cases} " + r" \\ ".join(equations) + r" \end{cases}"

def _solve_gaussian_elimination(aug_matrix_fractions, var_names):
    """
    Performs Gaussian elimination to Reduced Row Echelon Form (RREF)
    and determines the solution type (unique, no solution, infinite solutions).
    
    Args:
        aug_matrix_fractions: A list of lists representing the augmented matrix,
                              with elements as fractions.Fraction.
        var_names: A list of strings for variable names, e.g., ['x', 'y', 'z'].
                              
    Returns:
        A tuple: (solution_type, solution_details, final_matrix_latex)
        - solution_type: "unique", "no_solution", or "infinite_solutions".
        - solution_details: A dict of solutions for 'unique' type, None otherwise.
        - final_matrix_latex: The LaTeX string of the matrix in RREF.
    """
    num_rows = len(aug_matrix_fractions)
    num_cols = len(aug_matrix_fractions[0]) # Includes RHS column
    num_vars = num_cols - 1

    matrix = [row[:] for row in aug_matrix_fractions] # Deep copy for manipulation

    # Forward elimination (to Reduced Row Echelon Form)
    lead = 0
    for r in range(num_rows):
        if lead >= num_vars:
            break
        i = r
        while i < num_rows and matrix[i][lead] == 0:
            i += 1
        if i == num_rows: # No pivot in this column, move to next column
            lead += 1
            continue
        
        # Swap rows to bring pivot to current row
        matrix[r], matrix[i] = matrix[i], matrix[r]
        
        # Normalize pivot row (make pivot 1)
        lv = matrix[r][lead]
        for j in range(lead, num_cols):
            matrix[r][j] /= lv
            
        # Eliminate other elements in the pivot column (make them 0)
        for i_row in range(num_rows):
            if i_row != r: # For all rows except the current pivot row
                factor = matrix[i_row][lead]
                for j in range(lead, num_cols):
                    matrix[i_row][j] -= factor * matrix[r][j]
        
        lead += 1

    # Determine solution type
    solution_type = "unique"
    solution_details = {}
    
    rank = 0
    for r_idx in range(num_rows):
        is_all_zeros_lhs = True
        for c_idx in range(num_vars):
            if matrix[r_idx][c_idx] != 0:
                is_all_zeros_lhs = False
                break
        
        if not is_all_zeros_lhs: # This row has a pivot
            rank += 1
        elif is_all_zeros_lhs and matrix[r_idx][num_vars] != 0:
            # Contradiction: [0, 0, ..., 0 | k] where k != 0
            solution_type = "no_solution"
            return solution_type, None, _matrix_to_latex(matrix)
    
    # If rank < num_vars, there are free variables -> infinite solutions
    if rank < num_vars:
        solution_type = "infinite_solutions"
    # If rank == num_vars and no contradiction, it's a unique solution.
    
    if solution_type == "unique":
        # Extract unique solution directly from RREF
        for i in range(num_vars):
            solution_details[var_names[i]] = matrix[i][num_vars]
    
    return solution_type, solution_details, _matrix_to_latex(matrix)


def _generate_solvable_matrix(num_vars, num_eqs, solution_type="unique"):
    """
    Generates an augmented matrix (list of lists of Fractions) corresponding to
    a system with the specified solution_type.
    """
    A = [[Fraction(0) for _ in range(num_vars + 1)] for _ in range(num_eqs)]
    
    if solution_type == "unique":
        # Generate an invertible main coefficient matrix
        # Start with a diagonal matrix to ensure independence
        for i in range(min(num_vars, num_eqs)):
            A[i][i] = Fraction(random.choice([-1, 1]))
        
        # Add random coefficients and apply random row operations to mix it up
        for _ in range(num_vars * 2): # Apply several random operations
            r1, r2 = random.sample(range(num_eqs), 2)
            factor = Fraction(random.randint(-2, 2))
            if factor == 0: continue # Skip zero factor
            for j in range(num_vars + 1):
                A[r1][j] += factor * A[r2][j]
        
        # Ensure the system has a unique solution by checking its determinant or RREF rank.
        # Simpler: Generate a random integer solution and then construct RHS
        # This will ensure solvability for the initial (potentially invertible) matrix.
        
        # Reset and use target solution to build matrix
        sol = [Fraction(random.randint(-5, 5)) for _ in range(num_vars)]
        
        # Generate random coefficients for a base matrix
        base_matrix = [[Fraction(random.randint(-3, 3)) for _ in range(num_vars)] for _ in range(num_eqs)]
        
        # Ensure the rank is full for unique solution. Quick check: make diagonal dominant.
        for i in range(min(num_vars, num_eqs)):
            if base_matrix[i][i] == 0:
                base_matrix[i][i] = Fraction(random.choice([-1, 1]))
            # Make diagonal dominant to improve chances of invertibility for square matrices
            # Or ensure leading 1s for echelon form
        
        # Calculate RHS based on the solution
        for i in range(num_eqs):
            rhs_val = Fraction(0)
            for j in range(num_vars):
                rhs_val += base_matrix[i][j] * sol[j]
            A[i] = base_matrix[i] + [rhs_val]

        # Apply random row operations to make it look more natural
        for _ in range(num_eqs * 2):
            r1 = random.randint(0, num_eqs - 1)
            r2 = random.randint(0, num_eqs - 1)
            if r1 == r2: continue
            
            op_type = random.choice(['swap', 'scale', 'add'])
            
            if op_type == 'swap':
                A[r1], A[r2] = A[r2], A[r1]
            elif op_type == 'scale':
                factor = Fraction(random.choice([-2, -1, 1, 2]))
                for j in range(num_vars + 1):
                    A[r1][j] *= factor
            elif op_type == 'add':
                factor = Fraction(random.randint(-2, 2))
                if factor == 0: continue
                for j in range(num_vars + 1):
                    A[r1][j] += factor * A[r2][j]

    elif solution_type == "infinite_solutions":
        # Generate `num_vars - 1` linearly independent rows
        # For simplicity, assume num_eqs = num_vars = 3, target rank = 2
        # Then make the last row a linear combination of the first two.
        
        R1 = [Fraction(random.randint(-3, 3)) for _ in range(num_vars + 1)]
        R2 = [Fraction(random.randint(-3, 3)) for _ in range(num_vars + 1)]
        
        # Ensure R1 and R2 are not all zeros for the coefficient part
        while all(x == 0 for x in R1[:num_vars]):
            R1 = [Fraction(random.randint(-3, 3)) for _ in range(num_vars + 1)]
        while all(x == 0 for x in R2[:num_vars]):
            R2 = [Fraction(random.randint(-3, 3)) for _ in range(num_vars + 1)]
            
        c1 = Fraction(random.randint(-2, 2))
        c2 = Fraction(random.randint(-2, 2))
        # Ensure non-trivial combination for dependence
        while c1 == 0 and c2 == 0: 
            c1 = Fraction(random.randint(-2, 2))
            c2 = Fraction(random.randint(-2, 2))
            
        R3 = [c1 * R1[j] + c2 * R2[j] for j in range(num_vars + 1)]
        
        A[0] = R1
        A[1] = R2
        A[2] = R3
        random.shuffle(A) # Shuffle rows to hide the dependency

    elif solution_type == "no_solution":
        # Generate `num_vars - 1` linearly independent rows
        # For simplicity, assume num_eqs = num_vars = 3, target rank = 2 for LHS
        # Then make the last row's coefficients a linear combination of the first two,
        # but with a different RHS to create a contradiction.
        
        R1 = [Fraction(random.randint(-3, 3)) for _ in range(num_vars + 1)]
        R2 = [Fraction(random.randint(-3, 3)) for _ in range(num_vars + 1)]
        
        while all(x == 0 for x in R1[:num_vars]):
            R1 = [Fraction(random.randint(-3, 3)) for _ in range(num_vars + 1)]
        while all(x == 0 for x in R2[:num_vars]):
            R2 = [Fraction(random.randint(-3, 3)) for _ in range(num_vars + 1)]
            
        c1 = Fraction(random.randint(-2, 2))
        c2 = Fraction(random.randint(-2, 2))
        while c1 == 0 and c2 == 0:
            c1 = Fraction(random.randint(-2, 2))
            c2 = Fraction(random.randint(-2, 2))
            
        R3_coeffs = [c1 * R1[j] + c2 * R2[j] for j in range(num_vars)]
        R3_rhs = c1 * R1[num_vars] + c2 * R2[num_vars] + Fraction(random.choice([-3, -2, -1, 1, 2, 3])) # Add non-zero difference
        
        A[0] = R1
        A[1] = R2
        A[2] = R3_coeffs + [R3_rhs]
        random.shuffle(A) # Shuffle rows

    return A

def generate(level=1):
    num_vars = 3 # For gh_GaussianElimination, typically 3 variables are used in examples
    var_names = ['x', 'y', 'z']
    
    problem_choice = random.choice([
        'matrix_to_equation', 
        'equation_to_matrix', 
        'solve_unique', 
        'solve_no_solution', 
        'solve_infinite_solutions', 
        'conceptual_true_false'
    ])
    
    if problem_choice == 'matrix_to_equation':
        coeffs = [[random.randint(-5, 5) for _ in range(num_vars)] for _ in range(num_vars)]
        rhs = [random.randint(-5, 5) for _ in range(num_vars)]
        matrix_list = [c + [r] for c, r in zip(coeffs, rhs)]
        
        question_matrix_latex = _matrix_to_latex(matrix_list)
        question_text = f"寫出下列增廣矩陣所對應的第一個聯立方程式：<br>{question_matrix_latex}"
        
        first_eq_parts = []
        first_row = matrix_list[0]
        for i in range(num_vars):
            coeff = first_row[i]
            var = var_names[i]
            if coeff == 0:
                continue
            
            coeff_str = ""
            if coeff == 1:
                coeff_str = ""
            elif coeff == -1:
                coeff_str = "-"
            elif isinstance(coeff, Fraction) and coeff.denominator == 1:
                coeff_str = str(int(coeff))
            else:
                coeff_str = str(coeff)
            
            if first_eq_parts and coeff > 0:
                first_eq_parts.append("+")
            
            if coeff_str == "-":
                first_eq_parts.append(coeff_str + var)
            elif coeff_str == "":
                first_eq_parts.append(var)
            else:
                first_eq_parts.append(coeff_str + var)
        
        rhs_val = first_row[num_vars]
        first_eq_str = " ".join(first_eq_parts).replace("+ -", "-")
        correct_answer = f"{first_eq_str}={int(rhs_val) if isinstance(rhs_val, Fraction) and rhs_val.denominator == 1 else str(rhs_val)}"
        
        return {
            "question_text": question_text,
            "answer": correct_answer, # Example: "3x - 2y + z = 2"
            "correct_answer": correct_answer
        }

    elif problem_choice == 'equation_to_matrix':
        coeffs = [[random.randint(-5, 5) for _ in range(num_vars)] for _ in range(num_vars)]
        rhs = [random.randint(-5, 5) for _ in range(num_vars)]
        matrix_list = [c + [r] for c, r in zip(coeffs, rhs)]
        
        question_system_latex = _system_to_latex(matrix_list, var_names)
        
        # Pick a random row to ask for
        row_idx_to_ask = random.randint(0, num_vars - 1)
        # Convert 0-indexed to 1-indexed for question text
        question_text = f"寫出下列聯立方程式所對應的增廣矩陣的第 ${row_idx_to_ask+1}$ 列：<br>{question_system_latex}"
        
        row_to_output = matrix_list[row_idx_to_ask]
        correct_answer_list = []
        for val in row_to_output:
            if isinstance(val, Fraction) and val.denominator == 1:
                correct_answer_list.append(str(int(val)))
            else:
                correct_answer_list.append(str(val))
        
        correct_answer = ",".join(correct_answer_list) # e.g., "3,2,1,-1"
        
        return {
            "question_text": question_text,
            "answer": correct_answer,
            "correct_answer": correct_answer
        }

    elif problem_choice in ['solve_unique', 'solve_no_solution', 'solve_infinite_solutions']:
        if problem_choice == 'solve_unique':
            matrix_type = "unique"
        elif problem_choice == 'solve_no_solution':
            matrix_type = "no_solution"
        else: # solve_infinite_solutions
            matrix_type = "infinite_solutions"
            
        aug_matrix = _generate_solvable_matrix(num_vars, num_vars, solution_type=matrix_type)
        aug_matrix_fractions = [[Fraction(val) for val in row] for row in aug_matrix]
        
        solution_type, solution_details, _ = _solve_gaussian_elimination(aug_matrix_fractions, var_names)
        
        question_system_latex = _system_to_latex(aug_matrix_fractions, var_names)
        
        if solution_type == "unique":
            question_text = f"利用高斯消去法解聯立方程式：<br>{question_system_latex}<br>請依序回答 $x, y, z$ 的值，以逗號分隔。例如: $1,2,3$"
            
            answer_parts = []
            for var in var_names:
                val = solution_details[var]
                if isinstance(val, Fraction) and val.denominator == 1:
                    answer_parts.append(str(int(val)))
                else:
                    answer_parts.append(str(val))
            correct_answer = ",".join(answer_parts)
            
        elif solution_type == "no_solution":
            question_text = f"利用高斯消去法解聯立方程式：<br>{question_system_latex}<br>此聯立方程式的解為何？(請回答: 無解)"
            correct_answer = "無解"
            
        elif solution_type == "infinite_solutions":
            question_text = f"利用高斯消去法解聯立方程式：<br>{question_system_latex}<br>此聯立方程式的解為何？(請回答: 無限多組解)"
            correct_answer = "無限多組解"
            
        return {
            "question_text": question_text,
            "answer": correct_answer,
            "correct_answer": correct_answer
        }

    elif problem_choice == 'conceptual_true_false':
        concepts = [
            ("將增廣矩陣的兩列互換，會改變聯立方程式的解。", False),
            ("將增廣矩陣的某一列乘以非零常數，會改變聯立方程式的解。", False),
            ("將增廣矩陣的某一列乘以非零常數後加到另一列，會改變聯立方程式的解。", False),
            (r"增廣矩陣 $\begin{bmatrix} 1 & 2 & | & 3 \\ 0 & 0 & | & 1 \end{bmatrix}$ 所對應的聯立方程式恰有一組解。", False),
            (r"增廣矩陣 $\begin{bmatrix} 1 & 2 & | & 3 \\ 0 & 0 & | & 0 \end{bmatrix}$ 所對應的聯立方程式有無窮多組解。", True),
            (r"任何聯立方程式都可以透過高斯消去法化簡為唯一的增廣矩陣階梯形。", False), # Echelon form is not unique. RREF is unique.
            (r"若一個 $3 \\times 4$ 的增廣矩陣，其簡化列階梯形 (RREF) 有三條非零列，則原聯立方程式恰有一組解。", True), # Rank = number of variables
            (r"若一個 $3 \\times 4$ 的增廣矩陣，其簡化列階梯形 (RREF) 有兩條非零列，則原聯立方程式有無窮多組解。", True), # Rank < number of variables
        ]
        
        question_concept, correct_is_true = random.choice(concepts)
        
        question_text = f"判斷下列敘述是否正確：<br>{question_concept} (請回答：O/X)"
        correct_answer = "O" if correct_is_true else "X"
        
        return {
            "question_text": question_text,
            "answer": correct_answer,
            "correct_answer": correct_answer
        }
        
    # Default fallback, should not be reached
    return {
        "question_text": "Error: Could not generate problem.",
        "answer": "",
        "correct_answer": ""
    }


def check(user_answer, correct_answer):
    """
    Checks if the user's answer is correct.
    Handles numerical answers (comma-separated for multiple variables)
    and string answers ('無解', '無限多組解', 'O/X').
    """
    user_answer_normalized = user_answer.strip().upper()
    correct_answer_normalized = correct_answer.strip().upper()

    is_correct = False
    result_text = ""

    if "," in correct_answer_normalized and "," in user_answer_normalized:
        # Handling for multi-variable numerical solutions (e.g., "1/2,1/3,1/6")
        user_parts = [p.strip() for p in user_answer_normalized.split(',')]
        correct_parts = [p.strip() for p in correct_answer_normalized.split(',')]

        if len(user_parts) == len(correct_parts):
            all_match = True
            for u_val_str, c_val_str in zip(user_parts, correct_parts):
                try:
                    if Fraction(u_val_str) != Fraction(c_val_str):
                        all_match = False
                        break
                except ValueError: # If conversion to Fraction fails
                    all_match = False
                    break
            is_correct = all_match
        else:
            is_correct = False
    else:
        # Handling for '無解', '無限多組解', 'O/X', or single numerical values
        is_correct = (user_answer_normalized == correct_answer_normalized)
        
        # Attempt float comparison as a fallback for single numerical answers
        if not is_correct:
            try:
                if float(user_answer_normalized) == float(correct_answer_normalized):
                    is_correct = True
            except ValueError:
                pass # Not a number, so previous string comparison stands

    if is_correct:
        result_text = "完全正確！"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer}$"

    return {"correct": is_correct, "result": result_text, "next_question": True}