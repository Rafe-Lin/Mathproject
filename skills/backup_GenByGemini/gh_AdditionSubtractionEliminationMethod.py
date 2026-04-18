import random
from fractions import Fraction
import uuid

def format_equation_latex(a, b, c, d, variables=('x', 'y', 'z')):
    """
    Formats a single linear equation (ax + by + cz = d) into a LaTeX string.
    Handles coefficients of 0, 1, and -1 appropriately.
    """
    terms = []

    # Handle x term
    if a == 1:
        terms.append(variables[0])
    elif a == -1:
        terms.append(f"-{variables[0]}")
    elif a != 0:
        terms.append(f"{a}{variables[0]}")

    # Handle y term
    if b == 1:
        terms.append(f"+{variables[1]}")
    elif b == -1:
        terms.append(f"-{variables[1]}")
    elif b > 0:
        terms.append(f"+{b}{variables[1]}")
    elif b < 0:
        terms.append(f"{b}{variables[1]}")
    
    # Handle z term
    if c == 1:
        terms.append(f"+{variables[2]}")
    elif c == -1:
        terms.append(f"-{variables[2]}")
    elif c > 0:
        terms.append(f"+{c}{variables[2]}")
    elif c < 0:
        terms.append(f"{c}{variables[2]}")

    if not terms: # All coefficients are zero
        return f"0 = {d}"
    
    eq_str = "".join(terms)
    # Remove leading '+' if it exists after joining terms (e.g., "+x" becomes "x")
    if eq_str.startswith("+"):
        eq_str = eq_str[1:]
    
    return f"{eq_str} = {d}"

def solve_linear_system_3x3(matrix):
    """
    Solves a 3x3 linear system using Gaussian elimination.
    matrix is a list of lists: [[a1,b1,c1,d1], [a2,b2,c2,d2], [a3,b3,c3,d3]].
    Coefficients and constants are converted to Fractions for precision.
    Returns: (solution_type, solution_values)
        solution_type: 'unique', 'no_solution', 'infinite'
        solution_values: (Fraction x, Fraction y, Fraction z) for unique, None for others.
    """
    mat = [list(map(Fraction, row)) for row in matrix] # Convert all to Fraction for precision

    # Forward elimination (to upper triangular form)
    for k in range(3): # k is the current pivot column/row
        # Find pivot row (first row with non-zero element in current column k)
        pivot_row = k
        while pivot_row < 3 and mat[pivot_row][k] == 0:
            pivot_row += 1

        if pivot_row == 3: # No non-zero pivot in this column below current row
            continue # This column is already eliminated, or system is singular/dependent

        # Swap current row with pivot row
        mat[k], mat[pivot_row] = mat[pivot_row], mat[k]

        # Eliminate elements below the pivot
        for i in range(k + 1, 3):
            if mat[i][k] != 0:
                factor = mat[i][k] / mat[k][k]
                for j in range(k, 4):
                    mat[i][j] -= factor * mat[k][j]

    # Analyze the reduced matrix (after forward elimination)
    # Check rank of coefficient matrix and augmented matrix
    rank_coeffs = 0
    for r in range(3):
        is_zero_coeffs_row = True
        for c_idx in range(3):
            if mat[r][c_idx] != 0:
                is_zero_coeffs_row = False
                break
        if not is_zero_coeffs_row:
            rank_coeffs += 1

    rank_augmented = 0
    for r in range(3):
        is_zero_augmented_row = True
        for c_idx in range(4):
            if mat[r][c_idx] != 0:
                is_zero_augmented_row = False
                break
        if not is_zero_augmented_row:
            rank_augmented += 1

    if rank_coeffs < rank_augmented:
        return 'no_solution', None
    elif rank_coeffs < 3 and rank_coeffs == rank_augmented:
        return 'infinite', None
    else: # rank_coeffs == 3 and rank_coeffs == rank_augmented, unique solution
        x, y, z = Fraction(0), Fraction(0), Fraction(0)
        
        # Back substitution from the last row upwards
        if mat[2][2] != 0:
            z = mat[2][3] / mat[2][2]
        else: # Should not happen if rank is 3
            return 'error', None 

        if mat[1][1] != 0:
            y = (mat[1][3] - mat[1][2] * z) / mat[1][1]
        else:
            return 'error', None

        if mat[0][0] != 0:
            x = (mat[0][3] - mat[0][1] * y - mat[0][2] * z) / mat[0][0]
        else:
            return 'error', None

        return 'unique', (x, y, z)


def generate_unique_solution_problem(level):
    """Generates a system of 3 linear equations with a unique solution."""
    x0 = random.randint(-5, 5)
    y0 = random.randint(-5, 5)
    z0 = random.randint(-5, 5)

    equations_raw = []
    # Generate random coefficients for 3 equations, ensuring a non-zero determinant.
    while True:
        coeffs_matrix = []
        for _ in range(3):
            coeffs = [random.randint(-3, 3) for _ in range(3)]
            # Ensure at least one coefficient is non-zero for each equation
            while all(c == 0 for c in coeffs):
                coeffs = [random.randint(-3, 3) for _ in range(3)]
            coeffs_matrix.append(coeffs)
        
        # Calculate determinant to ensure a unique solution
        a1, b1, c1 = coeffs_matrix[0]
        a2, b2, c2 = coeffs_matrix[1]
        a3, b3, c3 = coeffs_matrix[2]

        det = (a1 * (b2 * c3 - b3 * c2) -
               b1 * (a2 * c3 - a3 * c2) +
               c1 * (a2 * b3 - a3 * b2))
        
        if det != 0: # Determinant must be non-zero for a unique solution
            break
    
    for i in range(3):
        a, b, c = coeffs_matrix[i]
        d = a * x0 + b * y0 + c * z0
        equations_raw.append([a, b, c, d])

    question_text = r"解三元一次聯立方程式" + "\n"
    question_text += r"$\begin{{cases}}"
    question_text += format_equation_latex(*equations_raw[0]) + r" \\ "
    question_text += format_equation_latex(*equations_raw[1]) + r" \\ "
    question_text += format_equation_latex(*equations_raw[2]) + r"\end{{cases}}$" + r"。"

    solution_type, solution_values = solve_linear_system_3x3(equations_raw)

    if solution_type == 'unique':
        x_val, y_val, z_val = solution_values
        # Format solution for display and checking
        correct_answer = (
            f"x={x_val.numerator if x_val.denominator == 1 else x_val}, "
            f"y={y_val.numerator if y_val.denominator == 1 else y_val}, "
            f"z={z_val.numerator if z_val.denominator == 1 else z_val}"
        )
    else: 
        # This case should theoretically not be reached if determinant check is correct
        correct_answer = "Error: Expected unique solution, got " + solution_type

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_no_solution_problem(level):
    """Generates a system of 3 linear equations with no solution."""
    # Strategy: Two equations are parallel planes but distinct.
    # Eq1: a*x + b*y + c*z = d1
    # Eq2: k*a*x + k*b*y + k*c*z = k*d1 + offset (offset != 0, k is a multiplier)
    # Eq3: An independent equation.

    # 1. Generate base coefficients (a, b, c) for the "parallel" part
    while True:
        a = random.randint(-3, 3)
        b = random.randint(-3, 3)
        c = random.randint(-3, 3)
        if not all(val == 0 for val in [a,b,c]): # Ensure at least one non-zero coefficient
            break

    d1 = random.randint(-10, 10)
    k = random.choice([-2, -1, 2, 3]) # Multiplier for the parallel plane

    # Generate offset such that k*d1 + offset is distinct from k*d1
    offset = 0
    while offset == 0:
        offset = random.randint(-5, 5)
    
    d2 = k * d1 + offset

    eq1_coeffs = [a, b, c, d1]
    eq2_coeffs = [k*a, k*b, k*c, d2]

    # 4. Generate a third independent equation.
    while True:
        a3 = random.randint(-3, 3)
        b3 = random.randint(-3, 3)
        c3 = random.randint(-3, 3)
        if all(val == 0 for val in [a3,b3,c3]):
            continue
        
        # Check if (a3,b3,c3) is parallel to (a,b,c) using cross product
        # Cross product (a,b,c) x (a3,b3,c3) should be non-zero for independence
        cp_x = b*c3 - c*b3
        cp_y = c*a3 - a*c3
        cp_z = a*b3 - b*a3
        
        if cp_x != 0 or cp_y != 0 or cp_z != 0: # Not parallel, so linearly independent
            # Pick arbitrary x0,y0,z0 for Eq3 to satisfy. It doesn't affect the 'no solution' property.
            x_rand = random.randint(-2, 2)
            y_rand = random.randint(-2, 2)
            z_rand = random.randint(-2, 2)
            d3 = a3 * x_rand + b3 * y_rand + c3 * z_rand
            eq3_coeffs = [a3, b3, c3, d3]
            break

    equations_raw = [eq1_coeffs, eq2_coeffs, eq3_coeffs]
    random.shuffle(equations_raw) # Shuffle order of equations
    
    equations_formatted = [format_equation_latex(*eq) for eq in equations_raw]

    question_text = r"解三元一次聯立方程式" + "\n"
    question_text += r"$\begin{{cases}}"
    question_text += equations_formatted[0] + r" \\ "
    question_text += equations_formatted[1] + r" \\ "
    question_text += equations_formatted[2] + r"\end{{cases}}$" + r"。"

    solution_type, _ = solve_linear_system_3x3(equations_raw)

    if solution_type == 'no_solution':
        correct_answer = "無解"
    else: 
        correct_answer = "Error: Expected no solution, got " + solution_type

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_infinite_solutions_problem(level):
    """Generates a system of 3 linear equations with infinitely many solutions."""
    # Strategy: Eq3 is a linear combination of Eq1 and Eq2.
    # 1. Generate Eq1: a1x + b1y + c1z = d1
    # 2. Generate Eq2: a2x + b2y + c2z = d2 (linearly independent from Eq1)
    # 3. Eq3 = k1*Eq1 + k2*Eq2 (for some non-zero integer k1, k2)

    # Choose a target solution (x0, y0, z0) to ensure consistency for constants.
    x0 = random.randint(-3, 3)
    y0 = random.randint(-3, 3)
    z0 = random.randint(-3, 3)

    # Generate Eq1 and Eq2 that are linearly independent (non-parallel coefficient vectors)
    while True:
        a1, b1, c1 = [random.randint(-3, 3) for _ in range(3)]
        if all(val == 0 for val in [a1, b1, c1]): continue

        a2, b2, c2 = [random.randint(-3, 3) for _ in range(3)]
        if all(val == 0 for val in [a2, b2, c2]): continue

        # Check linear independence of (a1,b1,c1) and (a2,b2,c2) using cross product
        cp_x = b1*c2 - c1*b2
        cp_y = c1*a2 - a1*c2
        cp_z = a1*b2 - b1*a2
        
        if cp_x != 0 or cp_y != 0 or cp_z != 0: # Not parallel, thus linearly independent
            break

    d1 = a1 * x0 + b1 * y0 + c1 * z0
    d2 = a2 * x0 + b2 * y0 + c2 * z0

    eq1_coeffs = [a1, b1, c1, d1]
    eq2_coeffs = [a2, b2, c2, d2]

    # Generate Eq3 as a linear combination of Eq1 and Eq2
    k1 = random.randint(1, 2) 
    k2 = random.randint(1, 2)

    a3 = k1 * a1 + k2 * a2
    b3 = k1 * b1 + k2 * b2
    c3 = k1 * c1 + k2 * c2
    d3 = k1 * d1 + k2 * d2

    eq3_coeffs = [a3, b3, c3, d3]
    
    equations_raw = [eq1_coeffs, eq2_coeffs, eq3_coeffs]
    random.shuffle(equations_raw) # Shuffle order of equations for more variation

    equations_formatted = [format_equation_latex(*eq) for eq in equations_raw]

    question_text = r"解三元一次聯立方程式" + "\n"
    question_text += r"$\begin{{cases}}"
    question_text += equations_formatted[0] + r" \\ "
    question_text += equations_formatted[1] + r" \\ "
    question_text += equations_formatted[2] + r"\end{{cases}}$" + r"。"

    solution_type, _ = solve_linear_system_3x3(equations_raw)

    if solution_type == 'infinite':
        correct_answer = "無窮多組解"
    else: 
        correct_answer = "Error: Expected infinite solutions, got " + solution_type
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    Generates a problem for solving 3-variable linear equations using the elimination method.
    The problem can have a unique solution, no solution, or infinitely many solutions.
    """
    # Adjust problem type distribution based on level
    problem_choice_weights = {
        'unique_solution': 0.7,
        'no_solution': 0.15,
        'infinite_solutions': 0.15
    }
    
    # For higher levels, slightly adjust the probability distribution if desired
    if level > 1:
        problem_choice_weights['unique_solution'] = 0.6
        problem_choice_weights['no_solution'] = 0.2
        problem_choice_weights['infinite_solutions'] = 0.2

    problem_type = random.choices(
        list(problem_choice_weights.keys()),
        weights=list(problem_choice_weights.values()),
        k=1
    )[0]

    if problem_type == 'unique_solution':
        return generate_unique_solution_problem(level)
    elif problem_type == 'no_solution':
        return generate_no_solution_problem(level)
    else: # 'infinite_solutions'
        return generate_infinite_solutions_problem(level)

def check(user_answer, correct_answer):
    """
    Checks if the user's answer is correct for the generated problem.
    Handles unique solutions, no solutions, and infinitely many solutions.
    """
    user_answer_normalized = user_answer.strip().replace(" ", "").lower()
    correct_answer_normalized = correct_answer.strip().replace(" ", "").lower()

    is_correct = False
    result_text = ""

    if correct_answer_normalized in ["無解", "無窮多組解"]:
        is_correct = (user_answer_normalized == correct_answer_normalized)
        if is_correct:
            result_text = f"完全正確！答案是 {correct_answer}。"
        else:
            result_text = f"答案不正確。正確答案應為：{correct_answer}"
    else: # Unique solution, e.g., "x=1, y=2, z=4"
        user_vals = {}
        try:
            parts = user_answer_normalized.split(',')
            for part in parts:
                if '=' in part:
                    var, val_str = part.split('=')
                    # Convert user input to Fraction to handle decimals/fractions
                    if '/' in val_str:
                        user_vals[var.strip()] = Fraction(val_str)
                    else:
                        user_vals[var.strip()] = Fraction(int(val_str))
                else:
                    # Catch malformed parts like "1" instead of "x=1"
                    raise ValueError("Malformed answer part")
        except (ValueError, IndexError):
            result_text = "請檢查您的答案格式，例如 'x=1, y=2, z=3' 或 'x=1/2, y=3, z=-1'。"
            return {"correct": False, "result": result_text, "next_question": False}

        correct_vals = {}
        try:
            parts = correct_answer_normalized.split(',')
            for part in parts:
                if '=' in part:
                    var, val_str = part.split('=')
                    if '/' in val_str:
                        correct_vals[var.strip()] = Fraction(val_str)
                    else:
                        correct_vals[var.strip()] = Fraction(int(val_str))
                else:
                    raise ValueError("Malformed answer part in correct_answer")
        except (ValueError, IndexError):
            # This should ideally not happen as correct_answer is generated by the script
            result_text = "Internal error: Could not parse correct answer."
            return {"correct": False, "result": result_text, "next_question": False}
        
        # Compare solutions for x, y, and z
        if len(user_vals) == 3 and all(var in user_vals for var in ['x', 'y', 'z']):
            if (user_vals.get('x') == correct_vals.get('x') and
                user_vals.get('y') == correct_vals.get('y') and
                user_vals.get('z') == correct_vals.get('z')):
                is_correct = True
                result_text = f"完全正確！答案是 ${correct_answer}$。"
            else:
                result_text = f"答案不正確。正確答案應為：${correct_answer}$"
        else:
            result_text = f"請提供 $x, y, z$ 三個變數的解。正確答案應為：${correct_answer}$"

    return {"correct": is_correct, "result": result_text, "next_question": True}