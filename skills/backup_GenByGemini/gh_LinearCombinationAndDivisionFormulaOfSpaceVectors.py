import random
from fractions import Fraction
import math

# Helper function to generate a random 3D vector (integer coordinates)
def generate_vector(min_val=-5, max_val=5, non_zero=False):
    x = random.randint(min_val, max_val)
    y = random.randint(min_val, max_val)
    z = random.randint(min_val, max_val)
    if non_zero and x == 0 and y == 0 and z == 0:
        # Regenerate if all components are zero and non_zero is required
        return generate_vector(min_val, max_val, non_zero)
    return (x, y, z)

# Helper function to format a vector for display in LaTeX
def format_vector_latex(v, label=None):
    # Ensure coordinates are integers for display if they are effectively integers (e.g., Fraction(5,1))
    coords_str = []
    for coord in v:
        if isinstance(coord, Fraction) and coord.denominator == 1:
            coords_str.append(str(int(coord)))
        elif isinstance(coord, Fraction):
            coords_str.append(f"\\frac{{{coord.numerator}}}{{{coord.denominator}}}")
        else: # int or float
            coords_str.append(str(coord))
            
    if label:
        return f"${label}({','.join(coords_str)})$"
    else:
        return f"$({','.join(coords_str)})$"

# Helper to check if two vectors are parallel (cross product is zero)
def are_parallel(v1, v2):
    cross_product_x = v1[1]*v2[2] - v1[2]*v2[1]
    cross_product_y = v1[2]*v2[0] - v1[0]*v2[2]
    cross_product_z = v1[0]*v2[1] - v1[1]*v2[0]
    return cross_product_x == 0 and cross_product_y == 0 and cross_product_z == 0

# Helper to format a Fraction for display in plain text (e.g., "1/2" or "3")
def display_fraction_plain(frac):
    if isinstance(frac, (int, float)):
        return str(frac)
    if isinstance(frac, Fraction):
        if frac.denominator == 1:
            return str(frac.numerator)
        return f"{frac.numerator}/{frac.denominator}"
    return str(frac)

# Helper to format a Fraction for display in LaTeX (e.g., "\\frac{1}{2}" or "3")
def display_fraction_latex(frac):
    if isinstance(frac, (int, float)):
        return str(frac)
    if isinstance(frac, Fraction):
        if frac.denominator == 1:
            return str(frac.numerator)
        return f"\\frac{{{frac.numerator}}}{{{frac.denominator}}}"
    return str(frac)

def generate_linear_combination_problem():
    # Problem Type: Find x, y, k (missing coordinate or coefficient)
    # OP = x*OA + y*OB
    
    # O is origin (0,0,0) as per examples
    O = (0, 0, 0)
    
    # Generate A and B such that OA and OB are not parallel
    A = generate_vector(min_val=-5, max_val=5, non_zero=True)
    B = generate_vector(min_val=-5, max_val=5, non_zero=True)
    
    attempts = 0
    while are_parallel(A, B) and attempts < 100:
        B = generate_vector(min_val=-5, max_val=5, non_zero=True)
        attempts += 1
    if attempts == 100: # Fallback if highly unlikely to find non-parallel in small range
        B = generate_vector(min_val=-10, max_val=10, non_zero=True)
        while are_parallel(A,B): # Should almost certainly find one now
            B = generate_vector(min_val=-10, max_val=10, non_zero=True)

    # Generate x and y coefficients as fractions
    x_val = Fraction(random.randint(-3, 3), random.choice([1, 2, 3]))
    y_val = Fraction(random.randint(-3, 3), random.choice([1, 2, 3]))

    # Avoid zero x_val and y_val simultaneously to ensure a non-trivial P
    if x_val == 0 and y_val == 0:
        x_val = Fraction(random.choice([-1,1]), 1) 

    # Calculate P based on x, y, A, B
    Px = x_val * A[0] + y_val * B[0]
    Py = x_val * A[1] + y_val * B[1]
    Pz = x_val * A[2] + y_val * B[2]
    P_calculated = (Px, Py, Pz)
    
    # Determine what to hide: 0: hide x, 1: hide y, 2: hide a coordinate of P (k)
    hide_what = random.randint(0, 2)
    
    question_text_base = (
        r"已知空間中的一點 $P$ 落在 $O{{(0,0,0)}}$, $A{A_vec_str}$, $B{B_vec_str}$ 三點決定的平面上，且 $\vec{{OP}}=x\vec{{OA}}+y\vec{{OB}}$。"
    ).format(A_vec_str=format_vector_latex(A, label="A"), B_vec_str=format_vector_latex(B, label="B"))
    
    correct_answer = "" # This will store the string representation of the answer for the `answer` field

    if hide_what == 0: # Hide x
        P_str = format_vector_latex(P_calculated, label="P")
        question_text = f"{question_text_base} 已知 {P_str}，求 $x$ 的值。"
        correct_answer = display_fraction_plain(x_val)
        
    elif hide_what == 1: # Hide y
        P_str = format_vector_latex(P_calculated, label="P")
        question_text = f"{question_text_base} 已知 {P_str}，求 $y$ 的值。"
        correct_answer = display_fraction_plain(y_val)
        
    else: # Hide a coordinate of P (k)
        missing_coord_idx = random.randint(0, 2)
        P_display_coords_list = list(P_calculated)
        P_display_coords_list[missing_coord_idx] = 'k'
        
        # Format P string with 'k' directly without using format_vector_latex
        P_str_coords = []
        for i, coord in enumerate(P_display_coords_list):
            if i == missing_coord_idx:
                P_str_coords.append('k')
            else:
                P_str_coords.append(display_fraction_latex(coord))
                
        P_str = f"$P({','.join(P_str_coords)})$"
        
        x_val_latex = display_fraction_latex(x_val)
        y_val_latex = display_fraction_latex(y_val)

        question_text = (
            f"{question_text_base} 已知 {P_str}，且 $x={x_val_latex}$, $y={y_val_latex}$，求 $k$ 的值。"
        )
        correct_answer = display_fraction_plain(P_calculated[missing_coord_idx])

    return {
        "question_text": question_text,
        "answer": correct_answer, # The correct numerical value/string
        "correct_answer": correct_answer # Same for this type
    }

def generate_division_formula_problem():
    # Problem Type: Division formula (internal/external)
    # Find a missing point coordinate
    
    A = generate_vector(min_val=-10, max_val=10)
    B = generate_vector(min_val=-10, max_val=10)
    
    # Ensure A and B are distinct
    while A == B:
        B = generate_vector(min_val=-10, max_val=10)

    # Choice for type of division: 0: internal, 1: external A-B-P, 2: external P-A-B
    choice = random.choice([0, 1, 2]) 
    
    P_calculated = (0,0,0) # Placeholder
    ratio_desc = ""

    if choice == 0: # Internal division: P divides AB in ratio m:n (m,n positive)
        m = random.randint(1, 5)
        n = random.randint(1, 5)
        P_calculated = (
            (Fraction(n * A[0] + m * B[0], m + n)),
            (Fraction(n * A[1] + m * B[1], m + n)),
            (Fraction(n * A[2] + m * B[2], m + n))
        )
        ratio_desc = f"將線段 $\\overline{{AB}}$ 以 ${m}:{n}$ 內分"
        
    else: # External division (A-B-P or P-A-B)
        # Use a scaling factor k for vector AP = k * AB
        # k > 1 for A-B-P, k < 0 for P-A-B
        k_val = Fraction(random.choice([-2, -1, 2, 3]), random.choice([1, 2, 3])) # Avoid k=0 (P=A) and k=1 (P=B)
        
        vec_AB = (B[0] - A[0], B[1] - A[1], B[2] - A[2])
        
        P_x = A[0] + k_val * vec_AB[0]
        P_y = A[1] + k_val * vec_AB[1]
        P_z = A[2] + k_val * vec_AB[2]
        P_calculated = (P_x, P_y, P_z)
        
        if k_val > 1: # A-B-P. Ratio AB:BP = 1:(k-1)
            ratio_BP = display_fraction_latex(abs(k_val - 1))
            ratio_desc = f"點 $P$ 在直線 $AB$ 上，且點 $B$ 介於點 $A$ 和點 $P$ 之間，且 $\\overline{{AB}}:\\overline{{BP}} = 1:{ratio_BP}$"
        elif k_val < 0: # P-A-B. Ratio PA:AB = |k|:1
            ratio_PA = display_fraction_latex(abs(k_val))
            ratio_desc = f"點 $P$ 在直線 $AB$ 上，且點 $A$ 介於點 $P$ 和點 $B$ 之間，且 $\\overline{{PA}}:\\overline{{AB}} = {ratio_PA}:1$"

    question_text = (
        f"已知空間中兩點 $A{format_vector_latex(A, include_label=False)}$, $B{format_vector_latex(B, include_label=False)}$。<br>"
        f"若點 $P$ {ratio_desc}，求點 $P$ 的座標。"
    )
    
    # correct_answer_str for display (e.g., in `answer` field)
    correct_answer_str = format_vector_latex(P_calculated, label="") # No label, just (x,y,z)
    
    # Store the actual tuple of Fractions for accurate checking in `check` function
    correct_answer_tuple = tuple(c.limit_denominator(100) for c in P_calculated)
    
    return {
        "question_text": question_text,
        "answer": correct_answer_str, # Formatted string for initial display
        "correct_answer": correct_answer_tuple # Exact tuple for check function
    }

def generate_region_problem_simplified():
    # Simplified region problem: Asking for coordinates of Q or similar specific point.
    # O is origin (0,0,0) as per examples
    O = (0, 0, 0)
    
    A = generate_vector(min_val=-5, max_val=5, non_zero=True)
    B = generate_vector(min_val=-5, max_val=5, non_zero=True)
    
    # Ensure OA and OB are not parallel
    attempts = 0
    while are_parallel(A, B) and attempts < 100:
        B = generate_vector(min_val=-5, max_val=5, non_zero=True)
        attempts += 1
    if attempts == 100:
        B = generate_vector(min_val=-10, max_val=10, non_zero=True)
        while are_parallel(A,B):
            B = generate_vector(min_val=-10, max_val=10, non_zero=True)
            
    # Always ask for P's coordinates when x=1, y=1 (P is Q, the fourth vertex of parallelogram OAQB)
    Px = A[0] + B[0]
    Py = A[1] + B[1]
    Pz = A[2] + B[2]
    P_calculated = (Fraction(Px), Fraction(Py), Fraction(Pz)) # Ensure it's a Fraction tuple
    
    question_text = (
        f"設 $\\vec{{OA}}$ 與 $\\vec{{OB}}$ 為空間中兩個不平行的非零向量，$O{{(0,0,0)}}$, $A{format_vector_latex(A, label='A')}$, $B{format_vector_latex(B, label='B')}$。<br>"
        r"若令 $\vec{{OP}}=x\vec{{OA}}+y\vec{{OB}}$，當 $x=1, y=1$ 時，試求點 $P$ 的座標。"
    )
    
    correct_answer_str = format_vector_latex(P_calculated, label="") # No label, just (x,y,z)
    
    # Store the actual tuple for checking
    correct_answer_tuple = tuple(c.limit_denominator(100) for c in P_calculated)

    return {
        "question_text": question_text,
        "answer": correct_answer_str,
        "correct_answer": correct_answer_tuple
    }


def generate(level=1):
    problem_types = [
        generate_linear_combination_problem,
        generate_division_formula_problem,
        generate_region_problem_simplified
    ]
    
    chosen_problem_generator = random.choice(problem_types)
    return chosen_problem_generator()

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    user_answer: string from user
    correct_answer: can be a string (for single value) or a tuple of Fractions (for vector coords)
    """
    user_answer_stripped = user_answer.strip()
    is_correct = False
    
    if isinstance(correct_answer, tuple): # Vector coordinate answer
        try:
            # Parse user_answer like "(x, y, z)"
            # Remove outer parentheses, handle potential inner parentheses for fractions, split by comma
            cleaned_answer = user_answer_stripped.replace('(', '').replace(')', '')
            # Use regex to split by comma, but not commas inside fractions (e.g. for (1/2, 3/4))
            # Simpler approach for basic input: assume no inner fractions like 1,2,3 for now, user writes 1/2.
            user_coords_str = [coord.strip() for coord in cleaned_answer.split(',')]
            
            if len(user_coords_str) != len(correct_answer):
                raise ValueError("Incorrect number of coordinates.")

            user_coords = tuple(Fraction(coord).limit_denominator(100) for coord in user_coords_str)
            
            if user_coords == correct_answer:
                is_correct = True
                
        except (ValueError, IndexError):
            is_correct = False
            
        formatted_coords = tuple(display_fraction_latex(c) for c in correct_answer)
        if is_correct:
            feedback = f"完全正確！答案是 $({','.join(formatted_coords)})$。"
        else:
            feedback = f"答案不正確。正確答案應為：$({','.join(formatted_coords)})$"

    else: # Single value answer (Fraction or integer, stored as string in correct_answer)
        try:
            user_val = Fraction(user_answer_stripped).limit_denominator(100)
            correct_val = Fraction(correct_answer).limit_denominator(100)
            
            if user_val == correct_val:
                is_correct = True
        except ValueError:
            is_correct = False
            
        if is_correct:
            feedback = f"完全正確！答案是 ${display_fraction_latex(correct_val)}$。"
        else:
            feedback = f"答案不正確。正確答案應為：${display_fraction_latex(correct_val)}$"

    return {"correct": is_correct, "result": feedback, "next_question": True}