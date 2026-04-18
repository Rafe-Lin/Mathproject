import random
from fractions import Fraction
import re

# Helper function to format a matrix into a LaTeX string
def format_matrix_latex(matrix_elements):
    rows = []
    for row in matrix_elements:
        rows.append(" & ".join(map(str, row)))
    return r"\begin{bmatrix}" + r" \\ ".join(rows) + r"\end{bmatrix}"

# Helper function to generate a random matrix elements and its dimensions
def generate_random_matrix_data(min_dim=2, max_dim=3, min_val=-5, max_val=5):
    rows = random.randint(min_dim, max_dim)
    cols = random.randint(min_dim, max_dim)
    elements = [[random.randint(min_val, max_val) for _ in range(cols)] for _ in range(rows)]
    return elements, rows, cols

def generate(level=1):
    """
    生成「矩陣的意義與相等」相關題目。
    包含：
    1. 矩陣基本定義與性質 (階數、矩陣元、方陣判斷)
    2. 依規則建構矩陣
    3. 矩陣相等 (簡單變數)
    4. 矩陣相等 (含運算式)
    5. 矩陣相等 (觀念判斷)
    """
    problem_type = random.choice([
        'matrix_properties',
        'construct_matrix',
        'matrix_equality_simple',
        'matrix_equality_expression',
        'matrix_equality_conceptual'
    ])

    if problem_type == 'matrix_properties':
        return generate_matrix_properties_problem()
    elif problem_type == 'construct_matrix':
        return generate_construct_matrix_problem()
    elif problem_type == 'matrix_equality_simple':
        return generate_matrix_equality_simple_problem()
    elif problem_type == 'matrix_equality_expression':
        return generate_matrix_equality_expression_problem()
    else: # matrix_equality_conceptual
        return generate_matrix_equality_conceptual_problem()

def generate_matrix_properties_problem():
    elements, rows, cols = generate_random_matrix_data(min_dim=2, max_dim=3)
    matrix_latex = format_matrix_latex(elements)
    
    question_options = [
        "order",        # 階數
        "num_rows_cols", # 列數與行數
        "element",      # 特定矩陣元
        "square_matrix" # 方陣
    ]
    
    question_type = random.choice(question_options)
    
    question_text = ""
    correct_answer = ""
    
    if question_type == "order":
        question_text = f"關於矩陣 $A = {matrix_latex}$，其階數為何？(請以 'rows x cols' 格式作答)"
        correct_answer = f"{rows}x{cols}"
    elif question_type == "num_rows_cols":
        question_text = f"關於矩陣 $A = {matrix_latex}$，選出所有正確的選項。<br>"
        options = []
        
        # Correct options related to rows/cols and order
        options.append(f"A有{rows}列{cols}行")
        options.append(f"A是 {rows}x{cols} 階的矩陣")

        # Incorrect options
        options.append(f"A有{cols}列{rows}行") # Swapped rows/cols
        options.append(f"A是 {cols}x{rows} 階的矩陣") # Swapped order
        
        # Square matrix check (correct or incorrect)
        if rows == cols:
            options.append("A是一個方陣")
        else:
            options.append("A是一個方陣") # This option will be incorrect

        random.shuffle(options)
        
        indexed_options = []
        for i, opt in enumerate(options):
            indexed_options.append(f"({i+1}) {opt}")
        
        question_text += "<br>".join(indexed_options) + "<br>請填寫正確選項的編號，以逗號分隔，例如 '1,3'。"
        
        # Determine correct answers based on shuffled options
        final_correct_answers = []
        for i, opt in enumerate(options):
            if f"{rows}列{cols}行" in opt or f"{rows}x{cols} 階的矩陣" in opt:
                final_correct_answers.append(str(i+1))
            elif "A是一個方陣" in opt and rows == cols:
                final_correct_answers.append(str(i+1))
                 
        correct_answer = ",".join(sorted(list(set(final_correct_answers))))
        if not correct_answer: # If no options are correct (shouldn't happen with the current setup, but for safety)
             correct_answer = "None"
        
    elif question_type == "element":
        r = random.randint(1, rows)
        c = random.randint(1, cols)
        element_val = elements[r-1][c-1]
        question_text = f"關於矩陣 $A = {matrix_latex}$，請問第 $({r},{c})$ 元為何？"
        correct_answer = str(element_val)
    elif question_type == "square_matrix":
        question_text = f"矩陣 $A = {matrix_latex}$ 是一個方陣嗎？(請回答 '是' 或 '否')"
        correct_answer = "是" if rows == cols else "否"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_construct_matrix_problem():
    rows = random.randint(2, 3)
    cols = random.randint(2, 3)
    
    rule_types = ['linear_i_j', 'mult_i_j', 'i_minus_j', 'i_plus_j']
    rule_type = random.choice(rule_types)
    
    a_ij_func = None
    rule_latex = ""

    if rule_type == 'linear_i_j':
        coeff_i = random.randint(-2, 3) # Can be 0
        coeff_j = random.randint(-2, 3) # Can be 0
        const = random.randint(-5, 5)
        
        # Ensure the rule is not trivially 0 everywhere or just a constant
        if coeff_i == 0 and coeff_j == 0 and const == 0:
            coeff_i = 1 # Fallback to a simple rule
        if coeff_i == 0 and coeff_j == 0 and const != 0: # a_ij = C
            pass # This is a valid rule
        
        rule_parts = []
        if coeff_i != 0:
            if coeff_i == 1: rule_parts.append("i")
            elif coeff_i == -1: rule_parts.append("-i")
            else: rule_parts.append(f"{coeff_i}i")
        
        if coeff_j != 0:
            if coeff_j == 1: rule_parts.append(f"+j" if rule_parts else "j")
            elif coeff_j == -1: rule_parts.append(f"-j")
            else: rule_parts.append(f"{'+' if coeff_j > 0 and rule_parts else ''}{coeff_j}j")
        
        if const != 0:
            rule_parts.append(f"{'+' if const > 0 and rule_parts else ''}{const}")
        
        rule_latex = "".join(rule_parts)
        if not rule_latex: # Case like all coeffs are 0, make it a simple rule
            rule_latex = str(const) if const != 0 else "0"
            a_ij_func = lambda i, j: const
        else:
            a_ij_func = lambda i, j: coeff_i * i + coeff_j * j + const
            
    elif rule_type == 'mult_i_j':
        rule_latex = "i \\times j"
        a_ij_func = lambda i, j: i * j
    elif rule_type == 'i_minus_j':
        rule_latex = "i - j"
        a_ij_func = lambda i, j: i - j
    elif rule_type == 'i_plus_j':
        rule_latex = "i + j"
        a_ij_func = lambda i, j: i + j
    
    # Final fallback if a_ij_func is still None (should not happen with current logic)
    if a_ij_func is None:
         a_ij_func = lambda i, j: i + j # Fallback
         rule_latex = "i+j"

    matrix_elements = []
    for r_idx in range(1, rows + 1):
        row = []
        for c_idx in range(1, cols + 1):
            row.append(a_ij_func(r_idx, c_idx))
        matrix_elements.append(row)
    
    correct_matrix_latex = format_matrix_latex(matrix_elements)
    
    question_text = f"已知矩陣 $A = [a_{{ij}}]_{{{rows} \\times {cols}}}$，且第 $ij$ 元 $a_{{ij}} = {rule_latex}$，求 $A$。"
    correct_answer = correct_matrix_latex
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_matrix_equality_simple_problem():
    rows = random.randint(2, 3)
    cols = random.randint(2, 3)
    
    vars_pool = ['a', 'b', 'c', 'd', 'x', 'y', 'z', 'p', 'q']
    num_vars_to_find = random.randint(2, min(rows * cols, 4)) # Find 2 to 4 variables
    vars_to_find = random.sample(vars_pool, num_vars_to_find)
    
    matrix_a_elements = []
    matrix_b_elements = []
    
    solution_map = {}
    var_idx = 0
    
    all_elements_processed = [] # To keep track of positions
    for r in range(rows):
        for c in range(cols):
            all_elements_processed.append((r, c))
    
    random.shuffle(all_elements_processed) # Randomize which positions get variables
    
    for r, c in all_elements_processed:
        if var_idx < len(vars_to_find): # Place a variable
            var_name = vars_to_find[var_idx]
            actual_val = random.randint(-10, 10)
            solution_map[var_name] = actual_val
            
            # Randomly put variable in A or B
            if random.random() < 0.5:
                matrix_a_elements.append((r, c, var_name))
                matrix_b_elements.append((r, c, actual_val))
            else:
                matrix_a_elements.append((r, c, actual_val))
                matrix_b_elements.append((r, c, var_name))
            var_idx += 1
        else: # Place a constant
            val = random.randint(-10, 10)
            matrix_a_elements.append((r, c, val))
            matrix_b_elements.append((r, c, val))
    
    # Convert lists of (r,c,val) to 2D lists
    final_a_elements = [[None for _ in range(cols)] for _ in range(rows)]
    final_b_elements = [[None for _ in range(cols)] for _ in range(rows)]
    for r, c, val in matrix_a_elements:
        final_a_elements[r][c] = val
    for r, c, val in matrix_b_elements:
        final_b_elements[r][c] = val

    matrix_a_latex = format_matrix_latex(final_a_elements)
    matrix_b_latex = format_matrix_latex(final_b_elements)
    
    # Ensure there's at least one variable to solve for
    if not solution_map:
        return generate_matrix_equality_simple_problem() # Regenerate if no variables were placed
        
    sorted_vars = sorted(solution_map.keys())
    
    question_text = f"已知 ${matrix_a_latex} = {matrix_b_latex}$，求 ${', '.join(sorted_vars)}$ 的值。"
    
    # Format correct answer as "var1=val1, var2=val2"
    correct_answer = ", ".join([f"{var}={solution_map[var]}" for var in sorted_vars])
    
    return {
        "question_text": question_text,
        "answer": correct_answer, # Store the structured answer for comparison
        "correct_answer": correct_answer
    }

def generate_matrix_equality_expression_problem():
    rows, cols = 2, 2 # Limit to 2x2 for simpler systems of equations

    var1, var2 = random.sample(['x', 'y', 'a', 'b'], 2)
    sol1 = random.randint(-5, 5)
    sol2 = random.randint(-5, 5)

    solution_map = {var1: sol1, var2: sol2}

    matrix_a_elements_temp = [[None, None], [None, None]]
    matrix_b_elements_temp = [[None, None], [None, None]]
    
    # Define two expressions for a 2x2 system (at least two elements will be expressions)
    # Using 'sum_diff' or 'simple_linear' patterns to guarantee a solvable system

    pattern_choice = random.choice(['sum_diff', 'simple_linear'])
    
    # Determine the positions for the two expressions that form the system
    pos1 = (random.randint(0,1), random.randint(0,1))
    pos2 = (random.randint(0,1), random.randint(0,1))
    while pos1 == pos2:
        pos2 = (random.randint(0,1), random.randint(0,1))

    if pattern_choice == 'sum_diff':
        # E.g., var1+var2 and var1-var2
        
        # Expression 1: var1 + var2
        matrix_a_elements_temp[pos1[0]][pos1[1]] = f"{var1}+{var2}"
        matrix_b_elements_temp[pos1[0]][pos1[1]] = sol1 + sol2
        
        # Expression 2: var1 - var2
        matrix_a_elements_temp[pos2[0]][pos2[1]] = f"{var1}-{var2}"
        matrix_b_elements_temp[pos2[0]][pos2[1]] = sol1 - sol2
        
    elif pattern_choice == 'simple_linear':
        # E.g., var1 and a*var1 + b*var2
        
        # Expression 1: A simple variable (either var1 or var2)
        if random.random() < 0.5: # Use var1 directly
            matrix_a_elements_temp[pos1[0]][pos1[1]] = var1
            matrix_b_elements_temp[pos1[0]][pos1[1]] = sol1
            eq1_coeffs = (1, 0) # (coeff_var1, coeff_var2)
        else: # Use var2 directly
            matrix_a_elements_temp[pos1[0]][pos1[1]] = var2
            matrix_b_elements_temp[pos1[0]][pos1[1]] = sol2
            eq1_coeffs = (0, 1)

        # Expression 2: A linear combination that ensures unique solution with Expr1
        coeff2_1 = random.choice([1, -1, 2])
        coeff2_2 = random.choice([1, -1, 2])

        # Ensure determinant is not zero: a1*b2 - a2*b1 != 0
        if eq1_coeffs == (1, 0): # First equation was `var1` (x=sol1)
            while coeff2_2 == 0: # Ensure var2 is present in the second equation (so det = coeff2_2 != 0)
                coeff2_2 = random.choice([1, -1, 2])
        elif eq1_coeffs == (0, 1): # First equation was `var2` (y=sol2)
            while coeff2_1 == 0: # Ensure var1 is present in the second equation (so det = -coeff2_1 != 0)
                coeff2_1 = random.choice([1, -1, 2])

        # Construct expression string for the second equation
        expr_str_parts = []
        if coeff2_1 != 0:
            if coeff2_1 == 1: expr_str_parts.append(var1)
            elif coeff2_1 == -1: expr_str_parts.append(f"-{var1}")
            else: expr_str_parts.append(f"{coeff2_1}{var1}")
        if coeff2_2 != 0:
            if coeff2_2 == 1: expr_str_parts.append(f"+{var2}" if expr_str_parts else var2)
            elif coeff2_2 == -1: expr_str_parts.append(f"-{var2}")
            else: expr_str_parts.append(f"{'+' if coeff2_2 > 0 and expr_str_parts else ''}{coeff2_2}{var2}")
        
        matrix_a_elements_temp[pos2[0]][pos2[1]] = "".join(expr_str_parts)
        matrix_b_elements_temp[pos2[0]][pos2[1]] = coeff2_1 * sol1 + coeff2_2 * sol2

    # Fill remaining elements with constants
    for r in range(rows):
        for c in range(cols):
            if matrix_a_elements_temp[r][c] is None:
                val = random.randint(-10, 10)
                matrix_a_elements_temp[r][c] = val
                matrix_b_elements_temp[r][c] = val
    
    matrix_a_latex = format_matrix_latex(matrix_a_elements_temp)
    matrix_b_latex = format_matrix_latex(matrix_b_elements_temp)
    
    question_text = f"已知 ${matrix_a_latex} = {matrix_b_latex}$，求 ${var1}, {var2}$ 的值。"
    
    # Format correct answer as "var1=val1, var2=val2"
    correct_answer = f"{var1}={sol1}, {var2}={sol2}" 
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def generate_matrix_equality_conceptual_problem():
    # Generate two matrices with different orders but potentially similar elements,
    # asking if they are equal. The answer is always '否'.
    
    # Option 1: Row vector vs Column vector
    if random.random() < 0.5:
        elements = [random.randint(-5, 5) for _ in range(random.randint(2,3))] # 1xN vs Nx1
        matrix_a_latex = format_matrix_latex([elements]) # 1xN matrix
        matrix_b_latex = format_matrix_latex([[e] for e in elements]) # Nx1 matrix
        question_text = f"判斷下列等式是否成立：${matrix_a_latex} = {matrix_b_latex}$。(請回答 '是' 或 '否')"
        correct_answer = "否"
    # Option 2: Two matrices with generally different dimensions
    else:
        rows1 = random.randint(1, 2)
        cols1 = random.randint(2, 3)
        rows2 = random.randint(1, 2)
        cols2 = random.randint(2, 3)
        
        # Ensure dimensions are different
        while rows1 == rows2 and cols1 == cols2:
            rows2 = random.randint(1, 2)
            cols2 = random.randint(2, 3)
            
        elements1 = [[random.randint(-5, 5) for _ in range(cols1)] for _ in range(rows1)]
        elements2 = [[random.randint(-5, 5) for _ in range(cols2)] for _ in range(rows2)]
        
        # To make it tricky, fill common part with same values if possible
        min_common_rows = min(rows1, rows2)
        min_common_cols = min(cols1, cols2)
        
        for r in range(min_common_rows):
            for c in range(min_common_cols):
                val = random.randint(-5, 5)
                elements1[r][c] = val
                elements2[r][c] = val
                
        matrix_a_latex = format_matrix_latex(elements1)
        matrix_b_latex = format_matrix_latex(elements2)
        
        question_text = f"判斷下列等式是否成立：${matrix_a_latex} = {matrix_b_latex}$。(請回答 '是' 或 '否')"
        correct_answer = "否"
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def check(user_answer, correct_answer):
    user_answer = user_answer.strip().replace(' ', '').lower()
    correct_answer = correct_answer.strip().replace(' ', '').lower()

    is_correct = False
    feedback = ""

    # Handle '是' / '否' answers
    if user_answer in ["是", "否"]:
        if user_answer == correct_answer:
            is_correct = True
            feedback = "完全正確！"
        else:
            feedback = f"答案不正確。正確答案應為：'{correct_answer}'"
    # Handle 'rows x cols' format (e.g., "2x3")
    elif re.fullmatch(r'\d+x\d+', user_answer):
        if user_answer == correct_answer:
            is_correct = True
            feedback = "完全正確！"
        else:
            feedback = f"答案不正確。正確答案應為：'{correct_answer}'"
    # Handle multiple choice answers (e.g., "1,3" or "none")
    elif re.fullmatch(r'(\d+(,\d+)*|none)', user_answer):
        user_parts = set(user_answer.split(',')) if user_answer != "none" else set()
        correct_parts = set(correct_answer.split(',')) if correct_answer != "none" else set()
        
        if user_parts == correct_parts:
            is_correct = True
            feedback = "完全正確！"
        else:
            feedback = f"答案不正確。正確答案應為：{correct_answer}"
    # Handle multiple variable answers (e.g., "x=3,y=2" or "a=3,b=7,c=-4,d=2")
    elif '=' in correct_answer: # Implies the answer is in "var=value" format
        user_vars = {}
        correct_vars = {}
        
        try:
            # Parse user input
            for item in user_answer.split(','):
                parts = item.split('=')
                if len(parts) == 2:
                    user_vars[parts[0]] = float(parts[1])
            
            # Parse correct answer
            for item in correct_answer.split(','):
                parts = item.split('=')
                if len(parts) == 2:
                    correct_vars[parts[0]] = float(parts[1])
            
            # Compare maps (order-independent comparison)
            if user_vars == correct_vars:
                is_correct = True
                feedback = "完全正確！"
            else:
                feedback = f"答案不正確。正確答案應為：${correct_answer}$"
        except ValueError:
            feedback = f"答案格式不正確。請確保輸入格式為 'var1=value1, var2=value2'。正確答案應為：${correct_answer}$"
    # Handle single numerical answers (must be last to avoid conflicts with 'x' in 2x3 etc.)
    else: # Default to numerical or direct string comparison for other cases
        try:
            # Try float comparison first
            if float(user_answer) == float(correct_answer):
                is_correct = True
                feedback = "完全正確！"
            else:
                feedback = f"答案不正確。正確答案應為：${correct_answer}$"
        except ValueError:
            # If not a float, do direct string comparison
            if user_answer == correct_answer:
                is_correct = True
                feedback = "完全正確！"
            else:
                feedback = f"答案不正確。正確答案應為：${correct_answer}$"

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    
    return {"correct": is_correct, "result": result_text, "next_question": True}