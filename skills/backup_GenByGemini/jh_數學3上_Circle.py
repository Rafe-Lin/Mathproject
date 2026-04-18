import random
import math
from fractions import Fraction

# --- Helper Functions for Formatting ---

def format_number(num):
    """Formats an integer or a Fraction object into a LaTeX string."""
    if isinstance(num, Fraction):
        if num.denominator == 1:
            return str(num.numerator)
        # Ensure we don't show negative in denominator
        if num.denominator < 0:
            num = Fraction(-num.numerator, -num.denominator)
        return f"\\frac{{{num.numerator}}}{{{num.denominator}}}"
    return str(num)

def format_pi_term(coeff):
    """Formats a coefficient into a pi term string, e.g., 5\\pi or \\frac{3}{2}\\pi."""
    if coeff == 0:
        return "0"
    coeff = Fraction(coeff).limit_denominator()
    if coeff.denominator == 1:
        num = coeff.numerator
        if num == 1: return "\\pi"
        if num == -1: return "-\\pi"
        return f"{num}\\pi"
    return f"{format_number(coeff)}\\pi"

def format_sqrt_term(coeff, radicand):
    """Formats a coefficient and a radicand into a sqrt term, e.g., 4\\sqrt{2}."""
    if coeff == 0:
        return "0"
    coeff = Fraction(coeff).limit_denominator()
    
    coeff_str = ""
    if coeff.denominator == 1:
        num = coeff.numerator
        if abs(num) != 1:
            coeff_str = str(num)
        elif num == -1:
            coeff_str = "-"
    else:
        coeff_str = format_number(coeff)
        
    return f"{coeff_str}\\sqrt{{{radicand}}}"


# --- Main Generator Function ---

def generate(level=1):
    """
    生成「圓」相關題目。
    包含：
    1. 基本定義填空
    2. 扇形計算 (弧長、周長、面積)
    3. 扇形逆向計算 (由面積或弧長求圓心角)
    4. 弓形計算 (周長、面積)
    """
    # Adjust weights to have more calculation problems
    problem_types = ['definition', 'sector_calc', 'reverse_sector_calc', 'segment_calc']
    weights = [1, 3, 2, 2]
    problem_type = random.choices(problem_types, weights=weights, k=1)[0]
    
    if problem_type == 'definition':
        return generate_definition_problem()
    elif problem_type == 'sector_calc':
        return generate_sector_calculation_problem()
    elif problem_type == 'reverse_sector_calc':
        return generate_reverse_sector_problem()
    else: # segment_calc
        return generate_segment_calculation_problem()

# --- Problem Type Generators ---

def generate_definition_problem():
    """生成圓的基本定義填空題。"""
    definitions = {
        "弦": "連接圓上任兩點的線段",
        "弓形": "圓的一弦和一弧所圍成的圖形",
        "直徑": "通過圓心的弦",
        "扇形": "兩半徑和一弧所圍成的圖形",
        "圓心角": "以圓心為頂點，兩半徑為邊所夾的角",
        "半徑": "圓心到圓上任一點的線段"
    }
    term, desc = random.choice(list(definitions.items()))
    
    question_text = f"在下列空格中填入適當名稱：<br>「{desc}」稱為 ____。"
    correct_answer = term
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_sector_calculation_problem():
    """生成扇形計算題 (弧長、周長、面積)。"""
    r = random.randint(3, 15)
    angle = random.choice([30, 45, 60, 90, 120, 135, 150, 180, 210, 240, 270])
    task = random.choice(['arc_length', 'perimeter', 'area'])

    if task == 'arc_length':
        question_text = f"一圓的半徑為 ${r}$ 公分，圓心角為 ${angle}°$，則此圓心角所對的弧長為多少公分？"
        arc_coeff = Fraction(2 * r * angle, 360)
        correct_answer = format_pi_term(arc_coeff)
        
    elif task == 'area':
        question_text = f"一扇形的半徑為 ${r}$ 公分，圓心角為 ${angle}°$，則此扇形的面積為多少平方公分？"
        area_coeff = Fraction(r**2 * angle, 360)
        correct_answer = format_pi_term(area_coeff)

    else: # perimeter
        question_text = f"一扇形的半徑為 ${r}$ 公分，圓心角為 ${angle}°$，則此扇形的周長為多少公分？"
        arc_coeff = Fraction(2 * r * angle, 360)
        arc_term = format_pi_term(arc_coeff)
        constant_term = 2 * r
        correct_answer = f"({arc_term}+{constant_term})"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_reverse_sector_problem():
    """由面積或弧長反求圓心角。"""
    r = random.randint(4, 20)
    angle = random.choice([30, 45, 60, 90, 120, 135, 150, 180])
    task = random.choice(['from_area', 'from_arc_length'])

    if task == 'from_area':
        area_coeff = Fraction(r**2 * angle, 360)
        # Ensure the coefficient is not too ugly
        if area_coeff.denominator > 4 and area_coeff.denominator != r:
            # Recalculate with a friendlier angle if needed
            r = random.choice([6, 8, 10, 12])
            angle = random.choice([30, 45, 60, 90, 120])
            area_coeff = Fraction(r**2 * angle, 360)

        area_str = format_pi_term(area_coeff)
        question_text = f"已知一扇形的面積為 ${area_str}$ 平方公分，半徑為 ${r}$ 公分，求此扇形的圓心角。(答案請包含單位 °)"
        correct_answer = f"{angle}°"
        
    else: # from_arc_length
        arc_coeff = Fraction(2 * r * angle, 360)
        # Ensure the coefficient is not too ugly
        if arc_coeff.denominator > 6:
            r = random.choice([6, 9, 10, 12, 15])
            angle = random.choice([30, 60, 90, 120])
            arc_coeff = Fraction(2 * r * angle, 360)

        arc_str = format_pi_term(arc_coeff)
        question_text = f"已知半徑為 ${r}$ 公分的圓中，有一弧長為 ${arc_str}$ 公分，求此弧所對應的圓心角。(答案請包含單位 °)"
        correct_answer = f"{angle}°"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_segment_calculation_problem():
    """生成特殊弓形計算題 (60度或90度)。"""
    r = random.choice([4, 6, 8, 10, 12])
    angle = random.choice([60, 90])
    task = random.choice(['area', 'perimeter'])

    if angle == 60:
        # Equilateral triangle
        question_intro = f"一圓的半徑為 ${r}$ 公分，其內有一弓形，所對的圓心角為 $60°$ (即弓形的弦與兩半徑形成正三角形)。"
        arc_coeff = Fraction(r, 3)
        chord_length = r
        sector_area_coeff = Fraction(r**2, 6)
        triangle_area_coeff_sqrt3 = Fraction(r**2, 4)
        
        if task == 'perimeter':
            question_text = question_intro + "<br>求此弓形的周長為多少公分？"
            arc_term = format_pi_term(arc_coeff)
            correct_answer = f"({arc_term}+{chord_length})"
        else: # area
            question_text = question_intro + "<br>求此弓形的面積為多少平方公分？"
            sector_area_term = format_pi_term(sector_area_coeff)
            triangle_area_term = format_sqrt_term(triangle_area_coeff_sqrt3, 3)
            correct_answer = f"({sector_area_term}-{triangle_area_term})"

    else: # angle == 90
        # Isosceles right triangle
        question_intro = f"一圓的半徑為 ${r}$ 公分，其內有一弓形，所對的圓心角為 $90°$。"
        arc_coeff = Fraction(r, 2)
        chord_length_term = format_sqrt_term(r, 2)
        sector_area_coeff = Fraction(r**2, 4)
        triangle_area = Fraction(r**2, 2)

        if task == 'perimeter':
            question_text = question_intro + "<br>求此弓形的周長為多少公分？"
            arc_term = format_pi_term(arc_coeff)
            correct_answer = f"({arc_term}+{chord_length_term})"
        else: # area
            question_text = question_intro + "<br>求此弓形的面積為多少平方公分？"
            sector_area_term = format_pi_term(sector_area_coeff)
            triangle_area_term = format_number(triangle_area)
            correct_answer = f"({sector_area_term}-{triangle_area_term})"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

# --- Check Function ---

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    # Normalize user answer: remove spaces, degree symbol, and convert 'pi' to LaTeX format
    norm_user = user_answer.strip().replace(" ", "").replace("pi", "\\pi").replace("°", "")
    
    # Normalize correct answer: remove spaces and degree symbol
    norm_correct = correct_answer.strip().replace(" ", "").replace("°", "")

    # For answers in parentheses, allow entry without them
    if norm_correct.startswith("(") and norm_correct.endswith(")"):
        if norm_user.lower() == norm_correct[1:-1].lower():
            is_correct = True
        else:
            is_correct = (norm_user.lower() == norm_correct.lower())
    else:
        is_correct = (norm_user.lower() == norm_correct.lower())
    
    if is_correct:
        result_text = f"完全正確！答案是 ${correct_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer}$"
    
    return {"correct": is_correct, "result": result_text, "next_question": True}