import random
from fractions import Fraction
import math

def generate(level=1):
    """
    生成「二元一次方程式圖形」相關題目。
    包含：
    1. 求兩軸截距與判斷象限
    2. 水平線與鉛直線
    3. 已知點求係數
    4. 判斷是否通過原點
    5. 已知兩點求方程式
    """
    problem_type = random.choice([
        'intercepts_quadrants',
        'special_lines',
        'find_coefficient',
        'check_origin',
        'find_equation_from_points'
    ])
    
    if problem_type == 'intercepts_quadrants':
        return generate_intercepts_quadrants_problem()
    elif problem_type == 'special_lines':
        return generate_special_lines_problem()
    elif problem_type == 'find_coefficient':
        return generate_find_coefficient_problem()
    elif problem_type == 'check_origin':
        return generate_check_origin_problem()
    else: # find_equation_from_points
        return generate_find_equation_from_points_problem()

def _format_number(n, force_sign=False):
    """Helper to format numbers, including Fractions into LaTeX."""
    if isinstance(n, Fraction):
        if n.denominator == 1:
            return _format_number(n.numerator, force_sign)
        sign = ""
        if n.numerator < 0:
            sign = "-"
            num = -n.numerator
        else:
            if force_sign:
                sign = "+"
            num = n.numerator
        return f"{sign}\\frac{{{num}}}{{{n.denominator}}}"
    else: # int
        if force_sign and n > 0:
            return f"+{n}"
        return str(n)

def _format_term(coeff, var):
    """Formats a single term like '2x' or '-x'."""
    if coeff == 0:
        return ""
    if abs(coeff) == 1:
        coeff_str = "" if coeff > 0 else "-"
    else:
        coeff_str = str(coeff)
    return f"{coeff_str}{var}"

def _format_equation(a, b, c, form='ax+by=c'):
    """Formats a linear equation from coefficients."""
    x_term = _format_term(a, 'x')
    y_term = _format_term(b, 'y')

    if not y_term:
        equation_body = x_term
    elif not x_term:
        equation_body = y_term
    else:
        if b > 0:
            y_part = f" + {y_term}"
        else: # b < 0, y_term already has '-'
            y_part = f" - {y_term[1:]}"
        equation_body = f"{x_term}{y_part}"
        
    if form == 'ax+by=c':
        return f"{equation_body} = {c}"
    else: # ax+by+c=0
        if c == 0:
            return f"{equation_body} = 0"
        elif c > 0:
            return f"{equation_body} + {c} = 0"
        else: # c < 0
            return f"{equation_body} - {abs(c)} = 0"

def generate_intercepts_quadrants_problem():
    x_int = random.choice([i for i in range(-8, 9) if i != 0])
    y_int = random.choice([i for i in range(-8, 9) if i != 0])
    
    g = math.gcd(abs(x_int), abs(y_int))
    a = y_int // g
    b = x_int // g
    c = (x_int * y_int) // g
    
    form = random.choice(['ax+by=c', 'ax+by+c=0'])
    if form == 'ax+by+c=0':
        eq_str = _format_equation(a, b, -c, form='ax+by+c=0')
    else:
        eq_str = _format_equation(a, b, c)

    if x_int > 0 and y_int > 0: not_passed = "三"
    elif x_int < 0 and y_int > 0: not_passed = "四"
    elif x_int < 0 and y_int < 0: not_passed = "一"
    else: # x_int > 0 and y_int < 0
        not_passed = "二"

    question_text = (f"⑴ 求方程式 ${eq_str}$ 的圖形與 $x$ 軸、$y$ 軸的交點坐標。<br>"
                     f"⑵ 承⑴，畫出方程式 ${eq_str}$ 的圖形，並判斷此圖形不通過第幾象限？")
    correct_answer = f"⑴ 與x軸交點$({x_int},0)$，與y軸交點$(0,{y_int})$。⑵ 不通過第{not_passed}象限。"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_special_lines_problem():
    axis = random.choice(['x', 'y'])
    
    if random.random() < 0.4: # Fraction
        den = random.randint(2, 5)
        num = random.choice([i for i in range(-9, 10) if i != 0 and math.gcd(i, den) == 1])
        val = Fraction(num, den)
        val_str = _format_number(val)
    else: # Integer
        val = random.randint(-9, 9)
        val_str = str(val)
        
    if axis == 'y':
        point = f"(0, {val_str})"
        desc = "水平"
    else: # axis == 'x'
        point = f"({val_str}, 0)"
        desc = "垂直"
        
    ans_desc = f"一條通過 ${point}$ 的{desc}線。"
    question_text = f"在坐標平面上，畫出方程式 ${axis}={val_str}$ 的圖形。"
    correct_answer = ans_desc

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_find_coefficient_problem():
    # Special case: pass through origin
    if random.random() < 0.25:
        a_orig = random.choice([i for i in range(-5, 6) if i != 0])
        b_orig = random.choice([i for i in range(-5, 6) if i != 0])
        eq_str = _format_equation(a_orig, b_orig, 0).replace("= 0", "=c")
        question_text = f"若方程式 ${eq_str}$ 的圖形通過原點，則 $c$ 的值是多少？"
        correct_answer = "0"
        return {
            "question_text": question_text,
            "answer": correct_answer,
            "correct_answer": correct_answer
        }

    p = random.choice([i for i in range(-6, 7) if i != 0])
    q = random.choice([i for i in range(-6, 7) if i != 0])
    a = random.choice([i for i in range(-5, 6) if i != 0])
    b = random.choice([i for i in range(-5, 6) if i != 0])
    c = a * p + b * q
    unknown = random.choice(['a', 'b', 'c'])
    
    if unknown == 'a':
        y_term_str = _format_term(b, 'y')
        if b > 0:
            eq_str = f"ax + {y_term_str} = {c}"
        else:
            eq_str = f"ax - {y_term_str[1:]} = {c}"
        question_text = f"若 Q$({p}, {q})$ 在方程式 ${eq_str}$ 的圖形上，則 $a$ 的值是多少？"
        correct_answer = str(a)
    elif unknown == 'b':
        x_term = _format_term(a, 'x')
        eq_str = f"{x_term} + by = {c}"
        question_text = f"若方程式 ${eq_str}$ 的圖形通過點 P$({p}, {q})$，則 $b$ 的值是多少？"
        correct_answer = str(b)
    else: # unknown == 'c'
        eq_str = _format_equation(a, b, 0).replace("= 0", "=c")
        question_text = f"若方程式 ${eq_str}$ 的圖形通過點 P$({p}, {q})$，則 $c$ 的值是多少？"
        correct_answer = str(c)
            
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_check_origin_problem():
    # Eq1 (Doesn't pass)
    if random.random() < 0.5:
        m1 = random.choice([i for i in range(-4, 5) if i != 0])
        c1_intercept = random.choice([i for i in range(-5, 6) if i != 0])
        sign = "+" if c1_intercept > 0 else "-"
        eq1_str = f"y={_format_term(m1, 'x')} {sign} {abs(c1_intercept)}"
    else:
        a1 = random.choice([i for i in range(-5, 6) if i != 0])
        b1 = random.choice([i for i in range(-5, 6) if i != 0])
        c1 = random.choice([i for i in range(-5, 6) if i != 0])
        eq1_str = _format_equation(a1, b1, c1)

    # Eq2 (Passes)
    a2 = random.choice([i for i in range(-5, 6) if i != 0])
    b2 = random.choice([i for i in range(-5, 6) if i != 0])
    eq2_str = _format_equation(a2, b2, 0)
    
    order = random.sample([(eq1_str, "不會"), (eq2_str, "會")], 2)
    
    question_text = (f"判斷下列二元一次方程式的圖形是否會通過原點。<br>"
                     f"⑴ ${order[0][0]}$<br>"
                     f"⑵ ${order[1][0]}$")
    correct_answer = f"⑴ {order[0][1]} ⑵ {order[1][1]}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_find_equation_from_points_problem():
    a = random.choice([i for i in range(-4, 5) if i != 0])
    b = random.randint(-5, 5)

    x1 = random.randint(-5, 5)
    y1 = a * x1 + b
    
    x2 = random.choice([i for i in range(-5, 5) if i != x1])
    y2 = a * x2 + b

    while y1 == y2 and x1 != x2:
        x2 = random.choice([i for i in range(-5, 5) if i != x1])
        y2 = a * x2 + b

    possible_x3 = [i for i in range(-8, 9) if i not in [x1, x2, 0]]
    if not possible_x3: possible_x3 = [9, -9]
    x3 = random.choice(possible_x3)
    y3 = a * x3 + b
    
    unknown_coord = random.choice(['x', 'y'])
    if unknown_coord == 'y':
        q2_point = f"({x3}, s)"
        q2_unknown = "s"
        ans2 = str(y3)
    else:
        q2_point = f"(k, {y3})"
        q2_unknown = "k"
        ans2 = str(x3)

    eq_b_part = _format_number(b, force_sign=True)
    eq_ans_str = f"y = {_format_term(a, 'x')} {eq_b_part}".replace("+ -", "- ").replace("  ", " ").strip()

    question_text = (f"已知 A$({x1}, {y1})$、B$({x2}, {y2})$ 兩點皆在方程式 $y=ax+b$ 的圖形上，則：<br>"
                     f"⑴ 此方程式為何？<br>"
                     f"⑵ 若 C${q2_point}$ 也在圖形上，求 ${q2_unknown}$ 的值為多少？")
    correct_answer = f"⑴ {eq_ans_str} ⑵ {q2_unknown}={ans2}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確，對多種格式的答案進行了優化。
    """
    # Normalize by removing spaces, making it half-width, and lowercase
    normalized_user = "".join(user_answer.replace('（', '(').replace('）', ')').replace('，', ',').split()).lower()
    normalized_correct = "".join(correct_answer.replace('（', '(').replace('）', ')').replace('，', ',').split()).lower()
    
    is_correct = (normalized_user == normalized_correct)
    
    if not is_correct:
        try:
            if float(user_answer.strip()) == float(correct_answer.strip()):
                is_correct = True
        except (ValueError, AttributeError):
            pass

    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}