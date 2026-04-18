import random
from fractions import Fraction
import math
import re # For advanced answer checking of inequalities

def generate(level=1):
    """
    生成「指數函數應用」相關題目 (標準 LaTeX 範本)。
    包含：
    1. 解指數方程式 (簡單型，二次型)
    2. 解指數不等式 (簡單型，二次型)
    3. 比較指數大小
    4. 半衰期應用
    5. 金融應用 (單利、複利)
    """
    problem_type_choices = [
        'equation_simple',
        'equation_quadratic',
        'comparison',
        'inequality_simple',
        'inequality_quadratic',
        'half_life',
        'financial'
    ]
    
    # Adjust problem distribution by level if desired.
    problem_type = random.choice(problem_type_choices)
    
    if problem_type == 'equation_simple':
        return _generate_equation_simple()
    elif problem_type == 'equation_quadratic':
        return _generate_equation_quadratic_form()
    elif problem_type == 'comparison':
        return _generate_comparison_problem()
    elif problem_type == 'inequality_simple':
        return _generate_inequality_simple()
    elif problem_type == 'inequality_quadratic':
        return _generate_inequality_quadratic_form()
    elif problem_type == 'half_life':
        return _generate_half_life_problem()
    elif problem_type == 'financial':
        return _generate_financial_problem()

def _generate_equation_simple():
    """
    生成簡單指數方程式，如 a^x = a^y 或 k * a^x = a^y。
    目標是讓指數變為整數或簡單分數。
    """
    base = random.choice([2, 3, 5])
    
    problem_scenario = random.choices(['simple_power', 'coeff_and_power', 'fraction_base_and_sqrt'], weights=[0.5, 0.3, 0.2], k=1)[0]

    if problem_scenario == 'simple_power': # Type: base^x = base^Y
        x_val = random.randint(-3, 5)
        # Introduce a fraction in the exponent sometimes
        if random.random() < 0.3:
            denominator = random.choice([2, 3])
            numerator = random.randint(-5, 5)
            # Ensure numerator is not 0 for interesting fractions
            if numerator == 0: numerator = 1
            x_val = Fraction(numerator, denominator)
        
        power_rhs = x_val
        
        # Display power_rhs appropriately for fraction
        power_rhs_display = f"\\frac{{{power_rhs.numerator}}}{{{power_rhs.denominator}}}" if isinstance(power_rhs, Fraction) and power_rhs.denominator != 1 else str(power_rhs)

        question_text = f"解下列各方程式：<br>$ {base}^{{x}} = {base}^{{{power_rhs_display}}} $"
        correct_answer = str(x_val)

    elif problem_scenario == 'coeff_and_power': # Type: A * base^(B*x) = base^C or base^A * base^(B*x) = base^C
        power_lhs_coeff_val = random.randint(-2, 2)
        if power_lhs_coeff_val == 0: power_lhs_coeff_val = random.choice([-1, 1])
        
        x_coeff_val = random.choice([1, 2, 3, Fraction(1, 2), Fraction(1, 3)])
        rhs_power = random.randint(-4, 4)
        
        # Construct the LHS display part
        lhs_display = ""
        if power_lhs_coeff_val != 0:
            lhs_display += f"{base}^{{{power_lhs_coeff_val}}} \\cdot "
        
        exponent_x_display = ""
        if x_coeff_val == 1:
            exponent_x_display = "x"
        elif isinstance(x_coeff_val, int):
            exponent_x_display = f"{x_coeff_val}x"
        else: # Fraction like 1/2
            exponent_x_display = f"\\frac{{x}}{{{x_coeff_val.denominator}}}"
            
        lhs_display += f"{base}^{{{exponent_x_display}}}"
        
        # Solve for x: power_lhs_coeff_val + x_coeff_val * x = rhs_power
        # x_coeff_val * x = rhs_power - power_lhs_coeff_val
        # x = (rhs_power - power_lhs_coeff_val) / x_coeff_val
        
        effective_x = Fraction(rhs_power - power_lhs_coeff_val) / x_coeff_val
        
        rhs_val = base**rhs_power
        
        question_text = f"解下列各方程式：<br>$ {lhs_display} = {rhs_val} $"
        correct_answer = str(effective_x.limit_denominator())

    else: # Type: (1/base^A) * (sqrt(base))^x = 1/base^B
        base_denom_power = random.randint(2, 4)
        rhs_denom_power = random.randint(base_denom_power - 2, base_denom_power + 2)
        if rhs_denom_power <= 0: rhs_denom_power = 1 # Ensure valid power for denominator

        # Equation: base^(-base_denom_power) * base^(x/2) = base^(-rhs_denom_power)
        # So, -base_denom_power + x/2 = -rhs_denom_power
        # x/2 = base_denom_power - rhs_denom_power
        # x = 2 * (base_denom_power - rhs_denom_power)
        
        x_val = 2 * (base_denom_power - rhs_denom_power)

        question_text = f"解下列各方程式：<br>$ \\frac{{1}}{{{base}^{{{base_denom_power}}}}} \\cdot (\\sqrt{{{base}}})^{{x}} = \\frac{{1}}{{{base}^{{{rhs_denom_power}}}}} $"
        correct_answer = str(x_val)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def _generate_equation_quadratic_form():
    """
    生成形如 (a^x)^2 + b(a^x) + c = 0 的指數方程式。
    設 t = a^x，解 t^2 + bt + c = 0。
    確保 t 的解有一個正數，且為底數的整數次冪。
    """
    base = random.choice([2, 3]) # Common bases
    
    # Generate roots for the quadratic equation t^2 + bt + c = 0
    # One positive root (must be base^power), one negative root (invalid for base^x)
    
    root_power = random.randint(1, 3) # The integer 'x' solution
    valid_t_root = base**root_power # This is t = base^x
    invalid_t_root = random.choice([-2, -3, -4, -5, -6]) # t = base^x cannot be negative
    
    # Construct quadratic factors: (t - valid_t_root)(t - invalid_t_root) = 0
    # t^2 - (valid_t_root + invalid_t_root)t + (valid_t_root * invalid_t_root) = 0
    b_coeff = -(valid_t_root + invalid_t_root)
    c_coeff = valid_t_root * invalid_t_root

    # The equation is (base^x)^2 + b_coeff * (base^x) + c_coeff = 0
    
    term1 = f"({base}^{{x}})^{{2}}"
    
    equation_parts = [term1]
    
    if b_coeff != 0:
        if b_coeff > 0:
            equation_parts.append(f"+ {b_coeff} \\cdot {base}^{{x}}")
        else: # b_coeff is negative
            equation_parts.append(f"{b_coeff} \\cdot {base}^{{x}}")
    
    if c_coeff != 0:
        if c_coeff > 0:
            equation_parts.append(f"+ {c_coeff}")
        else: # c_coeff is negative
            equation_parts.append(f"{c_coeff}")
        
    question_text = f"解下列各方程式：<br>$ {' '.join(equation_parts)} = 0 $"
    
    correct_answer = str(root_power)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def _generate_comparison_problem():
    """
    生成比較指數大小的題目，利用指數函數嚴格遞增（減）的特性。
    """
    base_type = random.choice(['gt_one', 'lt_one']) # Base > 1 or 0 < Base < 1
    
    if base_type == 'gt_one':
        base = random.choice([2, 3, 4, 5])
        exponents_base = sorted([random.randint(-3, 3) for _ in range(3)])
        while len(set(exponents_base)) < 3: # Ensure distinct base exponents
            exponents_base = sorted([random.randint(-3, 3) for _ in range(3)])
        # Use Fraction to allow for fractional exponents
        exponents = [Fraction(e) for e in exponents_base]

    else: # 0 < base < 1
        base_num = random.choice([3, 5, 7])
        base_den = random.choice([4, 6, 8, 10]) 
        base = Fraction(base_num, base_den)
        
        exponents_base = sorted([random.randint(-3, 3) for _ in range(3)], reverse=True) # Descending for 0<base<1 base values
        while len(set(exponents_base)) < 3: # Ensure distinct base exponents
            exponents_base = sorted([random.randint(-3, 3) for _ in range(3)], reverse=True)
        exponents = [Fraction(e) for e in exponents_base] # Convert to Fraction objects
            
    # Modify exponents to make them more complex (e.g., fractional or with negative signs)
    # Ensure exponents remain distinct after modification
    final_exponents = []
    for i, exp in enumerate(exponents):
        if random.random() < 0.6 and exp.denominator == 1: # Convert some integer exponents to fractions
            final_exponents.append(exp / random.choice([2, 3]))
        else:
            final_exponents.append(exp)
    
    # Ensure all exponents are distinct after modification
    unique_exponents = sorted(list(set(final_exponents)))
    # If not enough distinct exponents, regenerate a simpler set
    if len(unique_exponents) < 3:
        exponents = sorted([Fraction(random.randint(-3, 3)) for _ in range(3)])
        while len(set(exponents)) < 3:
            exponents = sorted([Fraction(random.randint(-3, 3)) for _ in range(3)])
        unique_exponents = exponents # Use simple integer exponents if complex ones cause duplicates
    
    # Shuffle for presentation labels
    exp_labels = ['a', 'b', 'c']
    random.shuffle(exp_labels)
    
    # Assign exponents to variables and generate question parts
    question_parts = []
    comparison_values = [] # Store (label, actual_value) for sorting
    
    for i, label in enumerate(exp_labels):
        exponent_frac = unique_exponents[i] # Get an exponent from the unique_exponents list
        
        base_for_display = base
        exponent_for_display = exponent_frac
        
        # Introduce a "tricky" variant, like (base^2)^(exp/2)
        if random.random() < 0.3:
            base_for_display = base**2
            exponent_for_display = exponent_frac / 2
            
        base_display = str(base_for_display)
        if isinstance(base_for_display, Fraction):
            base_display = f"\\frac{{{base_for_display.numerator}}}{{{base_for_display.denominator}}}"
            base_display = f"\\left({base_display}\\right)" # Add parentheses for fractional bases

        exponent_display = str(exponent_for_display)
        if isinstance(exponent_for_display, Fraction) and exponent_for_display.denominator != 1:
            exponent_display = f"\\frac{{{exponent_for_display.numerator}}}{{{exponent_for_display.denominator}}}"
        
        question_parts.append(f"${label} = {base_display}^{{{exponent_display}}}$")
        comparison_values.append((label, float(base**exponent_frac))) # Calculate actual value using original base and exponent
            
    question_text = f"利用指數函數嚴格遞增（減）的特性，比較 {' '.join(question_parts)} 三數的大小關係。"
    
    # Sort based on calculated values
    # If base < 1, the order of values is reversed compared to the order of exponents.
    # Here, we sort by calculated float values directly, so reverse is not needed for the sort itself,
    # but for base < 1, the larger exponent gives a smaller value.
    comparison_values.sort(key=lambda x: x[1], reverse=True) # Sort largest to smallest value
    
    # Construct correct answer string (e.g., c > b > a)
    correct_answer = " > ".join([item[0] for item in comparison_values])
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def _generate_inequality_simple():
    """
    生成簡單指數不等式，如 a^(f(x)) > a^(g(x))。
    """
    base_type = random.choice(['gt_one', 'lt_one'])
    
    if base_type == 'gt_one':
        base = random.choice([2, 3, 5])
    else: # 0 < base < 1
        base_num = random.choice([2, 3])
        base_den = random.choice([3, 4, 5])
        base = Fraction(base_num, base_den)
    
    operator = random.choice(['>', '<', '>=', '<='])
    
    x_coeff_lhs = random.randint(1, 3)
    x_coeff_rhs = random.randint(1, 3)
    
    const_lhs = random.randint(-5, 5)
    const_rhs = random.randint(-5, 5)
    
    # Ensure the coefficients of x are distinct to avoid trivial cases
    while x_coeff_lhs == x_coeff_rhs:
        x_coeff_rhs = random.randint(1, 3)
            
    # Build exponent strings
    lhs_exp_str = f"{x_coeff_lhs}x" + (f" {'+' if const_lhs > 0 else '-'} {abs(const_lhs)}" if const_lhs != 0 else "")
    rhs_exp_str = f"{x_coeff_rhs}x" + (f" {'+' if const_rhs > 0 else '-'} {abs(const_rhs)}" if const_rhs != 0 else "")
    
    base_display = str(base)
    if isinstance(base, Fraction):
        base_display = f"\\left(\\frac{{{base.numerator}}}{{{base.denominator}}}\\right)"

    question_text = f"解下列各不等式：<br>$ {base_display}^{{{lhs_exp_str}}} {operator} {base_display}^{{{rhs_exp_str}}} $"
    
    # Solve the linear inequality: (x_coeff_lhs * x + const_lhs) compared to (x_coeff_rhs * x + const_rhs)
    # Rearrange to: (x_coeff_lhs - x_coeff_rhs)x [effective_operator] (const_rhs - const_lhs)
    
    effective_operator = operator
    if base_type == 'lt_one': # Flip operator if base < 1
        if operator == '>': effective_operator = '<'
        elif operator == '<': effective_operator = '>'
        elif operator == '>=': effective_operator = '<='
        elif operator == '<=': effective_operator = '>='

    diff_x_coeff = x_coeff_lhs - x_coeff_rhs
    diff_const = const_rhs - const_lhs
    
    if diff_x_coeff == 0: # This case is avoided by generation logic for x_coeff, but good to have
        # This implies const_lhs operator const_rhs, e.g., 5 > 3.
        # This inequality either holds for all x or no x.
        # To avoid actual `eval` with user input, pre-compute the boolean outcome
        dummy_x = 0 # x doesn't matter
        lhs_val = x_coeff_lhs * dummy_x + const_lhs
        rhs_val = x_coeff_rhs * dummy_x + const_rhs
        
        if (operator == '>' and lhs_val > rhs_val) or \
           (operator == '<' and lhs_val < rhs_val) or \
           (operator == '>=' and lhs_val >= rhs_val) or \
           (operator == '<=' and lhs_val <= rhs_val):
            correct_answer = r"x \\in \\mathbb{R}" # All real numbers
        else:
            correct_answer = r"\emptyset" # Empty set
    else:
        # Determine final operator based on sign of diff_x_coeff
        final_op = effective_operator
        if diff_x_coeff < 0: # Flip operator again if coefficient of x is negative
            if effective_operator == '>': final_op = '<'
            elif effective_operator == '<': final_op = '>'
            elif effective_operator == '>=': final_op = '<='
            elif effective_operator == '<=': final_op = '>='
        
        result_frac = Fraction(diff_const, diff_x_coeff).limit_denominator()
        result_frac_display = f"\\frac{{{result_frac.numerator}}}{{{result_frac.denominator}}}" if result_frac.denominator != 1 else str(result_frac)
        
        correct_answer = f"x {final_op} {result_frac_display}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def _generate_inequality_quadratic_form():
    """
    生成形如 (a^x)^2 + b(a^x) + c > 0 的指數不等式。
    設 t = a^x，解 t^2 + bt + c > 0。
    確保 t 的解範圍能與 t = a^x > 0 結合。
    """
    base = random.choice([2, 3])
    operator = random.choice(['>', '<', '>=', '<='])
    
    # Generate roots for quadratic t^2 + bt + c
    # We want one positive root (t_p) and one negative root (t_n) for t.
    root_power = random.randint(1, 3) # This will be the x value in base^x = t_p
    t_p = base**root_power # Positive root
    t_n = random.randint(-5, -1) # Negative root (t = base^x > 0, so this root is ignored)
    
    # Coefficients for t^2 + bt + c = (t - t_p)(t - t_n)
    b_coeff = -(t_p + t_n)
    c_coeff = t_p * t_n
    
    # Construct the inequality (base^x)^2 + b_coeff * (base^x) + c_coeff operator 0
    term1 = f"({base}^{{x}})^{{2}}"
    
    equation_parts = [term1]
    
    if b_coeff != 0:
        if b_coeff > 0:
            equation_parts.append(f"+ {b_coeff} \\cdot {base}^{{x}}")
        else:
            equation_parts.append(f"{b_coeff} \\cdot {base}^{{x}}")
    
    if c_coeff != 0:
        if c_coeff > 0:
            equation_parts.append(f"+ {c_coeff}")
        else:
            equation_parts.append(f"{c_coeff}")
        
    question_text = f"解下列各不等式：<br>$ {' '.join(equation_parts)} {operator} 0 $"
    
    # Solution logic:
    # Let t = base^x. Since base > 0, t must be > 0.
    # Solve (t - t_p)(t - t_n) operator 0
    # Roots are t_n (negative) and t_p (positive).
    
    # Case 1: operator is '>' or '>='
    # (t - t_p)(t - t_n) > 0 implies t < t_n or t > t_p.
    # Since t > 0, t < t_n (negative range) is not possible.
    # So, the solution for t is t > t_p (or t >= t_p).
    # This means base^x > t_p (or base^x >= t_p).
    # Since t_p = base^root_power and base > 1, the inequality direction is preserved:
    # x > root_power (or x >= root_power).
    if operator in ['>', '>=']:
        correct_answer = f"x {operator} {root_power}"
        
    # Case 2: operator is '<' or '<='
    # (t - t_p)(t - t_n) < 0 implies t_n < t < t_p.
    # Since t > 0, the solution for t is 0 < t < t_p (or 0 < t <= t_p).
    # This means 0 < base^x < t_p (or 0 < base^x <= t_p).
    # The condition 0 < base^x is always true.
    # So, base^x < t_p (or base^x <= t_p).
    # Since t_p = base^root_power and base > 1, the inequality direction is preserved:
    # x < root_power (or x <= root_power).
    elif operator in ['<', '<=']:
        correct_answer = f"x {operator} {root_power}"
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def _generate_half_life_problem():
    """
    生成半衰期應用問題。
    N(t) = N_0 * (1/2)^(t/T)
    """
    half_life_val = random.choice([5700, 1620, 20000]) # Common half-life values
    
    # Final amount is 1/(2^power) of original amount
    final_fraction_power = random.randint(3, 5) # e.g., 1/8, 1/16, 1/32
    
    time_unit = "年"
    
    question_template = random.choice([
        "考古學家發現了一尊古物，利用碳14鑑定後，發現該古物的碳14數量少於原來的 $\\frac{{1}}{{{2**final_fraction_power}}}$。已知碳14的半衰期約為 ${half_life_val}$ {time_unit}，問：該古物至少為幾{time_unit}前的古物？",
        "某放射性物質的半衰期為 ${half_life_val}$ {time_unit}。若經過 $x$ {time_unit}後，該物質的數量少於原來的 $\\frac{{1}}{{{2**final_fraction_power}}}$，請問 $x$ 至少為多少？"
    ])
    
    question_text = question_template.format(
        half_life_val=half_life_val,
        time_unit=time_unit,
        final_fraction_power=final_fraction_power
    )
    
    # Mathematical setup: (1/2)^(x/half_life_val) < 1 / (2^final_fraction_power)
    # This simplifies to (1/2)^(x/half_life_val) < (1/2)^final_fraction_power
    # Since the base (1/2) is less than 1, the inequality direction flips for the exponents:
    # x / half_life_val > final_fraction_power
    # x > half_life_val * final_fraction_power
    
    min_time = half_life_val * final_fraction_power
    
    # The 'answer' for checking is just the numerical value.
    # The 'correct_answer' includes units and context for display.
    correct_answer_display = f"至少 {min_time} {time_unit}"
    
    return {
        "question_text": question_text,
        "answer": str(min_time), # The raw number for flexible checking
        "correct_answer": correct_answer_display
    }

def _generate_financial_problem():
    """
    生成金融應用問題，包括單利和複利。
    """
    principal_base = random.choice([10, 50, 100, 200])
    principal = principal_base * 10000 # In units of 萬元 (10,000)
    
    rate_percent = random.choice([2, 2.5, 3, 4, 5])
    rate = rate_percent / 100
    years = random.randint(5, 15)
    
    question_template = (
        "某銀行推出存款方案如下：存入 $ {principal_wan} $ 萬元、年利率為 $ {rate_percent}\\% $、每年計息一次，$ {years} $ 年後期滿一次領回本利和。<br>"
        "(1) 以單利計息，期滿領回時可領多少錢？(單位：萬元，四捨五入到小數點後兩位)<br>"
        "(2) 以複利計息，期滿領回時可領多少錢？(單位：萬元，四捨五入到小數點後兩位)"
    )
    
    question_text = question_template.format(
        principal_wan=int(principal/10000),
        rate_percent=rate_percent,
        years=years
    )
    
    # (1) Simple Interest: A = P(1 + rt)
    simple_interest_amount = principal * (1 + rate * years)
    simple_interest_wan = round(simple_interest_amount / 10000, 2)
    
    # (2) Compound Interest: A = P(1 + r)^t
    compound_interest_amount = principal * (1 + rate)**years
    compound_interest_wan = round(compound_interest_amount / 10000, 2)
    
    # Correct answer for checking is a combined string, user should provide "X與Y"
    correct_answer = f"{simple_interest_wan}與{compound_interest_wan}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer, # Store the combined string for checking
        "correct_answer": correct_answer # Also for display in feedback
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    對於金融問題，會檢查多個部分。
    對於其他問題，則是直接比較。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    
    is_correct = False
    result_text = ""

    # Handle financial problems with multiple answers separated by "與"
    if "與" in correct_answer:
        user_parts = [p.strip() for p in user_answer.split('與')]
        correct_parts = [p.strip() for p in correct_answer.split('與')]
        
        if len(user_parts) != len(correct_parts):
            is_correct = False
            result_text = f"答案格式不正確。請提供兩個答案，並用'與'字連接，例如：${correct_parts[0]}$與${correct_parts[1]}$"
        else:
            feedback = []
            all_parts_correct = True
            
            for i in range(len(correct_parts)):
                try:
                    user_val = float(user_parts[i])
                    correct_val = float(correct_parts[i])
                    
                    if abs(user_val - correct_val) < 0.02: # Allow small floating point error for financial calcs
                        feedback.append(f"第({i+1})部分：正確 (${correct_val}$ 萬元)")
                    else:
                        all_parts_correct = False
                        feedback.append(f"第({i+1})部分：不正確。您的答案是 ${user_val}$，正確答案應為 ${correct_val}$ 萬元。")
                except ValueError:
                    all_parts_correct = False
                    feedback.append(f"第({i+1})部分：您的答案 '{user_parts[i]}' 無法識別為數字。正確答案應為 ${correct_parts[i]}$ 萬元。")
            
            is_correct = all_parts_correct
            if is_correct:
                result_text = f"完全正確！<br>{'；<br>'.join(feedback)}"
            else:
                result_text = f"答案不完全正確。<br>{'；<br>'.join(feedback)}"

    else: # Single answer problems (equations, inequalities, comparison, half-life)
        # Clean answers for robust comparison
        # Remove spaces, convert common LaTeX operators to plain text, convert to lowercase
        user_clean = user_answer.replace(" ", "").replace(r"\\ge", ">=").replace(r"\\le", "<=").replace(r"\\mathbb{R}", "R").replace(r"\emptyset", "empty").lower()
        correct_clean = correct_answer.replace(" ", "").replace(r"\\ge", ">=").replace(r"\\le", "<=").replace(r"\\mathbb{R}", "R").replace(r"\emptyset", "empty").lower()
        
        # 1. Direct string comparison (for symbolic answers like R or empty set, or simple integer/fraction)
        if user_clean == correct_clean:
            is_correct = True
        
        # 2. Try comparing as fractions (for exact numerical answers)
        if not is_correct:
            try:
                user_frac = Fraction(user_clean)
                correct_frac = Fraction(correct_clean)
                if user_frac == correct_frac:
                    is_correct = True
            except ValueError:
                pass # Not a simple fraction, continue to next check

        # 3. Try comparing as floats (for half-life which may not be an exact fraction, or other numerical answers)
        if not is_correct:
            try:
                user_float = float(user_clean)
                correct_float = float(correct_clean)
                if abs(user_float - correct_float) < 1e-6: # Small tolerance for floats
                    is_correct = True
            except ValueError:
                pass # Not a float, continue

        # 4. For inequality expressions (e.g., "x > 2" or "x >= 3/2")
        # Standardize user input to "x op val" for comparison
        if not is_correct and ('x' in user_clean or 'r' in user_clean): # If it contains x or R (for real numbers)
            # Regex to parse "x op val" or "val op x"
            # It should handle "x>1", "1<x", "x<=1/2", "x >= -3"
            
            # Pattern for: x [op] val
            match_x_op_val = re.match(r"x\s*([<>]|[<>]=)\s*(-?\d+(\/\d+)?)", user_clean)
            # Pattern for: val [op] x (then we reverse op)
            match_val_op_x = re.match(r"(-?\d+(\/\d+)?)\s*([<>]|[<>]=)\s*x", user_clean)
            
            parsed_user_op = None
            parsed_user_val = None

            if match_x_op_val:
                parsed_user_op = match_x_op_val.group(1)
                parsed_user_val = Fraction(match_x_op_val.group(2))
            elif match_val_op_x:
                # Need to reverse the operator if val [op] x
                op_char = match_val_op_x.group(3)
                if op_char == '>': parsed_user_op = '<'
                elif op_char == '<': parsed_user_op = '>'
                elif op_char == '>=': parsed_user_op = '<='
                elif op_char == '<=': parsed_user_op = '>='
                parsed_user_val = Fraction(match_val_op_x.group(1))

            if parsed_user_op and parsed_user_val:
                # Parse correct answer in canonical "x op val" form
                correct_match = re.match(r"x\s*([<>]|[<>]=)\s*(-?\d+(\/\d+)?)", correct_clean)
                if correct_match:
                    correct_op = correct_match.group(1)
                    correct_val = Fraction(correct_match.group(2))
                    
                    if parsed_user_op == correct_op and parsed_user_val == correct_val:
                        is_correct = True

        if is_correct:
            result_text = f"完全正確！答案是 ${correct_answer}$。"
        else:
            result_text = f"答案不正確。正確答案應為：${correct_answer}$"

    return {"correct": is_correct, "result": result_text, "next_question": True}