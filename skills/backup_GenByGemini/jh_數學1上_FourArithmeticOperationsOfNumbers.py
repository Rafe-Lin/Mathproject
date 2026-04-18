import random
from fractions import Fraction

def _format_number_latex(num):
    """將數字 (int, float, Fraction) 格式化為 LaTeX 字串 (整數、帶分數或真分數)"""
    if not isinstance(num, Fraction):
        num = Fraction(num).limit_denominator()

    if num.denominator == 1:
        return str(num.numerator)

    sign = ""
    if num < 0:
        sign = "-"
        num = abs(num)

    if num.numerator > num.denominator:
        integer_part = num.numerator // num.denominator
        rem_numerator = num.numerator % num.denominator
        if rem_numerator == 0:
            return f"{sign}{integer_part}"
        return f"{sign}{integer_part}\\frac{{{rem_numerator}}}{{{num.denominator}}}"
    else:
        return f"{sign}\\frac{{{num.numerator}}}{{{num.denominator}}}"

def _format_answer(num):
    """將 Fraction 物件格式化為用於答案比對的標準字串 (例如: '1', '-5', '1/3', '1 1/2')"""
    if not isinstance(num, Fraction):
        num = Fraction(num).limit_denominator()

    if num.denominator == 1:
        return str(num.numerator)

    sign = ""
    if num < 0:
        sign = "-"
        num = abs(num)
    
    if num.numerator > num.denominator:
        integer_part = num.numerator // num.denominator
        rem_numerator = num.numerator % num.denominator
        if rem_numerator == 0:
            return f"{sign}{integer_part}"
        return f"{sign}{integer_part} {rem_numerator}/{num.denominator}"
    else:
        return f"{sign}{num.numerator}/{num.denominator}"

def generate(level=1):
    """
    生成「數的四則運算」相關題目。
    包含：
    1. 純計算 (整數、分數、小數混合)
    2. 分配律應用
    3. 應用題
    """
    problem_type = random.choice(['mixed_ops', 'distributive', 'word_problem'])

    if problem_type == 'mixed_ops':
        return generate_mixed_operations_problem()
    elif problem_type == 'distributive':
        return generate_distributive_property_problem()
    else:
        return generate_word_problem()

def generate_mixed_operations_problem():
    """生成混合四則運算題目，如: 3/2÷(-0.6)×(-3/5)-1/2"""
    
    def get_term():
        term_type = random.choice(['int', 'frac', 'decimal'])
        if term_type == 'int':
            val = random.randint(-9, 9)
            val = val if val != 0 else 1
            return Fraction(val), str(val)
        elif term_type == 'frac':
            den = random.randint(2, 9)
            num = random.randint(1, den - 1)
            f = Fraction(num, den) * random.choice([-1, 1])
            return f, _format_number_latex(f)
        else: # decimal
            d = random.choice([-0.5, 0.25, 1.5, -0.6, -1.25, 0.2, 0.4])
            return Fraction(d), str(d)

    n1_f, n1_s = get_term()
    n2_f, n2_s = get_term()
    n3_f, n3_s = get_term()

    op1 = random.choice(['\\times', '\\div'])
    op2 = random.choice(['+', '-'])

    # 處理負數時的括號
    if n2_f < 0: n2_s = f"({n2_s})"
    if n3_f < 0: n3_s = f"({n3_s})"

    question_text = f"計算下列各式的值。\n${n1_s} {op1} {n2_s} {op2} {n3_s}$"

    # 計算答案
    result = Fraction(0)
    if op1 == '\\times':
        temp_result = n1_f * n2_f
    else: # div
        temp_result = n1_f / n2_f

    if op2 == '+':
        result = temp_result + n3_f
    else:
        result = temp_result - n3_f
    
    correct_answer = _format_answer(result)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_distributive_property_problem():
    """生成使用分配律的題目，如: 3 9/11×(-57) - 1 9/11×(-57)"""
    c = random.randint(-100, 100)
    while c in [-1, 0, 1]:
        c = random.randint(-50, 50)

    den = random.randint(5, 15)
    num = random.randint(1, den - 1)
    frac_part = Fraction(num, den)

    int_a = random.randint(5, 20)
    int_b = random.randint(1, int_a - 1)

    a = int_a + frac_part
    b = int_b + frac_part
    op_str, op_func = random.choice([('+', lambda x, y: x + y), ('-', lambda x, y: x - y)])

    result = op_func(a - b if random.random() < 0.8 else a, b) * c
    if op_str == '-':
        result = (a - b) * c
    else:
        result = (a + b) * c

    a_s = _format_number_latex(a)
    b_s = _format_number_latex(b)
    c_s = f"({c})" if c < 0 else str(c)

    terms = [f"{a_s} \\times {c_s}", f"{b_s} \\times {c_s}"]
    random.shuffle(terms)

    question_text = f"計算下列各式的值。\n${terms[0]} {op_str} {terms[1]}$"
    correct_answer = _format_answer(result)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_word_problem():
    """隨機生成一種應用題"""
    if random.random() < 0.5:
        return generate_juice_word_problem()
    else:
        return generate_drone_word_problem()

def generate_juice_word_problem():
    """生成果汁與瓶重問題"""
    den = random.randint(3, 8)
    num = random.randint(1, den - 1)
    frac_drunk = Fraction(num, den)

    juice_w = random.randint(10, 50) * den
    bottle_w = random.randint(100, 400)

    total_w = bottle_w + juice_w
    juice_drunk_w = juice_w * frac_drunk
    remaining_w = int(total_w - juice_drunk_w)

    frac_drunk_s = _format_number_latex(frac_drunk)

    question_text = f"有一瓶果汁，連瓶子共重 ${total_w}$ 公克，喝了 ${frac_drunk_s}$ 瓶的果汁後，剩餘的果汁連瓶子共重 ${remaining_w}$ 公克，求空瓶子重多少公克？"
    correct_answer = str(bottle_w)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_drone_word_problem():
    """生成無人機與農藥重量問題"""
    T = random.randint(4, 6) * 10
    t = random.randint(1, T // 10 - 1) * 10

    time_frac = Fraction(t, T)
    sprayed_w = random.randint(4, 10) * time_frac.numerator
    total_pesticide_w = int(sprayed_w / time_frac)

    drone_w = random.randint(20, 40)
    total_w_full = drone_w + total_pesticide_w
    weight_after_t = total_w_full - sprayed_w

    unit = "公斤"

    question_text = f"一臺農用無人機裝滿農藥的重量為 ${total_w_full}$ {unit}，若每分鐘噴灑的農藥重量皆相等，噴灑飛行 ${T}$ 分鐘後，可將農藥噴完沒有剩下。某次此無人機裝滿農藥噴灑飛行 ${t}$ 分鐘後，無人機與剩餘農藥重量為 ${weight_after_t}$ {unit}，則此無人機未裝農藥時的重量為多少{unit}？"
    correct_answer = str(drone_w)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確，能處理整數、小數、分數與帶分數。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    is_correct = False

    try:
        # 處理帶分數格式，例如 '1 1/2'
        def parse_to_fraction(s):
            s = s.strip()
            if ' ' in s and '/' in s:
                parts = s.split(' ')
                if len(parts) == 2:
                    whole = Fraction(parts[0])
                    frac = Fraction(parts[1])
                    return whole + frac if whole >= 0 else whole - frac
            return Fraction(s)

        user_frac = parse_to_fraction(user_answer).limit_denominator()
        correct_frac = parse_to_fraction(correct_answer).limit_denominator()

        if user_frac == correct_frac:
            is_correct = True
            
    except (ValueError, ZeroDivisionError):
        # 如果無法轉換為分數，則進行字串比較
        if user_answer.upper() == correct_answer.upper():
            is_correct = True

    # 使用 LaTeX 格式化正確答案以供顯示
    try:
        correct_answer_latex = _format_number_latex(Fraction(correct_answer))
    except (ValueError, ZeroDivisionError):
        correct_answer_latex = correct_answer

    result_text = f"完全正確！答案是 ${correct_answer_latex}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer_latex}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}
