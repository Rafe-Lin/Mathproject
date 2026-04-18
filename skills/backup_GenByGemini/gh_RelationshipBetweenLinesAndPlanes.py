import random
from fractions import Fraction
import math

# Helper function to format vectors/points as (x,y,z)
def format_point(p):
    # Ensures integer output for whole numbers, Fraction for others
    formatted_coords = []
    for coord in p:
        if isinstance(coord, Fraction) and coord.denominator == 1:
            formatted_coords.append(str(int(coord)))
        else:
            formatted_coords.append(str(coord))
    return f"({','.join(formatted_coords)})"

# Helper function to generate random integers within a range, avoiding zero if needed
def rand_nonzero_int(min_val=-5, max_val=5):
    val = 0
    while val == 0:
        val = random.randint(min_val, max_val)
    return val

# Helper to format a term like "+ax" or "-ax" for plane equations
def format_term(coeff, var, first_term=False):
    if coeff == 0:
        return ""
    
    sign = "+" if coeff > 0 else "-"
    abs_coeff = abs(coeff)
    
    if abs_coeff == 1:
        coeff_str = ""
    else:
        coeff_str = str(abs_coeff)
    
    term = f"{coeff_str}{var}"
    
    if first_term:
        return f"{'-' if sign == '-' else ''}{term}" # No '+' for first term positive
    else:
        return f"{sign}{term}"

# Helper to format plane equation Ax + By + Cz = D
def format_plane_equation(n_plane, D_plane):
    terms = []
    
    if n_plane[0] != 0:
        terms.append(format_term(n_plane[0], 'x', first_term=True))
    if n_plane[1] != 0:
        terms.append(format_term(n_plane[1], 'y', first_term=len(terms)==0))
    if n_plane[2] != 0:
        terms.append(format_term(n_plane[2], 'z', first_term=len(terms)==0))

    if not terms: # All coeffs are zero, should not happen with rand_nonzero_int
        return "0 = 0" # Fallback, though ideally `n_plane` is non-zero
    
    return f"{''.join(terms)} = {D_plane}"

# Helper to format parametric line equations { x = x0 + at, y = y0 + bt, z = z0 + ct }
def format_parametric_line(p0, v):
    param_eqs = []
    variables = ['x', 'y', 'z']
    for i in range(3):
        p0_val = p0[i]
        v_val = v[i]
        
        eq_parts = [variables[i], " = "]
        
        if p0_val != 0:
            eq_parts.append(str(p0_val))
        
        if v_val != 0:
            v_term = ""
            if abs(v_val) == 1:
                v_term = "t"
            else:
                v_term = f"{abs(v_val)}t"
            
            if v_val > 0:
                if p0_val != 0:
                    eq_parts.append("+")
                eq_parts.append(v_term)
            else: # v_val < 0
                if p0_val != 0:
                    eq_parts.append("-")
                else: # if p0_val is 0, we just need the negative sign for the term itself
                    eq_parts.append("-")
                eq_parts.append(v_term)

        if len(eq_parts) == 2: # means it's like "x = " and p0_val and v_val were 0
             eq_parts.append("0") # x = 0
            
        param_eqs.append("".join(eq_parts))
    return param_eqs

# Helper to format symmetric line equations (x-x0)/a = (y-y0)/b = (z-z0)/c
# Handles cases where some direction vector components are zero
def format_symmetric_line(p0, v):
    sym_parts = []
    
    for i in range(3):
        var_char = ('x', 'y', 'z')[i]
        p0_val = p0[i]
        v_val = v[i]

        if v_val != 0:
            numerator_str = f"{var_char}"
            if p0_val != 0:
                numerator_str += f"{'-' if p0_val > 0 else '+'}{abs(p0_val)}"
            sym_parts.append(r"\\frac{{{}}}{{{}}}".format(numerator_str, v_val))
        else:
            # If v_val is 0, then the variable is fixed: e.g., x = x0
            sym_parts.append(f"{var_char}={p0_val}")
    
    # If there are mixed zero/non-zero v components, separate by comma.
    # Example: x=1, (y-2)/3 = (z-4)/5
    equal_sections = []
    fixed_vars = []
    for part in sym_parts:
        if '=' in part: # e.g. x=1
            fixed_vars.append(part)
        else: # e.g. (y-2)/3
            equal_sections.append(part)
    
    if fixed_vars:
        return f"{', '.join(fixed_vars + [' = '.join(equal_sections)])}" if equal_sections else f"{', '.join(fixed_vars)}"
    else:
        return f"{' = '.join(equal_sections)}"


# Generates initial parameters for a line and a plane
def generate_line_and_plane_params(level=1):
    # Line P0 + t*v
    p0_line = (random.randint(-5, 5), random.randint(-5, 5), random.randint(-5, 5))
    v_line = (rand_nonzero_int(-3, 3), rand_nonzero_int(-3, 3), rand_nonzero_int(-3, 3))
    
    # Plane n . (X - P_plane) = 0 => n.X = n.P_plane
    n_plane = (rand_nonzero_int(-3, 3), rand_nonzero_int(-3, 3), rand_nonzero_int(-3, 3))
    
    p_plane_on_plane = (random.randint(-5, 5), random.randint(-5, 5), random.randint(-5, 5))
    D_plane = sum(n_plane[i] * p_plane_on_plane[i] for i in range(3))

    return {
        "p0_line": p0_line,
        "v_line": v_line,
        "n_plane": n_plane,
        "D_plane": D_plane
    }

# Solves for t when substituting line into plane equation
# Returns solution type ("one_solution", "no_solution", "infinite_solutions") and t_val (if "one_solution")
def solve_for_t(p0_line, v_line, n_plane, D_plane):
    # Line: x = x0 + at, y = y0 + bt, z = z0 + ct
    # Plane: Ax + By + Cz = D
    # Substitute: A(x0+at) + B(y0+bt) + C(z0+ct) = D
    # (Ax0+By0+Cz0) + (Aa+Bb+Cc)t = D
    # (n_plane . p0_line) + (n_plane . v_line)t = D
    
    dot_np0 = sum(n_plane[i] * p0_line[i] for i in range(3))
    dot_nv = sum(n_plane[i] * v_line[i] for i in range(3))
    
    # Equation becomes: dot_np0 + dot_nv * t = D_plane
    # dot_nv * t = D_plane - dot_np0
    
    rhs = D_plane - dot_np0
    
    if dot_nv == 0:
        if rhs == 0:
            return "infinite_solutions", None # Line lies in plane (0t = 0)
        else:
            return "no_solution", None      # Line is parallel (0t = k, k!=0)
    else:
        t_val = Fraction(rhs, dot_nv)
        return "one_solution", t_val

# Generates a problem to determine the relationship between a line and a plane
def generate_intersection_type_problem(level=1):
    params = generate_line_and_plane_params(level)
    p0_line = params["p0_line"]
    v_line = params["v_line"]
    n_plane = params["n_plane"]
    D_plane = params["D_plane"]

    line_param_eqs = format_parametric_line(p0_line, v_line)
    plane_eq_str = format_plane_equation(n_plane, D_plane)

    solution_type, t_val = solve_for_t(p0_line, v_line, n_plane, D_plane)

    question_text = (
        f"判斷直線 $L$ 的參數式為：<br>"
        f"$\quad {{ {{ {line_param_eqs[0]} }} }} $<br>"
        f"$\quad {{ {{ {line_param_eqs[1]} }} }} $<br>"
        f"$\quad {{ {{ {line_param_eqs[2]} }} }} $<br>"
        f"與平面 $E: {{ {plane_eq_str} }}$ 的相交情形。"
        f"<br>請回答 '一點', '平行' 或 '包含'。"
    )
    
    intersection_point_str = None
    if solution_type == "one_solution":
        correct_answer_type = "一點"
        ix = p0_line[0] + v_line[0] * t_val
        iy = p0_line[1] + v_line[1] * t_val
        iz = p0_line[2] + v_line[2] * t_val
        intersection_point_str = format_point((ix, iy, iz))
    elif solution_type == "no_solution":
        correct_answer_type = "平行"
    else: # infinite_solutions
        correct_answer_type = "包含"

    # Store details for check function
    problem_details = {
        "correct_answer_type": correct_answer_type, # The string type for comparison
        "intersection_point": intersection_point_str
    }

    return {
        "question_text": question_text,
        "answer": correct_answer_type, # This is the expected user input for this type
        "correct_answer": problem_details # Detailed answer for check
    }

# Generates a problem to find the intersection point of a line and a plane
def generate_intersection_point_problem(level=1):
    while True: # Keep generating until we get 'one_solution' with simple t and non-zero line direction components
        params = generate_line_and_plane_params(level)
        p0_line = params["p0_line"]
        v_line = params["v_line"]
        n_plane = params["n_plane"]
        D_plane = params["D_plane"]
        
        # Ensure v_line has non-zero components for symmetric form display
        if any(comp == 0 for comp in v_line):
            continue

        solution_type, t_val = solve_for_t(p0_line, v_line, n_plane, D_plane)
        if solution_type == "one_solution" and t_val.denominator <= 5 and abs(t_val.numerator) <= 10: # Keep t simple for integer/simple fraction answers
            break
    
    line_sym_eq = format_symmetric_line(p0_line, v_line)
    plane_eq_str = format_plane_equation(n_plane, D_plane)

    # Calculate intersection point
    ix = p0_line[0] + v_line[0] * t_val
    iy = p0_line[1] + v_line[1] * t_val
    iz = p0_line[2] + v_line[2] * t_val
    intersection_point = (ix, iy, iz)

    question_text = (
        f"求直線 $L: {{ {line_sym_eq} }}$ 與平面 $E: {{ {plane_eq_str} }}$ 的交點坐標。"
        f"<br>請以 $(x,y,z)$ 格式回答，例如 $(1,2,3)$。"
    )
    
    correct_answer = format_point(intersection_point)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

# Generates a problem to find the projection point of a point onto a plane
def generate_projection_point_problem(level=1):
    while True:
        # Generate point A
        point_A = (random.randint(-5, 5), random.randint(-5, 5), random.randint(-5, 5))
        
        # Generate plane E
        n_plane = (rand_nonzero_int(-3, 3), rand_nonzero_int(-3, 3), rand_nonzero_int(-3, 3))
        p_plane_on_plane = (random.randint(-5, 5), random.randint(-5, 5), random.randint(-5, 5))
        D_plane = sum(n_plane[i] * p_plane_on_plane[i] for i in range(3))
        
        # Ensure point A is NOT on the plane
        if sum(n_plane[i] * point_A[i] for i in range(3)) == D_plane:
            continue
        
        # Line AH has direction vector n_plane, passes through point_A
        p0_line_ah = point_A
        v_line_ah = n_plane # The normal vector of the plane is the direction vector of AH
        
        # Solve for t for the intersection of AH and E (which is H)
        solution_type, t_val = solve_for_t(p0_line_ah, v_line_ah, n_plane, D_plane)

        # We must get a solution here, as A is not on E and n_plane is non-zero
        # Check if t_val is simple enough
        if solution_type == "one_solution" and t_val.denominator <= 5 and abs(t_val.numerator) <= 10:
            break
            
    plane_eq_str = format_plane_equation(n_plane, D_plane)

    # Calculate projection point H
    hx = p0_line_ah[0] + v_line_ah[0] * t_val
    hy = p0_line_ah[1] + v_line_ah[1] * t_val
    hz = p0_line_ah[2] + v_line_ah[2] * t_val
    projection_point_H = (hx, hy, hz)

    question_text = (
        f"已知點 $A{format_point(point_A)}$ 為平面 $E: {{ {plane_eq_str} }}$ 外一點，"
        f"求 $A$ 點在平面 $E$ 上的投影點坐標。"
        f"<br>請以 $(x,y,z)$ 格式回答，例如 $(1,2,3)$。"
    )

    correct_answer = format_point(projection_point_H)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

# Generates a problem to find the symmetric point of a point with respect to a plane
def generate_symmetric_point_problem(level=1):
    while True:
        # Generate point A
        point_A = (random.randint(-5, 5), random.randint(-5, 5), random.randint(-5, 5))
        
        # Generate plane E
        n_plane = (rand_nonzero_int(-3, 3), rand_nonzero_int(-3, 3), rand_nonzero_int(-3, 3))
        p_plane_on_plane = (random.randint(-5, 5), random.randint(-5, 5), random.randint(-5, 5))
        D_plane = sum(n_plane[i] * p_plane_on_plane[i] for i in range(3))
        
        # Ensure point A is NOT on the plane
        if sum(n_plane[i] * point_A[i] for i in range(3)) == D_plane:
            continue
        
        # Line AH has direction vector n_plane, passes through point_A
        p0_line_ah = point_A
        v_line_ah = n_plane 
        
        # Solve for t for the intersection of AH and E (which is H)
        solution_type, t_val = solve_for_t(p0_line_ah, v_line_ah, n_plane, D_plane)

        if solution_type == "one_solution" and t_val.denominator <= 5 and abs(t_val.numerator) <= 10:
            break
            
    plane_eq_str = format_plane_equation(n_plane, D_plane)

    # Calculate projection point H
    hx = p0_line_ah[0] + v_line_ah[0] * t_val
    hy = p0_line_ah[1] + v_line_ah[1] * t_val
    hz = p0_line_ah[2] + v_line_ah[2] * t_val
    projection_point_H = (hx, hy, hz)

    # Calculate symmetric point A' = 2H - A
    sym_x = 2 * hx - point_A[0]
    sym_y = 2 * hy - point_A[1]
    sym_z = 2 * hz - point_A[2]
    symmetric_point_A_prime = (sym_x, sym_y, sym_z)

    question_text = (
        f"已知點 $A{format_point(point_A)}$ 為平面 $E: {{ {plane_eq_str} }}$ 外一點，"
        f"求 $A$ 點關於平面 $E$ 的對稱點坐標。"
        f"<br>請以 $(x,y,z)$ 格式回答，例如 $(1,2,3)$。"
    )

    correct_answer = format_point(symmetric_point_A_prime)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    problem_type = random.choice([
        'intersection_type', 
        'intersection_point', 
        'projection_point', 
        'symmetric_point'
    ])
    
    if problem_type == 'intersection_type':
        return generate_intersection_type_problem(level)
    elif problem_type == 'intersection_point':
        return generate_intersection_point_problem(level)
    elif problem_type == 'projection_point':
        return generate_projection_point_problem(level)
    else: # symmetric_point
        return generate_symmetric_point_problem(level)


def check(user_answer, correct_answer_details):
    user_answer = user_answer.strip()
    is_correct = False
    result_text = ""

    if isinstance(correct_answer_details, dict) and "correct_answer_type" in correct_answer_details:
        # This is an intersection_type problem (e.g., '一點', '平行', '包含')
        correct_answer_type = correct_answer_details["correct_answer_type"]
        
        # Normalize user input for type comparison
        normalized_user_answer = user_answer.replace(" ", "").lower()
        
        if correct_answer_type == "一點":
            is_correct = (normalized_user_answer == "一點" or normalized_user_answer == "交於一點" or normalized_user_answer == "相交一點")
            if is_correct:
                result_text = f"完全正確！直線與平面相交於一點。"
            else:
                result_text = f"答案不正確。正確答案應為：'一點'。直線與平面相交於一點。"
        elif correct_answer_type == "平行":
            is_correct = (normalized_user_answer == "平行" or normalized_user_answer == "互相平行")
            if is_correct:
                result_text = f"完全正確！直線與平面平行。"
            else:
                result_text = f"答案不正確。正確答案應為：'平行'。直線與平面平行。"
        elif correct_answer_type == "包含":
            is_correct = (normalized_user_answer == "包含" or normalized_user_answer == "落在平面上" or normalized_user_answer == "直線上")
            if is_correct:
                result_text = f"完全正確！直線包含在平面內。"
            else:
                result_text = f"答案不正確。正確答案應為：'包含'。直線包含在平面內。"
        
        # Add intersection point detail if applicable (optional, for advanced feedback)
        if correct_answer_type == "一點" and correct_answer_details["intersection_point"]:
            result_text += f"交點坐標為 {correct_answer_details['intersection_point']}。"

    else:
        # This is a coordinate point problem (intersection, projection, symmetric)
        # Expected format for user_answer and correct_answer_details: "(x,y,z)" or "(x, y, z)"
        
        # Parse user answer
        try:
            # Remove parentheses and split by comma
            user_coords_str = user_answer.strip('() ').split(',')
            # Convert each string coordinate to a Fraction
            user_coords = tuple(Fraction(c.strip()) for c in user_coords_str)
        except (ValueError, IndexError):
            is_correct = False
            result_text = f"你的答案格式不正確。請以 $(x,y,z)$ 格式回答，例如 $(1,2,3)$。正確答案應為：${correct_answer_details}$"
            return {"correct": is_correct, "result": result_text, "next_question": True}

        # Parse correct answer (similar logic)
        try:
            correct_coords_str = correct_answer_details.strip('() ').split(',')
            correct_coords = tuple(Fraction(c.strip()) for c in correct_coords_str)
        except (ValueError, IndexError):
            is_correct = False
            result_text = f"系統內部錯誤，無法解析正確答案格式。請聯繫管理員。"
            return {"correct": is_correct, "result": result_text, "next_question": True}
        
        if user_coords == correct_coords:
            is_correct = True
            result_text = f"完全正確！答案是 ${correct_answer_details}$。"
        else:
            is_correct = False
            result_text = f"答案不正確。正確答案應為：${correct_answer_details}$"

    return {"correct": is_correct, "result": result_text, "next_question": True}