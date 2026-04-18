import math
import random
import re

# Helper class to represent sine values with numerical and LaTeX forms
class SineValue:
    def __init__(self, angle_deg):
        self.angle_deg = angle_deg
        self.value = math.sin(math.radians(angle_deg))
        
        # Check for special angle values and store their LaTeX representation and a simple exact form
        # The exact_form is a simplified string representation used for internal logic
        # and for constructing simple ratio answers.
        if abs(self.value - 0.5) < 1e-9: # 30, 150 degrees
            self.latex_str = r"\\frac{1}{2}"
            self.exact_form = "1/2" 
        elif abs(self.value - math.sqrt(2)/2) < 1e-9: # 45, 135 degrees
            self.latex_str = r"\\frac{\\sqrt{2}}{2}"
            self.exact_form = "sqrt2/2"
        elif abs(self.value - math.sqrt(3)/2) < 1e-9: # 60, 120 degrees
            self.latex_str = r"\\frac{\\sqrt{3}}{2}"
            self.exact_form = "sqrt3/2"
        elif abs(self.value - 1.0) < 1e-9: # 90 degrees
            self.latex_str = r"1"
            self.exact_form = "1"
        else:
            self.latex_str = f"{self.value:.4f}" # For non-special angles, round for display
            self.exact_form = None # No simple exact form

# Helper function to parse user input for numbers, including square roots and fractions
def parse_numeric_input(input_str):
    input_str_normalized = input_str.strip().lower().replace(" ", "")

    # Try to parse as float directly (handles integers too)
    try:
        return float(input_str_normalized)
    except ValueError:
        pass

    # Handle simple fractions like N/M
    match_fraction = re.match(r'^(-?\d+(?:\.\d+)?)/(-?\d+(?:\.\d+)?)$', input_str_normalized)
    if match_fraction:
        numerator = float(match_fraction.group(1))
        denominator = float(match_fraction.group(2))
        if denominator != 0:
            return numerator / denominator
        return float('nan') # Division by zero

    # Handle square root expressions: N*sqrt(M), sqrt(M), N*sqrt{M}, sqrt{M}, N*sqrt[M]
    # This regex is robust for various sqrt notations (parentheses, braces, no symbol between coeff and sqrt)
    match_sqrt = re.match(r'^(?:(\d+(?:\.\d+)?)\*?)?(?:r?|\\)?(?:sqrt)\s*[\(\{](\d+(?:\.\d+)?)[\)\}]$', input_str_normalized)
    if match_sqrt:
        coeff = float(match_sqrt.group(1)) if match_sqrt.group(1) else 1.0
        val = float(match_sqrt.group(2))
        if val >= 0:
            return coeff * math.sqrt(val)
        return float('nan') # Square root of negative number

    # Handle fractions with square roots like sqrt(N)/M or N*sqrt(M)/P
    match_sqrt_fraction = re.match(r'^(?:(\d+(?:\.\d+)?)\*?)?(?:r?|\\)?(?:sqrt)\s*[\(\{](\d+(?:\.\d+)?)[\)\}]/(\d+(?:\.\d+)?)$', input_str_normalized)
    if match_sqrt_fraction:
        coeff = float(match_sqrt_fraction.group(1)) if match_sqrt_fraction.group(1) else 1.0
        numerator_val = float(match_sqrt_fraction.group(2))
        denominator = float(match_sqrt_fraction.group(3))
        if numerator_val >=0 and denominator != 0:
            return coeff * math.sqrt(numerator_val) / denominator
        return float('nan')

    return None # Unable to parse as numeric

# --- Problem Generation Functions ---

def generate_find_side_problem():
    problem_pattern = random.choice([1, 2, 3]) # 1: integer/simple_sqrt ans, 2: a is sqrt, ans is simple, 3: float ans
    
    a_val_int = random.randint(1, 10) # Base integer for side 'a'
    
    if problem_pattern == 1:
        # Combinations chosen to produce integer or simple sqrt answers for side 'b'
        choices = [
            (30, 60, a_val_int), # b = a*sqrt(3)
            (30, 90, a_val_int), # b = 2a
            (45, 90, a_val_int), # b = a*sqrt(2)
            (60, 90, a_val_int * 3), # b = a*2*sqrt(3)/3. Choose a as multiple of 3 to make it integer coeff for sqrt(3).
            (30, 45, a_val_int), # b = a*sqrt(2)
        ]
        A_deg, B_deg, a_val = random.choice(choices)
        
        sinA = SineValue(A_deg)
        sinB = SineValue(B_deg)
        b_val_float = a_val * sinB.value / sinA.value

        if A_deg == 60 and B_deg == 90: 
            answer_latex = f"{a_val // 3 * 2}{r'\\sqrt{3}'}" # a_val was 3k, b is 2k*sqrt(3)
            correct_answer = f"{a_val // 3 * 2 * math.sqrt(3):.2f}"
            a_display = f"{a_val}"
        elif A_deg == 30 and B_deg == 60: 
            answer_latex = f"{a_val}{r'\\sqrt{3}'}"
            correct_answer = f"{a_val * math.sqrt(3):.2f}"
            a_display = f"{a_val}"
        elif A_deg == 30 and B_deg == 90: 
            answer_latex = f"{2*a_val}"
            correct_answer = f"{2*a_val:.2f}"
            a_display = f"{a_val}"
        elif A_deg == 45 and B_deg == 90: 
            answer_latex = f"{a_val}{r'\\sqrt{2}'}"
            correct_answer = f"{a_val * math.sqrt(2):.2f}"
            a_display = f"{a_val}"
        elif A_deg == 30 and B_deg == 45: 
            answer_latex = f"{a_val}{r'\\sqrt{2}'}"
            correct_answer = f"{a_val * math.sqrt(2):.2f}"
            a_display = f"{a_val}"
        else: # Fallback to float (should not be reached by design)
            correct_answer = f"{b_val_float:.2f}"
            answer_latex = correct_answer
            a_display = f"{a_val}"

    elif problem_pattern == 2:
        # 'a' involves sqrt to make 'b' a simple integer or simple sqrt
        choices = [
            (45, 60, r"\\sqrt{2}", math.sqrt(2), r"\\sqrt{3}", math.sqrt(3)), # A=45, a=sqrt(2) => B=60, b=sqrt(3)
            (30, 45, r"\\sqrt{2}", math.sqrt(2), r"2", 2.0), # A=30, a=sqrt(2) => B=45, b=2
            (30, 60, r"\\sqrt{3}", math.sqrt(3), r"3", 3.0), # A=30, a=sqrt(3) => B=60, b=3
        ]
        A_deg, B_deg, a_display, a_num, b_latex, b_num = random.choice(choices)
        
        answer_latex = b_latex
        correct_answer = f"{b_num:.2f}" # Numerical answer for checking

    else: # Default to float answers, requiring rounding
        A_deg = random.choice([20, 25, 35, 50, 70, 80]) 
        B_deg = random.choice([20, 25, 35, 50, 70, 80])
        while A_deg + B_deg >= 180 or A_deg == B_deg: # Ensure valid triangle and distinct angles
            A_deg = random.choice([20, 25, 35, 50, 70, 80])
            B_deg = random.choice([20, 25, 35, 50, 70, 80])

        a_val = random.randint(5, 20)
        a_display = str(a_val)
        
        sinA = SineValue(A_deg)
        sinB = SineValue(B_deg)
        b_val_float = a_val * sinB.value / sinA.value
        
        correct_answer = f"{b_val_float:.1f}" # Round to 1 decimal place
        answer_latex = correct_answer

    question_text = (
        f"在 ${{r'\\triangle ABC'}}$ 中，已知 ${{r'\\angle A'}} = {A_deg}{{r'\\circ'}}$，"
        f"${{r'\\angle B'}} = {B_deg}{{r'\\circ'}}$，邊長 $a = {a_display}$，"
        f"請求出邊長 $b$ 的長度。({r'請將答案四捨五入到小數點以下第1位，或填寫精確根式'})"
    )

    return {
        "question_text": question_text,
        "answer": answer_latex, # Displayed answer, could be surd or float
        "correct_answer": correct_answer # Numerical answer for robust checking
    }

def generate_find_angle_problem():
    
    if random.random() < 0.7: # Mostly Scenario 1: Exact angle B (special angles)
        problem_set = [
            {"A": 45, "a_disp": r"\\sqrt{2}", "a_num": math.sqrt(2), "b_disp": r"\\sqrt{3}", "b_num": math.sqrt(3), "ans_B": 60, "note": r""},
            {"A": 30, "a_disp": r"1", "a_num": 1, "b_disp": r"\\sqrt{2}", "b_num": math.sqrt(2), "ans_B": 45, "note": r"(請取銳角)"},
            {"A": 30, "a_disp": r"1", "a_num": 1, "b_disp": r"\\sqrt{2}", "b_num": math.sqrt(2), "ans_B": 135, "note": r"(請取鈍角)"},
            {"A": 30, "a_disp": r"1", "a_num": 1, "b_disp": r"2", "b_num": 2, "ans_B": 90, "note": r""},
            {"A": 60, "a_disp": r"\\sqrt{3}", "a_num": math.sqrt(3), "b_disp": r"1", "b_num": 1, "ans_B": 30, "note": r""},
            {"A": 30, "a_disp": r"3", "a_num": 3, "b_disp": r"3\\sqrt{3}", "b_num": 3*math.sqrt(3), "ans_B": 60, "note": r"(請取銳角)"},
            {"A": 30, "a_disp": r"3", "a_num": 3, "b_disp": r"3\\sqrt{3}", "b_num": 3*math.sqrt(3), "ans_B": 120, "note": r"(請取鈍角)"},
        ]
        
        problem_choice = random.choice(problem_set)
        
        A_deg = problem_choice["A"]
        a_disp = problem_choice["a_disp"]
        b_disp = problem_choice["b_disp"]
        correct_B_deg = problem_choice["ans_B"]
        angle_note = problem_choice["note"]
        
        question_text = (
            f"在 ${{r'\\triangle ABC'}}$ 中，已知 ${{r'\\angle A'}} = {A_deg}{{r'\\circ'}}$，"
            f"邊長 $a = {a_disp}$，邊長 $b = {b_disp}$，"
            f"請求出 ${{r'\\angle B'}}$ 的角度。{angle_note}"
        )
        answer_latex = str(correct_B_deg)
        correct_answer = str(correct_B_deg) # For exact integer angle
        
    else: # Scenario 2: Numerical angle B, requiring rounding and handling ambiguous case
        A_deg = random.choice([20, 30, 40, 50, 60, 70, 80])
        a_val = random.randint(5, 15)
        b_val = random.randint(5, 15)
        
        # Ensure a solution exists: a >= b * sinA
        min_a_for_sol = b_val * math.sin(math.radians(A_deg))
        if a_val < min_a_for_sol:
            # Adjust `a_val` to ensure a solution
            a_val = math.ceil(min_a_for_sol * random.uniform(1.05, 1.2)) # Add buffer for floating point stability
            
        sinA_num = math.sin(math.radians(A_deg))
        sinB_calc = b_val * sinA_num / a_val
        
        sinB_calc = min(1.0, max(-1.0, sinB_calc)) # Clamp to [-1, 1] for asin safety
        
        B1_rad = math.asin(sinB_calc)
        B1_deg = math.degrees(B1_rad)
        
        B2_deg = 180 - B1_deg
        
        valid_solutions = []
        # Check if B1 and B2 form a valid triangle (A+B < 180)
        if A_deg + B1_deg < 180 - 0.1: # Small margin for float comparison
            valid_solutions.append(B1_deg)
        if A_deg + B2_deg < 180 - 0.1 and abs(B1_deg - B2_deg) > 0.1: # Also ensure B1 != B2
            valid_solutions.append(B2_deg)
            
        if not valid_solutions: # If no valid triangle formed, regenerate
            return generate_find_angle_problem() 
        
        if len(valid_solutions) == 1: # Unique solution
            correct_B_deg = valid_solutions[0]
            angle_note = r"(四捨五入到小數點以下第1位)"
        else: # Two solutions (ambiguous case)
            if random.random() < 0.5: # Randomly ask for acute or obtuse
                correct_B_deg = min(valid_solutions) # Take the smaller (acute) angle
                angle_note = r"(請取銳角，四捨五入到小數點以下第1位)"
            else:
                correct_B_deg = max(valid_solutions) # Take the larger (obtuse) angle
                angle_note = r"(請取鈍角，四捨五入到小數點以下第1位)"

        question_text = (
            f"在 ${{r'\\triangle ABC'}}$ 中，已知 ${{r'\\angle A'}} = {A_deg}{{r'\\circ'}}$，"
            f"邊長 $a = {a_val}$，邊長 $b = {b_val}$，"
            f"請求出 ${{r'\\angle B'}}$ 的角度。{angle_note}"
        )
        correct_answer = f"{correct_B_deg:.1f}"
        answer_latex = correct_answer # Display as rounded float.

    return {
        "question_text": question_text,
        "answer": answer_latex,
        "correct_answer": correct_answer
    }

def generate_circumradius_problem():
    # Find R given A and a: a/sinA = 2R => R = a / (2*sinA)
    
    A_deg = random.choice([30, 45, 60, 90, 120, 150])
    sinA_obj = SineValue(A_deg)
    
    a_val_int = random.randint(3, 10) # Base integer for side 'a'
    
    # Select `a` based on A_deg to get a simple R
    if A_deg == 30 or A_deg == 150: # R = a
        a_val = a_val_int
        a_display = str(a_val_int)
        R_latex = str(a_val_int)
        R_num = float(a_val_int)
    elif A_deg == 45: # R = a*sqrt(2)/2. Choose a as `2k` to make R = k*sqrt(2)
        a_val = a_val_int * 2
        a_display = str(a_val)
        R_latex = f"{a_val_int}{r'\\sqrt{2}'}"
        R_num = a_val_int * math.sqrt(2)
    elif A_deg == 60 or A_deg == 120: # R = a*sqrt(3)/3. Choose a as `3k` to make R = k*sqrt(3)
        a_val = a_val_int * 3
        a_display = str(a_val)
        R_latex = f"{a_val_int}{r'\\sqrt{3}'}"
        R_num = a_val_int * math.sqrt(3)
    elif A_deg == 90: # R = a/2. Choose a as `2k` to make R = k
        a_val = a_val_int * 2
        a_display = str(a_val)
        R_latex = str(a_val_int)
        R_num = float(a_val_int)
    else: # Fallback (should not be reached with current A_deg choices)
        a_val = random.randint(5, 20)
        a_display = str(a_val)
        sinA_obj = SineValue(A_deg) # Re-calculate if angle was not a special one
        R_num = a_val / (2 * sinA_obj.value)
        R_latex = f"{R_num:.1f}" # Round to 1 decimal place
    
    question_text = (
        f"在 ${{r'\\triangle ABC'}}$ 中，已知 ${{r'\\angle A'}} = {A_deg}{{r'\\circ'}}$，"
        f"邊長 $a = {a_display}$，"
        f"請求出 ${{r'\\triangle ABC'}}$ 的外接圓半徑 $R$。"
        f"({r'請將答案四捨五入到小數點以下第1位，或填寫精確根式'})"
    )
    
    correct_answer = f"{R_num:.1f}" # Numerical answer for robust checking
    
    return {
        "question_text": question_text,
        "answer": R_latex, # Displayed answer, could be surd or float
        "correct_answer": correct_answer # Numerical answer for robust checking
    }

def generate_angle_ratio_to_side_ratio_problem():
    # Given A:B:C = x:y:z, find a:b:c, where a:b:c = sinA:sinB:sinC
    
    ratio_options = [
        (1, 1, 4), # -> 30,30,120 -> sin30:sin30:sin120 = 1/2:1/2:sqrt(3)/2 -> 1:1:sqrt(3)
        (1, 2, 3), # -> 30,60,90 -> sin30:sin60:sin90 = 1/2:sqrt(3)/2:1 -> 1:sqrt(3):2
        (1, 3, 2), # -> 30,90,60 -> sin30:sin90:sin60 = 1/2:1:sqrt(3)/2 -> 1:2:sqrt(3)
        (1, 4, 1), # -> 30,120,30 -> sin30:sin120:sin30 = 1/2:sqrt(3)/2:1/2 -> 1:sqrt(3):1
        (2, 1, 3), # -> 60,30,90 -> sin60:sin30:sin90 = sqrt(3)/2:1/2:1 -> sqrt(3):1:2
        (3, 1, 2), # -> 90,30,60 -> sin90:sin30:sin60 = 1:1/2:sqrt(3)/2 -> 2:1:sqrt(3)
    ]
    
    x, y, z = random.choice(ratio_options)
    total_ratio = x + y + z
    
    A_deg = int((x / total_ratio) * 180)
    B_deg = int((y / total_ratio) * 180)
    C_deg = int((z / total_ratio) * 180)
    
    sinA_obj = SineValue(A_deg)
    sinB_obj = SineValue(B_deg)
    sinC_obj = SineValue(C_deg)
    
    # Map internal `exact_form` to display LaTeX string for simplified ratio
    ratio_map = {
        "1/2": "1",
        "sqrt2/2": r"\\sqrt{2}", # Not used in these specific ratios, but good to keep
        "sqrt3/2": r"\\sqrt{3}",
        "1": "2" # If we multiply all by 2 to get integer/surd ratio
    }
    
    result_ratio_parts = []
    for angle_obj in [sinA_obj, sinB_obj, sinC_obj]:
        result_ratio_parts.append(ratio_map.get(angle_obj.exact_form, angle_obj.latex_str))
    
    ans_latex = f"{result_ratio_parts[0]} : {result_ratio_parts[1]} : {result_ratio_parts[2]}"
    
    question_text = (
        f"在 ${{r'\\triangle ABC'}}$ 中，已知 ${{r'\\angle A'}}:{{r'\\angle B'}}:{{r'\\angle C'}} = {x}:{y}:{z}$，"
        f"請求出邊長比 $a:b:c$。"
        f"({r'請用最簡整數比或最簡根式比表示'})"
    )
    
    correct_answer = ans_latex.replace(" ", "").replace("\\", "") # Remove spaces and backslashes for checking
    
    return {
        "question_text": question_text,
        "answer": ans_latex, # Displayed answer
        "correct_answer": correct_answer # Normalized string for checking
    }

def generate_true_false_problem():
    # Problems asking to judge a statement as True or False
    
    problem_type = random.choice([1, 2])
    
    if problem_type == 1: # Angle ratio to side ratio (Statement is generally False)
        # Choose ratios where A:B:C != a:b:c
        x, y, z = random.choice([(1,2,3), (2,3,4), (1,4,1)]) 
        
        total_ratio = x + y + z
        A_deg = int((x / total_ratio) * 180)
        B_deg = int((y / total_ratio) * 180)
        C_deg = int((z / total_ratio) * 180)
        
        # For the chosen `ratio_options`, `a:b:c` is never `x:y:z`.
        # E.g., for (1,2,3) -> angles (30,60,90) -> sides (1,sqrt(3),2), which is not (1,2,3).
        # E.g., for (2,3,4) -> angles (40,60,80) -> sides (sin40,sin60,sin80), which is not (2,3,4).
        is_statement_true = False 
        
        question_text = (
            f"在 ${{r'\\triangle ABC'}}$ 中，若 $a, b, c$ 分別表示三內角 ${{r'\\angle A'}}, {{r'\\angle B'}}, {{r'\\angle C'}}$ 的對邊長，"
            f"判斷下列敘述是否正確：「當 ${{r'\\angle A'}}:{{r'\\angle B'}}:{{r'\\angle C'}} = {x}:{y}:{z}$ 時，$a:b:c = {x}:{y}:{z}$。」"
            f"({r'請填寫 O 或 X'})"
        )
        correct_answer_tf = "O" if is_statement_true else "X"
        
    else: # Problem Type 2: Relation between R, a, A (Can be True or False)
        is_statement_true = random.choice([True, False])
        
        R_val = random.randint(3, 10)
        A_deg_options = [30, 45, 60, 90, 150]
        A_deg = random.choice(A_deg_options)
        
        sinA_val = math.sin(math.radians(A_deg))
        calculated_a = 2 * R_val * sinA_val
        
        if is_statement_true:
            a_to_display = calculated_a
            
            # Format 'a' nicely if it's an integer or simple surd
            if abs(a_to_display - int(a_to_display)) < 1e-9:
                a_display = str(int(a_to_display))
            elif A_deg == 45: # a = R*sqrt(2)
                a_display = f"{R_val}{r'\\sqrt{2}'}"
            elif A_deg == 60: # a = R*sqrt(3)
                a_display = f"{R_val}{r'\\sqrt{3}'}"
            else: # Fallback for other special angles like 150 if calculated 'a' is float
                a_display = f"{a_to_display:.1f}"
            
            correct_answer_tf = "O"
        else: # False case: make 'a' slightly off from the correct value
            a_false_val = calculated_a + random.choice([-1, 1]) * random.uniform(0.5, 2)
            if abs(a_false_val - int(a_false_val)) < 1e-9:
                a_display = str(int(a_false_val))
            else:
                a_display = f"{a_false_val:.1f}"
            correct_answer_tf = "X"

        question_text = (
            f"在 ${{r'\\triangle ABC'}}$ 中，若 $a, b, c$ 分別表示三內角 ${{r'\\angle A'}}, {{r'\\angle B'}}, {{r'\\angle C'}}$ 的對邊長，"
            f"判斷下列敘述是否正確：「當 ${{r'\\triangle ABC'}}$ 的外接圓半徑為 ${R_val}$，"
            f"${{r'\\angle A'}} = {A_deg}{{r'\\circ'}}$ 時，$a = {a_display}$。」"
            f"({r'請填寫 O 或 X'})"
        )
        
    correct_answer = correct_answer_tf # 'O' or 'X'
    answer_latex = correct_answer_tf
    
    return {
        "question_text": question_text,
        "answer": answer_latex,
        "correct_answer": correct_answer
    }

# --- Main Generator Function ---
def generate(level=1):
    problem_type = random.choice([
        'find_side', 
        'find_angle', 
        'find_circumradius', 
        'angle_ratio_to_side_ratio',
        'true_false'
    ])
    
    if problem_type == 'find_side':
        return generate_find_side_problem()
    elif problem_type == 'find_angle':
        return generate_find_angle_problem()
    elif problem_type == 'find_circumradius':
        return generate_circumradius_problem()
    elif problem_type == 'angle_ratio_to_side_ratio':
        return generate_angle_ratio_to_side_ratio_problem()
    elif problem_type == 'true_false':
        return generate_true_false_problem()
    else: # Fallback in case of unexpected problem_type
        return generate_find_side_problem()

# --- Answer Checker Function ---
def check(user_answer, correct_answer):
    user_answer = user_answer.strip().lower()
    correct_answer = correct_answer.strip().lower()
    
    is_correct = False
    tolerance = 0.11 # For 1 decimal place rounding (e.g., 1.7 vs 1.73 is acceptable)

    # Case 1: 'O' or 'X' answers
    if correct_answer in ['o', 'x']:
        is_correct = (user_answer == correct_answer)
    # Case 2: Ratio answers (e.g., "1:sqrt{3}:2")
    elif ':' in correct_answer:
        # Normalize by removing spaces and backslashes for comparison (user might type 'sqrt{3}' or '\\sqrt{3}')
        normalized_user = user_answer.replace(" ", "").replace("\\", "")
        normalized_correct = correct_answer.replace(" ", "").replace("\\", "")
        is_correct = (normalized_user == normalized_correct)
    # Case 3: Numeric answers (could be float, int, or surd form)
    else:
        user_num = parse_numeric_input(user_answer)
        correct_num = parse_numeric_input(correct_answer)
        
        if user_num is not None and correct_num is not None:
            # Compare with tolerance for floating-point answers
            is_correct = abs(user_num - correct_num) < tolerance
            
            # Additional check for exact integer comparison if both are effectively integers
            if not is_correct and correct_num == int(correct_num) and user_num == int(user_num):
                is_correct = (int(user_num) == int(correct_num))
            
    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}