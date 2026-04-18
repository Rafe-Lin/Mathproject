import random
from fractions import Fraction
import math
import re

# Helper to format coefficient strings for the equation
def format_coeff(coeff, var, first=False):
    if coeff == 0:
        return ""
    
    # If coeff is a string (e.g., 'k', 'k+1'), treat it as a k-expression
    if isinstance(coeff, str):
        sign = "+" if not first else ""
        return f"{sign}{coeff}{var}"

    abs_coeff = abs(coeff)
    sign = "+" if coeff > 0 else "-"
    if first:
        sign = "-" if coeff < 0 else ""

    if abs_coeff == 1 and var != "": 
        return f"{sign}{var}"
    else:
        return f"{sign}{abs_coeff}{var}"

# Helper to format a full equation line
def format_equation_line(a, b, c):
    parts = []
    if a != 0 or isinstance(a, str): # Include if a is 0 but is a k-expression like 'k'
        parts.append(format_coeff(a, "x", first=True))
    if b != 0 or isinstance(b, str):
        parts.append(format_coeff(b, "y", first=len(parts)==0))
    
    if not parts:
        left_side = "0"
    else:
        left_side = "".join(parts)
        if left_side.startswith("+"):
            left_side = left_side[1:]
    
    return f"{left_side} = {c}"

# Helper to format a fraction string for LaTeX output
def simplify_fraction_str(numerator, denominator):
    if denominator == 0:
        return r"\text{undefined}"
    
    if numerator == 0:
        return "0"

    common = math.gcd(abs(numerator), abs(denominator))
    num_simplified = numerator // common
    den_simplified = denominator // common
    
    if den_simplified < 0:
        num_simplified *= -1
        den_simplified *= -1

    if den_simplified == 1:
        return str(num_simplified)
    else:
        return r"\\frac{{{}}}{{{}}}".format(num_simplified, den_simplified)

# Helper to format terms like 'k', 'k+val', 'k-val'
def format_k_term(k_val_offset):
    if k_val_offset == 0:
        return 'k'
    elif k_val_offset > 0:
        return f"k+{k_val_offset}"
    else: # k_val_offset < 0
        return f"k{k_val_offset}"

# --- Problem Type Specific Generators ---

def generate_parallel_distinct_problem():
    # Goal: Delta = 0, and (Delta_x != 0 or Delta_y != 0) (No solution, parallel and distinct lines)
    
    a1_base = random.randint(1, 5) * random.choice([-1, 1])
    b1_base = random.randint(1, 5) * random.choice([-1, 1])
    c1_base = random.randint(-5, 5)
    
    m = random.randint(2, 4) * random.choice([-1, 1]) # Multiplier for a2, b2
    
    a2_base_val = a1_base * m
    b2_base_val = b1_base * m
    
    c2_base_val = c1_base * m + random.randint(1, 3) * random.choice([-1, 1]) # Ensure c2_base != c1*m
    while c2_base_val == 0 and c1_base == 0: # Avoid 0=0 and 0=non-zero, which leads to parallel 0=0 and 0=C
        c2_base_val = c1_base * m + random.randint(1, 3) * random.choice([-1, 1])
    
    # Randomly inject 'k' into one of a1, b1, a2, b2
    k_insert_target = random.choice(['a1', 'b1', 'a2', 'b2'])
    
    k_coeffs = {'a1': a1_base, 'b1': b1_base, 'c1': c1_base, 'a2': a2_base_val, 'b2': b2_base_val, 'c2': c2_base_val}
    k_val = None

    # Calculate the k value that makes Delta = 0
    # Add retry logic for division by zero to ensure robustness
    if k_insert_target == 'a1':
        if b2_base_val == 0: return generate_parallel_distinct_problem()
        k_val = Fraction(a2_base_val * b1_base, b2_base_val)
        k_coeffs['a1'] = 'k'
    elif k_insert_target == 'b1':
        if a2_base_val == 0: return generate_parallel_distinct_problem()
        k_val = Fraction(a1_base * b2_base_val, a2_base_val)
        k_coeffs['b1'] = 'k'
    elif k_insert_target == 'a2':
        if b1_base == 0: return generate_parallel_distinct_problem()
        k_val = Fraction(a1_base * b2_base_val, b1_base)
        k_coeffs['a2'] = 'k'
    elif k_insert_target == 'b2':
        if a1_base == 0: return generate_parallel_distinct_problem()
        k_val = Fraction(a2_base_val * b1_base, a1_base)
        k_coeffs['b2'] = 'k'
            
    if k_val is None: return generate_parallel_distinct_problem() # Should not be reached with retry logic

    q_a1 = k_coeffs['a1']
    q_b1 = k_coeffs['b1']
    q_c1 = k_coeffs['c1']
    q_a2 = k_coeffs['a2']
    q_b2 = k_coeffs['b2']
    q_c2 = k_coeffs['c2']

    question_text = (
        f"已知聯立方程式 $<br>"
        f"$\\begin{{cases}} "
        f"{format_equation_line(q_a1, q_b1, q_c1)} \\\\ "
        f"{format_equation_line(q_a2, q_b2, q_c2)} "
        f"\\end{{cases}}$<br>"
        f"無解，求 $k$ 的值。"
    )
    correct_answer = str(k_val) if k_val.denominator == 1 else simplify_fraction_str(k_val.numerator, k_val.denominator)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_inf_solutions_problem():
    # Goal: Delta = 0, Delta_x = 0, Delta_y = 0 (Infinitely many solutions, coincident lines)
    
    a1_base = random.randint(1, 5) * random.choice([-1, 1])
    b1_base = random.randint(1, 5) * random.choice([-1, 1])
    c1_base = random.randint(-5, 5)
    
    m = random.randint(2, 4) * random.choice([-1, 1]) # Multiplier
    
    a2_base_val = a1_base * m
    b2_base_val = b1_base * m
    c2_base_val = c1_base * m
    
    k_insert_target = random.choice(['a1', 'b1', 'a2', 'b2', 'c2'])

    k_coeffs = {'a1': a1_base, 'b1': b1_base, 'c1': c1_base, 'a2': a2_base_val, 'b2': b2_base_val, 'c2': c2_base_val}
    k_val = None

    if k_insert_target == 'a1':
        if b2_base_val == 0: return generate_inf_solutions_problem()
        k_val = Fraction(a2_base_val * b1_base, b2_base_val)
        k_coeffs['a1'] = 'k'
    elif k_insert_target == 'b1':
        if a2_base_val == 0: return generate_inf_solutions_problem()
        k_val = Fraction(a1_base * b2_base_val, a2_base_val)
        k_coeffs['b1'] = 'k'
    elif k_insert_target == 'a2':
        if b1_base == 0: return generate_inf_solutions_problem()
        k_val = Fraction(a1_base * b2_base_val, b1_base)
        k_coeffs['a2'] = 'k'
    elif k_insert_target == 'b2':
        if a1_base == 0: return generate_inf_solutions_problem()
        k_val = Fraction(a2_base_val * b1_base, a1_base)
        k_coeffs['b2'] = 'k'
    elif k_insert_target == 'c2':
        # For coincident lines, Delta=0 is already satisfied by construction.
        # We need Delta_x = c1*b2_base_val - k*b1_base = 0 AND Delta_y = a1_base*k - a2_base_val*c1_base = 0
        # If b1_base is 0, use a1_base. Both cannot be 0 for a meaningful line.
        if b1_base == 0 and a1_base == 0: return generate_inf_solutions_problem()
        if b1_base != 0:
            k_val = Fraction(c1_base * b2_base_val, b1_base)
        elif a1_base != 0:
            k_val = Fraction(a2_base_val * c1_base, a1_base)
        else: return generate_inf_solutions_problem() # Should not happen
        k_coeffs['c2'] = 'k'
    
    if k_val is None: return generate_inf_solutions_problem()

    q_a1 = k_coeffs['a1']
    q_b1 = k_coeffs['b1']
    q_c1 = k_coeffs['c1']
    q_a2 = k_coeffs['a2']
    q_b2 = k_coeffs['b2']
    q_c2 = k_coeffs['c2']

    question_text = (
        f"已知聯立方程式 $<br>"
        f"$\\begin{{cases}} "
        f"{format_equation_line(q_a1, q_b1, q_c1)} \\\\ "
        f"{format_equation_line(q_a2, q_b2, q_c2)} "
        f"\\end{{cases}}$<br>"
        f"有無窮多組解，求 $k$ 的值。"
    )
    correct_answer = str(k_val) if k_val.denominator == 1 else simplify_fraction_str(k_val.numerator, k_val.denominator)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_parallel_lines_problem():
    # This problem type, as per the example, implies finding k where lines are parallel.
    # The example distinguishes between parallel (distinct) and coincident.
    # We will generate a system where Delta=0 has two roots (r_common, r_other),
    # and one root leads to infinitely many solutions, the other to no solution (parallel distinct).
    # Then we ask for the k value for parallel lines (meaning parallel distinct).

    # Choose `r_common` and `r_other` (roots of Delta=0)
    r_common = random.randint(-3, 3)
    if r_common == 0: r_common = 1 # Avoid k-0 = k for common factor
    r_other = random.randint(-3, 3)
    while r_other == r_common:
        r_other = random.randint(-3, 3)

    # Let $a_1 = k+P$, $b_1 = B_1$, $a_2 = A_2$, $b_2 = k+Q$
    # We want $\\Delta = (k-r_{common})(k-r_{other}) = k^2 - (r_{common}+r_{other})k + r_{common}r_{other}$
    # And $\\Delta = (k+P)(k+Q) - A_2 B_1 = k^2 + (P+Q)k + PQ - A_2 B_1$
    
    # So, $P+Q = -(r_{common}+r_{other})$
    # And $PQ - A_2 B_1 = r_{common}r_{other}$
    
    # Generate P and Q
    P = random.randint(-3, 3)
    Q = -(r_common + r_other) - P
    
    # Calculate $A_2 B_1$
    A2_B1 = P*Q - (r_common * r_other)
    
    # Find factors for $A_2, B_1$ such that $A_2 B_1 = A2_B1$
    factors = []
    for i in range(1, int(abs(A2_B1)**0.5) + 1):
        if A2_B1 % i == 0:
            factors.append(i)
            factors.append(A2_B1 // i)
    factors = [f * s for f in set(factors) for s in [-1, 1]]
    factors = [f for f in factors if abs(f) <= 5 and f != 0] # Keep coefficients small and non-zero

    if not factors: return generate_parallel_lines_problem() # Retry if no small factors
    
    A2 = random.choice(factors)
    B1 = A2_B1 // A2

    # Now define C1, C2 such that Delta_x and Delta_y have (k-r_common) as a factor.
    # This ensures r_common leads to infinite solutions.
    # Let $C_1, C_2$ be constants from:
    # $C_x (Q+r_{common}) - B_1 C_y = 0$
    # $-A_2 C_x + (P+r_{common}) C_y = 0$
    # Choose a scale, then $C_x = (P+r_{common}) \\cdot \text{scale}$ and $C_y = A_2 \\cdot \text{scale}$
    
    scale = random.randint(1, 3) * random.choice([-1, 1])
    
    C1_val = (P + r_common) * scale
    C2_val = A2 * scale

    # Check if `r_other` leads to parallel distinct lines.
    # This means $\\Delta_x(r_{other}) \ne 0$ or $\\Delta_y(r_{other}) \ne 0$.
    # Delta_x(k) = C1_val * (k+Q) - B1 * C2_val
    # Delta_y(k) = (k+P) * C2_val - C1_val * A2
    
    det_x_at_r_other = C1_val * (r_other + Q) - B1 * C2_val
    det_y_at_r_other = (r_other + P) * C2_val - C1_val * A2

    if det_x_at_r_other == 0 and det_y_at_r_other == 0:
        return generate_parallel_lines_problem() # Both roots give inf solutions, retry.
    
    q_a1_str = format_k_term(P)
    q_b1_str = str(B1)
    q_c1_str = str(C1_val)
    q_a2_str = str(A2)
    q_b2_str = format_k_term(Q)
    q_c2_str = str(C2_val)

    question_text = (
        f"已知聯立方程式 $<br>"
        f"$\\begin{{cases}} "
        f"{format_equation_line(q_a1_str, q_b1_str, q_c1_str)} \\\\ "
        f"{format_equation_line(q_a2_str, q_b2_str, q_c2_str)} "
        f"\\end{{cases}}$<br>"
        f"兩直線平行，求 $k$ 的值。"
    )
    correct_answer = str(r_other)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_unique_solution_explicit_problem():
    # Goal: Delta != 0, and express x,y in terms of k.
    # We generate a system where Delta = (k-r_common)(k-r_other),
    # Delta_x = C_x * (k-r_common), Delta_y = C_y * (k-r_common).
    # Then x = C_x / (k-r_other), y = C_y / (k-r_other).
    
    # Choose `r_common` and `r_other` (roots of Delta=0)
    r_common = random.randint(-3, 3)
    if r_common == 0: r_common = 1 # Avoid k-0 = k
    r_other = random.randint(-3, 3)
    while r_other == r_common:
        r_other = random.randint(-3, 3)

    # Use the same construction for P, Q, A2, B1 as `generate_parallel_lines_problem`
    P = random.randint(-3, 3)
    Q = -(r_common + r_other) - P
    
    A2_B1 = P*Q - (r_common * r_other)
    
    factors = []
    for i in range(1, int(abs(A2_B1)**0.5) + 1):
        if A2_B1 % i == 0:
            factors.append(i)
            factors.append(A2_B1 // i)
    factors = [f * s for f in set(factors) for s in [-1, 1]]
    factors = [f for f in factors if abs(f) <= 5 and f != 0]

    if not factors: return generate_unique_solution_explicit_problem()
    
    A2 = random.choice(factors)
    B1 = A2_B1 // A2

    # And for C1, C2 based on `r_common` (for simplification)
    scale = random.randint(1, 3) * random.choice([-1, 1])
    
    C1_val = (P + r_common) * scale
    C2_val = A2 * scale

    q_a1_str = format_k_term(P)
    q_b1_str = str(B1)
    q_c1_str = str(C1_val)
    q_a2_str = str(A2)
    q_b2_str = format_k_term(Q)
    q_c2_str = str(C2_val)

    question_text = (
        f"已知聯立方程式 $<br>"
        f"$\\begin{{cases}} "
        f"{format_equation_line(q_a1_str, q_b1_str, q_c1_str)} \\\\ "
        f"{format_equation_line(q_a2_str, q_b2_str, q_c2_str)} "
        f"\\end{{cases}}$<br>"
        f"恰有一組解，求 $k$ 的範圍及聯立方程式的解（以 $k$ 表示）。"
    )
    
    k_range_exceptions = sorted([r_common, r_other])
    
    # Solutions x and y in terms of k
    # x = C_x / (k-r_other), y = C_y / (k-r_other)
    # Here C_x is C1_val (which is (P+r_common)*scale)
    # C_y is C2_val (which is A2*scale)
    
    x_sol_num = C1_val
    y_sol_num = C2_val
    
    k_denominator_offset = -r_other
    sol_den_str = format_k_term(k_denominator_offset)

    if x_sol_num == 0:
        x_sol_str = "0"
    else:
        x_sol_str = r"\\frac{{{}}}{{{}}}".format(str(x_sol_num), sol_den_str)
    
    if y_sol_num == 0:
        y_sol_str = "0"
    else:
        y_sol_str = r"\\frac{{{}}}{{{}}}".format(str(y_sol_num), sol_den_str)

    # Full LaTeX answer string
    full_latex_answer = (
        f"k的範圍為 $k \\ne {k_range_exceptions[0]}$ 且 $k \\ne {k_range_exceptions[1]}$，"
        f"且其解為 $x={x_sol_str}, y={y_sol_str}$。"
    )
    
    return {
        "question_text": question_text,
        "answer": full_latex_answer,
        "correct_answer": full_latex_answer
    }

def generate(level=1):
    problem_scenario = random.choice([
        "parallel_lines", "inf_solutions", "unique_solution_explicit", "no_solution"
    ])

    if problem_scenario == "parallel_lines":
        return generate_parallel_lines_problem()
    elif problem_scenario == "inf_solutions":
        return generate_inf_solutions_problem()
    elif problem_scenario == "unique_solution_explicit":
        return generate_unique_solution_explicit_problem()
    elif problem_scenario == "no_solution":
        return generate_parallel_distinct_problem() # This is the "no solution" case

def check(user_answer, correct_answer):
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()

    is_correct = False
    result_text = ""

    # Check for unique_solution_explicit problem type (answer contains full LaTeX)
    if "k的範圍為" in correct_answer:
        # Extract expected k exceptions and x, y solutions from the correct_answer string
        k_range_part = correct_answer.split("k的範圍為")[1].split("，且其解為")[0]
        sol_part = correct_answer.split("，且其解為")[1]

        k_exception_values_str = re.findall(r'k \\ne (-?\d+)', k_range_part)
        k_exception_values = sorted([int(v) for v in k_exception_values_str])

        x_sol_match = re.search(r'x=(.+?),', sol_part)
        y_sol_match = re.search(r'y=(.+?)\.', sol_part)
        
        expected_x_sol_latex = x_sol_match.group(1).strip() if x_sol_match else ""
        expected_y_sol_latex = y_sol_match.group(1).strip() if y_sol_match else ""

        # Parse user's answer (expecting format: "k!=val1,val2; x=expr; y=expr")
        user_parts = user_answer.split(';')
        user_k_exceptions = []
        user_x_sol = ""
        user_y_sol = ""

        for part in user_parts:
            part = part.strip()
            if part.lower().startswith('k!='):
                user_k_exceptions_raw = part[3:].strip()
                try:
                    user_k_exceptions = sorted([int(val_str.strip()) for val_str in user_k_exceptions_raw.split(',')])
                except ValueError:
                    pass # Invalid input
            elif part.lower().startswith('x='):
                user_x_sol = part[2:].strip()
            elif part.lower().startswith('y='):
                user_y_sol = part[2:].strip()
        
        # Compare k exceptions
        k_exceptions_correct = (user_k_exceptions == k_exception_values)

        # Compare x and y solutions as strings (requires exact LaTeX match)
        x_sol_correct = (user_x_sol == expected_x_sol_latex)
        y_sol_correct = (user_y_sol == expected_y_sol_latex)

        if k_exceptions_correct and x_sol_correct and y_sol_correct:
            is_correct = True
            result_text = f"完全正確！答案是 ${correct_answer}$。"
        else:
            feedback_parts = ["答案不正確。"]
            if not k_exceptions_correct:
                feedback_parts.append(f"k的例外值應為 {','.join(map(str, k_exception_values))}。")
            if not x_sol_correct:
                feedback_parts.append(f"x的解應為 ${expected_x_sol_latex}$。")
            if not y_sol_correct:
                feedback_parts.append(f"y的解應為 ${expected_y_sol_latex}$。")
            result_text = " ".join(feedback_parts)

    else: # For single k value problems (parallel_lines, inf_solutions, no_solution)
        correct_values_raw = correct_answer.split(',')
        user_values_raw = user_answer.split(',')

        correct_nums = []
        for val_str in correct_values_raw:
            try:
                if '/' in val_str:
                    correct_nums.append(float(Fraction(val_str)))
                else:
                    correct_nums.append(float(val_str))
            except ValueError:
                pass

        user_nums = []
        for val_str in user_values_raw:
            try:
                if '/' in val_str:
                    user_nums.append(float(Fraction(val_str)))
                else:
                    user_nums.append(float(val_str))
            except ValueError:
                pass

        correct_nums = sorted(correct_nums)
        user_nums = sorted(user_nums)
        
        if len(correct_nums) == len(user_nums) and all(math.isclose(u, c, rel_tol=1e-9) for u, c in zip(user_nums, correct_nums)):
            is_correct = True
            result_text = f"完全正確！答案是 ${correct_answer}$。"
        else:
            result_text = f"答案不正確。正確答案應為：${correct_answer}$"
    
    return {"correct": is_correct, "result": result_text, "next_question": True}