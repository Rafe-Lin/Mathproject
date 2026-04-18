import random
from fractions import Fraction

def _get_base_latex_str(allow_neg=True, allow_frac=True):
    """Helper to generate a base for exponent problems in LaTeX format."""
    is_fraction = random.random() < 0.4 and allow_frac
    if is_fraction:
        num = random.randint(1, 5)
        den = random.randint(num + 1, 9)
        base_frac = Fraction(num, den)
        frac_latex = f"\\frac{{{base_frac.numerator}}}{{{base_frac.denominator}}}"
        if random.random() < 0.3 and allow_neg:
            return f"\\left(-{frac_latex}\\right)"
        else:
            return f"\\left({frac_latex}\\right)"
    else: # integer
        base_val = random.randint(2, 9)
        if random.random() < 0.3 and allow_neg:
            return f"({base_val})"
        else:
            return str(base_val)

def generate(level=1):
    """
    生成「指數律」相關題目 (標準 LaTeX 範本)。
    包含：    1. 指數律填空 (同底數乘除、次方乘方、積的次方、0次方)
    2. 指數律綜合計算
    3. 指數律應用題
    4. 指數律易錯題計算
    """
    if level == 1:
        problem_type = 'fill_in_the_blank'
    elif level == 2:
        problem_type = random.choice(['calculation', 'word_problem'])
    else: # level 3
        problem_type = random.choice(['calculation', 'error_analysis'])
    
    if problem_type == 'fill_in_the_blank':
        return generate_fill_in_the_blank_problem()
    elif problem_type == 'calculation':
        return generate_calculation_problem()
    elif problem_type == 'word_problem':
        return generate_word_problem()
    else: # 'error_analysis'
        return generate_error_analysis_problem()

def generate_fill_in_the_blank_problem():
    """生成指數律基礎填空題"""
    rule = random.choice(['product', 'quotient', 'power_of_power', 'power_of_product', 'zero_exponent'])
    
    question_prompt = "在下列□中填入適當的數，使等號成立。"

    if rule == 'product':
        base_str = _get_base_latex_str()
        m = random.randint(2, 9)
        n = random.randint(2, 9)
        question_text = f"{question_prompt}\n${base_str}^{{{m}}} \\times {base_str}^{{{n}}} = {base_str}^{{□}}$"
        correct_answer = str(m + n)
        
    elif rule == 'quotient':
        base_str = _get_base_latex_str()
        m = random.randint(5, 12)
        n = random.randint(2, m - 1)
        question_text = f"{question_prompt}\n${base_str}^{{{m}}} \\div {base_str}^{{{n}}} = {base_str}^{{□}}$"
        correct_answer = str(m - n)
        
    elif rule == 'power_of_power':
        base_str = _get_base_latex_str()
        m = random.randint(2, 5)
        n = random.randint(2, 5)
        question_text = f"{question_prompt}\n$\\left({base_str}^{{{m}}}\\right)^{{{n}}} = {base_str}^{{□}}$"
        correct_answer = str(m * n)

    elif rule == 'power_of_product':
        m = random.randint(2, 7)
        bases = random.sample([2, 3, 5, 7, 11], 2)
        base1_val, base2_val = bases[0], bases[1]
        question_text = f"{question_prompt}\n$\\left({base1_val} \\times {base2_val}\\right)^{{{m}}} = {base1_val}^{{□}} \\times {base2_val}^{{□}}$"
        correct_answer = str(m)
        
    elif rule == 'zero_exponent':
        base_str = _get_base_latex_str()
        if random.random() < 0.5:
            m = random.randint(2, 9)
            question_text = f"{question_prompt}\n${base_str}^{{{m}}} \\div {base_str}^{{{m}}} = {base_str}^{{□}}$"
            correct_answer = "0"
        else:
            question_text = f"{question_prompt}\n${base_str}^{{0}} = □$"
            correct_answer = "1"
            
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_calculation_problem():
    """生成指數律綜合計算題"""
    template = random.choice([1, 2])
    
    if template == 1:
        # (a^x * b)^y / (b^z)^w  where y=zw, simplifies to a^(xy)
        a = 2
        b = random.choice([3, 5])
        x = random.randint(2, 3)
        z = random.randint(2, 3)
        w = random.randint(2, 3)
        y = z * w
        expr = f"\\left({a}^{{{x}}} \\times {b}\\right)^{{{y}}} \\div \\left({b}^{{{z}}}\\right)^{{{w}}}"
        answer = a**(x*y)
    else:
        # (-(ac/b))^m * (b/c)^m / (-a)^n, simplifies to (-a)^(m-n)
        a = random.randint(2, 4)
        b, c = random.sample([5, 7, 11], 2)
        n = random.randint(3, 5)
        m = random.randint(n + 1, 9)
        frac1_num = a * c
        frac1_den = b
        frac2_num = b
        frac2_den = c
        expr = f"\\left(-\\frac{{{frac1_num}}}{{{frac1_den}}}\\right)^{{{m}}} \\times \\left(\\frac{{{frac2_num}}}{{{frac2_den}}}\\right)^{{{m}}} \\div (-{a})^{{{n}}}"
        answer = (-a)**(m-n)

    question_text = f"計算下列各式的值。\n${expr}$"
    correct_answer = str(answer)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_word_problem():
    """生成指數律應用題"""
    # 15天 = 360小時, 每20小時分裂一次, 共18次
    # 10天 = 240小時, 每12小時分裂一次, 共20次
    d_h_k = [
        (15, 20, 18),
        (10, 12, 20),
        (5, 6, 20),
        (20, 24, 20)
    ]
    d, h, k = random.choice(d_h_k)
    b = random.choice([2, 4])
    item = random.choice(["綠藻細胞", "A種細菌", "酵母菌"])
    
    question_text = f"假設在理想環境下，1 個{item}每 ${h}$ 小時可分裂成 ${b}$ 個。若從 1 個{item}開始培養，經過 ${d}$ 天後，共分裂成 ${b}^{{k}}$ 個，則 $k$ 之值為何？"
    correct_answer = str(k)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_error_analysis_problem():
    """生成指數律易錯觀念計算題"""
    # 基於 (-A)^E * -(B^E) 的易錯題型
    A = random.randint(2, 5)
    B = random.randint(2, 5)
    while A == B:
        B = random.randint(2, 5)
    
    E = random.choice([2, 4]) # 偶數次方，使 (-A)^E 為正
    
    # (-5)^6 * ( -2^6 ) is rendered as (-5)^{6} \\times (-2^{6})
    expr = f"(-{A})^{{{E}}} \\times (-{B}^{{{E}}})"
    
    question_text = f"計算下列各式的值。\n${expr}$"
    
    # 正確答案為 -(A*B)^E
    result = -((A * B) ** E)
    correct_answer = str(result)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip()
    correct_answer = str(correct_answer).strip()
    
    is_correct = (user_answer == correct_answer)
    
    if not is_correct:
        try:
            if float(user_answer) == float(correct_answer):
                is_correct = True
        except (ValueError, TypeError):
            pass

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}
