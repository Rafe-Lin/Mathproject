import random
from fractions import Fraction

def _latex_format(f, use_mixed=False):
    """
    將 Fraction 物件轉換為 LaTeX 格式的字串。
    - f: fractions.Fraction 物件。
    - use_mixed: 是否要轉換為帶分數。
    """
    if not isinstance(f, Fraction):
        f = Fraction(f)

    if f == 0:
        return "0"

    sign = "-" if f < 0 else ""
    f = abs(f)

    if f.denominator == 1:
        return f"{sign}{f.numerator}"

    if use_mixed and f.numerator > f.denominator:
        integer_part = f.numerator // f.denominator
        frac_part = f % 1
        if frac_part.numerator == 0: # Should not happen with f.denominator != 1 but as a safeguard
            return f"{sign}{integer_part}"
        return f"{sign}{integer_part}\\frac{{{frac_part.numerator}}}{{{frac_part.denominator}}}"
    else:
        return f"{sign}\\frac{{{f.numerator}}}{{{f.denominator}}}"

def _create_fraction(min_val=1, max_val=10, allow_improper=True, allow_negative=True):
    """生成一個隨機分數。"""
    den = random.randint(min_val + 1, max_val)
    if allow_improper:
        num = random.randint(min_val, max_val * 2)
    else:
        num = random.randint(min_val, den - 1)
    
    f = Fraction(num, den).limit_denominator(max_val + 5)
    
    if allow_negative and random.random() < 0.5:
        f = -f
        
    return f

def generate(level=1):
    """
    生成「分數的乘法」相關題目。
    包含：
    1. 兩個分數相乘 (可約分)
    2. 含帶分數或整數的乘法
    3. 連續乘法 (三個數)
    4. 分數的次方
    """
    problem_type = random.choice(['two_fractions', 'with_mixed', 'chain', 'exponent'])
    
    if problem_type == 'two_fractions':
        return generate_two_fractions_problem()
    elif problem_type == 'with_mixed':
        return generate_with_mixed_problem()
    elif problem_type == 'chain':
        return generate_chain_problem()
    else: # exponent
        return generate_exponent_problem()

def generate_two_fractions_problem():
    """題型1：兩個分數相乘，設計可約分的情境。"""
    # 為了製造可約分的情境，從質數因子建立分數
    factors = random.sample([2, 3, 5, 7, 11], 4)
    p1, p2, p3, p4 = factors

    n1 = p1 * random.randint(1, 3)
    d1 = p2 * random.randint(1, 3)
    n2 = p2 * random.randint(1, 3)
    d2 = p3 * random.randint(1, 3)

    f1 = Fraction(n1, d1)
    f2 = Fraction(n2, d2)

    if random.random() < 0.5:
        f1 = -f1
    if random.random() < 0.5:
        f2 = -f2

    result = f1 * f2

    # 產生 LaTeX 題目字串，負數要加括號
    f1_tex = f"({_latex_format(f1)})" if f1 < 0 else _latex_format(f1)
    f2_tex = f"({_latex_format(f2)})" if f2 < 0 else _latex_format(f2)

    question_text = f"計算 ${f1_tex} \\times {f2_tex}$ 的值。"
    
    # 標準答案格式為 n/d 或 n
    correct_answer = str(result.numerator) if result.denominator == 1 else f"{result.numerator}/{result.denominator}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_with_mixed_problem():
    """題型2：含帶分數或整數的乘法。"""
    # 生成一個帶分數
    i_part = random.randint(1, 3)
    f_part = _create_fraction(max_val=7, allow_improper=False, allow_negative=False)
    f1 = i_part + f_part
    if random.random() < 0.5:
        f1 = -f1

    # 另一個數可能是分數或整數
    if random.random() < 0.3:
        f2 = random.randint(2, 9)
        if random.random() < 0.5:
            f2 = -f2
    else:
        f2 = _create_fraction(max_val=9)

    # 隨機交換順序
    if random.random() < 0.5:
        f1, f2 = f2, f1

    result = f1 * f2

    f1_tex = f"({_latex_format(f1, use_mixed=True)})" if f1 < 0 else _latex_format(f1, use_mixed=True)
    f2_tex = f"({_latex_format(f2, use_mixed=True)})" if f2 < 0 else _latex_format(f2, use_mixed=True)

    question_text = f"計算 ${f1_tex} \\times {f2_tex}$ 的值。"
    correct_answer = str(result.numerator) if result.denominator == 1 else f"{result.numerator}/{result.denominator}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_chain_problem():
    """題型3：三個數連乘。"""
    fractions = [_create_fraction(max_val=7, allow_improper=True) for _ in range(3)]
    
    # 確保不會太複雜，分母太大的話重來
    result = fractions[0] * fractions[1] * fractions[2]
    while result.denominator > 100 or result.numerator > 200:
        fractions = [_create_fraction(max_val=7, allow_improper=True) for _ in range(3)]
        result = fractions[0] * fractions[1] * fractions[2]

    # 有機會將其中一個換成帶分數
    use_mixed_flags = [False, False, False]
    if random.random() < 0.4:
        idx = random.randint(0,2)
        if abs(fractions[idx].numerator) > fractions[idx].denominator:
            use_mixed_flags[idx] = True

    tex_parts = []
    for i, f in enumerate(fractions):
        tex = _latex_format(f, use_mixed=use_mixed_flags[i])
        if f < 0:
            tex_parts.append(f"({tex})")
        else:
            tex_parts.append(tex)

    question_text = f"計算 ${' \\times '.join(tex_parts)}$ 的值。"
    correct_answer = str(result.numerator) if result.denominator == 1 else f"{result.numerator}/{result.denominator}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_exponent_problem():
    """題型4：分數的次方。"""
    den = random.randint(2, 5)
    num = random.randint(1, den - 1)
    base = Fraction(num, den)
    if random.random() < 0.6:
        base = -base

    exp = random.randint(2, 4)

    result = base ** exp

    base_tex = _latex_format(base)
    question_text = f"計算 $({base_tex})^{{{exp}}}$ 的值。"
    correct_answer = str(result.numerator) if result.denominator == 1 else f"{result.numerator}/{result.denominator}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查使用者答案是否正確。能處理整數、分數、帶分數形式。
    """
    user_answer = user_answer.strip()
    is_correct = False

    try:
        correct_f = Fraction(correct_answer)
        user_f = None

        # 處理帶分數格式, e.g., "1 2/3" or "-2 1/4"
        if ' ' in user_answer and '/' in user_answer:
            parts = user_answer.split(' ')
            if len(parts) == 2:
                integer_part = int(parts[0])
                frac_part = Fraction(parts[1])
                if integer_part < 0:
                    user_f = integer_part - frac_part
                else:
                    user_f = integer_part + frac_part
        else:
            # 處理分數或整數格式
            user_f = Fraction(user_answer)

        if user_f is not None and user_f == correct_f:
            is_correct = True

    except (ValueError, ZeroDivisionError):
        is_correct = False

    # 產生包含 LaTeX 的答案說明
    final_answer_f = Fraction(correct_answer)
    display_answer_tex = _latex_format(final_answer_f)

    # 若為假分數，同時顯示帶分數
    if abs(final_answer_f.numerator) > final_answer_f.denominator and final_answer_f.denominator != 1:
        mixed_tex = _latex_format(final_answer_f, use_mixed=True)
        answer_display_str = f"${display_answer_tex}$ (或 ${mixed_tex}$)"
    else:
        answer_display_str = f"${display_answer_tex}$"

    if is_correct:
        result_text = f"完全正確！答案是 {answer_display_str}。"
    else:
        result_text = f"答案不正確。正確答案應為：{answer_display_str}"

    return {"correct": is_correct, "result": result_text, "next_question": True}
