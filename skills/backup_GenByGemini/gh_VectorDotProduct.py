import random
import math
from fractions import Fraction
import uuid

# Define common angles and their cosine values for display (LaTeX)
COSINE_DISPLAY_VALUES = {
    0: "1",
    30: r"\\frac{{\\sqrt{{3}}}}{{2}}",
    45: r"\\frac{{\\sqrt{{2}}}}{{2}}",
    60: r"\\frac{{1}}{{2}}",
    90: "0",
    120: r"-\\frac{{1}}{{2}}",
    135: r"-\\frac{{\\sqrt{{2}}}}{{2}}",
    150: r"-\\frac{{\\sqrt{{3}}}}{{2}}",
    180: "-1"
}

# Values for actual calculation (float)
COSINE_CALC_VALUES = {
    0: 1.0,
    30: math.sqrt(3)/2,
    45: math.sqrt(2)/2,
    60: 0.5,
    90: 0.0,
    120: -0.5,
    135: -math.sqrt(2)/2,
    150: -math.sqrt(3)/2,
    180: -1.0
}

# Angles that lead to rational cosine values (for simpler answers in calculation problems)
RATIONAL_COSINE_ANGLES = [0, 60, 90, 120, 180] 
# Angles that give sqrt values for cosine (can be used for angle identification problems)
SURD_COSINE_ANGLES = [30, 45, 135, 150]

def get_angle_from_cosine(cos_val):
    """
    Returns the degree angle if cos_val matches a special angle cosine.
    """
    for angle_deg, calc_val in COSINE_CALC_VALUES.items():
        if are_close(cos_val, calc_val):
            return angle_deg
    return None

def format_value_for_latex(value):
    """
    Formats a numeric value for LaTeX display. Handles integers and fractions.
    Assumes values are rational after generation logic.
    """
    if isinstance(value, int):
        return str(value)
    
    # Check if the value is very close to an integer
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    
    # Try to represent as a fraction
    if isinstance(value, float):
        frac_val = Fraction(value).limit_denominator(100)
        # Ensure it's very close to the float value, not just an approximation
        if are_close(float(frac_val), value):
            if frac_val.denominator == 1:
                return str(frac_val.numerator)
            return r"\\frac{{{}}}{{{}}}".format(frac_val.numerator, frac_val.denominator)
    
    # Fallback for other floats (should be rare if generation is controlled)
    return str(round(value, 4))

def are_close(a, b, rel_tol=1e-9, abs_tol=1e-12):
    """Checks if two float numbers are approximately equal."""
    # Ensure both inputs are floats for comparison
    a = float(a)
    b = float(b)
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

def vector_magnitude(v_coords):
    """Calculates the magnitude of a 2D vector."""
    return math.sqrt(sum(c**2 for c in v_coords))

def dot_product_coords(v1_coords, v2_coords):
    """Calculates the dot product of two 2D vectors from their coordinates."""
    return sum(c1 * c2 for c1, c2 in zip(v1_coords, v2_coords))

def generate_dot_product_geometric_problem():
    """
    題目: 已知向量 $\vec{a}$ 與 $\vec{b}$ 的夾角為120°，且 $|\vec{a}|=2, |\vec{b}|=3$，求 $\vec{a} \\cdot \vec{b}$ 的值。
    """
    mag_a = random.randint(2, 8)
    mag_b = random.randint(2, 8)
    
    # Only use angles that result in rational cosines for simpler answers
    angle_deg = random.choice(RATIONAL_COSINE_ANGLES) 
    
    cos_theta = COSINE_CALC_VALUES[angle_deg]
    dot_product_val = mag_a * mag_b * cos_theta
    
    question_text = (
        f"已知向量 $\\vec{{a}}$ 與 $\\vec{{b}}$ 的夾角為 ${angle_deg}°$，"
        f"且 $|\\vec{{a}}|={mag_a}$, $|\\vec{{b}}|={mag_b}$，求 $\\vec{{a}} \\cdot \\vec{{b}}$ 的值。"
    )
    
    correct_answer = format_value_for_latex(dot_product_val)
            
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_dot_product_coords_problem():
    """
    題目: 已知 $\vec{a}=(7,1), \vec{b}=(3,4)$。求 $\vec{a} \\cdot \vec{b}$ 的值。
    """
    v1 = (random.randint(-7, 7), random.randint(-7, 7))
    v2 = (random.randint(-7, 7), random.randint(-7, 7))
    
    # Avoid zero vectors for more meaningful problems
    while v1 == (0,0): v1 = (random.randint(-7, 7), random.randint(-7, 7))
    while v2 == (0,0): v2 = (random.randint(-7, 7), random.randint(-7, 7))
    
    dot_prod = dot_product_coords(v1, v2)
    
    question_text = (
        f"已知 $\\vec{{a}}=({v1[0]},{v1[1]}), "
        f"\\vec{{b}}=({v2[0]},{v2[1]})$。"
        f"求 $\\vec{{a}} \\cdot \\vec{{b}}$ 的值。"
    )
    correct_answer = str(dot_prod)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_angle_from_coords_problem():
    """
    題目: 已知 $\vec{a}=(7,1), \vec{b}=(3,4)$。求 $\vec{a}$ 與 $\vec{b}$ 的夾角。
    """
    attempts = 0
    max_attempts = 100 
    while attempts < max_attempts:
        v1_base = (random.randint(-3, 3), random.randint(-3, 3))
        v2_base = (random.randint(-3, 3), random.randint(-3, 3))
        
        if v1_base == (0,0) or v2_base == (0,0):
            attempts += 1
            continue
        
        scale1 = random.randint(1, 2)
        scale2 = random.randint(1, 2)
        v1 = (v1_base[0] * scale1, v1_base[1] * scale1)
        v2 = (v2_base[0] * scale2, v2_base[1] * scale2)
        
        dp = dot_product_coords(v1, v2)
        mag1 = vector_magnitude(v1)
        mag2 = vector_magnitude(v2)
        
        if mag1 == 0 or mag2 == 0:
            attempts += 1
            continue
            
        cos_theta = dp / (mag1 * mag2)
        angle_deg = get_angle_from_cosine(cos_theta)
        
        if angle_deg is not None:
            question_text = (
                f"已知 $\\vec{{a}}=({v1[0]},{v1[1]}), "
                f"\\vec{{b}}=({v2[0]},{v2[1]})$。"
                f"求 $\\vec{{a}}$ 與 $\\vec{{b}}$ 的夾角。"
            )
            correct_answer = str(angle_deg) + "°"
            return {
                "question_text": question_text,
                "answer": correct_answer,
                "correct_answer": correct_answer
            }
        attempts += 1
        
    return generate_dot_product_coords_problem() 


def generate_triangle_dot_product_problem():
    """
    題目: 已知△ABC的三邊長為 $\\overline{AB}=5, \\overline{BC}=6, \\overline{CA}=7$，求下列各值：
    (1) $\vec{AB} \\cdot \vec{AC}$。
    """
    attempts = 0
    max_attempts = 100
    while attempts < max_attempts:
        s_ab = random.randint(4, 10) 
        s_bc = random.randint(4, 10) 
        s_ca = random.randint(4, 10) 
        
        if not (s_ab + s_bc > s_ca and s_ab + s_ca > s_bc and s_bc + s_ca > s_ab):
            attempts += 1
            continue
        
        s_half = (s_ab + s_bc + s_ca) / 2
        area_sq = s_half * (s_half - s_ab) * (s_half - s_bc) * (s_half - s_ca)
        if area_sq <= 0: 
            attempts += 1
            continue

        choice = random.choice([
            ('AB', 'AC', s_ab, s_ca, s_bc, 'A'), 
            ('BA', 'BC', s_ab, s_bc, s_ca, 'B'), 
            ('CA', 'CB', s_ca, s_bc, s_ab, 'C')  
        ])
        
        v1_name, v2_name, mag1, mag2, opposite_side, vertex_angle_label = choice
        
        numerator = mag1**2 + mag2**2 - opposite_side**2
        
        if numerator % 2 != 0: # Ensure integer result
            attempts += 1
            continue
        
        dot_product_val = numerator // 2
        
        question_text = (
            f"已知$\\triangle ABC$的三邊長為 "
            f"$\\overline{{AB}}={s_ab}$, $\\overline{{BC}}={s_bc}$, $\\overline{{CA}}={s_ca}$。"
            f"求 $\\vec{{{v1_name}}} \\cdot \\vec{{{v2_name}}}$ 的值。"
        )
        correct_answer = str(dot_product_val)
        
        return {
            "question_text": question_text,
            "answer": correct_answer,
            "correct_answer": correct_answer
        }
    
    return generate_dot_product_coords_problem()


def generate_dot_product_properties_problem():
    """
    題目: 已知 $|\vec{a}|=2, |\vec{b}|=3$，且 $\vec{a}$ 與 $\vec{b}$ 的夾角為60°，求下列各值：
    (1) $(3\vec{a}+\vec{b}) \\cdot (\vec{a}-2\vec{b})$。
    (2) $|3\vec{a}-2\vec{b}|$。
    """
    mag_a = random.randint(2, 5)
    mag_b = random.randint(2, 5)
    
    # Only use angles that result in rational cosines for simpler calculations and answers
    angle_deg = random.choice(RATIONAL_COSINE_ANGLES) 
    
    cos_theta = COSINE_CALC_VALUES[angle_deg]
    a_dot_b = mag_a * mag_b * cos_theta

    c1, c2 = random.randint(-3, 3), random.randint(-3, 3)
    c3, c4 = random.randint(-3, 3), random.randint(-3, 3)
    
    while c1 == 0 and c2 == 0: c1, c2 = random.randint(-3, 3), random.randint(-3, 3)
    while c3 == 0 and c4 == 0: c3, c4 = random.randint(-3, 3), random.randint(-3, 3)
    
    problem_choice = random.choice(['dot_combo', 'mag_combo'])

    if problem_choice == 'dot_combo':
        result = c1 * c3 * mag_a**2 + (c1 * c4 + c2 * c3) * a_dot_b + c2 * c4 * mag_b**2
        
        def format_vec_term(coeff, vec_char):
            if coeff == 1: return f"\\vec{{{vec_char}}}"
            if coeff == -1: return f"-\\vec{{{vec_char}}}"
            return f"{coeff}\\vec{{{vec_char}}}"
        
        expr1_terms = []
        if c1 != 0: expr1_terms.append(format_vec_term(c1, 'a'))
        if c2 != 0: expr1_terms.append(format_vec_term(c2, 'b'))
        expr1_str = " + ".join(expr1_terms).replace(" + -", " - ")

        expr2_terms = []
        if c3 != 0: expr2_terms.append(format_vec_term(c3, 'a'))
        if c4 != 0: expr2_terms.append(format_vec_term(c4, 'b'))
        expr2_str = " + ".join(expr2_terms).replace(" + -", " - ")

        question_text = (
            f"已知 $|\\vec{{a}}|={mag_a}$, $|\\vec{{b}}|={mag_b}$，"
            f"且 $\\vec{{a}}$ 與 $\\vec{{b}}$ 的夾角為 ${angle_deg}°$，"
            f"求 $({expr1_str}) \\cdot ({expr2_str})$ 的值。"
        )
        
        correct_answer = format_value_for_latex(result)
        
    else: # 'mag_combo'
        attempts = 0
        max_attempts = 100
        while attempts < max_attempts:
            squared_magnitude = c1**2 * mag_a**2 + 2 * c1 * c2 * a_dot_b + c2**2 * mag_b**2
            
            if squared_magnitude < 0: 
                c1, c2 = random.randint(-3, 3), random.randint(-3, 3)
                while c1 == 0 and c2 == 0: c1, c2 = random.randint(-3, 3), random.randint(-3, 3)
                attempts += 1
                continue
            
            magnitude_val = math.sqrt(squared_magnitude)
            
            if magnitude_val.is_integer(): # Ensure integer magnitude for simpler answers
                correct_answer = str(int(magnitude_val))
                break 
            
            attempts += 1
            if attempts == max_attempts: 
                # If cannot find integer, regenerate this problem type
                return generate_dot_product_properties_problem()
            
            c1, c2 = random.randint(-3, 3), random.randint(-3, 3)
            while c1 == 0 and c2 == 0: c1, c2 = random.randint(-3, 3), random.randint(-3, 3)


        def format_vec_term(coeff, vec_char):
            if coeff == 1: return f"\\vec{{{vec_char}}}"
            if coeff == -1: return f"-\\vec{{{vec_char}}}"
            return f"{coeff}\\vec{{{vec_char}}}"
            
        expr_terms = []
        if c1 != 0: expr_terms.append(format_vec_term(c1, 'a'))
        if c2 != 0: expr_terms.append(format_vec_term(c2, 'b'))
        expr_str = " + ".join(expr_terms).replace(" + -", " - ")

        question_text = (
            f"已知 $|\\vec{{a}}|={mag_a}$, $|\\vec{{b}}|={mag_b}$，"
            f"且 $\\vec{{a}}$ 與 $\\vec{{b}}$ 的夾角為 ${angle_deg}°$，"
            f"求 $|{expr_str}|$ 的值。"
        )

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_perpendicular_vectors_problem():
    """
    題目: 設向量 $\vec{a}=(1,-3), \vec{b}=(3,s), \vec{c}=(2,-1)$。
    (1)已知 $\vec{a} \\perp \vec{b}$，求實數s的值。
    (2)已知 $(\vec{a}+t\vec{c}) \perp \vec{c}$，求實數t的值。
    """
    problem_type = random.choice(['simple_perp', 'linear_combo_perp'])
    
    attempts = 0
    max_attempts = 100

    while attempts < max_attempts:
        if problem_type == 'simple_perp':
            v1_x = random.randint(-7, 7)
            v1_y = random.randint(-7, 7)
            while v1_x == 0 and v1_y == 0:
                v1_x = random.randint(-7, 7)
                v1_y = random.randint(-7, 7)

            unknown_coord_idx = random.choice([0, 1])
            
            if unknown_coord_idx == 0: # v2 = (s, v2_y)
                v2_y = random.randint(-7, 7)
                
                if v1_x == 0: 
                    attempts += 1
                    continue
                
                temp_s_numerator = -v1_y * v2_y
                if temp_s_numerator % v1_x != 0: 
                    attempts += 1
                    continue
                s_val = temp_s_numerator // v1_x
                
                v1_coords_str = f"({v1_x},{v1_y})"
                v2_coords_str = f"(s,{v2_y})"
                
            else: # v2 = (v2_x, s)
                v2_x = random.randint(-7, 7)
                
                if v1_y == 0: 
                    attempts += 1
                    continue

                temp_s_numerator = -v1_x * v2_x
                if temp_s_numerator % v1_y != 0: 
                    attempts += 1
                    continue
                s_val = temp_s_numerator // v1_y
                
                v1_coords_str = f"({v1_x},{v1_y})"
                v2_coords_str = f"({v2_x},s)"
                
            question_text = (
                f"設向量 $\\vec{{a}}={v1_coords_str}$, $\\vec{{b}}={v2_coords_str}$。"
                f"已知 $\\vec{{a}} \\perp \\vec{{b}}$，求實數 $s$ 的值。"
            )
            correct_answer = str(s_val)
            return {
                "question_text": question_text,
                "answer": correct_answer,
                "correct_answer": correct_answer
            }

        else: # 'linear_combo_perp' (a + tc) . c = 0
            vec_a_coords = (random.randint(-7, 7), random.randint(-7, 7))
            vec_c_coords = (random.randint(-7, 7), random.randint(-7, 7))
            while vec_c_coords == (0,0): 
                vec_c_coords = (random.randint(-7, 7), random.randint(-7, 7))
                
            dot_a_c = dot_product_coords(vec_a_coords, vec_c_coords)
            mag_c_sq = vec_c_coords[0]**2 + vec_c_coords[1]**2
            
            if mag_c_sq == 0: 
                 attempts += 1
                 continue
                 
            if (-dot_a_c) % mag_c_sq != 0: 
                attempts += 1
                continue
                
            t_val = (-dot_a_c) // mag_c_sq
            
            question_text = (
                f"設向量 $\\vec{{a}}=({vec_a_coords[0]},{vec_a_coords[1]}), "
                f"\\vec{{c}}=({vec_c_coords[0]},{vec_c_coords[1]})$。"
                f"已知 $(\\vec{{a}}+t\\vec{{c}}) \\perp \\vec{{c}}$，求實數 $t$ 的值。"
            )
            correct_answer = str(t_val)
            return {
                "question_text": question_text,
                "answer": correct_answer,
                "correct_answer": correct_answer
            }
        
        attempts += 1
    
    return generate_dot_product_coords_problem() 


def generate(level=1):
    problem_types = []
    if level == 1:
        problem_types = [
            generate_dot_product_geometric_problem,
            generate_dot_product_coords_problem
        ]
    elif level == 2:
        problem_types = [
            generate_angle_from_coords_problem,
            generate_triangle_dot_product_problem
        ]
    else: # level 3 or higher
        problem_types = [
            generate_dot_product_properties_problem,
            generate_perpendicular_vectors_problem
        ]
        
    return random.choice(problem_types)()

def check(user_answer, correct_answer):
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    
    is_correct = False
    feedback_message = ""

    # First, try exact string match (handles LaTeX, degrees, specific formatting)
    if user_answer == correct_answer:
        is_correct = True
    else:
        # Attempt numeric comparison if possible
        try:
            # Handle degree symbol '°' for angle answers
            user_val_str = user_answer
            correct_val_str = correct_answer
            if correct_answer.endswith("°"):
                correct_val_str = correct_answer[:-1].strip()
                user_val_str = user_answer[:-1].strip() if user_answer.endswith("°") else user_answer.strip()

            def parse_latex_fraction_to_float(latex_str):
                # Only handles simple \\frac{{num}}{{den}}
                if r"\\frac" in latex_str:
                    try:
                        parts = latex_str.replace(r"\\frac{{", "").replace("}}{{", "}").replace("}}", "")
                        parts_split = parts.split('}')
                        num_str = parts_split[0]
                        den_str = parts_split[1] if len(parts_split) > 1 else '1' 
                        return float(Fraction(int(num_str), int(den_str)))
                    except Exception:
                        return None 
                return None

            correct_num = None
            user_num = None

            try:
                correct_num = float(correct_val_str)
            except ValueError:
                correct_num = parse_latex_fraction_to_float(correct_val_str)

            try:
                user_num = float(user_val_str)
            except ValueError:
                user_num = parse_latex_fraction_to_float(user_val_str)

            if correct_num is not None and user_num is not None:
                if are_close(user_num, correct_num):
                    is_correct = True
            
        except ValueError:
            pass

    if is_correct:
        feedback_message = f"完全正確！答案是 ${correct_answer}$。"
    else:
        feedback_message = f"答案不正確。正確答案應為：${correct_answer}$"
        
    return {"correct": is_correct, "result": feedback_message, "next_question": True}