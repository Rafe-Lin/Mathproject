import random
from fractions import Fraction
import math

# Helper functions
def generate_point_3d(min_val=-5, max_val=5):
    """Generates a random 3D point (x, y, z)."""
    return (random.randint(min_val, max_val),
            random.randint(min_val, max_val),
            random.randint(min_val, max_val))

def simplify_vector(vec):
    """
    Simplifies a 3D vector by dividing by the greatest common divisor of its components.
    Ensures the first non-zero component is positive for a canonical form.
    """
    a, b, c = vec
    if a == 0 and b == 0 and c == 0:
        return (0, 0, 0)
    
    # Make the first non-zero component positive for canonical form
    if a != 0 and a < 0:
        a, b, c = -a, -b, -c
    elif a == 0 and b != 0 and b < 0:
        a, b, c = -a, -b, -c
    elif a == 0 and b == 0 and c != 0 and c < 0:
        a, b, c = -a, -b, -c
        
    common = abs(math.gcd(a, math.gcd(b, c)))
    
    # common can be 0 if all components are 0, but that case is handled above.
    # For non-zero vectors, common will be at least 1.
    return (a // common, b // common, c // common)

def generate_vector_3d(min_val=-5, max_val=5, allow_zero_vector=False):
    """
    Generates a random 3D vector (a, b, c).
    By default, it ensures the vector is not the zero vector.
    Returns a simplified and canonical form.
    """
    vec = (0, 0, 0)
    while not allow_zero_vector and vec == (0, 0, 0):
        vec = (random.randint(min_val, max_val),
               random.randint(min_val, max_val),
               random.randint(min_val, max_val))
    return simplify_vector(vec)

def format_parametric_eq(point, vector, var='t'):
    """
    Formats a 3D line's parametric equations into a LaTeX string.
    e.g., {x = 2 + t, y = -1 + 2t, z = 3 - 2t}
    Handles zero coefficients and zero constant terms for clean output.
    """
    x0, y0, z0 = point
    a, b, c = vector # Assumed to be simplified and canonical
    
    eqs = []
    
    def format_term_param(coord, coeff):
        parts = []
        # Handle constant term (x0, y0, z0)
        if coord != 0:
            parts.append(str(coord))
        
        # Handle parameter term (at, bt, ct)
        if coeff != 0:
            if coeff == 1:
                t_term = var
            elif coeff == -1:
                t_term = f"-{var}"
            else:
                t_term = f"{coeff}{var}"
            
            # Decide on the sign for the parameter term
            if parts and coeff > 0: # e.g., "2 + t"
                parts.append(f"+{t_term}")
            elif parts and coeff < 0: # e.g., "2 - t"
                parts.append(t_term) # t_term already includes "-"
            else: # No initial coord, or coord is 0 (e.g., "t" or "-t")
                parts.append(t_term)

        if not parts: # If both constant and coefficient are 0 (e.g., "x = 0")
            return "0"
        
        # Clean up "X+-Y" to "X-Y"
        return "".join(parts).replace("+-", "-")

    eqs.append(f"x = {format_term_param(x0, a)}")
    eqs.append(f"y = {format_term_param(y0, b)}")
    eqs.append(f"z = {format_term_param(z0, c)}")
    
    return r"""
\begin{{cases}}
  {} \\
  {} \\
  {}
\end{{cases}}
""".format(*eqs)

def format_symmetric_eq(point, vector):
    """
    Formats a 3D line's symmetric equations into a LaTeX string.
    e.g., (x-5)/(-2) = (y-4)/(-3) = (z+3)/4
    Assumes all vector components are non-zero.
    """
    x0, y0, z0 = point
    a, b, c = vector # Assumed to be simplified, canonical, and all non-zero
    
    parts = []

    def format_numerator_sym(val, coord_char):
        if val == 0:
            return coord_char # e.g. x/a if x0=0
        elif val > 0:
            return f"{coord_char} - {val}"
        else: # val < 0
            return f"{coord_char} + {-val}" # e.g. z+3 if z0=-3

    parts.append(r"\\frac{{{}}}{{{}}}".format(format_numerator_sym(x0, 'x'), a))
    parts.append(r"\\frac{{{}}}{{{}}}".format(format_numerator_sym(y0, 'y'), b))
    parts.append(r"\\frac{{{}}}{{{}}}".format(format_numerator_sym(z0, 'z'), c))
    
    return " = ".join(parts)

def solve_2x2_system(a1, b1, c1, a2, b2, c2):
    """
    Solves a 2x2 linear system: a1*x + b1*y = c1, a2*x + b2*y = c2
    Returns (x, y) as Fractions, or (None, None) if no unique solution.
    """
    det = a1*b2 - a2*b1
    if det == 0:
        return None, None # No unique solution (parallel or identical lines/equations)
    
    x_num = c1*b2 - c2*b1
    y_num = a1*c2 - a2*c1
    
    x = Fraction(x_num, det)
    y = Fraction(y_num, det)
    return x, y

def format_equation_part(coeff, var, show_plus=True):
    """Helper to format a single term in a linear equation (e.g., '3x', '-y', '+2z')."""
    if coeff == 0:
        return ""
    abs_coeff = abs(coeff)
    sign_str = "+" if coeff > 0 else "-"
    term = f"{abs_coeff}{var}" if abs_coeff != 1 else var
    
    if sign_str == "+" and not show_plus:
        sign_str = "" # No leading '+' for the very first term
    
    return f"{sign_str}{term}"

def format_plane_equation_string(A, B, C, D):
    """
    Formats a plane equation (Ax + By + Cz = D) into a LaTeX string.
    e.g., '3x+2y+z = 4'
    """
    parts = []
    
    x_term = format_equation_part(A, 'x', show_plus=False)
    if x_term: parts.append(x_term)

    y_term = format_equation_part(B, 'y', show_plus=bool(parts))
    if y_term: parts.append(y_term)

    z_term = format_equation_part(C, 'z', show_plus=bool(parts))
    if z_term: parts.append(z_term)
    
    lhs = "".join(parts)
    if not lhs: lhs = "0" # Should not happen for a valid plane equation
    
    return f"{lhs} = {D}"

def generate_line_from_two_planes_data():
    """
    Generates two plane equations and calculates the parametric form (point and direction vector)
    of their intersection line.
    Ensures planes are not parallel or identical, and that a valid line is formed.
    """
    while True: # Loop until valid intersecting planes and a point are found
        A1, B1, C1, D1 = [random.randint(-5, 5) for _ in range(4)]
        A2, B2, C2, D2 = [random.randint(-5, 5) for _ in range(4)]

        N1 = (A1, B1, C1)
        N2 = (A2, B2, C2)
        
        # Calculate direction vector as cross product of normal vectors
        a = N1[1]*N2[2] - N1[2]*N2[1]
        b = N1[2]*N2[0] - N1[0]*N2[2]
        c = N1[0]*N2[1] - N1[1]*N2[0]
        
        # Conditions for invalid planes or non-intersecting planes:
        # - Normal vectors are (0,0,0) (not a plane)
        # - Cross product is (0,0,0) (planes are parallel or identical)
        if ((A1, B1, C1) == (0,0,0) or (A2, B2, C2) == (0,0,0) or (a, b, c) == (0, 0, 0)):
            continue # Regenerate planes

        direction_vec = simplify_vector((a, b, c))
        
        point_on_line = None
        # Attempt to find a point on the line by setting one coordinate to 0
        
        # Try setting z=0
        x, y = solve_2x2_system(A1, B1, D1, A2, B2, D2)
        if x is not None and y is not None:
            point_on_line = (x, y, Fraction(0))

        # If not found, try setting y=0
        if point_on_line is None:
            x, z = solve_2x2_system(A1, C1, D1, A2, C2, D2)
            if x is not None and z is not None:
                point_on_line = (x, Fraction(0), z)

        # If not found, try setting x=0
        if point_on_line is None:
            y, z = solve_2x2_system(B1, C1, D1, B2, C2, D2)
            if y is not None and z is not None:
                point_on_line = (Fraction(0), y, z)
                
        if point_on_line is not None:
            # Convert fractions back to int if whole number for cleaner display
            point_on_line_display = tuple(int(p) if p.denominator == 1 else p for p in point_on_line)
            direction_vec_display = tuple(int(v) if v.denominator == 1 else v for v in direction_vec)

            plane1_str = format_plane_equation_string(A1, B1, C1, D1)
            plane2_str = format_plane_equation_string(A2, B2, C2, D2)
            
            return plane1_str, plane2_str, point_on_line_display, direction_vec_display
        
        # If point_on_line is still None, it means no unique solution for finding a point
        # (e.g., all 2x2 systems were singular). This should be rare but can happen if
        # the initial plane generation somehow leads to this edge case despite the cross product check.
        # Continue the loop to regenerate.


def generate(level=1):
    """
    Generates a 3D line equation problem based on the specified skill level.
    """
    problem_types_by_level = {
        1: [
            'parametric_from_point_vector',
            'point_on_line_check',
            'find_coords_on_line',
            'parametric_from_two_points',
            'symmetric_from_two_points',
            'parametric_from_two_planes',
            'two_plane_form'
        ],
        2: [
            'point_on_line_check',
            'find_coords_on_line',
            'symmetric_from_two_points',
            'parametric_from_two_planes',
            'two_plane_form'
        ],
        3: [
            'find_coords_on_line',
            'symmetric_from_two_points',
            'parametric_from_two_planes',
            'two_plane_form'
        ]
    }
    
    problem_type = random.choice(problem_types_by_level.get(level, problem_types_by_level[1]))

    if problem_type == 'parametric_from_point_vector':
        return generate_parametric_from_point_vector()
    elif problem_type == 'point_on_line_check':
        return generate_point_on_line_check()
    elif problem_type == 'find_coords_on_line':
        return generate_find_coords_on_line()
    elif problem_type == 'parametric_from_two_points':
        return generate_parametric_from_two_points()
    elif problem_type == 'symmetric_from_two_points':
        return generate_symmetric_from_two_points()
    elif problem_type == 'parametric_from_two_planes':
        return generate_parametric_from_two_planes()
    elif problem_type == 'two_plane_form':
        return generate_two_plane_form()

def generate_parametric_from_point_vector():
    """Generates a problem to find the parametric form given a point and a direction vector."""
    point = generate_point_3d()
    vector = generate_vector_3d(allow_zero_vector=False) # Direction vector cannot be zero vector
    
    x0, y0, z0 = point
    a, b, c = vector
    
    question_text = f"設直線$L$通過點 $A({x0},{y0},{z0})$ 且方向向量為 $({a},{b},{c})$ 。<br>求直線$L$的參數式。"
    
    correct_answer = format_parametric_eq(point, vector)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_point_on_line_check():
    """Generates a problem to check if a given point lies on a line (given by point and vector)."""
    point = generate_point_3d()
    vector = generate_vector_3d(allow_zero_vector=False)
    
    x0, y0, z0 = point
    a, b, c = vector
    
    is_on_line = random.choice([True, False])
    
    if is_on_line:
        t_val_on = random.randint(-2, 2)
        px, py, pz = (x0 + a * t_val_on, y0 + b * t_val_on, z0 + c * t_val_on)
    else:
        # Generate a point that is NOT on the line
        while True: # Loop until a truly 'off' point is generated
            t_val_off = random.randint(-2, 2)
            px_base = x0 + a * t_val_off
            py_base = y0 + b * t_val_off
            pz_base = z0 + c * t_val_off
            
            test_point_list = [px_base, py_base, pz_base]
            
            # Perturb one coordinate to make it off the line
            perturbed_idx = random.choice([0, 1, 2])
            change = random.choice([-1, 1, -2, 2]) # Add a small non-zero change
            if vector[perturbed_idx] == 0: # If direction component is 0, changing this coord will definitely make it off unless it was already off.
                pass # The change is enough
            else:
                # To ensure it's truly off, make sure the new point doesn't fall on the line with a different 't'
                # This is a robust check: if it's still on the line, the t for the perturbed coord must match others.
                
                # Try to perturb. If after perturbing, the implicit 't' value is different from other coordinates, it's off.
                test_point_list[perturbed_idx] += change

                t_values_from_coords = []
                if a != 0: t_values_from_coords.append(Fraction(test_point_list[0] - x0, a))
                if b != 0: t_values_from_coords.append(Fraction(test_point_list[1] - y0, b))
                if c != 0: t_values_from_coords.append(Fraction(test_point_list[2] - z0, c))
                
                # Check for consistency of t values. If all t values are not the same, the point is off the line.
                if len(t_values_from_coords) < 2 or not all(t == t_values_from_coords[0] for t in t_values_from_coords):
                    break # Point is definitely off, exit inner loop
            
            # If after perturbation, it accidentally lands back on the line (e.g., if change was multiple of vector component)
            # or if the direction vector component was zero and the point was already off, regenerate.
            # This 'break' logic covers the "definitely off" part. If it doesn't break, the loop continues.
        
        px, py, pz = test_point_list
    
    question_text = f"設直線$L$通過點 $A({x0},{y0},{z0})$ 且方向向量為 $({a},{b},{c})$ 。<br>判斷 $P({px},{py},{pz})$ 是否在直線$L$上。"
    correct_answer = "是" if is_on_line else "否"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_find_coords_on_line():
    """Generates a problem to find unknown coordinates (m, k) of a point known to be on a line."""
    point = generate_point_3d()
    vector = generate_vector_3d(allow_zero_vector=False)
    
    x0, y0, z0 = point
    a, b, c = vector
    
    # Pick a random t value to generate the point
    t_val = random.randint(-3, 3)
    
    px = x0 + a * t_val
    py = y0 + b * t_val
    pz = z0 + c * t_val
    
    # Choose one or two coordinates to replace with variables (m, k)
    unknown_indices = random.sample([0, 1, 2], random.choice([1, 2])) # Select 1 or 2 unique indices
    
    test_coords_str = [str(px), str(py), str(pz)]
    
    unknown_map = {} # Store actual values for 'm' and 'k'
    
    # Assign 'm' to the first chosen unknown index, 'k' to the second
    # This ensures consistent naming regardless of which coordinates are chosen.
    if 0 in unknown_indices:
        test_coords_str[0] = 'm'
        unknown_map['m'] = px
    
    if 1 in unknown_indices:
        if 'm' not in unknown_map: # If 'y' is the first unknown
            test_coords_str[1] = 'm'
            unknown_map['m'] = py
        else: # 'y' is the second unknown (after 'x' was 'm')
            test_coords_str[1] = 'k'
            unknown_map['k'] = py

    if 2 in unknown_indices:
        if 'm' not in unknown_map: # If 'z' is the first unknown
            test_coords_str[2] = 'm'
            unknown_map['m'] = pz
        elif 'k' not in unknown_map: # If 'z' is the second unknown (after 'x' or 'y' was 'm')
            test_coords_str[2] = 'k'
            unknown_map['k'] = pz
        # If both 'm' and 'k' are already assigned (e.g., x=m, y=k), this condition won't be met,
        # implying we only handle up to two unknowns.
    
    point_str = f"P({test_coords_str[0]}, {test_coords_str[1]}, {test_coords_str[2]})"
    
    question_text = f"設直線$L$通過點 $A({x0},{y0},{z0})$ 且方向向量為 $({a},{b},{c})$ 。<br>已知點 ${point_str}$ 在直線$L$上，求 "
    
    ans_parts = []
    # Order the answer consistently (m then k)
    if 'm' in unknown_map:
        question_text += f"$m$"
        ans_parts.append(f"m = {unknown_map['m']}")
    if 'k' in unknown_map:
        if 'm' in unknown_map: question_text += f", $k$"
        else: question_text += f"$k$"
        ans_parts.append(f"k = {unknown_map['k']}")
    question_text += " 的值。"
    
    correct_answer = ", ".join(ans_parts)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_parametric_from_two_points():
    """Generates a problem to find the parametric form of a line given two points."""
    point_a = generate_point_3d()
    point_b = generate_point_3d()
    
    while point_a == point_b: # Ensure points are distinct to form a line
        point_b = generate_point_3d()
        
    x1, y1, z1 = point_a
    x2, y2, z2 = point_b
    
    # Direction vector AB, then simplify
    vector_ab = simplify_vector((x2 - x1, y2 - y1, z2 - z1))
    
    question_text = f"已知空間中兩點 $A({x1},{y1},{z1})$ 與 $B({x2},{y2},{z2})$ ，求直線$AB$的參數式。"
    
    correct_answer = format_parametric_eq(point_a, vector_ab)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_symmetric_from_two_points():
    """
    Generates a problem to find the symmetric form of a line given two points.
    Ensures all components of the direction vector are non-zero for simple symmetric form.
    """
    point_a = generate_point_3d()
    point_b = generate_point_3d()
    
    while True:
        if point_a == point_b: # Ensure points are distinct
            point_b = generate_point_3d()
            continue
            
        x1, y1, z1 = point_a
        x2, y2, z2 = point_b
        
        vector_ab = (x2 - x1, y2 - y1, z2 - z1)
        
        # For symmetric form, all components of the direction vector must be non-zero.
        if any(v == 0 for v in vector_ab):
            point_a = generate_point_3d() # Regenerate points if any component is zero
            point_b = generate_point_3d()
        else:
            break # Valid points and vector found
    
    # Simplify after ensuring non-zero components
    vector_ab_simplified = simplify_vector(vector_ab)

    question_text = f"已知空間中兩點 $A({x1},{y1},{z1})$ 與 $B({x2},{y2},{z2})$ ，求直線$AB$的比例式。"
    
    correct_answer = format_symmetric_eq(point_a, vector_ab_simplified)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_parametric_from_two_planes():
    """Generates a problem to find the parametric form of a line given by the intersection of two planes."""
    plane1_str, plane2_str, point_on_line, direction_vec = generate_line_from_two_planes_data()
    
    question_text = f"已知兩平面 $E_1 : {plane1_str}$ 與 $E_2: {plane2_str}$ 交於直線$L$。<br>求直線$L$的參數式。"
    
    correct_answer = format_parametric_eq(point_on_line, direction_vec)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_two_plane_form():
    """Generates a problem to simply state the two-plane form of a line given two plane equations."""
    plane1_str, plane2_str, _, _ = generate_line_from_two_planes_data() # Discard point and vector
    
    question_text = f"已知兩平面 $E_1 : {plane1_str}$ 與 $E_2: {plane2_str}$ 交於直線$L$。<br>求直線$L$的兩面式。"
    
    # The two-plane form is just the system of the two plane equations.
    # The order of equations is preserved from generation for consistency.
    correct_answer = r"""
\begin{{cases}}
  {} \\
  {}
\end{{cases}}
""".format(plane1_str, plane2_str)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    Checks if the user's answer is correct.
    Normalizes both answers by removing whitespace and standardizing parameter names
    and equation order within LaTeX 'cases' environments for robust comparison.
    """
    
    def normalize_latex_string(s):
        """Helper to normalize LaTeX strings for robust comparison."""
        # Remove all whitespace (spaces, newlines, tabs)
        s = s.strip().replace(" ", "").replace("\n", "").replace("\t", "")
        
        # Standardize parameter variable for parametric equations (t, s, k -> __VAR__)
        s = s.replace("t", "__VAR__").replace("s", "__VAR__").replace("k", "__VAR__")
        
        # If it's a LaTeX 'cases' environment (for parametric or two-plane forms),
        # extract equations, sort them, and reconstruct to ignore order differences.
        if r"\begin{cases}" in s and r"\end{cases}" in s:
            start_idx = s.find(r"\begin{cases}") + len(r"\begin{cases}")
            end_idx = s.find(r"\end{cases}")
            
            # Extract content between \begin{cases} and \end{cases}
            content = s[start_idx:end_idx]
            
            # Split individual equations (separated by \\), strip whitespace, filter empty strings
            equations = [eq.strip() for eq in content.split(r"\\") if eq.strip()]
            equations.sort() # Sort equations alphabetically to ensure canonical order
            
            # Reconstruct the string with sorted equations
            s = s[:start_idx] + r"\\".join(equations) + s[end_idx:]
        
        return s

    normalized_user_answer = normalize_latex_string(user_answer)
    normalized_correct_answer = normalize_latex_string(correct_answer)
    
    is_correct = (normalized_user_answer == normalized_correct_answer)
    
    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}