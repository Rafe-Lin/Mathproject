import random
from fractions import Fraction
import math

def generate(level=1):
    """
    生成「二元一次式」相關題目 (標準 LaTeX 範本)。
    包含：
    1. 情境列式
    2. 同類項合併
    3. 去括號合併
    4. 分配律
    5. 分數型式
    """
    problem_types = [
        'word_problem', 
        'combine_simple', 
        'combine_parentheses', 
        'distributive',
        'fractional'
    ]
    problem_type = random.choice(problem_types)
    
    if problem_type == 'word_problem':
        return generate_word_problem()
    elif problem_type == 'combine_simple':
        return generate_combine_simple()
    elif problem_type == 'combine_parentheses':
        return generate_combine_parentheses()
    elif problem_type == 'distributive':
        return generate_distributive_problem()
    else: # 'fractional'
        return generate_fractional_problem()

def non_zero_randint(min_val, max_val):
    """Generates a random integer in the range [min_val, max_val] that is not zero."""
    val = 0
    while val == 0:
        val = random.randint(min_val, max_val)
    return val

def format_term_display(coeff, var, first_term=False):
    """Formats a single term for display in a question (e.g., '+ 5x', '- y')."""
    if coeff == 0:
        return ""

    sign = ""
    if first_term:
        if coeff < 0:
            sign = "-"
    else:
        sign = " + " if coeff > 0 else " - "
    
    coeff_val = abs(coeff)
    
    if coeff_val == 1 and var:
        return f"{sign}{var}"
    else:
        return f"{sign}{coeff_val}{var}"

def format_expression_display(x_coeff, y_coeff, const_coeff):
    """Formats a full expression for display (e.g., '3x - y + 5')."""
    parts = []
    term_x = format_term_display(x_coeff, 'x', True)
    if term_x:
        parts.append(term_x)
        
    term_y = format_term_display(y_coeff, 'y', not parts)
    if term_y:
        parts.append(term_y)
        
    term_c = format_term_display(const_coeff, '', not parts)
    if term_c:
        parts.append(term_c)
        
    if not parts:
        return "0"
        
    full_str = "".join(parts)
    if full_str.startswith(" + "):
        return full_str[3:]
    return full_str.strip()

def format_answer_canonical(x_coeff, y_coeff, const_coeff):
    """Formats the answer into a canonical string for checking (e.g., '3x-y+5')."""
    parts = []
    
    if x_coeff != 0:
        if x_coeff == 1:
            parts.append("x")
        elif x_coeff == -1:
            parts.append("-x")
        else:
            parts.append(f"{x_coeff}x")
            
    if y_coeff != 0:
        sign = "+" if y_coeff > 0 and parts else ""
        if y_coeff == 1:
            parts.append(f"{sign}y")
        elif y_coeff == -1:
            parts.append("-y")
        else:
            parts.append(f"{sign}{y_coeff}y")
            
    if const_coeff != 0:
        sign = "+" if const_coeff > 0 and parts else ""
        parts.append(f"{sign}{const_coeff}")
        
    if not parts:
        return "0"
    
    return "".join(parts)

def lcm(a, b):
    """Calculates the least common multiple of two integers."""
    if a == 0 or b == 0:
        return 0
    return abs(a * b) // math.gcd(a, b)

def generate_word_problem():
    """Generates a word problem for forming a two-variable linear expression."""
    total = random.randint(20, 100) * 10
    cost_x = random.randint(10, 50)
    cost_y = random.randint(5, 25)
    while cost_x == cost_y:
        cost_y = random.randint(5, 25)
        
    items = [
        ("午餐", "文具"), ("原子筆", "橡皮擦"), ("飲料", "麵包"), ("玩具車", "機器人")
    ]
    item_x, item_y = random.choice(items)

    question_text = f"小明身上原有 ${total}$ 元，買了 $x$ 個單價 ${cost_x}$ 元的{item_x}，和 $y$ 個單價 ${cost_y}$ 元的{item_y}，請問小明身上還剩下多少錢？（以二元一次式表示）"
    
    correct_answer = f"{total}-{cost_x}x-{cost_y}y"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }
    
def generate_combine_simple():
    """Generates a problem for combining like terms without parentheses."""
    a = non_zero_randint(-9, 9)
    b = non_zero_randint(-9, 9)
    e = random.randint(-9, 9)
    c = non_zero_randint(-9, 9)
    d = non_zero_randint(-9, 9)
    f = random.randint(-9, 9)

    # Construct the expression string piece by piece to handle signs correctly
    term1_str = format_expression_display(a, b, e)
    term2_str = format_term_display(c, 'x')
    term3_str = format_term_display(d, 'y')
    term4_str = format_term_display(f, '')
    expr_str = f"{term1_str}{term2_str}{term3_str}{term4_str}"
    
    res_x = a + c
    res_y = b + d
    res_c = e + f
    
    correct_answer = format_answer_canonical(res_x, res_y, res_c)
    
    question_text = f"化簡下列各式：<br>${expr_str}$"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_combine_parentheses():
    """Generates a problem for adding or subtracting expressions in parentheses."""
    coeffs1 = [non_zero_randint(-9, 9) for _ in range(2)] + [random.randint(-9, 9)]
    coeffs2 = [non_zero_randint(-9, 9) for _ in range(2)] + [random.randint(-9, 9)]
    random.shuffle(coeffs1)
    random.shuffle(coeffs2)
    a, b, c = coeffs1
    d, e, f = coeffs2

    op = random.choice(['+', '-'])
    
    expr1_str = format_expression_display(a, b, c)
    expr2_str = format_expression_display(d, e, f)
    
    question_text = f"化簡下列各式：<br>$({expr1_str}) {op} ({expr2_str})$"
    
    if op == '+':
        res_x, res_y, res_c = a + d, b + e, c + f
    else: # op == '-'
        res_x, res_y, res_c = a - d, b - e, c - f
        
    correct_answer = format_answer_canonical(res_x, res_y, res_c)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_distributive_problem():
    """Generates a problem involving the distributive property."""
    k1 = non_zero_randint(-5, 5)
    while abs(k1) == 1:
        k1 = non_zero_randint(-5, 5)

    k2 = non_zero_randint(-5, 5)
    
    a1, b1 = non_zero_randint(-6, 6), non_zero_randint(-6, 6)
    a2, b2 = non_zero_randint(-6, 6), non_zero_randint(-6, 6)
    
    expr1_str = format_expression_display(a1, b1, 0)
    expr2_str = format_expression_display(a2, b2, 0)
    
    k2_display = f" {format_term_display(k2, '', False)}"
    
    question_text = f"化簡下列各式：<br>${k1}({expr1_str}){k2_display}({expr2_str})$"
    
    res_x = k1 * a1 + k2 * a2
    res_y = k1 * b1 + k2 * b2
    
    correct_answer = format_answer_canonical(res_x, res_y, 0)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_fractional_problem():
    """Generates a problem with fractional coefficients."""
    d1, d2 = random.randint(2, 5), random.randint(2, 5)
    while d1 == d2:
        d2 = random.randint(2,5)
        
    a1, b1, c1 = [non_zero_randint(-5, 5) for _ in range(2)] + [random.randint(-5,5)]
    a2, b2, c2 = [non_zero_randint(-5, 5) for _ in range(2)] + [random.randint(-5,5)]

    op = random.choice(['+', '-'])
    
    expr1_str = format_expression_display(a1, b1, c1)
    expr2_str = format_expression_display(a2, b2, c2)
    
    question_text = f"化簡下列各式：<br>$\\frac{{{expr1_str}}}{{{d1}}} {op} \\frac{{{expr2_str}}}{{{d2}}}$"
    
    common_den = lcm(d1, d2)
    m1 = common_den // d1
    m2 = common_den // d2
    
    if op == '+':
        res_x = m1 * a1 + m2 * a2
        res_y = m1 * b1 + m2 * b2
        res_c = m1 * c1 + m2 * c2
    else: # op == '-'
        res_x = m1 * a1 - m2 * a2
        res_y = m1 * b1 - m2 * b2
        res_c = m1 * c1 - m2 * c2

    if res_x == 0 and res_y == 0 and res_c == 0:
        correct_answer = "0"
    else:
        common_divisor = math.gcd(math.gcd(abs(res_x), abs(res_y)), abs(res_c))
        final_gcd = math.gcd(common_divisor, common_den)
        
        num_x = res_x // final_gcd
        num_y = res_y // final_gcd
        num_c = res_c // final_gcd
        
        final_den = common_den // final_gcd
        
        num_str = format_answer_canonical(num_x, num_y, num_c)
        
        if final_den == 1:
            correct_answer = num_str
        elif num_x == 0 and num_y == 0 and num_c != 0:
             frac = Fraction(num_c, final_den)
             correct_answer = f"{frac.numerator}/{frac.denominator}"
        else:
            correct_answer = f"({num_str})/{final_den}"
            
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_ans_norm = user_answer.replace(" ", "")
    
    is_correct = (user_ans_norm == correct_answer)
    
    # Create a display-friendly LaTeX version of the answer
    if "/" in correct_answer and "(" in correct_answer:
        parts = correct_answer.split('/')
        num = parts[0][1:-1] # Remove parentheses
        den = parts[1]
        correct_answer_latex = f"$\\frac{{{num}}}{{{den}}}$"
    elif "/" in correct_answer:
        parts = correct_answer.split('/')
        correct_answer_latex = f"$\\frac{{{parts[0]}}}{{{parts[1]}}}$"
    else:
        correct_answer_latex = f"${correct_answer}$"

    if is_correct:
        result_text = f"完全正確！答案是 {correct_answer_latex}。"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer_latex}"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}
