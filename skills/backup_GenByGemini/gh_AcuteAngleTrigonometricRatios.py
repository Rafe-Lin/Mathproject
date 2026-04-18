import random
import math
from fractions import Fraction
import re

# --- Helper functions ---
def get_pythagorean_triple():
    """Returns a tuple (opposite_side, adjacent_side, hypotenuse) for an acute angle."""
    triples = [
        (3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25), (20, 21, 29)
    ]
    a, b, c = random.choice(triples)
    # Randomly assign a or b as the 'opposite' side for angle A
    if random.choice([True, False]):
        return a, b, c # A's opp = a, A's adj = b
    else:
        return b, a, c # A's opp = b, A's adj = a

def format_value_latex(value):
    """Formats a numerical value as a LaTeX string for display in the question."""
    if isinstance(value, Fraction):
        if value.denominator == 1:
            return str(value.numerator)
        return r"\\frac{{{}}}{{{}}}".format(value.numerator, value.denominator)
    if isinstance(value, int):
        return str(value)
    
    # Numerical comparison for special values to produce canonical LaTeX forms
    if abs(value - Fraction(1, 2)) < 1e-9: return r"\\frac{{1}}{{2}}"
    if abs(value - (math.sqrt(3) / 2)) < 1e-9: return r"\\frac{{\\sqrt{{3}}}}{{2}}"
    if abs(value - (math.sqrt(2) / 2)) < 1e-9: return r"\\frac{{\\sqrt{{2}}}}{{2}}"
    if abs(value - 1) < 1e-9: return "1"
    if abs(value - math.sqrt(3)) < 1e-9: return r"\\sqrt{{3}}"
    if abs(value - (1 / math.sqrt(3))) < 1e-9: return r"\\frac{{\\sqrt{{3}}}}{{3}}" # Rationalized form for tan 30
                
    return str(value) # Fallback for other numerical values

def format_value_for_check(value):
    """Formats a numerical value as a plain string suitable for parsing by check()."""
    if isinstance(value, Fraction):
        return f"{value.numerator}/{value.denominator}"
    if isinstance(value, int):
        return str(value)
    
    # Numerical comparison for special values to produce canonical string forms for check()
    if abs(value - Fraction(1, 2)) < 1e-9: return "1/2"
    if abs(value - (math.sqrt(3) / 2)) < 1e-9: return "sqrt(3)/2"
    if abs(value - (math.sqrt(2) / 2)) < 1e-9: return "sqrt(2)/2"
    if abs(value - 1) < 1e-9: return "1"
    if abs(value - math.sqrt(3)) < 1e-9: return "sqrt(3)"
    if abs(value - (1 / math.sqrt(3))) < 1e-9: return "sqrt(3)/3"
    
    # For floats (like angles), return rounded string
    if isinstance(value, float):
        return str(round(value, 3)) 
    
    return str(value) # Fallback

# --- Problem Generation Functions ---

def generate_find_one_ratio_from_sides():
    opp_A, adj_A, hyp = get_pythagorean_triple()
    
    ratio_type = random.choice(['sin', 'cos', 'tan'])
    
    numerator, denominator = 0, 0
    if ratio_type == 'sin':
        numerator, denominator = opp_A, hyp
        question_text = f"在直角三角形 $ABC$ 中，已知 $\\angle C = 90^\\circ$ , $AB = {hyp}$ , $AC = {adj_A}$ , $BC = {opp_A}$，求 $\\sin A$ 的值。"
    elif ratio_type == 'cos':
        numerator, denominator = adj_A, hyp
        question_text = f"在直角三角形 $ABC$ 中，已知 $\\angle C = 90^\\circ$ , $AB = {hyp}$ , $AC = {adj_A}$ , $BC = {opp_A}$，求 $\\cos A$ 的值。"
    else: # tan
        numerator, denominator = opp_A, adj_A
        question_text = f"在直角三角形 $ABC$ 中，已知 $\\angle C = 90^\\circ$ , $AB = {hyp}$ , $AC = {adj_A}$ , $BC = {opp_A}$，求 $\\tan A$ 的值。"

    calculated_val = Fraction(numerator, denominator)
    
    return {
        "question_text": question_text,
        "answer": format_value_latex(calculated_val),
        "correct_answer": format_value_for_check(calculated_val)
    }

def generate_find_one_other_ratio():
    opp, adj, hyp = get_pythagorean_triple()
    
    given_ratio_type = random.choice(['sin', 'cos', 'tan'])
    
    target_num, target_den = 0, 0
    given_val = None

    if given_ratio_type == 'sin':
        given_val = Fraction(opp, hyp)
        ask_ratio_type = random.choice(['cos', 'tan'])
        if ask_ratio_type == 'cos':
            target_val = Fraction(adj, hyp)
            question_text = f"已知 $\\angle A$ 為銳角且 $\\sin A = {format_value_latex(given_val)}$，求 $\\cos A$ 的值。"
        else: # ask for tan
            target_val = Fraction(opp, adj)
            question_text = f"已知 $\\angle A$ 為銳角且 $\\sin A = {format_value_latex(given_val)}$，求 $\\tan A$ 的值。"
            
    elif given_ratio_type == 'cos':
        given_val = Fraction(adj, hyp)
        ask_ratio_type = random.choice(['sin', 'tan'])
        if ask_ratio_type == 'sin':
            target_val = Fraction(opp, hyp)
            question_text = f"已知 $\\angle A$ 為銳角且 $\\cos A = {format_value_latex(given_val)}$，求 $\\sin A$ 的值。"
        else: # ask for tan
            target_val = Fraction(opp, adj)
            question_text = f"已知 $\\angle A$ 為銳角且 $\\cos A = {format_value_latex(given_val)}$，求 $\\tan A$ 的值。"
            
    else: # given_ratio_type == 'tan'
        given_val = Fraction(opp, adj)
        hyp_from_tan = int(math.sqrt(opp**2 + adj**2)) 
        ask_ratio_type = random.choice(['sin', 'cos'])
        if ask_ratio_type == 'sin':
            target_val = Fraction(opp, hyp_from_tan)
            question_text = f"已知 $\\angle A$ 為銳角且 $\\tan A = {format_value_latex(given_val)}$，求 $\\sin A$ 的值。"
        else: # ask for cos
            target_val = Fraction(adj, hyp_from_tan)
            question_text = f"已知 $\\angle A$ 為銳角且 $\\tan A = {format_value_latex(given_val)}$，求 $\\cos A$ 的值。"

    return {
        "question_text": question_text,
        "answer": format_value_latex(target_val),
        "correct_answer": format_value_for_check(target_val)
    }

def generate_special_angle_value():
    angle = random.choice([30, 45, 60])
    ratio_type = random.choice(['sin', 'cos', 'tan'])
    
    value = 0
    if angle == 30:
        if ratio_type == 'sin': value = Fraction(1, 2)
        elif ratio_type == 'cos': value = math.sqrt(3) / 2
        else: value = 1 / math.sqrt(3) # Tan 30
    elif angle == 45:
        if ratio_type == 'sin': value = math.sqrt(2) / 2
        elif ratio_type == 'cos': value = math.sqrt(2) / 2
        else: value = 1
    else: # angle == 60
        if ratio_type == 'sin': value = math.sqrt(3) / 2
        elif ratio_type == 'cos': value = Fraction(1, 2)
        else: value = math.sqrt(3) # Tan 60

    return {
        "question_text": f"求 ${ratio_type} {angle}^\\circ$ 的值。",
        "answer": format_value_latex(value),
        "correct_answer": format_value_for_check(value)
    }

def generate_find_angle_from_ratio():
    opp, adj, hyp = get_pythagorean_triple()
    
    ratio_choice = random.choice(['sin', 'cos', 'tan'])
    
    angle_rad = 0
    
    if ratio_choice == 'sin':
        angle_rad = math.asin(opp / hyp)
        question_text = f"在直角三角形 $ABC$ 中，已知 $\\angle C = 90^\\circ$ , $BC = {opp}$ , $AB = {hyp}$，求 $\\angle A$ 的角度。（四捨五入到小數點以下第1位）"
    elif ratio_choice == 'cos':
        angle_rad = math.acos(adj / hyp)
        question_text = f"在直角三角形 $ABC$ 中，已知 $\\angle C = 90^\\circ$ , $AC = {adj}$ , $AB = {hyp}$，求 $\\angle A$ 的角度。（四捨五入到小數點以下第1位）"
    else: # tan
        angle_rad = math.atan(opp / adj)
        question_text = f"在直角三角形 $ABC$ 中，已知 $\\angle C = 90^\\circ$ , $BC = {opp}$ , $AC = {adj}$，求 $\\angle A$ 的角度。（四捨五入到小數點以下第1位）"

    angle_deg_val = round(math.degrees(angle_rad), 1)
    
    return {
        "question_text": question_text,
        "answer": f"${angle_deg_val}^\\circ$",
        "correct_answer": str(angle_deg_val)
    }


def generate(level=1):
    problem_type = random.choice([
        'find_one_ratio_from_sides',
        'find_one_other_ratio',
        'special_angle_value',
        'find_angle_from_ratio'
    ])
    
    if problem_type == 'find_one_ratio_from_sides':
        return generate_find_one_ratio_from_sides()
    elif problem_type == 'find_one_other_ratio':
        return generate_find_one_other_ratio()
    elif problem_type == 'special_angle_value':
        return generate_special_angle_value()
    else: # 'find_angle_from_ratio'
        return generate_find_angle_from_ratio()


def _parse_sqrt_expression(s):
    """Parses a string like 'sqrt(X)', 'sqrt(X)/Y', or 'X/sqrt(Y)' into a float value."""
    s = s.replace(' ', '')
    
    match_frac_sqrt = re.match(r"sqrt\((\d+)\)/(\d+)", s)
    if match_frac_sqrt:
        val = math.sqrt(int(match_frac_sqrt.group(1))) / int(match_frac_sqrt.group(2))
        return val
    
    match_sqrt = re.match(r"sqrt\((\d+)\)", s)
    if match_sqrt:
        return math.sqrt(int(match_sqrt.group(1)))
    
    match_frac_denom_sqrt = re.match(r"(\d+)/sqrt\((\d+)\)", s)
    if match_frac_denom_sqrt:
        val = int(match_frac_denom_sqrt.group(1)) / math.sqrt(int(match_frac_denom_sqrt.group(2)))
        return val
        
    return None # Not a sqrt expression

def check(user_answer, correct_answer):
    user_answer_clean = user_answer.strip().lower().replace(' ', '')
    correct_answer_clean = correct_answer.strip().lower().replace(' ', '')

    is_correct = False
    
    # 1. Try float comparison (for angles or decimal approximations)
    try:
        user_float = float(user_answer_clean)
        correct_float = float(correct_answer_clean)
        # For angles rounded to 0.1, a tolerance of 0.05 is appropriate
        # For other values, 1e-9 for exact float comparison
        tolerance = 0.05 if correct_answer_clean.replace('.', '', 1).isdigit() and '.' in correct_answer_clean else 1e-9
        if abs(user_float - correct_float) < tolerance:
            is_correct = True
    except ValueError:
        pass # Not a float comparison

    if not is_correct:
        # 2. Try Fraction comparison (for simple fractions like "1/2" or "0.5")
        try:
            user_frac = Fraction(user_answer_clean)
            correct_frac = Fraction(correct_answer_clean)
            if user_frac == correct_frac:
                is_correct = True
        except ValueError:
            pass # Not a fraction comparison (or user input wasn't a valid fraction)

    if not is_correct:
        # 3. Try custom sqrt string comparison (e.g., "sqrt(3)/2")
        user_sqrt_val = _parse_sqrt_expression(user_answer_clean)
        correct_sqrt_val = _parse_sqrt_expression(correct_answer_clean)
        
        if user_sqrt_val is not None and correct_sqrt_val is not None:
            if abs(user_sqrt_val - correct_sqrt_val) < 1e-9:
                is_correct = True
        
        # Also check if user entered a decimal approximation for a radical
        if not is_correct and user_sqrt_val is None and correct_sqrt_val is not None:
            try:
                user_float = float(user_answer_clean)
                if abs(user_float - correct_sqrt_val) < 1e-9:
                    is_correct = True
            except ValueError:
                pass


    # 4. Fallback to direct string comparison (for "1" or other exact matches not covered)
    if not is_correct:
        if user_answer_clean == correct_answer_clean:
            is_correct = True
            
    # Generate feedback
    # Note: `answer` field (LaTeX formatted) is not passed to check, so we use correct_answer_clean.
    # We add LaTeX formatting for display in feedback.
    if is_correct:
        # Heuristic to check if the correct answer looks like an angle (e.g., "53.1")
        # and append degree symbol in LaTeX.
        if correct_answer_clean.replace('.', '', 1).isdigit() and '.' in correct_answer_clean:
            result_text = f"完全正確！答案是 ${correct_answer_clean}^\\circ$。"
        else:
            result_text = f"完全正確！答案是 ${correct_answer_clean}$。"
    else:
        if correct_answer_clean.replace('.', '', 1).isdigit() and '.' in correct_answer_clean:
            result_text = f"答案不正確。正確答案應為：${correct_answer_clean}^\\circ$"
        else:
            result_text = f"答案不正確。正確答案應為：${correct_answer_clean}$"
            
    return {"correct": is_correct, "result": result_text, "next_question": True}