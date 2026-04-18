# ==============================================================================
# ID: jh_數學1上_FactorsAndMultiples
# Model: qwen2.5-coder:7b | Strategy: Architect-Engineer Pipeline (Phi4 Plan + Qwen Code)
# Duration: 182.74s | RAG: 4 examples
# Created At: 2026-01-06 14:38:42
# Fix Status: [Repaired]
# ==============================================================================

from fractions import Fraction
import random

def to_latex(num):
    if isinstance(num, int): return str(num)
    if isinstance(num, float): num = Fraction(str(num)).limit_denominator(100)
    if isinstance(num, Fraction):
        if num.denominator == 1: return str(num.numerator)
        if abs(num.numerator) > num.denominator:
            sign = "-" if num.numerator < 0 else ""
            rem = abs(num) - (abs(num).numerator // abs(num).denominator)
            return f"{sign}{abs(num).numerator // abs(num).denominator} \\frac{{{rem.numerator}}}{{{rem.denominator}}}"
        return f"\\frac{{{num.numerator}}}{{{num.denominator}}}"
    return str(num)

def fmt_num(num):
    """Formats negative numbers with parentheses for equations."""
    if num < 0: return f"({num})"
    return str(num)

def draw_number_line(points_map):
    """Generates aligned ASCII number line with HTML CSS (Scrollable)."""
    values = [int(v) if isinstance(v, (int, float)) else int(v.numerator/v.denominator) for v in points_map.values()]
    if not values: values = [0]
    r_min, r_max = min(min(values)-1, -5), max(max(values)+1, 5)
    if r_max - r_min > 12: c=sum(values)//len(values); r_min, r_max = c-6, c+6
    
    u_w = 5
    l_n, l_a, l_l = "", "", ""
    for i in range(r_min, r_max+1):
        l_n += f"{str(i):^{u_w}}"
        l_a += ("+" + " "*(u_w-1)) if i == r_max else ("+" + "-"*(u_w-1))
        lbls = [k for k,v in points_map.items() if (v==i if isinstance(v, int) else int(v)==i)]
        l_l += f"{lbls[0]:^{u_w}}" if lbls else " "*u_w
    
    content = f"{l_n}\n{l_a}\n{l_l}"
    return (f"<div style='width: 100%; overflow-x: auto; background: #f8f9fa; padding: 10px; border-radius: 5px; margin: 10px 0;'>"
            f"<pre style='font-family: Consolas, monospace; line-height: 1.1; display: inline-block; margin: 0;'>{content}</pre></div>")



def generate_type_A_problem():
    target_number = random.randint(20, 100)
    factors = [i for i in range(1, target_number + 1) if target_number % i == 0]
    return {
        'question_text': f"將 {target_number} 寫成 a×b，其中 a、b 為正整數，並由小到大寫出 {target_number} 的所有因數。",
        'answer': factors,
        'correct_answer': ', '.join(map(str, factors))
    }

def generate_type_B_problem():
    target_number = random.randint(50, 150)
    factors = [i for i in range(1, target_number + 1) if target_number % i == 0]
    return {
        'question_text': f"將 {target_number} 寫成 c×d，其中 c、d 為正整數，並由小到大寫出 {target_number} 的所有因數。",
        'answer': factors,
        'correct_answer': ', '.join(map(str, factors))
    }

def generate_type_C_problem():
    original_number = random.randint(24, 72)
    all_factors = sorted([i for i in range(1, original_number + 1) if original_number % i == 0])
    
    while len(all_factors) < 4:
        original_number = random.randint(24, 72)
        all_factors = sorted([i for i in range(1, original_number + 1) if original_number % i == 0])

    problem_factors_list = list(all_factors)
    num_internal_missing = random.choice([1, 2])
    placeholders_to_ask_for = []
    available_placeholders = ['a', 'b', 'c', 'd', 'e']
    
    for _ in range(num_internal_missing):
        idx = random.randint(1, len(all_factors) - 2)
        placeholder_name = random.choice(available_placeholders)
        placeholders_to_ask_for.append(placeholder_name)
        available_placeholders.remove(placeholder_name)
        problem_factors_list[idx] = placeholder_name
    
    final_placeholder_name = random.choice(['M', 'N', 'P'])
    placeholders_to_ask_for.append(final_placeholder_name)
    problem_factors_list[-1] = final_placeholder_name
    
    question_text = f"有一正整數 {final_placeholder_name} 的所有因數由小到大排列為 {', '.join(map(str, problem_factors_list))}，則 {', '.join(placeholders_to_ask_for)} 的值為何？"
    
    return {
        'question_text': question_text,
        'answer': placeholders_to_ask_for,
        'correct_answer': ', '.join(map(str, all_factors))
    }

def generate(level=1):
    type = random.choice(['type_A', 'type_B', 'type_C'])
    if type == 'type_A': return generate_type_A_problem()
    elif type == 'type_B': return generate_type_B_problem()
    else: return generate_type_C_problem()