import random
from fractions import Fraction

def _fraction_to_latex(f_obj):
    """Converts a Fraction object or a string representation to a LaTeX string."""
    try:
        f = Fraction(f_obj)
        if f.denominator == 1:
            return str(f.numerator)
        
        if f.numerator < 0:
            return f"-\\frac{{{abs(f.numerator)}}}{{{f.denominator}}}"
        else:
            return f"\\frac{{{f.numerator}}}{{{f.denominator}}}"
    except (ValueError, TypeError):
        return str(f_obj) # Fallback for non-fraction strings like "3:4"

def generate(level=1):
    """
    生成「比與比值」相關題目 (標準 LaTeX 範本)。
    包含：
    1. 生活情境題 (求比值或倍數)
    2. 比率問題 (求未知數)
    3. 比率問題 (求總數)
    4. 純計算 (求比值)
    5. 比例式 (求未知數)
    """
    problem_types = [
        'recipe_ratio',
        'rate_solve_x',
        'rate_solve_total',
        'pure_ratio_value',
        'proportionality'
    ]
    problem_type = random.choice(problem_types)

    if problem_type == 'recipe_ratio':
        return generate_recipe_ratio_problem()
    elif problem_type == 'rate_solve_x':
        return generate_rate_solve_x_problem()
    elif problem_type == 'rate_solve_total':
        return generate_rate_solve_total_problem()
    elif problem_type == 'pure_ratio_value':
        return generate_pure_ratio_value_problem()
    elif problem_type == 'proportionality':
        return generate_proportionality_problem()

def generate_recipe_ratio_problem():
    scenarios = [
        {
            "context": "調製泡泡水", "unit": "公克",
            "items": [("清水", 200), ("洗碗精", 100), ("膠水", 50)]
        },
        {
            "context": "調配消毒酒精", "unit": "c.c.",
            "items": [("精製酒精", 300), ("純水", 80)]
        },
        {
            "context": "製作特調奶茶", "unit": "毫升",
            "items": [("紅茶", 250), ("鮮奶", 150), ("糖漿", 25)]
        },
        {
            "context": "烘焙餅乾", "unit": "克",
            "items": [("麵粉", 300), ("奶油", 180), ("糖", 120)]
        }
    ]
    
    scenario = random.choice(scenarios)
    item1, item2 = random.sample(scenario["items"], 2)
    
    name1, qty1 = item1
    name2, qty2 = item2
    
    if random.random() < 0.5:
        name1, name2, qty1, qty2 = name2, name1, qty2, qty1

    sub_type = random.choice(['get_ratio', 'get_value', 'get_times'])
    
    ratio_val = Fraction(qty1, qty2)
    simplified_ratio_str = f"{ratio_val.numerator}:${ratio_val.denominator}"

    if sub_type == 'get_ratio':
        question_text = (
            f"在「{scenario['context']}」的配方中，"
            f"「{name1}」的用量為 ${qty1}$ {scenario['unit']}，"
            f"「{name2}」的用量為 ${qty2}$ {scenario['unit']}。<br>"
            f"請問「{name1}」用量與「{name2}」用量的最簡整數比為何？"
        )
        correct_answer = simplified_ratio_str
    elif sub_type == 'get_value':
        question_text = (
            f"在「{scenario['context']}」的配方中，"
            f"「{name1}」的用量為 ${qty1}$ {scenario['unit']}，"
            f"「{name2}」的用量為 ${qty2}$ {scenario['unit']}。<br>"
            f"請問「{name1}」用量與「{name2}」用量的比值為何？(以最簡分數或整數表示)"
        )
        correct_answer = str(ratio_val)
    else: # 'get_times'
        question_text = (
            f"在「{scenario['context']}」的配方中，"
            f"「{name1}」的用量為 ${qty1}$ {scenario['unit']}，"
            f"「{name2}」的用量為 ${qty2}$ {scenario['unit']}。<br>"
            f"請問「{name1}」的用量是「{name2}」用量的幾倍？(以最簡分數或整數表示)"
        )
        correct_answer = str(ratio_val)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_rate_solve_x_problem():
    context = random.choice([
        {"noun": "打數", "verb": "安打", "rate": "打擊率", "unit": "支"},
        {"noun": "投籃數", "verb": "命中", "rate": "命中率", "unit": "球"},
        {"noun": "測驗題數", "verb": "答對", "rate": "答對率", "unit": "題"},
    ])

    x, initial_successes, total_trials = 0, 0, 0
    while not (5 <= x <= 40 and initial_successes > 0 and initial_successes < total_trials * 0.4):
        future_trials = random.randint(20, 50)
        x = random.randint(5, future_trials - 2)
        initial_trials = random.randint(80, 160)
        total_trials = initial_trials + future_trials

        possible_total_successes = []
        for s in range(int(total_trials * 0.2), int(total_trials * 0.6)):
            if (s * 100) % total_trials == 0:
                rate_percent = (s * 100) // total_trials
                if rate_percent % 5 == 0:
                    possible_total_successes.append(s)
        
        if not possible_total_successes:
            continue

        total_successes = random.choice(possible_total_successes)
        initial_successes = total_successes - x

    target_rate_percent = (total_successes * 100) // total_trials

    question_text = (
        f"某選手在過去 ${initial_trials}$ 次{context['noun']}中，"
        f"共有 ${initial_successes}$ {context['unit']}的{context['verb']}。<br>"
        f"如果他希望在接下來的 ${future_trials}$ 次{context['noun']}中，"
        f"將整體的{context['rate']}提升到 ${target_rate_percent}\%$，"
        f"則他必須再有幾{context['unit']}的{context['verb']}？"
    )
    
    correct_answer = str(x)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_rate_solve_total_problem():
    context = random.choice([
        {"noun": "總投球數", "verb": "投進", "rate": "命中率", "unit": "球"},
        {"noun": "總題數", "verb": "答對", "rate": "答對率", "unit": "題"},
        {"noun": "總人數", "verb": "通過測驗", "rate": "通過率", "unit": "人"},
    ])
    
    rate_percent = random.choice([10, 20, 25, 30, 40, 50, 60, 70, 75, 80, 90])
    rate_frac = Fraction(rate_percent, 100)
    n, d = rate_frac.numerator, rate_frac.denominator

    multiplier = random.randint(2, 10)
    successes = n * multiplier
    total = d * multiplier

    question_text = (
        f"在某次活動中，已知{context['verb']}了 ${successes}$ {context['unit']}。"
        f"若此次活動的{context['rate']}為 ${rate_percent}\%$，"
        f"請問{context['noun']}為多少{context['unit']}？"
    )
    
    correct_answer = str(total)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_pure_ratio_value_problem():
    problem_subtype = random.choice(['int', 'frac', 'decimal'])
    
    if problem_subtype == 'int':
        a = random.choice([i for i in range(-20, 21) if i != 0])
        b = random.choice([i for i in range(-20, 21) if i != 0])
        
        a_str = f"({a})" if a < 0 else str(a)
        b_str = f"({b})" if b < 0 else str(b)
        
    elif problem_subtype == 'frac':
        n1 = random.choice([i for i in range(-9, 10) if i != 0])
        d1 = random.randint(2, 9)
        a = Fraction(n1, d1)
        
        n2 = random.choice([i for i in range(-9, 10) if i != 0])
        d2 = random.randint(2, 9)
        b = Fraction(n2, d2)

        def frac_to_latex_display(f):
            if f.denominator == 1:
                return f"({f.numerator})" if f.numerator < 0 else str(f.numerator)
            num, den = f.numerator, f.denominator
            if num < 0:
                return f"(-\\frac{{{abs(num)}}}{{{den}}})"
            else:
                return f"\\frac{{{num}}}{{{den}}}"

        a_str = frac_to_latex_display(a)
        b_str = frac_to_latex_display(b)
        
    else: # decimal
        a = round(random.uniform(-5, 5), 1)
        while a == 0: a = round(random.uniform(-5, 5), 1)
        b = round(random.uniform(-5, 5), 1)
        while b == 0: b = round(random.uniform(-5, 5), 1)

        a_str = f"({a})" if a < 0 else str(a)
        b_str = f"({b})" if b < 0 else str(b)
        a = Fraction(str(a))
        b = Fraction(str(b))

    question_text = f"求比 ${a_str}：${b_str}$ 的比值，並以最簡分數或整數表示。"
    result = a / b
    correct_answer = str(result)
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_proportionality_problem():
    a = random.choice([i for i in range(-10, 11) if i != 0])
    b = random.choice([i for i in range(-10, 11) if i != 0])
    m = random.choice([i for i in range(-5, 6) if i not in [0, 1, -1]])
    
    c = a * m
    d = b * m
    
    values = [a, b, c, d]
    missing_idx = random.randint(0, 3)
    correct_answer = str(values[missing_idx])
    
    display_values = []
    for i, v in enumerate(values):
        val_str = f"({v})" if v < 0 else str(v)
        if i == missing_idx:
            display_values.append("\Box")
        else:
            display_values.append(val_str)
            
    a_disp, b_disp, c_disp, d_disp = display_values

    question_text = f"在下列的式子中，求 $\Box$ 所代表的數：<br>${a_disp}：${b_disp} = {c_disp}：${d_disp}$"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。能處理整數、分數、小數與比的格式。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    is_correct = False

    if ':' in correct_answer:
        user_ans_norm = ''.join(user_answer.replace('：', ':').split())
        corr_ans_norm = ''.join(correct_answer.replace('：', ':').split())
        is_correct = (user_ans_norm == corr_ans_norm)
    else:
        try:
            user_frac = Fraction(user_answer).limit_denominator()
            corr_frac = Fraction(correct_answer).limit_denominator()
            if user_frac == corr_frac:
                is_correct = True
        except (ValueError, ZeroDivisionError):
            pass

    display_answer = correct_answer
    if ':' not in correct_answer:
        display_answer = _fraction_to_latex(correct_answer)

    result_text = f"完全正確！答案是 ${display_answer}$。" if is_correct else f"答案不正確。正確答案應為：${display_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}
