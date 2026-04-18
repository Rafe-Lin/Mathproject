import random
from fractions import Fraction
import math

# Helper function to format numbers as integers or fractions for display in LaTeX
def format_number_latex(num):
    # Handle floats that are actually integers
    if isinstance(num, float) and num.is_integer():
        num = int(num)

    if isinstance(num, int):
        return str(num)
    
    frac = Fraction(num).limit_denominator(100) # Limit denominator to avoid overly complex fractions
    if frac.denominator == 1:
        return str(frac.numerator)
    
    # Use raw string and double braces for frac
    return r"\\frac{{{}}}{{{}}}".format(frac.numerator, frac.denominator)

# Helper function to format general quadratic equation y = ax^2 + bx + c
def format_quadratic_eq(a, b, c):
    parts = []
    
    # a x^2 term
    if a != 0:
        if a == 1:
            parts.append(r"x^{{2}}")
        elif a == -1:
            parts.append(r"-x^{{2}}")
        else:
            parts.append(f"{format_number_latex(a)}x^{{2}}")
            
    # b x term
    if b != 0:
        if b > 0:
            if parts: parts.append("+")
            if b == 1:
                parts.append("x")
            else:
                parts.append(f"{format_number_latex(b)}x")
        else: # b < 0
            if b == -1:
                parts.append("-x")
            else:
                parts.append(f"{format_number_latex(b)}x") # format_number_latex will include the negative sign
                
    # c term
    if c != 0:
        if c > 0:
            if parts: parts.append("+")
            parts.append(format_number_latex(c))
        else: # c < 0
            parts.append(format_number_latex(c)) # format_number_latex will include the negative sign
            
    if not parts:
        return "0" # Should not happen for a quadratic function where a != 0
    
    return "".join(parts)

# Helper function to format vertex form y = a(x-h)^2 + k
def format_vertex_form(a, h, k):
    parts = []
    
    # a term
    if a == 1:
        parts.append("")
    elif a == -1:
        parts.append("-")
    else:
        parts.append(format_number_latex(a))

    # (x-h)^2 term
    if h == 0:
        parts.append(r"x^{{2}}")
    elif h > 0:
        parts.append(f"(x - {format_number_latex(h)})^{{2}}")
    else: # h < 0
        parts.append(f"(x + {format_number_latex(abs(h))})^{{2}}")

    # k term
    if k != 0:
        if k > 0:
            parts.append(f" + {format_number_latex(k)}")
        else: # k < 0
            parts.append(f" {format_number_latex(k)}") # format_number_latex includes negative
            
    return "".join(parts)


def generate(level=1):
    problem_type = random.choice([
        'complete_square',
        'vertex_axis',
        'max_min_overall',
        'translation_desc',
        'opening_direction',
        'x_intercepts'
    ])

    a = 0
    while a == 0:
        a_choices = [-3, -2, -1, 1, 2, 3] # Avoid making 'a' too complex or zero
        if level >= 2: # Introduce more variability for higher levels
            a_choices.extend([-5, -4, 4, 5])
        a = random.choice(a_choices)

    b_range = (-10, 10)
    c_range = (-10, 10)
    if level >= 2:
        b_range = (-15, 15)
        c_range = (-15, 15)

    b = random.randint(*b_range)
    c = random.randint(*c_range)

    # Calculate h and k using Fraction for precision
    h_frac = Fraction(-b, 2 * a)
    k_frac = Fraction(4 * a * c - b * b, 4 * a)
    
    quad_eq_str = format_quadratic_eq(a, b, c)
    vertex_form_str = format_vertex_form(a, h_frac, k_frac)

    question_text = ""
    correct_answer = ""

    if problem_type == 'complete_square':
        question_text = f"將下列函數化成 $y = a(x-h)^{{2}} + k$ 的形式：<br>$y = {quad_eq_str}$"
        correct_answer = f"y = {vertex_form_str}"
        
    elif problem_type == 'vertex_axis':
        question_text = f"請找出二次函數 $y = {quad_eq_str}$ 圖形的頂點坐標及對稱軸方程式。"
        correct_answer = f"頂點為 $({format_number_latex(h_frac)}, {format_number_latex(k_frac)})$，對稱軸為直線 $x = {format_number_latex(h_frac)}$。"

    elif problem_type == 'max_min_overall':
        question_text = f"已知二次函數 $y = {quad_eq_str}$，求 $y$ 的最大值或最小值及發生最大值或最小值時之 $x$ 值。"
        
        value_type = "最小值" if a > 0 else "最大值"
        correct_answer = f"當 $x = {format_number_latex(h_frac)}$ 時，$y$ 有{value_type} ${format_number_latex(k_frac)}$。"

    elif problem_type == 'translation_desc':
        # Generate h, k for translation. Make them integers more often.
        h_trans = random.randint(-5, 5)
        k_trans = random.randint(-5, 5)
        
        # Ensure at least one translation happens
        while h_trans == 0 and k_trans == 0:
            h_trans = random.randint(-5, 5)
            k_trans = random.randint(-5, 5)
        
        translated_vertex_form_str = format_vertex_form(a, h_trans, k_trans)

        horizontal_shift_desc = ""
        if h_trans > 0:
            horizontal_shift_desc = f"往右平移 ${format_number_latex(h_trans)}$ 單位"
        elif h_trans < 0:
            horizontal_shift_desc = f"往左平移 ${format_number_latex(abs(h_trans))}$ 單位"

        vertical_shift_desc = ""
        if k_trans > 0:
            vertical_shift_desc = f"向上平移 ${format_number_latex(k_trans)}$ 單位"
        elif k_trans < 0:
            vertical_shift_desc = f"向下平移 ${format_number_latex(abs(k_trans))}$ 單位"

        if horizontal_shift_desc and vertical_shift_desc:
            translation_desc = f"{horizontal_shift_desc}，再{vertical_shift_desc}可得"
        elif horizontal_shift_desc:
            translation_desc = f"{horizontal_shift_desc}可得"
        else: # only vertical_shift_desc
            translation_desc = f"{vertical_shift_desc}可得"

        question_text = f"描述二次函數 $y = {translated_vertex_form_str}$ 的圖形相對於 $y = {format_number_latex(a)}x^{{2}}$ 的平移方式。"
        correct_answer = f"圖形由 $y = {format_number_latex(a)}x^{{2}}$ 的圖形{translation_desc}。"
        
    elif problem_type == 'opening_direction':
        question_text = f"判斷二次函數 $y = {quad_eq_str}$ 的圖形開口方向。"
        if a > 0:
            correct_answer = "開口向上"
        else:
            correct_answer = "開口向下"
            
    elif problem_type == 'x_intercepts':
        question_text = f"判斷二次函數 $y = {quad_eq_str}$ 的圖形與 $x$ 軸有幾個交點？"
        discriminant = b*b - 4*a*c
        if discriminant > 0:
            correct_answer = "2"
        elif discriminant == 0:
            correct_answer = "1"
        else:
            correct_answer = "0"

    return {
        "question_text": question_text,
        "answer": correct_answer, # For display purposes if needed
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()

    is_correct = False
    feedback = ""

    # Normalize spacing and common algebraic simplifications before comparison
    # This is a basic attempt, not a full algebraic parser.
    # It removes spaces and handles "a+-b" -> "a-b"
    normalized_user = user_answer.replace(" ", "").replace("+-", "-")
    normalized_correct = correct_answer.replace(" ", "").replace("+-", "-")

    if normalized_user == normalized_correct:
        is_correct = True
    else:
        # Specific checks for certain answer types where exact string match might be too strict
        if "開口" in correct_answer:
            user_lower = user_answer.lower().replace(" ", "")
            correct_lower = correct_answer.lower().replace(" ", "")
            if user_lower in ["開口向上", "向上", "上"] and "向上" in correct_lower:
                is_correct = True
            elif user_lower in ["開口向下", "向下", "下"] and "向下" in correct_lower:
                is_correct = True
        elif correct_answer.isdigit() or ('/' in correct_answer and all(p.isdigit() for p in correct_answer.split('/'))): # Check if correct answer is a simple integer/fraction string
             try:
                user_num = Fraction(user_answer)
                correct_num = Fraction(correct_answer)
                if user_num == correct_num:
                    is_correct = True
             except ValueError:
                pass
        
        # For complex string answers (vertex, max/min, translation, completing the square),
        # if the direct normalized match fails, we assume incorrect.
        # A full algebraic expression parser would be needed for more lenient checking,
        # which is beyond the scope of a simple `check` function.
        
    if is_correct:
        feedback = f"完全正確！答案是 ${correct_answer}$。"
    else:
        feedback = f"答案不正確。正確答案應為：${correct_answer}$"

    return {"correct": is_correct, "result": feedback, "next_question": True}