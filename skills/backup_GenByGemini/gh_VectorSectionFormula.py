import random
from fractions import Fraction
import re

# Helper class for representing points/vectors in 2D space
class Point:
    def __init__(self, x, y=None):
        self.x = Fraction(x)
        self.y = Fraction(y) if y is not None else None

    def __str__(self):
        if self.y is not None:
            return f"({self.x}, {self.y})"
        return f"({self.x})"
    
    def __add__(self, other):
        if self.y is not None and other.y is not None:
            return Point(self.x + other.x, self.y + other.y)
        # Assuming 1D if y is None for both, or error if mixed
        if self.y is None and other.y is None:
            return Point(self.x + other.x)
        raise TypeError("Cannot add 1D and 2D points")

    def __sub__(self, other):
        if self.y is not None and other.y is not None:
            return Point(self.x - other.x, self.y - other.y)
        if self.y is None and other.y is None:
            return Point(self.x - other.x)
        raise TypeError("Cannot subtract 1D and 2D points")

    def __mul__(self, scalar):
        scalar = Fraction(scalar)
        if self.y is not None:
            return Point(self.x * scalar, self.y * scalar)
        return Point(self.x * scalar)

    def __truediv__(self, scalar):
        scalar = Fraction(scalar)
        if scalar == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        if self.y is not None:
            return Point(self.x / scalar, self.y / scalar)
        return Point(self.x / scalar)
    
    def __rmul__(self, scalar): # For scalar * Point
        return self.__mul__(scalar)

    def to_latex(self):
        # Helper to convert fractions to LaTeX format
        def frac_to_latex(f):
            if f.denominator == 1:
                return str(f.numerator)
            return r"\\frac{{{}}}{{{}}}".format(f.numerator, f.denominator)

        if self.y is not None:
            return f"({frac_to_latex(self.x)}, {frac_to_latex(self.y)})"
        return f"{frac_to_latex(self.x)}"

# Helper function to format fractions for display in LaTeX
def format_fraction_for_display(f):
    if f.denominator == 1:
        return str(f.numerator)
    return r"\\frac{{{}}}{{{}}}".format(f.numerator, f.denominator)

# --- Problem Generation Functions ---

def generate_vector_section_internal(level):
    m = random.randint(1, 4)
    n = random.randint(1, 4)
    
    # Ensure m and n are not too simple (e.g., always 1:1) but also not too complex for level 1
    if level == 1:
        # For level 1, ensure ratios are small integers
        m = random.randint(1,3)
        n = random.randint(1,3)
        while m==n: # Avoid always 1:1, 2:2, etc. (unless it's a specific test for midpoint)
            n = random.randint(1,3)
    
    question_text = ""
    correct_x, correct_y = Fraction(0), Fraction(0)

    # Choose between ratio AP:PB or vector relation BP = kAP
    if random.random() < 0.7: # AP:PB = m:n
        question_text = f"在$\\triangle OAB$中，$P$為 $AB$ 邊上一點，且 $AP:PB = {m}:{n}$。<br>已知 $\\vec{{OP}}=x\\vec{{OA}}+y\\vec{{OB}}$，求 $x, y$ 的值。"
        # OP = (nOA + mOB) / (m+n)
        correct_x = Fraction(n, m + n)
        correct_y = Fraction(m, m + n)
    else: # Vector relation, e.g., BP = kAP or AP = kBP
        k_val_num = random.randint(1,3)
        k_val_den = random.randint(1,3)
        while k_val_num == k_val_den: # Avoid k=1 which implies P is midpoint (AP:PB = 1:1)
            k_val_den = random.randint(1,3)

        k_val = Fraction(k_val_num, k_val_den)
        
        if random.random() < 0.5: # BP = kAP
            # This means AP:PB = 1:k_val. So m=1, n=k_val in the formula.
            question_text = f"在$\\triangle OAB$中，$P$為 $AB$ 邊上一點，且 $\\vec{{BP}} = {format_fraction_for_display(k_val)}\\vec{{AP}}$。<br>已知 $\\vec{{OP}}=x\\vec{{OA}}+y\\vec{{OB}}$，求 $x, y$ 的值。"
            correct_x = Fraction(k_val, 1 + k_val)
            correct_y = Fraction(1, 1 + k_val)
        else: # AP = kBP
            # This means AP:PB = k_val:1. So m=k_val, n=1 in the formula.
            question_text = f"在$\\triangle OAB$中，$P$為 $AB$ 邊上一點，且 $\\vec{{AP}} = {format_fraction_for_display(k_val)}\\vec{{BP}}$。<br>已知 $\\vec{{OP}}=x\\vec{{OA}}+y\\vec{{OB}}$，求 $x, y$ 的值。"
            correct_x = Fraction(1, k_val + 1)
            correct_y = Fraction(k_val, k_val + 1)
            
    correct_answer = f"x={format_fraction_for_display(correct_x)}, y={format_fraction_for_display(correct_y)}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_vector_section_external(level):
    m = random.randint(2, 6) # Ensure m > 1 for external division with reasonable ratios
    n = random.randint(1, 5)
    while m == n: # Ensure m and n are different for external division
        n = random.randint(1, 5)
    
    question_text = f"已知 $O, A, B$ 三點不共線，$P$點在直線$AB$上，但$P$點不在線段$AB$上，且 $AP:PB = {m}:{n}$。"
    
    correct_x, correct_y = Fraction(0), Fraction(0)
    
    # Case 1: m > n => A-B-P. B divides AP in ratio (m-n):n.
    #   OP = (-n/(m-n))OA + (m/(m-n))OB
    # Case 2: n > m => P-A-B. A divides PB in ratio m:(n-m).
    #   OP = (n/(n-m))OA + (-m/(n-m))OB

    if m > n: 
        correct_x = Fraction(-n, m - n)
        correct_y = Fraction(m, m - n)
    else: # n > m
        correct_x = Fraction(n, n - m)
        correct_y = Fraction(-m, n - m)
            
    question_text += f"<br>已知 $\\vec{{OP}}=x\\vec{{OA}}+y\\vec{{OB}}$，求 $x, y$ 的值。"
    correct_answer = f"x={format_fraction_for_display(correct_x)}, y={format_fraction_for_display(correct_y)}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_coordinate_section_internal(level):
    x_a = random.randint(-10, 10)
    y_a = random.randint(-10, 10)
    x_b = random.randint(-10, 10)
    y_b = random.randint(-10, 10)
    
    A = Point(x_a, y_a)
    B = Point(x_b, y_b)
    
    m = random.randint(1, 4)
    n = random.randint(1, 4)
    if level == 1:
        m = random.randint(1,3)
        n = random.randint(1,3)
        while m==n:
            n = random.randint(1,3)

    question_text = f"設 $A{A.to_latex()}$, $B{B.to_latex()}$ 為坐標平面上的兩點，$P$為線段$AB$上一點，且 $AP:PB={m}:{n}$。"
    
    # P = (n A + m B) / (m+n)
    P = (n * A + m * B) / (m + n)
            
    question_text += f"<br>求 $P$ 點坐標。"
    correct_answer = P.to_latex()
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_coordinate_section_external(level):
    x_a = random.randint(-10, 10)
    y_a = random.randint(-10, 10)
    x_b = random.randint(-10, 10)
    y_b = random.randint(-10, 10)
    
    A = Point(x_a, y_a)
    B = Point(x_b, y_b)
    
    m = random.randint(2, 6) # Ensure m != n for external
    n = random.randint(1, 5)
    while m == n:
        n = random.randint(1, 5)

    question_text = f"設 $A{A.to_latex()}$, $B{B.to_latex()}$ 為坐標平面上的兩點，$P$為直線$AB$上一點，但$P$點不在線段$AB$上，且 $AP:PB={m}:{n}$。"
    
    P = Point(0,0) # Placeholder, will be overwritten
    # If P divides AB in ratio m:n externally:
    # Case 1: m > n (A-B-P). B divides AP. P = (mB - (m-n)A) / n
    # Case 2: n > m (P-A-B). A divides PB. P = (nA - mB) / (n-m)
    if m > n: 
        P = (m * B - (m - n) * A) / n
    else: # n > m
        P = (n * A - m * B) / (n - m)
            
    question_text += f"<br>求 $P$ 點坐標。"
    correct_answer = P.to_latex()
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_vector_decomposition(level):
    # This problem first finds OP using section formula, then OC, then CP = OP - OC.
    
    # Define P's position on AB (internal or external)
    is_external_for_P = (level >= 2) and (random.random() < 0.4) # Introduce external for higher levels
    
    m_p = random.randint(1, 4)
    n_p = random.randint(1, 4)
    if is_external_for_P:
        while m_p == n_p: 
            n_p = random.randint(1, 4)
    else: # internal
        m_p = random.randint(1,2)
        n_p = random.randint(1,2)
        if m_p == n_p: # If 1:1, make it 1:2 or 2:1 for more variety
            if random.random() < 0.5:
                n_p = 2
            else:
                m_p = 2
        
    op_x, op_y = Fraction(0), Fraction(0)
    op_text_part = ""
    if not is_external_for_P: # P is on AB
        op_text_part = f"$P$為 $AB$ 邊上一點，且 $AP:PB = {m_p}:{n_p}$。"
        op_x = Fraction(n_p, m_p + n_p)
        op_y = Fraction(m_p, m_p + n_p)
    else: # P is not on AB
        op_text_part = f"$P$點在直線$AB$上，但$P$點不在線段$AB$上，且 $AP:PB = {m_p}:{n_p}$。"
        if m_p > n_p: # A-B-P
            op_x = Fraction(-n_p, m_p - n_p)
            op_y = Fraction(m_p, m_p - n_p)
        else: # P-A-B
            op_x = Fraction(n_p, n_p - m_p)
            op_y = Fraction(-m_p, n_p - m_p)
    
    # Define C's position (usually on OA or OB)
    c_on_oa = random.choice([True, False]) # C on OA or OB
    
    oc_num = random.randint(1, 2)
    oc_den = random.randint(1, 2)
    while oc_num == oc_den and oc_num == 1: # Avoid OC=1OA. Make it a midpoint or 1/3, 2/3 etc.
        oc_den = random.randint(1, 2)
    
    oc_vec_mult = Fraction(oc_num, oc_num + oc_den) # OC:CA = num:den => OC is num/(num+den) of OA
    
    oc_x, oc_y = Fraction(0), Fraction(0)
    oc_text_part = ""
    if c_on_oa: # C is on OA
        oc_text_part = f"$C$為 $OA$ 邊上一點，且 $OC:CA = {oc_num}:{oc_den}$。"
        oc_x = oc_vec_mult
        oc_y = Fraction(0)
    else: # C is on OB
        oc_text_part = f"$C$為 $OB$ 邊上一點，且 $OC:CB = {oc_num}:{oc_den}$。"
        oc_x = Fraction(0)
        oc_y = oc_vec_mult
    
    # Calculate CP = OP - OC
    final_r = op_x - oc_x
    final_s = op_y - oc_y
    
    question_text = f"在$\\triangle OAB$中，{op_text_part}<br>{oc_text_part}<br>已知 $\\vec{{CP}} = r\\vec{{OA}}+s\\vec{{OB}}$，求 $r, s$ 的值。"
    correct_answer = f"r={format_fraction_for_display(final_r)}, s={format_fraction_for_display(final_s)}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_triangle_centroid_vector(level):
    # This function generates two types of centroid vector problems based on level
    # Level 1: AG = xAB + yAC (simpler derivation based on median AD)
    # Level 2+: OG = (1/3)(OA+OB+OC) (can be derived from previous)
    
    if level == 1: 
        question_text = f"設 $G$ 是$\\triangle ABC$的重心，$O$為平面上任一點。<br>已知 $\\vec{{AG}} = x\\vec{{AB}}+y\\vec{{AC}}$，求 $x, y$ 的值。"
        # G divides median AD in 2:1 ratio. D is midpoint of BC.
        # AD = (1/2)(AB+AC)
        # AG = (2/3)AD = (2/3)*(1/2)(AB+AC) = (1/3)AB + (1/3)AC
        correct_x = Fraction(1, 3)
        correct_y = Fraction(1, 3)
        correct_answer = f"x={format_fraction_for_display(correct_x)}, y={format_fraction_for_display(correct_y)}"
        
    else: # level >= 2: Ask for OG = (1/3)(OA+OB+OC)
        question_text = f"設 $G$ 是$\\triangle ABC$的重心，$O$為平面上任一點。<br>已知 $\\vec{{OG}} = a\\vec{{OA}}+b\\vec{{OB}}+c\\vec{{OC}}$，求 $a, b, c$ 的值。"
        
        correct_a = Fraction(1, 3)
        correct_b = Fraction(1, 3)
        correct_c = Fraction(1, 3)
        correct_answer = f"a={format_fraction_for_display(correct_a)}, b={format_fraction_for_display(correct_b)}, c={format_fraction_for_display(correct_c)}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_triangle_centroid_coordinate(level):
    x_a = random.randint(-10, 10)
    y_a = random.randint(-10, 10)
    x_b = random.randint(-10, 10)
    y_b = random.randint(-10, 10)
    x_c = random.randint(-10, 10)
    y_c = random.randint(-10, 10)
    
    A = Point(x_a, y_a)
    B = Point(x_b, y_b)
    C = Point(x_c, y_c)
    
    # Centroid G = (A + B + C) / 3
    G_x = (A.x + B.x + C.x) / 3
    G_y = (A.y + B.y + C.y) / 3
    
    G = Point(G_x, G_y)
    
    question_text = f"設 $A{A.to_latex()}$, $B{B.to_latex()}$, $C{C.to_latex()}$ 為坐標平面上的三點。<br>若 $G$ 是$\\triangle ABC$的重心，求 $G$ 點坐標。"
    correct_answer = G.to_latex()
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    problem_types_level1 = [
        'vector_section_internal',
        'coordinate_section_internal',
        'triangle_centroid_vector_ag'
    ]
    
    problem_types_level2_plus = [
        'vector_section_internal',
        'vector_section_external',
        'coordinate_section_internal',
        'coordinate_section_external',
        'vector_decomposition',
        'triangle_centroid_vector_og', 
        'triangle_centroid_coordinate'
    ]

    if level == 1:
        problem_type = random.choice(problem_types_level1)
    else: # level >= 2
        problem_type = random.choice(problem_types_level2_plus)

    if problem_type == 'vector_section_internal':
        return generate_vector_section_internal(level)
    elif problem_type == 'vector_section_external':
        return generate_vector_section_external(level)
    elif problem_type == 'coordinate_section_internal':
        return generate_coordinate_section_internal(level)
    elif problem_type == 'coordinate_section_external':
        return generate_coordinate_section_external(level)
    elif problem_type == 'vector_decomposition':
        return generate_vector_decomposition(level)
    elif problem_type == 'triangle_centroid_vector_ag':
        return generate_triangle_centroid_vector(1) # Force AG type
    elif problem_type == 'triangle_centroid_vector_og':
        return generate_triangle_centroid_vector(2) # Force OG type
    elif problem_type == 'triangle_centroid_coordinate':
        return generate_triangle_centroid_coordinate(level)
    else:
        # Fallback to a basic problem type if problem_type is somehow not in defined lists
        return generate_vector_section_internal(level)


def check(user_answer, correct_answer):
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    
    # Normalize answers: handles "x=1/2, y=1/3" or "(1/2, 1/3)" or single "1/2"
    def normalize_answer(ans_str):
        normalized_parts = {}
        
        # Pattern for coordinate point: (x, y)
        coord_match = re.match(r"\(\s*([^,]+)\s*,\s*([^)]+)\s*\)", ans_str)
        if coord_match:
            try:
                x_val = Fraction(coord_match.group(1))
                y_val = Fraction(coord_match.group(2))
                return {"x_coord": x_val, "y_coord": y_val}
            except ValueError:
                pass
        
        # Pattern for vector components: x=val, y=val, (z=val)
        # Handles single letter variables (a-z) followed by = and a value
        parts = re.findall(r"([a-zA-Z])\s*=\s*([+\-]?\d+(?:/\d+)?(?:\.\d+)?)\s*(?:,|$)", ans_str)
        if parts:
            for var, val_str in parts:
                try:
                    normalized_parts[var.lower()] = Fraction(val_str)
                except ValueError:
                    return None # Cannot parse a value in a part
            return normalized_parts
            
        # Pattern for a single fraction/number (e.g., AG=1/3AB+1/3AC, only asking for x,y so x=1/3,y=1/3)
        # If it's just a single value and no specific format, try to parse as a single number/fraction
        try:
            return {"value": Fraction(ans_str)}
        except ValueError:
            pass # Not a single fraction/number either
            
        return None # Could not parse the answer

    normalized_user = normalize_answer(user_answer)
    normalized_correct = normalize_answer(correct_answer)
    
    is_correct = False
    result_text = ""

    if normalized_user is None:
        result_text = "您的答案格式不正確，請確保使用數字或分數表示，例如：$(1/2, 3/4)$ 或 $x=1/2, y=3/4$。"
    elif normalized_user == normalized_correct:
        is_correct = True
        result_text = f"完全正確！答案是 ${correct_answer}$。"
    else:
        # Provide more specific feedback if structures match but values differ
        if normalized_user.keys() == normalized_correct.keys():
            all_match = True
            feedback_parts = []
            for k in sorted(normalized_correct.keys()): # Sort keys for consistent feedback
                if k in normalized_user and normalized_user[k] == normalized_correct[k]:
                    pass 
                else:
                    all_match = False
                    if k.endswith("_coord"): # For coordinate points
                         feedback_parts.append(f"${k[0]}$ 座標應為 ${format_fraction_for_display(normalized_correct[k])}$")
                    else: # For vector coefficients (x, y, r, s, a, b, c)
                        feedback_parts.append(f"${k}$ 應該是 ${format_fraction_for_display(normalized_correct[k])}$")
            
            if all_match: # This case should ideally be caught by direct equality, but as a safeguard.
                is_correct = True
                result_text = f"完全正確！答案是 ${correct_answer}$。"
            else:
                result_text = "答案不正確。" + " ".join(feedback_parts) + f" 正確答案應為：${correct_answer}$"
        else:
            result_text = f"您的答案格式或變數不符。正確答案應為：${correct_answer}$"
    
    return {"correct": is_correct, "result": result_text, "next_question": True}