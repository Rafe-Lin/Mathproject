import random
from fractions import Fraction
import math

def simplify_ratio(n, d):
    """
    將比例化為最簡整數比。
    """
    if d == 0:
        return n, d
    common = math.gcd(int(n), int(d))
    return n // common, d // common

def format_fraction(frac):
    """
    將 Fraction 物件格式化為字串，整數或 a/b 形式。
    """
    if frac.denominator == 1:
        return str(frac.numerator)
    return f"{frac.numerator}/{frac.denominator}"

def generate_solve_for_x_simple_problem():
    """
    生成求解基本比例式的題目，如 a:b = c:x。
    """
    a, b, c = [random.randint(2, 15) for _ in range(3)]
    if a == b: b += 1
    if b == c: c += 1
    
    # a:b = c:x  => ax = bc => x = bc/a
    x = Fraction(b * c, a)
    
    # 修正：確保整句比例式包在同一個 $ 中，移除多餘的 $
    question_text = f"求下列比例式中的 $x$ 值。<br>${a}：{b} = {c}：x$"
    correct_answer = format_fraction(x)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_solve_for_x_linear_problem():
    """
    生成求解含一次式的比例式題目，如 (x+a):b = (x+c):d。
    保證整數解。
    """
    x_sol = random.randint(-30, 30)
    b = random.randint(3, 9)
    d = random.randint(3, 9)
    if b == d: d += 1
    
    g = math.gcd(b, d)
    b_s = b // g
    d_s = d // g
    
    k = random.randint(1, 5) * random.choice([-1, 1])
    
    # (x_sol+a)/(x_sol+c) = b/d = b_s/d_s
    # Let x_sol+a = b_s*k and x_sol+c = d_s*k
    a = b_s * k - x_sol
    c = d_s * k - x_sol

    # 避免 a=0, c=0 或 a=c 的無趣題目
    if a == 0 or c == 0 or a == c:
        return generate_solve_for_x_simple_problem()
    
    def format_term(var, val):
        if val == 0:
            return var
        op = "+" if val > 0 else "-"
        return f"{var} {op} {abs(val)}"

    term1 = format_term("x", a)
    term2 = format_term("x", c)
    
    # 修正：移除 {b} 和 {d} 前多餘的 $
    question_text = f"求下列比例式中的 $x$ 值。<br>$({term1})：{b} = ({term2})：{d}$"
    correct_answer = str(x_sol)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_find_values_from_ratio_problem():
    """
    生成已知比例與和/差，求兩數值的題目。
    """
    a = random.randint(2, 9)
    b = random.randint(2, 9)
    if a == b: b = random.randint(2, 9)
    
    g = math.gcd(a, b)
    a //= g
    b //= g

    r = random.randint(2, 10)
    
    x = a * r
    y = b * r
    
    if random.random() < 0.6 and a != b:
        op_str = "－"
        val = abs(x - y)
    else:
        op_str = "＋"
        val = x + y

    # 修正：移除 {b} 前多餘的 $
    question_text = f"有兩數 $x$、$y$，已知 $x：y = {a}：{b}$，且 $x {op_str} y = {val}$，則 $x$、 $y$ 的值分別為多少？(請依序回答 x, y，並用逗號分隔)"
    correct_answer = f"{x},{y}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_equation_to_ratio_problem():
    """
    生成由 ax=by 求比例的題目。
    """
    # ax = by => x:y = b:a
    a = random.randint(2, 9)
    b = random.randint(2, 9)
    if a == b: b += 1
    
    g = math.gcd(a, b)
    a //= g
    b //= g

    question_prefix = f"設 $x$、$y$ 皆不為 0，且 ${a}x = {b}y$，"

    if random.random() > 0.5:
        # 題型 ⑴ 求 x：y
        b_ans, a_ans = simplify_ratio(b, a)
        question_text = f"{question_prefix}求 $x：y$ 的最簡整數比。"
        # 修正：移除 {a_ans} 前多餘的 $
        correct_answer = f"{b_ans}：{a_ans}"
    else:
        # 題型 ⑵ 求 cx：dy
        c = random.randint(2, 5)
        d = random.randint(2, 5)
        
        # substitute x=b, y=a => cx:dy = cb:da
        n = c * b
        m = d * a
        n_ans, m_ans = simplify_ratio(n, m)
        # 修正：移除 {d} 前多餘的 $，確保 LaTeX 完整
        question_text = f"{question_prefix}求 ${c}x：{d}y$ 的最簡整數比。"
        # 修正：移除 {m_ans} 前多餘的 $
        correct_answer = f"{n_ans}：{m_ans}"
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }
    
def generate_sum_diff_ratio_problem():
    """
    生成由 (a+b):(a-b) 求比例或比值的題目。
    """
    # 倒推法: 假設 a:b = n:m
    n = random.randint(1, 9)
    m = random.randint(1, 9)
    # 確保 a-b 不為 0
    if n == m: m += 1
    
    # (a+b):(a-b) = (n+m):(n-m)
    c_val = n + m
    d_val = n - m
        
    c_disp, d_disp = simplify_ratio(c_val, d_val)
    
    # 修正：移除 {d_disp} 前多餘的 $
    question_prefix = f"設 $(a＋b)：(a-b) = {c_disp}：{d_disp}$，"
    
    if random.random() > 0.5:
        # 題型 ⑴ 求 a：b
        n_ans, m_ans = simplify_ratio(n, m)
        question_text = f"{question_prefix}求 $a：b$ 的最簡整數比。"
        # 修正：移除 {m_ans} 前多餘的 $
        correct_answer = f"{n_ans}：{m_ans}"
    else:
        # 題型 ⑵ 求 b：(a-b) 的比值
        # b:(a-b) = m:(n-m)
        frac = Fraction(m, n - m)
        question_text = f"{question_prefix}求 $b：(a-b)$ 的比值。"
        correct_answer = format_fraction(frac)
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    生成「比例式」相關題目。
    """
    problem_generators = [
        generate_solve_for_x_simple_problem,
        generate_solve_for_x_linear_problem,
        generate_find_values_from_ratio_problem,
        generate_equation_to_ratio_problem,
        generate_sum_diff_ratio_problem
    ]
    return random.choice(problem_generators)()

def check(user_answer, correct_answer):
    """
    檢查使用者答案是否正確，能處理數值、分數、比例、多值答案。
    """
    user_answer = user_answer.strip().replace(' ', '').replace('：', ':')
    correct_answer = correct_answer.strip().replace(' ', '').replace('：', ':')
    
    is_correct = False
    
    # Case 1: 比例 (e.g., "4:7")
    if ':' in correct_answer:
        try:
            c_n, c_d = map(float, correct_answer.split(':'))
            # 使用者可能會輸入非最簡整數比，但只要比例相等就算對 (若要嚴格限制最簡，需另外處理)
            if ':' in user_answer:
                u_n, u_d = map(float, user_answer.split(':'))
                if c_d * u_n == c_n * u_d:
                    is_correct = True
        except (ValueError, IndexError):
            pass

    # Case 2: 多值答案 (e.g., "12,8")
    elif ',' in correct_answer:
        try:
            correct_vals = [val.strip() for val in correct_answer.split(',')]
            user_vals = [val.strip() for val in user_answer.split(',')]
            if len(correct_vals) == len(user_vals):
                is_match = all(Fraction(c) == Fraction(u) for c, u in zip(correct_vals, user_vals))
                if is_match:
                    is_correct = True
        except (ValueError, IndexError):
            pass

    # Case 3: 數值或分數 (e.g., "32", "63/4")
    else:
        try:
            if Fraction(user_answer) == Fraction(correct_answer):
                is_correct = True
        except (ValueError, ZeroDivisionError):
            pass

    # Fallback
    if not is_correct:
        if user_answer.upper() == correct_answer.upper():
            is_correct = True

    # 產生 LaTeX 格式的回饋訊息
    display_answer = correct_answer
    try:
        if '/' in correct_answer and ':' not in correct_answer:
            num, den = correct_answer.split('/')
            display_answer = f"\\frac{{{num}}}{{{den}}}"
        elif ':' in correct_answer:
            display_answer = correct_answer.replace(':', '：')
    except Exception:
        pass

    if is_correct:
        result_text = f"完全正確！答案是 ${display_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${display_answer}$"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}