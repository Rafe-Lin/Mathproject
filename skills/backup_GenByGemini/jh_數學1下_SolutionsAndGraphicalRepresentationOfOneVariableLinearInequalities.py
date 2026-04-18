import random
from fractions import Fraction
import math

def format_value(val):
    """Helper function to format a value as a string (integer or LaTeX fraction)."""
    if isinstance(val, Fraction):
        if val.denominator == 1:
            return str(val.numerator)
        return f"\\frac{{{val.numerator}}}{{{val.denominator}}}"
    return str(val)

def format_term(coeff, var='x'):
    """Helper function to format linear terms, e.g., 1x -> x, -1x -> -x, 5x."""
    if coeff == 1:
        return var
    if coeff == -1:
        return f"-{var}"
    if coeff == 0:
        return ""
    return f"{coeff}{var}"

def format_inequality_lhs(a, b):
    """Helper function to format an inequality expression ax + b."""
    term_a = format_term(a, 'x')
    if b == 0:
        return term_a
    
    sign = "+" if b > 0 else "-"
    abs_b = abs(b)
    
    return f"{term_a} {sign} {abs_b}"

def generate(level=1):
    """
    生成「一元一次不等式的解與圖示」相關題目。
    包含：
    1. 驗證不等式的解
    2. 解一元一次不等式
    3. 簡單不等式的圖示描述
    4. 複合不等式的圖示描述
    """
    problem_type = random.choice(['verify_solution', 'solve_inequality', 'graph_simple', 'graph_compound'])
    
    if problem_type == 'verify_solution':
        return generate_verify_solution_problem()
    elif problem_type == 'solve_inequality':
        return generate_solve_inequality_problem()
    elif problem_type == 'graph_simple':
        return generate_graph_simple_problem()
    else: # 'graph_compound'
        return generate_graph_compound_problem()

def generate_verify_solution_problem():
    """題型：下列何者為不等式 ax + b < c 的解？"""
    a = random.choice([i for i in range(-5, 6) if i != 0])
    b = random.randint(-10, 10)
    op, op_func = random.choice([
        ('<', lambda x, y: x < y),
        ('>', lambda x, y: x > y),
        ('\\le', lambda x, y: x <= y),
        ('\\ge', lambda x, y: x >= y)
    ])

    boundary = Fraction(random.randint(-15, 15), random.choice([1, 2, 3]))
    c_val = a * boundary + b

    options = {}
    
    # Option 1: The boundary value itself (a good distractor)
    options[format_value(boundary)] = op_func(a * boundary, c_val - b)
    
    # Option 2: A correct solution
    while True:
        delta = Fraction(random.randint(1, 5), random.choice([1, 2]))
        if (op in ['>', '\\ge'] and a > 0) or (op in ['<', '\\le'] and a < 0):
             potential_sol = boundary + delta
        else:
             potential_sol = boundary - delta
        
        if format_value(potential_sol) not in options:
             options[format_value(potential_sol)] = True
             break

    # Option 3: An incorrect solution
    while True:
        delta = Fraction(random.randint(1, 5), random.choice([1, 2]))
        if (op in ['>', '\\ge'] and a > 0) or (op in ['<', '\\le'] and a < 0):
             potential_nonsol = boundary - delta
        else:
             potential_nonsol = boundary + delta
        
        if format_value(potential_nonsol) not in options:
            options[format_value(potential_nonsol)] = False
            break

    option_list = list(options.keys())
    random.shuffle(option_list)
    
    correct_label = ''
    option_str_parts = []
    for i, opt_val_str in enumerate(option_list):
        label = chr(ord('A') + i)
        option_str_parts.append(f"({label}) ${opt_val_str}$")
        if options[opt_val_str] == True:
            correct_label = label
            
    if not correct_label:
        return generate_verify_solution_problem()

    lhs_str = format_inequality_lhs(a, b)
    rhs_str = format_value(c_val)
    
    options_str = "<br>".join(option_str_parts)
    
    question_text = f"下列各選項中，何者為不等式 ${lhs_str} {op} {rhs_str}$ 的解？<br>{options_str}"
    
    return {
        "question_text": question_text,
        "answer": correct_label,
        "correct_answer": correct_label
    }

def generate_solve_inequality_problem():
    """題型：解一元一次不等式"""
    a = random.choice([i for i in range(-6, 7) if i != 0])
    b = random.randint(-20, 20)
    op = random.choice(['<', '>', '\\le', '\\ge'])
    
    boundary = random.randint(-5, 5)
    c = a * boundary + b

    lhs_str = format_inequality_lhs(a, b)
    
    question_text = f"請解一元一次不等式：${lhs_str} {op} {c}$"
    
    final_op = op
    if a < 0:
        op_map = {'<': '>', '>': '<', '\\le': '\\ge', '\\ge': '\\le'}
        final_op = op_map[op]
        
    correct_answer = f"x {final_op} {boundary}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_graph_simple_problem():
    """題型：描述簡單不等式的數線圖示"""
    k = random.randint(-10, 10)
    op = random.choice(['<', '>', '\\le', '\\ge'])
    
    inequality = f"x {op} {k}"
    
    question_text = f"在數線上圖示不等式 ${inequality}$ 的解時，其圖形特徵應為何？"
    
    circle_type = "空心圓圈" if op in ['<', '>'] else "實心圓圈"
    direction = "向左畫線" if op in ['<', '\\le'] else "向右畫線"
    
    correct_answer = f"在數線上標示 ${k}$ 的點為{circle_type}，並{direction}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_graph_compound_problem():
    """題型：描述複合不等式的數線圖示"""
    k1 = random.randint(-10, 5)
    k2 = k1 + random.randint(2, 8)
    
    op1 = random.choice(['<', '\\le'])
    op2 = random.choice(['<', '\\le'])
    
    inequality = f"{k1} {op1} x {op2} {k2}"
    
    question_text = f"在數線上圖示不等式 ${inequality}$ 的解時，其圖形特徵應為何？"
    
    circle1_type = "空心圓圈" if op1 == '<' else "實心圓圈"
    circle2_type = "空心圓圈" if op2 == '<' else "實心圓圈"
    
    correct_answer = f"在數線上標示 ${k1}$ 的點為{circle1_type}，標示 ${k2}$ 的點為{circle2_type}，並在這兩點之間畫線"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }
    
def check(user_answer, correct_answer):
    """檢查答案是否正確。"""
    user_answer = user_answer.strip()
    is_correct = False

    # First, try a simple direct match (for 'A', 'B', 'C' and text answers)
    if user_answer.upper() == correct_answer.upper():
        is_correct = True
    # More lenient check for text answers, ignoring punctuation and spaces
    elif user_answer.replace(" ", "").replace("，", "").replace("。", "") == correct_answer.replace(" ", "").replace("，", "").replace("。", ""):
        is_correct = True
    else:
        # Specialized check for inequality answers like "x > 5"
        import re
        
        ops_group = r"<|>|\\le|\\ge|<=|>=|≤|≥"
        p1 = re.compile(rf"^\s*x\s*({ops_group})\s*(-?\d+(\.\d+)?)\s*$")
        p2 = re.compile(rf"^\s*(-?\d+(\.\d+)?)\s*({ops_group})\s*x\s*$")

        match_user = p1.match(user_answer) or p2.match(user_answer)
        match_correct = p1.match(correct_answer)
        
        if match_user and match_correct:
            op_map = {'<': '<', '>': '>', '\\le': '<=', '<=': '<=', '≤': '<=', '\\ge': '>=', '>=': '>=', '≥': '>='}
            rev_op_map = {'<': '>', '>': '<', '<=': '>=', '>=': '<='}
            
            # Extract and standardize user answer
            if p1.match(user_answer):
                u_op_raw, u_val_str, _ = match_user.groups()
                u_op_std = op_map.get(u_op_raw)
            else: # Reversed order
                u_val_str, _, u_op_raw = match_user.groups()
                u_op_std = op_map.get(u_op_raw)
                if u_op_std in rev_op_map:
                    u_op_std = rev_op_map[u_op_std]
            
            # Extract and standardize correct answer
            c_op_raw, c_val_str, _ = match_correct.groups()
            c_op_std = op_map.get(c_op_raw)

            try:
                u_val = float(u_val_str)
                c_val = float(c_val_str)
                if u_op_std and c_op_std and u_op_std == c_op_std and math.isclose(u_val, c_val):
                    is_correct = True
            except (ValueError, TypeError):
                pass # Parsing failed

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}
