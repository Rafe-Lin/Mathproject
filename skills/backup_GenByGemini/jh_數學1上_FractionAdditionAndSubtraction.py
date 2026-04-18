import random
from fractions import Fraction
import math

def latex_frac(f, use_mixed=False, add_paren_on_neg=False):
    """
    將 Fraction 物件轉換為 LaTeX 字串。
    - f: Fraction 物件
    - use_mixed: 是否使用帶分數表示
    - add_paren_on_neg: 是否在負數時加上括號
    """
    if f.denominator == 1:
        val_str = str(f.numerator)
        if add_paren_on_neg and f.numerator < 0:
            return f"({val_str})"
        return val_str

    sign = ""
    f_abs = f
    if f < 0:
        sign = "-"
        f_abs = abs(f)

    if use_mixed and f_abs.numerator >= f_abs.denominator:
        i_part = f_abs.numerator // f_abs.denominator
        n_part = f_abs.numerator % f_abs.denominator
        if n_part == 0:  # 剛好是整數
            val_str = f"{sign}{i_part}"
        else:
            val_str = f"{sign}{i_part} \\frac{{{n_part}}}{{{f_abs.denominator}}}"
    else:
        val_str = f"{sign}\\frac{{{f_abs.numerator}}}{{{f_abs.denominator}}}"

    if add_paren_on_neg and f < 0:
        return f"({val_str})"
    return val_str

def format_answer(f):
    """將 Fraction 物件格式化為標準答案字串 (假分數或帶分數)。"""
    if f.denominator == 1:
        return str(f.numerator)

    improper_str = f"{f.numerator}/{f.denominator}"

    if abs(f.numerator) >= f.denominator:
        sign = -1 if f < 0 else 1
        f_abs = abs(f)
        i_part = f_abs.numerator // f_abs.denominator
        n_part = f_abs.numerator % f_abs.denominator

        if n_part == 0:
            return improper_str

        mixed_str = f"{sign * i_part} {n_part}/{f_abs.denominator}"
        return f"{improper_str} (或 {mixed_str})"
    else:
        return improper_str


def generate_simple_fraction(min_den=2, max_den=12, max_num_factor=1.5):
    """生成一個簡單的分數"""
    den = random.randint(min_den, max_den)
    max_num = int(den * max_num_factor)
    num = random.choice(list(range(-max_num, -0)) + list(range(1, max_num + 1)))
    return Fraction(num, den)


def generate_mixed_fraction():
    """生成一個帶分數"""
    i = random.choice(list(range(-5, 0)) + list(range(1, 6)))
    d = random.randint(2, 12)
    n = random.randint(1, d - 1)
    if i > 0:
        return Fraction(i * d + n, d)
    else:
        return Fraction(i * d - n, d)

def generate_same_denominator_problem():
    """題型：同分母分數加減"""
    d = random.randint(2, 15)
    n1 = random.choice(list(range(-2 * d, -0)) + list(range(1, 2 * d + 1)))
    n2 = random.choice(list(range(-d, -0)) + list(range(1, d + 1)))
    
    f1 = Fraction(n1, d)
    f2 = Fraction(n2, d)
    op = random.choice(['+', '-'])

    if op == '+':
        result = f1 + f2
    else:
        result = f1 - f2
    
    question_text = f"計算 ${latex_frac(f1, add_paren_on_neg=True)} {op} {latex_frac(f2, add_paren_on_neg=True)}$ 的值。"
    correct_answer = format_answer(result)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_diff_denominator_problem():
    """題型：異分母分數加減 (2-3項)"""
    num_terms = random.choice([2, 3])
    denominators = random.sample([2, 3, 4, 5, 6, 7, 8, 9, 12], num_terms)
    fractions = []
    for d in denominators:
        max_n = int(d * 1.5)
        n = random.choice(list(range(-max_n, -0)) + list(range(1, max_n + 1)))
        fractions.append(Fraction(n, d))
    
    ops = random.choices(['+', '-'], k=num_terms - 1)
    
    expr_list = [latex_frac(fractions[0], add_paren_on_neg=True)]
    result = fractions[0]
    for i in range(num_terms - 1):
        expr_list.append(f" {ops[i]} {latex_frac(fractions[i+1], add_paren_on_neg=True)}")
        if ops[i] == '+':
            result += fractions[i+1]
        else:
            result -= fractions[i+1]

    expression = "".join(expr_list)
    question_text = f"計算 ${expression}$ 的值。"
    correct_answer = format_answer(result)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_associative_problem():
    """題型：利用交換律/結合律簡化計算"""
    # 產生 f1, f3，使其運算後可簡化
    d_common = random.choice([11, 13, 17, 19, 22, 26, 29, 31, 91, 99])
    k = random.randint(1, 3)
    n_sum = k * d_common
    n1 = random.randint(1, n_sum - 1)
    n3 = n_sum - n1
    if random.random() < 0.5: n1 = -n1
    if random.random() < 0.5: n3 = -n3

    f1 = Fraction(n1, d_common)
    f3 = Fraction(n3, d_common)

    # 產生 f2
    d_other = random.choice([d for d in [2,3,4,5,6,7,8,9] if d_common % d != 0])
    f2 = generate_simple_fraction(min_den=d_other, max_den=d_other)
    
    op1 = random.choice(['+', '-'])
    op2 = random.choice(['+', '-'])

    # 隨機排列並加上括號
    terms = [f1, f2, f3]
    random.shuffle(terms)
    
    t1, t2, t3 = terms
    expression = f"{latex_frac(t1, add_paren_on_neg=True)} {op1} ({latex_frac(t2, add_paren_on_neg=True)} {op2} {latex_frac(t3, add_paren_on_neg=True)})"
    
    res_inner = t2 + t3 if op2 == '+' else t2 - t3
    result = t1 + res_inner if op1 == '+' else t1 - res_inner

    question_text = f"計算 ${expression}$ 的值。"
    correct_answer = format_answer(result)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_mixed_number_problem():
    """題型：帶分數加減"""
    num_terms = random.choice([2, 3])
    fractions = [generate_mixed_fraction() for _ in range(num_terms)]
    ops = random.choices(['+', '-'], k=num_terms - 1)

    result = fractions[0]
    expr_list = [latex_frac(fractions[0], use_mixed=True, add_paren_on_neg=True)]

    for i in range(num_terms - 1):
        expr_list.append(f" {ops[i]} {latex_frac(fractions[i+1], use_mixed=True, add_paren_on_neg=True)}")
        if ops[i] == '+':
            result += fractions[i+1]
        else:
            result -= fractions[i+1]
    
    expression = "".join(expr_list)
    question_text = f"計算 ${expression}$ 的值。"
    correct_answer = format_answer(result)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    生成「分數的加減」相關題目 (標準 LaTeX 範本)。
    包含：
    1. 同分母加減
    2. 異分母加減
    3. 結合律應用
    4. 帶分數加減
    """
    problem_type = random.choice(['same_denom', 'diff_denom', 'associative', 'mixed_numbers'])
    
    if problem_type == 'same_denom':
        return generate_same_denominator_problem()
    elif problem_type == 'diff_denom':
        return generate_diff_denominator_problem()
    elif problem_type == 'associative':
        return generate_associative_problem()
    else: # mixed_numbers
        return generate_mixed_number_problem()

def check(user_answer, correct_answer):
    """
    檢查答案是否正確，可接受假分數、帶分數、小數等格式。
    """
    def parse_to_fraction(s):
        s = s.strip()
        if ' ' in s:
            parts = s.split(' ', 1)
            if len(parts) == 2 and '/' in parts[1]:
                integer = int(parts[0])
                fractional = Fraction(parts[1])
                return Fraction(integer * fractional.denominator + fractional.numerator, fractional.denominator) if integer >= 0 else Fraction(integer * fractional.denominator - fractional.numerator, fractional.denominator)
        return Fraction(s).limit_denominator()

    try:
        correct_frac_str = correct_answer.split(' ')[0]
        correct_f = Fraction(correct_frac_str)
    except (ValueError, IndexError):
        # 若正確答案格式有誤，直接進行字串比對
        is_correct = user_answer.strip() == correct_answer.strip()
        result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
        return {"correct": is_correct, "result": result_text, "next_question": True}

    is_correct = False
    try:
        user_f = parse_to_fraction(user_answer)
        if user_f == correct_f:
            is_correct = True
    except (ValueError, ZeroDivisionError):
        try:
            if math.isclose(float(user_answer), float(correct_f)):
                is_correct = True
        except (ValueError, TypeError):
            pass

    def latex_answer_format(f):
        improper_latex = latex_frac(f)
        if f.denominator != 1 and abs(f.numerator) > f.denominator:
            mixed_latex = latex_frac(f, use_mixed=True)
            return f"${improper_latex}$ (或 ${mixed_latex}$)"
        return f"${improper_latex}$"

    latex_ans = latex_answer_format(correct_f)
    result_text = f"完全正確！答案是 {latex_ans}。" if is_correct else f"答案不正確。正確答案應為：${latex_ans}"
    
    return {"correct": is_correct, "result": result_text, "next_question": True}
