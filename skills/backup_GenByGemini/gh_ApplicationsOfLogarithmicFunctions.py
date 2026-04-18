import random
import math
from fractions import Fraction

# Helper function to get a random logarithm base
def _get_random_log_base():
    return random.choice([2, 3, 5, 10, 'e']) # 'e' signifies natural logarithm

# Helper function to format logarithm expressions in LaTeX
def _format_log(base, arg):
    if isinstance(base, Fraction):
        # Format fractional base for LaTeX, e.g., 1/3 -> \\frac{1}{3}
        if base.denominator == 1: # If it's an integer like 2/1
            base_display = str(base.numerator)
        else:
            base_display = r"\\frac{{{}}}{{{}}}".format(base.numerator, base.denominator)
        return r"\\log_{{{}}}".format(base_display) + f"({{{arg}}})"
    elif base == 10:
        return r"\\log" + f"({{{arg}}})"
    elif base == 'e':
        return r"\\ln" + f"({{{arg}}})"
    else: # Integer base
        return r"\\log_{{{base}}}" + f"({{{arg}}})"

def generate(level=1):
    """
    生成應用對數函數單調性解方程式與不等式的題目。
    """
    problem_types_level1 = [
        'equation_simple_add_sub',
        'inequality_simple',
        'application_growth_domino_simple'
    ]
    
    problem_types_level2 = [
        'equation_simple_add_sub', 
        'inequality_simple',       
        'equation_change_base_same_root',
        'application_growth_domino', 
        'comparison_values'
    ]
    
    # For level 3 and beyond, use the same set as level 2 or expand with more complex ones
    problem_types_level3 = problem_types_level2
    # Future expansion: 'inequality_quadratic', 'equation_more_complex'

    if level == 1:
        problem_type = random.choice(problem_types_level1)
    elif level == 2:
        problem_type = random.choice(problem_types_level2)
    else: # level >= 3
        problem_type = random.choice(problem_types_level3)

    if problem_type == 'equation_simple_add_sub':
        return generate_log_equation_simple_add_sub()
    elif problem_type == 'equation_change_base_same_root':
        return generate_log_equation_change_base_same_root()
    elif problem_type == 'inequality_simple':
        return generate_log_inequality_simple()
    elif problem_type == 'application_growth_domino':
        return generate_application_growth_domino(full_problem=True)
    elif problem_type == 'application_growth_domino_simple':
        return generate_application_growth_domino(full_problem=False)
    elif problem_type == 'comparison_values':
        return generate_log_comparison_values()
    else:
        # Fallback to a simple problem type if a new type is added but not implemented
        return generate_log_equation_simple_add_sub()

def generate_log_equation_simple_add_sub():
    base = _get_random_log_base()
    op_type = random.choice(['add', 'sub']) # log A + log B = log C or log A - log B = log C
    
    if op_type == 'add':
        # Scenario: log x + log (x - offset) = log K
        # Domain: x > offset.
        # Let 'sol' be the positive integer solution. 'offset' must be less than 'sol'.
        offset_val = random.randint(1, 3) # e.g., for x-1, x-2, x-3
        sol = random.randint(offset_val + 2, offset_val + 5) # Ensure sol is clearly > offset_val
        
        K_rhs = sol * (sol - offset_val) # Derived from x(x - offset) = K_rhs
        
        arg1_str = "x"
        arg2_str = f"x - {{{offset_val}}}"
        rhs_val = K_rhs
        
        question_text = f"解方程式：${_format_log(base, arg1_str)} + {_format_log(base, arg2_str)} = {_format_log(base, rhs_val)}$"
        correct_answer = str(sol)
    else: # op_type == 'sub'
        # Scenario: log(x + A) - log(x) = log K
        # Domain: x > 0 and x + A > 0 => x > 0
        # (x + A) / x = K => x + A = Kx => A = (K-1)x => x = A / (K-1)
        
        sol = random.randint(1, 10) # Target integer solution
        K_val = random.randint(2, 5) # K must be > 1 to make K-1 positive
        A_val_linear = sol * (K_val - 1)
        
        arg1_str = f"x + {{{A_val_linear}}}"
        arg2_str = "x"
        rhs_val = K_val
        
        question_text = f"解方程式：${_format_log(base, arg1_str)} - {_format_log(base, arg2_str)} = {_format_log(base, rhs_val)}$"
        correct_answer = str(sol)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_log_equation_change_base_same_root():
    # Scenario: log_a x + log_{a^k} x = C
    # This simplifies to (1 + 1/k) log_a x = C => log_a x = C * k / (k+1)
    # x = a^(C * k / (k+1))
    
    base = random.choice([2, 3, 4])
    k_val = random.randint(2, 3) # k can be 2 or 3
    
    second_base = base**k_val # The second log's base will be a^k
    
    # To get an integer solution `x_sol` and a simple `C` value,
    # let `log_a x_sol` be a multiple of `k_val`.
    power_of_x_base = random.randint(1, 2) * k_val 
    x_sol = base**power_of_x_base
    
    # Calculate C_prime = log_a x_sol + log_{a^k} x_sol
    # C_prime = power_of_x_base + (1/k_val) * power_of_x_base
    # C_prime = power_of_x_base * (1 + 1/k_val) = power_of_x_base * (k_val+1)/k_val
    C_prime = power_of_x_base * (k_val + 1) // k_val # Use integer division
    
    question_text = (
        f"解方程式：${_format_log(base, x_sol)} + {_format_log(second_base, x_sol)} = {{{C_prime}}}$"
    )
    correct_answer = str(x_sol)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_log_inequality_simple():
    base_int = random.choice([2, 3, 10])
    is_decreasing = random.random() < 0.5 # If true, base < 1
    
    if is_decreasing:
        # For decreasing function, base must be a fraction like 1/base_int
        base_frac = Fraction(1, base_int)
    else:
        base_frac = base_int # Base is integer
    
    ineq_op = random.choice(['<', '>']) # < or >
    
    # log_b (x + c_val) < K_rhs_val or log_b (x + c_val) > K_rhs_val
    
    K_rhs_val = random.randint(1, 3) # RHS value, e.g., 1, 2, 3
    
    attempts = 0
    c_val = 0 # Default c_val to ensure problem generation
    
    # Attempt to find a suitable c_val that results in a valid, non-empty interval
    while attempts < 10:
        c_val = random.randint(-3, 3) # Constant term in the log argument
        
        # This is the value `x+c_val` compares against after removing log
        actual_comparison_val = base_frac**K_rhs_val
        
        # The point `x` would equal if it were an equation: x = actual_comparison_val - c_val
        boundary_x_point = actual_comparison_val - c_val
        
        # Domain requirement: x + c_val > 0 => x > -c_val
        domain_lower_bound = -c_val
        
        if boundary_x_point > domain_lower_bound: # Valid range
            break
        attempts += 1
    
    # Fallback to c_val = 0 if no suitable value found after attempts
    if attempts == 10:
        c_val = 0
        actual_comparison_val = base_frac**K_rhs_val
        boundary_x_point = actual_comparison_val - c_val
        domain_lower_bound = -c_val
    
    question_expr = f"x + {{{c_val}}}"
    
    result_ineq = ""
    if is_decreasing: # Base < 1, inequality flips
        if ineq_op == '<': # log_b (expr) < K => expr > b^K. So x + c_val > actual_comparison_val
            lower_bound_result = max(boundary_x_point, domain_lower_bound)
            result_ineq = f"x > {{{lower_bound_result}}}"
        else: # ineq_op == '>', log_b (expr) > K => expr < b^K. So x + c_val < actual_comparison_val
            upper_bound_result = boundary_x_point
            lower_bound_result = domain_lower_bound
            if lower_bound_result >= upper_bound_result: # Empty set, regenerate
                return generate_log_inequality_simple()
            result_ineq = f"{{{lower_bound_result}}} < x < {{{upper_bound_result}}}"
    else: # Base > 1, inequality maintains
        if ineq_op == '<': # log_b (expr) < K => expr < b^K. So x + c_val < actual_comparison_val
            upper_bound_result = boundary_x_point
            lower_bound_result = domain_lower_bound
            if lower_bound_result >= upper_bound_result: # Empty set, regenerate
                return generate_log_inequality_simple()
            result_ineq = f"{{{lower_bound_result}}} < x < {{{upper_bound_result}}}"
        else: # ineq_op == '>', log_b (expr) > K => expr > b^K. So x + c_val > actual_comparison_val
            lower_bound_result = max(boundary_x_point, domain_lower_bound)
            result_ineq = f"x > {{{lower_bound_result}}}"
            
    question_text = f"解不等式：${_format_log(base_frac, question_expr)} {ineq_op} {{{K_rhs_val}}}$"
    correct_answer = result_ineq.replace(' ', '') # Remove spaces for checking

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_application_growth_domino(full_problem=True):
    # Model: Height of n-th item = initial_height * growth_factor^(n-1)
    
    initial_height = random.randint(2, 5) # e.g., 2 inches
    
    if full_problem:
        # Part (2): When height exceeds a large value, requiring logarithms
        growth_factor = Fraction(random.randint(12, 18), 10) # e.g., 1.5 (15/10), 1.2 (12/10)
        
        target_height_base = random.choice([10000, 20000, 50000]) 
        target_height = target_height_base * initial_height # e.g., 20000 * 2 = 40000
        
        # Inequality: initial_height * growth_factor^(n-1) > target_height
        # growth_factor^(n-1) > target_height / initial_height
        # (n-1) log(growth_factor) > log(target_height / initial_height)
        # n-1 > log(target_height / initial_height) / log(growth_factor)
        
        rhs_ratio = Fraction(target_height, initial_height)
        
        # Calculate log values for hints (using common logarithm, base 10)
        log_growth_factor_val = round(math.log10(growth_factor), 4)
        log_rhs_ratio_val = round(math.log10(rhs_ratio), 4)
        
        n_minus_1_approx = log_rhs_ratio_val / log_growth_factor_val
        n_sol = math.floor(n_minus_1_approx) + 1 # The smallest integer n that satisfies the inequality
        
        question_text = (
            f"一張骨牌的高度為 ${initial_height}$ 英吋，之後每一張骨牌的高度皆為前一張骨牌高度的 ${growth_factor}$ 倍。"
            f"試問：從第幾張骨牌開始，骨牌的高度會超過 ${target_height}$ 英吋？"
            r"<br>(請利用常用對數，已知 $\\log {{{growth_factor}}} \\approx {{{log_growth_factor_val}}} $, $\\log {{{rhs_ratio}}} \\approx {{{log_rhs_ratio_val}}} $。"
            r"計算結果取最接近的整數。)"
        )
        correct_answer = str(int(n_sol))
        
    else: # Simple version: iterate to find the answer without explicit logs
        growth_factor = Fraction(random.randint(12, 18), 10)
        target_height = random.randint(10, 50)
        
        current_height = initial_height
        n = 1
        while current_height <= target_height:
            current_height *= growth_factor
            n += 1
        
        question_text = (
            f"一張骨牌的高度為 ${initial_height}$ 英吋，之後每一張骨牌的高度皆為前一張骨牌高度的 ${growth_factor}$ 倍。"
            f"試問：從第幾張骨牌開始，骨牌的高度會超過 ${target_height}$ 英吋？"
        )
        correct_answer = str(n)
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_log_comparison_values():
    # Compares values like a = log_B1 X1, b = log_B2 X2, c = log_B3 X3
    # Converts all to a common base (e.g., natural log or common log) to compare their numerical values.
    
    common_base_for_generation = random.choice([2, 3, 5]) # e.g. for log_3 4
    
    expr_list = []
    labels = ['a', 'b', 'c']
    actual_values_and_labels = []
    
    for i in range(3):
        label = labels[i]
        
        # Vary base and argument structure to create different comparison scenarios
        choice = random.randint(1, 4)
        
        if choice == 1: # log_base X
            base = common_base_for_generation
            arg = random.randint(2, 10)
            expr_str = _format_log(base, arg)
            val = math.log(arg, base)
            
        elif choice == 2: # log_{base^k} X^(m) or X
            base_power = random.randint(2, 3) # Exponent for the base, k
            base = common_base_for_generation ** base_power
            
            # Argument can also have an exponent to simplify the value
            arg_power_num = random.randint(1, base_power) 
            arg_val = random.randint(2, 10) 
            arg_display = f"{arg_val}^{{{arg_power_num}}}" if arg_power_num > 1 else str(arg_val)
            
            expr_str = _format_log(base, arg_display)
            val = (arg_power_num / base_power) * math.log(arg_val, common_base_for_generation)
            
        elif choice == 3: # log_{1/base} X (negative values)
            base_num = common_base_for_generation
            base_frac = Fraction(1, base_num)
            arg = random.randint(2, 10)
            expr_str = _format_log(base_frac, arg)
            val = math.log(arg, base_frac)
            
        else: # log_base (X/Y) to get values < 1, resulting in negative log if base > 1
            base = common_base_for_generation
            arg_num = random.randint(1, 5)
            arg_den = random.randint(6, 10)
            # Ensure arg_num < arg_den for the argument to be < 1
            if base > 1 and arg_num >= arg_den:
                arg_num, arg_den = arg_den, arg_num # Swap to make fraction < 1
            
            arg_frac = Fraction(arg_num, arg_den)
            
            expr_str = _format_log(base, arg_frac)
            val = math.log(arg_frac, base)
            
        expr_list.append(f"${label} = {expr_str}$")
        actual_values_and_labels.append((val, label))
        
    # Sort values to determine the correct order
    actual_values_and_labels.sort()
    
    # Extract labels in sorted order
    sorted_labels = [item[1] for item in actual_values_and_labels]
    
    question_text = f"利用對數函數的單調性，比較下列三數的大小關係：{', '.join(expr_list)}。"
    question_text += "<br>請以 `a < b < c` 的格式填入答案。"
    
    correct_answer = " < ".join(sorted_labels)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip().lower().replace(' ', '')
    correct_answer = correct_answer.strip().lower().replace(' ', '')
    
    is_correct = (user_answer == correct_answer)
    
    if not is_correct:
        try:
            # For simple numerical answers, compare floats
            if float(user_answer) == float(correct_answer):
                is_correct = True
        except ValueError:
            pass
            
    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}