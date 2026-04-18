import random
from math import gcd

def lcm(a, b):
    """Calculates the least common multiple of two integers."""
    return (a * b) // gcd(a, b) if a != 0 and b != 0 else 0

def generate(level=1):
    """
    生成「連比」相關題目。
    包含：
    1. 直接寫出連比 (情境應用)
    2. 連比的化簡與求值
    3. 合併連比 (共同項數字相同)
    4. 合併連比 (共同項數字不同)
    5. 從等式求連比
    """
    problem_type = random.choice([
        'direct_ratio', 
        'simplify_ratio', 
        'combine_easy', 
        'combine_lcm', 
        'from_equation'
    ])
    
    if problem_type == 'direct_ratio':
        return generate_direct_ratio_problem()
    elif problem_type == 'simplify_ratio':
        return generate_simplify_ratio_problem()
    elif problem_type == 'combine_easy':
        return generate_combine_easy_problem()
    elif problem_type == 'combine_lcm':
        return generate_combine_lcm_problem()
    else: # from_equation
        return generate_from_equation_problem()

def generate_direct_ratio_problem():
    """
    題型：給定三個數量，求其連比。
    例如：蘋果汁 3 杯、鳳梨汁 2 杯、胡蘿蔔汁 5 杯，連比為 3:2:5。
    """
    a = random.randint(2, 10)
    b = random.randint(2, 10)
    c = random.randint(2, 10)
    
    items = random.sample(['紅色積木', '藍色積木', '綠色積木', '黃色球', '白色球', '黑色球'], 3)
    
    question_text = f"一個箱子裡有 {a} 個{items[0]}、{b} 個{items[1]} 和 {c} 個{items[2]}。請問{items[0]}、{items[1]}與{items[2]}的數量連比為何？(請以最簡整數比表示)"
    
    common_divisor = gcd(gcd(a, b), c)
    ans_a = a // common_divisor
    ans_b = b // common_divisor
    ans_c = c // common_divisor
    
    correct_answer = f"{ans_a}:{ans_b}:{ans_c}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_simplify_ratio_problem():
    """
    題型：化簡連比或求連比中的未知數。
    例如：若 15:20:25 = □:△:5，求 □ 和 △。
    """
    a = random.randint(2, 5)
    b = random.randint(2, 5)
    c = random.randint(2, 5)
    while a == b and b == c: # Ensure they are not all the same
        a, b, c = random.randint(2, 5), random.randint(2, 5), random.randint(2, 5)

    m = random.randint(2, 5)
    
    A, B, C = a * m, b * m, c * m
    
    reveal_idx = random.randint(0, 2)
    
    q_placeholders = ['\\square', '\\triangle']
    ans_vars = []
    ans_vals = []
    simplified_ratio_parts = [a, b, c]
    
    final_ratio_str_parts = [""] * 3
    
    for i in range(3):
        if i == reveal_idx:
            final_ratio_str_parts[i] = str(simplified_ratio_parts[i])
        else:
            placeholder = q_placeholders.pop(0)
            final_ratio_str_parts[i] = placeholder
            ans_vars.append(placeholder)
            ans_vals.append(str(simplified_ratio_parts[i]))
            
    final_ratio_str = ":".join(final_ratio_str_parts)
    ans_vars_str = "、".join(ans_vars)
    
    question_text = f"若 ${A}:{B}:{C} = {final_ratio_str}$，則 ${ans_vars_str}$ 的值分別為多少？(請依序用逗號分隔)"
    correct_answer = ",".join(ans_vals)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_combine_easy_problem():
    """
    題型：合併兩個比，其共同項的對應數字相同。
    例如：a:b = 2:3, b:c = 3:4，求 a:b:c。
    """
    v_common = random.randint(2, 10)
    v1, v2 = random.sample([i for i in range(2, 11) if i != v_common], 2)
    
    var_names = random.sample(['x', 'y', 'z'], 3)
    
    common_pos = random.choice(['first', 'middle', 'last'])
    
    if common_pos == 'middle':
        q_text = f"設 ${var_names[0]}:{var_names[1]} = {v1}:{v_common}$，${var_names[1]}:{var_names[2]} = {v_common}:{v2}$，求 ${var_names[0]}:{var_names[1]}:{var_names[2]}$。"
        final_parts = [v1, v_common, v2]
    elif common_pos == 'last':
        q_text = f"設 ${var_names[0]}:{var_names[2]} = {v1}:{v_common}$，${var_names[1]}:{var_names[2]} = {v2}:{v_common}$，求 ${var_names[0]}:{var_names[1]}:{var_names[2]}$。"
        final_parts = [v1, v2, v_common]
    else: # 'first'
        q_text = f"設 ${var_names[0]}:{var_names[1]} = {v_common}:{v1}$，${var_names[0]}:{var_names[2]} = {v_common}:{v2}$，求 ${var_names[0]}:{var_names[1]}:{var_names[2]}$。"
        final_parts = [v_common, v1, v2]
    
    common_divisor = gcd(gcd(final_parts[0], final_parts[1]), final_parts[2])
    simplified_parts = [p // common_divisor for p in final_parts]
    correct_answer = ":".join(map(str, simplified_parts))

    q_text += "(請以最簡整數比表示)"

    return {
        "question_text": q_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_combine_lcm_problem():
    """
    題型：合併兩個比，其共同項的對應數字不同。
    例如：x:y = 3:4, y:z = 2:7，求 x:y:z。
    """
    var_names = random.sample(['x', 'y', 'z'], 3)
    
    v1 = random.randint(2, 9)
    v2 = random.randint(2, 9)
    c1, c2 = random.sample(range(2, 10), 2)
    while c1 % c2 == 0 or c2 % c1 == 0: # Avoid simple multiple cases
        c1, c2 = random.sample(range(2, 10), 2)
        
    common_var_idx = random.randint(0, 2)
    common_var = var_names[common_var_idx]
    other_vars = [v for v in var_names if v != common_var]
    
    order_rand = random.random()
    if order_rand < 0.25: # a:b, b:c
        ratio1_str = f"${other_vars[0]}:{common_var} = {v1}:{c1}$"
        ratio2_str = f"${common_var}:{other_vars[1]} = {c2}:{v2}$"
        L = lcm(c1, c2)
        final_vals = {other_vars[0]: v1 * (L//c1), common_var: L, other_vars[1]: v2 * (L//c2)}
    elif order_rand < 0.5: # b:a, b:c
        ratio1_str = f"${common_var}:{other_vars[0]} = {c1}:{v1}$"
        ratio2_str = f"${common_var}:{other_vars[1]} = {c2}:{v2}$"
        L = lcm(c1, c2)
        final_vals = {common_var: L, other_vars[0]: v1 * (L//c1), other_vars[1]: v2 * (L//c2)}
    elif order_rand < 0.75: # a:c, b:c
        ratio1_str = f"${other_vars[0]}:{common_var} = {v1}:{c1}$"
        ratio2_str = f"${other_vars[1]}:{common_var} = {v2}:{c2}$"
        L = lcm(c1, c2)
        final_vals = {other_vars[0]: v1 * (L//c1), other_vars[1]: v2 * (L//c2), common_var: L}
    else: # c:a, c:b
        ratio1_str = f"${common_var}:{other_vars[0]} = {c1}:{v1}$"
        ratio2_str = f"${common_var}:{other_vars[1]} = {c2}:{v2}$"
        L = lcm(c1, c2)
        final_vals = {common_var: L, other_vars[0]: v1 * (L//c1), other_vars[1]: v2 * (L//c2)}

    final_parts = [final_vals[v] for v in var_names]
    common_divisor = gcd(gcd(final_parts[0], final_parts[1]), final_parts[2])
    simplified_parts = [p // common_divisor for p in final_parts]
    correct_answer = ":".join(map(str, simplified_parts))
    
    question_text = f"設 {ratio1_str}，{ratio2_str}，求 ${':'.join(var_names)}$。(請以最簡整數比表示)"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_from_equation_problem():
    """
    題型：從等式求連比。
    例如：2x = 3y, 4y = 5z，求 x:y:z。
    """
    var_names = random.sample(['x', 'y', 'z'], 3)
    
    common_var_idx = random.randint(0, 2)
    common_var = var_names[common_var_idx]
    other_vars = [v for v in var_names if v != common_var]
    
    a, b = random.randint(2, 9), random.randint(2, 9)
    c, d = random.randint(2, 9), random.randint(2, 9)
    while b == d or b % d == 0 or d % b == 0: # Avoid simple multiple cases for ratio values
        b, d = random.randint(2, 9), random.randint(2, 9)

    # Eq1: a*other[0] = b*common  => other[0]:common = b:a
    # Eq2: c*other[1] = d*common  => other[1]:common = d:c
    eq1_str = f"${a}{other_vars[0]} = {b}{common_var}$"
    eq2_str = f"${c}{other_vars[1]} = {d}{common_var}$"
    
    # Common term corresponds to 'a' and 'c' in the ratios
    L = lcm(a, c)
    
    final_vals = {
        other_vars[0]: b * (L // a),
        other_vars[1]: d * (L // c),
        common_var: L
    }
    
    final_parts = [final_vals[v] for v in var_names]
    common_divisor = gcd(gcd(final_parts[0], final_parts[1]), final_parts[2])
    simplified_parts = [p // common_divisor for p in final_parts]
    correct_answer = ":".join(map(str, simplified_parts))

    question_text = f"設 $x、y、z$ 皆不為 0，且 {eq1_str}、{eq2_str}，求 ${':'.join(var_names)}$。(請以最簡整數比表示)"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_ans_std = user_answer.strip().replace(' ', '').replace('：', ':').replace('，', ',')
    corr_ans_std = correct_answer.strip().replace(' ', '').replace('：', ':').replace('，', ',')
    
    is_correct = (user_ans_std == corr_ans_std)

    result_text = f"完全正確！答案是 ${corr_ans_std}$。" if is_correct else f"答案不正確。正確答案應為：${corr_ans_std}$"
    
    return {"correct": is_correct, "result": result_text, "next_question": True}