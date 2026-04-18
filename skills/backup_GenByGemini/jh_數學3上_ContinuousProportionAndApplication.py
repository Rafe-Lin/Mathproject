import random
from fractions import Fraction
import math

def format_fraction(f: Fraction) -> str:
    """Formats a Fraction object into a string 'a/b' or 'a'."""
    if f.denominator == 1:
        return str(f.numerator)
    return f"{f.numerator}/{f.denominator}"

def format_fraction_latex(f: Fraction) -> str:
    """Formats a Fraction object into a LaTeX string."""
    if f.denominator == 1:
        return str(f.numerator)
    return f"\\frac{{{f.numerator}}}{{{f.denominator}}}"

def simplify_ratio(*args: int) -> list[int]:
    """Simplifies a ratio of integers, including negative numbers and zeros."""
    if all(x == 0 for x in args):
        return list(args)
    
    common_divisor = 0
    for x in args:
        if x != 0:
            current_abs_x = abs(x)
            if common_divisor == 0:
                common_divisor = current_abs_x
            else:
                common_divisor = math.gcd(common_divisor, current_abs_x)

    if common_divisor == 0: # This case happens if only one non-zero number exists or all are zero.
        return list(args)

    simplified = [x // common_divisor for x in args]
    return simplified

def generate(level=1):
    """
    Generates a problem related to continuous proportion and its applications.
    """
    problem_types = [
        'direct_calculation', 
        'find_one_value', 
        'combine_and_calculate_new_ratio',
        'application_distribution',
        'application_combined_ratio'
    ]
    problem_type = random.choice(problem_types)
    
    if problem_type == 'direct_calculation':
        return generate_direct_calculation_problem()
    elif problem_type == 'find_one_value':
        return generate_find_one_value_problem()
    elif problem_type == 'combine_and_calculate_new_ratio':
        return generate_combine_and_calculate_new_ratio_problem()
    elif problem_type == 'application_distribution':
        return generate_application_distribution_problem()
    else: # 'application_combined_ratio'
        return generate_application_combined_ratio_problem()

def generate_direct_calculation_problem():
    """
    Generates a problem of type: 設 a:x:y = b:c:d，求 x、y 的值。
    """
    k1 = random.randint(2, 9)
    k2 = random.randint(2, 9)
    while k1 == k2:
        k2 = random.randint(2, 9)
    k3 = random.randint(2, 9)
    k4 = random.randint(2, 9)

    x = Fraction(k1 * k3, k2)
    y = Fraction(k1 * k4, k2)
    
    question_text = f"設 ${k1}:x:y = {k2}:{k3}:{k4}$，求 $x$、y 的值。(請依序回答，以逗號分隔)"
    correct_answer = f"{format_fraction(x)}, {format_fraction(y)}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_find_one_value_problem():
    """
    Generates a problem of type: 設 x:y:z = a:b:c，若 z=k，則 x=？
    """
    nums = random.sample(range(1, 10), 3)
    a, b, c = nums[0], nums[1], nums[2]
    
    var_map = {'x': a, 'y': b, 'z': c}
    vars_list = list(var_map.keys())
    
    known_var = random.choice(vars_list)
    unknown_var = random.choice([v for v in vars_list if v != known_var])
    
    known_ratio = var_map[known_var]
    unknown_ratio = var_map[unknown_var]
    
    val_known = random.randint(2, 20)
    
    answer_val = Fraction(val_known * unknown_ratio, known_ratio)
    
    question_text = f"設 $x:y:z={a}:{b}:{c}$，若 ${known_var}=${val_known}$，則 ${unknown_var}=？$"
    correct_answer = format_fraction(answer_val)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_combine_and_calculate_new_ratio_problem():
    """
    Generates a problem of type: 設 x:y=a:b, y:z=c:d，求 2x:3y:4z 或 (x-y):(y-z):(z-x)
    """
    a, b = random.sample(range(1, 8), 2)
    c, d = random.sample(range(1, 8), 2)
    
    # Calculate x:y:z = p:q:r
    lcm_val = (b * c) // math.gcd(b, c)
    p = a * (lcm_val // b)
    q = lcm_val
    r = d * (lcm_val // c)
    
    # Choose sub-type for the expression to calculate
    if random.random() < 0.5:
        # Type: k1*x : k2*y : k3*z
        k1, k2, k3 = [random.randint(1, 5) for _ in range(3)]
        expr = f"{k1}x:{k2}y:{k3}z"
        res = [k1 * p, k2 * q, k3 * r]
    else:
        # Type: (x±y):(y±z):(z±x)
        ops = [('+', lambda m, n: m + n), ('-', lambda m, n: m - n)]
        op1_str, op1_func = random.choice(ops)
        op2_str, op2_func = random.choice(ops)
        op3_str, op3_func = random.choice(ops)
        expr = f"(x{op1_str}y):(y{op2_str}z):(z{op3_str}x)"
        res = [op1_func(p, q), op2_func(q, r), op3_func(r, p)]
        
        # Avoid 0:0:0 result, regenerate if it happens
        if all(val == 0 for val in res):
            return generate_combine_and_calculate_new_ratio_problem()

    simplified_res = simplify_ratio(*res)
    answer = ":".join(map(str, simplified_res))
    
    question_text = f"設 $x:y={a}:{b}$，$y:z={c}:{d}$，求連比 ${expr}$。"
    
    return {
        "question_text": question_text,
        "answer": answer,
        "correct_answer": answer
    }

def generate_application_distribution_problem():
    """
    Generates an application problem involving distributing a total amount.
    """
    sub_type = random.choice(['money', 'mixture', 'triangle'])
    
    if sub_type == 'triangle':
        # Sum of angles is 180. The sum of ratio parts must be a factor of 180.
        factors_of_180 = [3, 4, 5, 6, 9, 10, 12, 15, 18, 20, 30, 36]
        s = random.choice(factors_of_180)
        # Generate a, b, c such that a+b+c = s
        a = random.randint(1, s - 2)
        b = random.randint(1, s - a - 1)
        c = s - a - b
        
        m = 180 // s
        total = 180
        unit = "度"
        item_name = "一個三角形的三內角"
        p1, p2, p3 = a * m, b * m, c * m
        question_text = f"若{item_name}比為 ${a}:{b}:{c}$，則此三個內角分別為多少{unit}？(請依序回答，以逗號分隔)"
        
    else: # money or mixture
        a, b, c = [random.randint(2, 10) for _ in range(3)]
        s = a + b + c
        m = random.randint(5, 50)
        total = s * m
        p1, p2, p3 = a * m, b * m, c * m

        if sub_type == 'money':
            names = random.sample(["小翊", "小靖", "小妍", "小明", "小華"], 3)
            unit = "元"
            question_text = f"{names[0]}、{names[1]}與{names[2]}三人合夥做生意，約定將獲利依 ${a}:{b}:{c}$ 的比例分配。若本次獲利共 ${total}$ {unit}，則三人分別可分得多少{unit}？(請依序回答，以逗號分隔)"
        else: # mixture
            total_vol = total
            unit = "毫升"
            item = random.choice(["特調果汁", "綜合咖啡", "雞尾酒"])
            ingredients = random.sample(["濃縮液A", "基底B", "風味糖漿C", "原料甲", "原料乙"], 3)
            question_text = f"一杯 ${total_vol}$ {unit}的{item}是由{ingredients[0]}、{ingredients[1]}和{ingredients[2]}三種成分調製而成，其容量比為 ${a}:{b}:{c}$。請問這三種成分各需要多少{unit}？(請依序回答，以逗號分隔)"
            
    correct_answer = f"{p1}, {p2}, {p3}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_application_combined_ratio_problem():
    """
    Generates an application problem requiring combining two ratios first.
    """
    a, b = random.sample(range(1, 8), 2)
    c, d = random.sample(range(1, 8), 2)
    
    # Calculate AB:BC:CD = p:q:r
    lcm_val = (b * c) // math.gcd(b, c)
    p = a * (lcm_val // b)
    q = lcm_val
    r = d * (lcm_val // c)
    
    s = p + q + r
    m = random.randint(5, 30)
    total_len = s * m
    
    # Story: Bamboo pole (AC) and broom (BD)
    pole_len = (p + q) * m
    broom_len = (q + r) * m
    
    question_text = (
        f"將一根竹竿和一支掃把重疊綁在一起，形成一根長掃把(A-B-C-D)。"
        f"其中 BC 段為重疊部分。已知綁好的總長度(AD)為 ${total_len}$ 公分，"
        f"若竹竿(AC)的兩部分長度比 $AB:BC={a}:{b}$，掃把(BD)的兩部分長度比 $BC:CD={c}:{d}$，"
        f"則竹竿和掃把的原長度分別為多少公分？(請依序回答竹竿、掃把的長度，以逗號分隔)"
    )
    
    correct_answer = f"{pole_len}, {broom_len}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }
    
def check(user_answer, correct_answer):
    """
    Checks if the user's answer is correct. Handles single values, comma-separated values, and ratios.
    """
    user_answer_cleaned = user_answer.strip().replace('，', ',').replace('：', ':')
    correct_answer = correct_answer.strip()
    is_correct = False
    
    # Handle ratio format (e.g., "3:4:5")
    if ':' in correct_answer:
        user_parts = [s.strip() for s in user_answer_cleaned.split(':')]
        correct_parts = [s.strip() for s in correct_answer.split(':')]
        try:
            user_nums = [int(p) for p in user_parts]
            correct_nums = [int(p) for p in correct_parts]
            # Ratios are equivalent if they simplify to the same thing
            if len(user_nums) == len(correct_nums):
                is_correct = (simplify_ratio(*user_nums) == simplify_ratio(*correct_nums))
        except ValueError:
            is_correct = (user_answer_cleaned == correct_answer)

    # Handle comma-separated values (e.g., "100, 150")
    elif ',' in correct_answer:
        user_parts = [s.strip() for s in user_answer_cleaned.split(',')]
        correct_parts = [s.strip() for s in correct_answer.split(',')]
        
        if len(user_parts) == len(correct_parts):
            all_parts_match = True
            for u_part, c_part in zip(user_parts, correct_parts):
                try:
                    if Fraction(u_part) != Fraction(c_part):
                        all_parts_match = False
                        break
                except (ValueError, ZeroDivisionError):
                    if u_part != c_part: # Fallback to string comparison
                        all_parts_match = False
                        break
            is_correct = all_parts_match
            
    # Handle single value
    else:
        try:
            is_correct = (Fraction(user_answer_cleaned) == Fraction(correct_answer))
        except (ValueError, ZeroDivisionError):
            is_correct = (user_answer_cleaned.upper() == correct_answer.upper())

    # Format the correct answer with LaTeX for display
    if ':' in correct_answer:
        final_answer_str = correct_answer
    elif ',' in correct_answer:
        parts = correct_answer.split(',')
        formatted_parts = []
        for part in parts:
            try:
                f = Fraction(part.strip())
                formatted_parts.append(format_fraction_latex(f))
            except ValueError:
                formatted_parts.append(part.strip())
        final_answer_str = ", ".join(formatted_parts)
    else:
        try:
            f = Fraction(correct_answer)
            final_answer_str = format_fraction_latex(f)
        except ValueError:
            final_answer_str = correct_answer

    if is_correct:
        result_text = f"完全正確！答案是 ${final_answer_str}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${final_answer_str}$"
    
    return {"correct": is_correct, "result": result_text, "next_question": True}