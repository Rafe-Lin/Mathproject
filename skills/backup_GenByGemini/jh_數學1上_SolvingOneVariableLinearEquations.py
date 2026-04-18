import random
from fractions import Fraction

def generate(level=1):
    """
    生成「一元一次方程式」相關題目。
    包含：
    1. 代入求值 (檢驗解)
    2. 移項求解 (整數解)
    3. 去括號求解 (整數解)
    4. 分數型方程式 (分數解)
    """
    # 根據難度調整題型權重
    if level == 1:
        problem_types = ['substitution', 'simple_equation']
    else:
        problem_types = ['simple_equation', 'parentheses', 'fractional']
    
    problem_type = random.choice(problem_types)
    
    if problem_type == 'substitution':
        return generate_substitution_problem()
    elif problem_type == 'simple_equation':
        return generate_simple_equation_problem()
    elif problem_type == 'parentheses':
        return generate_parentheses_problem()
    else: # fractional
        return generate_fractional_equation_problem()

def _format_equation_side(x_coeff, const):
    """輔助函式，用於格式化方程式的一邊 (例如: 5x - 3)"""
    parts = []
    if x_coeff == 1:
        parts.append("x")
    elif x_coeff == -1:
        parts.append("-x")
    elif x_coeff != 0:
        parts.append(f"{x_coeff}x")

    if const != 0:
        if parts:
            if const > 0:
                parts.append(f"+ {const}")
            else:
                parts.append(f"- {abs(const)}")
        else:
            parts.append(str(const))
    
    if not parts:
        return "0"
    
    return " ".join(parts)

def generate_substitution_problem():
    """題型1：檢驗看看, -2、8、11 三數中, 哪一個是方程式 ... 的解？"""
    a = random.choice([-4, -3, -2, 2, 3, 4, 5])
    x = random.randint(-9, 9)
    b = random.randint(-15, 15)
    c = a * x + b

    # 產生干擾選項
    options = {x}
    while len(options) < 3:
        offset = random.choice([-3, -2, -1, 1, 2, 3])
        options.add(x + offset)
    
    shuffled_options = random.sample(list(options), 3)
    options_str = '、'.join(map(str, shuffled_options))

    # 格式化方程式字串
    ax_part = ""
    if a == 1:
        ax_part = "x"
    elif a == -1:
        ax_part = "-x"
    else:
        ax_part = f"{a}x"

    b_part = ""
    if b > 0:
        b_part = f" + {b}"
    elif b < 0:
        b_part = f" - {abs(b)}"

    equation_str = f"{ax_part}{b_part} = {c}"

    question_text = f"檢驗看看, {options_str} 三數中, 哪一個是方程式 ${equation_str}$ 的解？"
    correct_answer = str(x)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "input_type": "text"
    }

def generate_simple_equation_problem():
    """題型2：解一元一次方程式 ax + b = cx + d (整數解)"""
    x = random.randint(-10, 10)
    a = random.choice(list(range(-7, 0)) + list(range(1, 8)))
    c = random.choice(list(range(-7, 8)))
    while a == c:
        c = random.choice(list(range(-7, 8)))
    
    b = random.randint(-15, 15)
    
    # 隨機簡化方程式結構
    if random.random() < 0.2: b = 0 # 形式: ax = cx + d
    if random.random() < 0.2: c = 0 # 形式: ax + b = d

    d = (a - c) * x + b

    left_str = _format_equation_side(a, b)
    right_str = _format_equation_side(c, d)

    question_text = f"解一元一次方程式 ${left_str} = {right_str}$。"
    correct_answer = str(x)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "input_type": "text"
    }

def generate_parentheses_problem():
    """題型3：解含括號的一元一次方程式 (整數解)"""
    x = random.randint(-8, 8)
    a = random.choice([-5, -4, -3, -2, 2, 3, 4, 5])
    
    b_x_coeff = random.choice([-3, -2, -1, 1, 2, 3])
    c_const = random.randint(-5, 5)

    d_x_coeff_rhs = random.randint(-5, 5)
    while a * b_x_coeff == d_x_coeff_rhs:
        d_x_coeff_rhs = random.randint(-5, 5)

    e_const_rhs = (a * b_x_coeff - d_x_coeff_rhs) * x + a * c_const

    inner_str = _format_equation_side(b_x_coeff, c_const)
    left_str = f"{a}({inner_str})"
    right_str = _format_equation_side(d_x_coeff_rhs, e_const_rhs)

    question_text = f"解一元一次方程式 ${left_str} = {right_str}$。"
    correct_answer = str(x)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "input_type": "text"
    }

def generate_fractional_equation_problem():
    """題型4：解分數型一元一次方程式 (解可能為分數)"""
    d1, d2 = random.sample(list(range(2, 8)), 2)
    k1, k2 = random.randint(1, 3), random.randint(1, 3)
    c1, c2 = random.randint(-7, 7), random.randint(-7, 7)

    # 確保 x 的係數不為零
    while d2 * k1 == d1 * k2:
        k1, k2 = random.randint(1, 3), random.randint(1, 3)

    numerator_B = d1 * c2 - d2 * c1
    denominator_A = d2 * k1 - d1 * k2

    x = Fraction(numerator_B, denominator_A)

    num1_str = _format_equation_side(k1, c1)
    num2_str = _format_equation_side(k2, c2)

    left_frac = f"\\frac{{{num1_str}}}{{{d1}}}"
    right_frac = f"\\frac{{{num2_str}}}{{{d2}}}"

    question_text = f"解一元一次方程式 ${left_frac} = {right_frac}$。"
    correct_answer = str(x)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "input_type": "handwriting"
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip()
    # 允許 'x=5' 的格式
    if user_answer.lower().startswith('x='):
        user_answer = user_answer[2:].strip()

    correct_answer_str = str(correct_answer).strip()
    is_correct = False
    try:
        # 使用 Fraction 比較，可同時處理整數、小數和分數
        if Fraction(user_answer) == Fraction(correct_answer_str):
            is_correct = True
    except (ValueError, ZeroDivisionError):
        # 若轉換失敗 (例如非數字答案)，則維持 is_correct = False
        pass
    
    # TeXify the correct answer for display
    try:
        f_ans = Fraction(correct_answer_str)
        if f_ans.denominator == 1:
            ans_tex = str(f_ans.numerator)
        else:
            ans_tex = f"\\frac{{{f_ans.numerator}}}{{{f_ans.denominator}}}"
    except ValueError:
        ans_tex = correct_answer_str

    result_text = f"完全正確！答案是 ${ans_tex}$。" if is_correct else f"答案不正確。正確答案應為：${ans_tex}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}
