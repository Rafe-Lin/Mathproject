import random
from fractions import Fraction
import re

def _format_expression(a, b, var='x'):
    """Formats an expression ax + b into a clean string."""
    expr = ""
    # Handle the 'a' coefficient part
    if a == 1:
        expr += var
    elif a == -1:
        expr += f"-{var}"
    elif a != 0:
        expr += f"{a}{var}"
    
    # Handle the 'b' constant part
    if b != 0:
        if b > 0:
            if expr:  # if 'a' part exists
                expr += f" + {b}"
            else:  # if 'a' is 0
                expr = str(b)
        else:  # b < 0
            if expr:
                expr += f" - {abs(b)}"
            else:
                expr = str(b)
    
    if not expr:
        return "0"
    return expr

def _parse_linear_expr(expr_str):
    """Parses a linear expression string like '2x-5' or '10-x' into coefficients (a, b)."""
    expr_str = expr_str.replace(' ', '').lower()
    if not expr_str:
        return 0, 0
    
    # Prepend '+' to handle expressions starting with a number, e.g., '5-x' -> '+5-x'
    if expr_str[0].isdigit():
        expr_str = '+' + expr_str
        
    terms = re.findall(r'([+-]\d*\.?\d*[xX]|[+-]\d+\.?\d*)', expr_str)
    a, b = 0, 0
    for term in terms:
        if 'x' in term:
            term_val = term.replace('x', '')
            if term_val == '+':
                a += 1
            elif term_val == '-':
                a -= 1
            else:
                a += float(term_val)
        else:
            b += float(term)
    return a, b

def generate(level=1):
    """
    Generates a question about function values.
    Covers:
    1. Calculating the value of a linear or constant function for a given x.
    2. Finding the x-value where two functions have an equal function value.
    3. Determining the equation of a linear function from two points.
    4. Solving a word problem involving a linear function.
    """
    problem_type = random.choice([
        'calc_value', 
        'find_x_equal', 
        'find_function_from_points', 
        'word_problem'
    ])
    
    if problem_type == 'calc_value':
        return generate_calc_value_problem()
    elif problem_type == 'find_x_equal':
        return generate_find_x_equal_problem()
    elif problem_type == 'find_function_from_points':
        return generate_find_function_from_points_problem()
    else: # word_problem
        return generate_word_problem()

def generate_calc_value_problem():
    """
    Generates a problem asking to calculate a function's value.
    e.g., Given y = 2x + 3, what is the value when x = 5?
    """
    if random.random() < 0.3: # 30% chance of constant function
        b = random.randint(-30, 30)
        x_val = random.randint(-20, 20)
        y_val = b
        
        question_text = f"求常數函數 $y = {b}$，在 $x = {x_val}$ 時的函數值。"
        correct_answer = str(y_val)
    else: # 70% chance of linear function
        a = random.choice([i for i in range(-10, 11) if i != 0])
        b = random.randint(-20, 20)
        x_val = random.randint(-10, 10)
        
        y_val = a * x_val + b
        func_str = _format_expression(a, b)
        
        question_text = f"求一次函數 $y = {func_str}$，在 $x = {x_val}$ 時的函數值。"
        correct_answer = str(y_val)
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_find_x_equal_problem():
    """
    Generates a problem asking for the x-value where two functions are equal.
    e.g., At what x=a do y=2x+3 and y=7x-2 have the same value?
    """
    if random.random() < 0.5: # Two linear functions
        x_sol = random.randint(-8, 8)
        a1 = random.choice([i for i in range(-5, 6) if i != 0])
        a2 = random.choice([i for i in range(-5, 6) if i not in [0, a1]])
        b1 = random.randint(-10, 10)
        
        b2 = (a1 - a2) * x_sol + b1
        
        func1_str = _format_expression(a1, b1)
        func2_str = _format_expression(a2, b2)
        
        question_text = f"若一次函數 $y = {func1_str}$ 與一次函數 $y = {func2_str}$ 在 $x=a$ 時的函數值相等，則 $a$ 為多少？"
        correct_answer = str(x_sol)
        
    else: # One linear, one constant
        x_sol = random.randint(-10, 10)
        
        if random.random() < 0.4: # Sub-type with fraction
            den = random.choice([i for i in range(-5, 6) if i not in [0, 1, -1]])
            c = random.randint(-5, 5)
            # We want (x_sol - num) / den = c => num = x_sol - c * den
            num = x_sol - c * den
            
            if num == 0:
                frac_str = f"\\frac{{x}}{{{den}}}"
            else:
                sign = "-" if num > 0 else "+"
                num_abs = abs(num)
                frac_str = f"\\frac{{x {sign} {num_abs}}}{{{den}}}"

            question_text = f"若一次函數 $y={frac_str}$ 與常數函數 $y={c}$ 在 $x=a$ 時的函數值相等，則 $a$ 為多少？"
        else: # Standard linear function
            a = random.choice([i for i in range(-5, 6) if i != 0])
            b = random.randint(-10, 10)
            c = a * x_sol + b # a*x_sol + b = c
            
            func_str = _format_expression(a, b)
            question_text = f"若一次函數 $y = {func_str}$ 與常數函數 $y = {c}$ 在 $x=a$ 時的函數值相等，則 $a$ 為多少？"
            
        correct_answer = str(x_sol)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_find_function_from_points_problem():
    """
    Generates a problem asking to find the function y=ax+b from two points.
    e.g., y=ax+b passes through (2,8) and (4,0). What is the function?
    """
    a = random.choice([i for i in range(-6, 7) if i != 0])
    b = random.randint(-20, 20)
    
    if random.random() < 0.3: # 30% chance one point is y-intercept
        x1 = 0
        x2 = random.choice([i for i in range(-5, 6) if i != 0])
    else:
        x1 = random.randint(-5, 5)
        x2 = random.choice([i for i in range(-5, 6) if i not in [0, x1]])
        
    y1 = a * x1 + b
    y2 = a * x2 + b
    
    if random.random() < 0.5: # Randomize point order
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        
    question_text = f"若一次函數 $y=ax+b$，在 $x={x1}$ 時的函數值是 ${y1}$，在 $x={x2}$ 時的函數值是 ${y2}$，則此一次函數為何？<br>(請以 $y=ax+b$ 的形式作答，例如 $y=2x-3$)"
    
    func_expr = _format_expression(a, b)
    correct_answer = f"y={func_expr.replace(' ', '')}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_word_problem():
    """
    Generates a word problem involving a linear function.
    """
    scenario = random.choice(['temperature', 'phone_plan'])
    
    if scenario == 'temperature':
        initial_temp = random.randint(20, 35)
        rate_per_100m = random.choice([0.5, 0.6, 0.7, 0.8])
        rate_per_m = rate_per_100m / 100
        altitude = random.randint(1000, 4000)
        
        final_temp = initial_temp - rate_per_m * altitude
        rounded_temp = round(final_temp)
        
        question_text = f"高山地區氣溫每上升 100 公尺下降攝氏 ${rate_per_100m}$ 度，若平地氣溫為 ${initial_temp}$ 度，高度為 $x$ 公尺處的氣溫為 $y$ 度。<br>請問在高度為 ${altitude}$ 公尺處，溫度約為多少度？(四捨五入至整數位)"
        correct_answer = str(rounded_temp)
        
    else: # phone_plan
        monthly_fee = random.choice([199, 299, 399, 499, 599])
        call_rate = random.randint(2, 6)
        minutes = random.randint(30, 200)
        
        total_cost = monthly_fee + call_rate * minutes
        
        question_text = f"某電信方案月租費為 ${monthly_fee}$ 元，通話費每分鐘 ${call_rate}$ 元。若某月通話時間為 $x$ 分鐘，總費用為 $y$ 元。<br>請問當月通話 ${minutes}$ 分鐘時，總費用為多少元？"
        correct_answer = str(total_cost)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    Checks if the user's answer is correct, handling numeric and function string answers.
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    is_correct = False

    if correct_answer.lower().startswith('y='):
        # Answer is a function string like y=2x-5. We parse it to allow flexible input.
        try:
            user_expr = user_answer.lower().split('=')[-1]
            correct_expr = correct_answer.lower().split('=')[-1]
            
            user_a, user_b = _parse_linear_expr(user_expr)
            correct_a, correct_b = _parse_linear_expr(correct_expr)
            
            # Compare coefficients, allowing for small floating point differences
            if abs(user_a - correct_a) < 1e-9 and abs(user_b - correct_b) < 1e-9:
                is_correct = True
        except Exception:
            # Fallback to simple string comparison if parsing fails
            is_correct = (user_answer.replace(' ', '').lower() == correct_answer.replace(' ', '').lower())
    else:
        # Answer is numeric.
        try:
            is_correct = (abs(float(user_answer) - float(correct_answer)) < 1e-9)
        except (ValueError, TypeError):
            # Fallback for non-numeric answers that are not functions (e.g., text)
            is_correct = (user_answer.upper() == correct_answer.upper())

    if is_correct:
        result_text = f"完全正確！答案是 ${correct_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer}$"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}