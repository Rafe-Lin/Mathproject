import random
from fractions import Fraction
import re

def _format_fraction(f):
    """
    Helper function to format a Fraction object into a LaTeX string.
    Handles proper, improper, and mixed fractions.
    """
    if f.denominator == 1:
        return str(f.numerator)

    sign = "" if f >= 0 else "-"
    f_abs = abs(f)
    
    num = f_abs.numerator
    den = f_abs.denominator
    
    if num < den:  # Proper fraction
        return f"{sign}\\frac{{{num}}}{{{den}}}"
    else:  # Improper fraction -> mixed number
        whole = num // den
        rem_num = num % den
        if rem_num == 0:
            return f"{sign}{whole}"
        else:
            return f"{sign}{whole} \\frac{{{rem_num}}}{{{den}}}"

def generate(level=1):
    """
    生成「相反數與絕對值」相關題目 (標準 LaTeX 範本)。
    包含：
    1. 求相反數
    2. 求絕對值
    3. 數值/絕對值大小比較
    4. 由絕對值反推原數
    5. 給定絕對值範圍，求所有整數
    """
    problem_type = random.choice([
        'opposite_number',
        'abs_value',
        'compare',
        'abs_solve',
        'abs_range'
    ])
    
    if problem_type == 'opposite_number':
        return generate_opposite_number_problem()
    elif problem_type == 'abs_value':
        return generate_abs_value_problem()
    elif problem_type == 'compare':
        return generate_compare_problem()
    elif problem_type == 'abs_solve':
        return generate_abs_solve_problem()
    else: # abs_range
        return generate_abs_range_problem()

def generate_opposite_number_problem():
    """生成求相反數的題目。"""
    subtype = random.choice(['int', 'dec', 'frac', 'double_neg'])
    
    if subtype == 'int':
        val = random.choice([i for i in range(-20, 21) if i != 0])
        q_val_str = str(val)
        ans_val_str = str(-val)
    elif subtype == 'dec':
        val = round(random.uniform(-15.0, 15.0), 1)
        if val == 0.0: val = 3.7
        q_val_str = str(val)
        ans_val_str = str(-val)
    elif subtype == 'frac':
        sign = random.choice([-1, 1])
        num = random.randint(1, 10)
        den = random.randint(num, 15)
        if den == num: den += 1
        val = Fraction(num, den) * sign
        q_val_str = _format_fraction(val)
        ans_val_str = _format_fraction(-val)
    else: # double_neg
        val = random.randint(1, 20)
        q_val_str = f"-(-{val})"
        ans_val_str = str(-val)
        
    question_text = f"請問 ${q_val_str}$ 的相反數為何？"
    
    return {
        "question_text": question_text,
        "answer": ans_val_str,
        "correct_answer": ans_val_str
    }

def generate_abs_value_problem():
    """生成求絕對值的題目。"""
    subtype = random.choice(['int', 'dec', 'frac'])
    
    if subtype == 'int':
        val = random.choice([i for i in range(-20, 21) if i != 0])
        q_val_str = str(val)
        ans_val_str = str(abs(val))
    elif subtype == 'dec':
        val = round(random.uniform(-15.0, 15.0), 1)
        if val == 0.0: val = -4.2
        q_val_str = str(val)
        ans_val_str = str(abs(val))
    else: # frac
        sign = random.choice([-1, 1])
        num = random.randint(1, 10)
        den = random.randint(num, 15)
        if den == num: den += 1
        val = Fraction(num, den) * sign
        q_val_str = _format_fraction(val)
        ans_val_str = _format_fraction(abs(val))

    question_text = f"請寫出 $|{q_val_str}|$ 的值。"
    
    return {
        "question_text": question_text,
        "answer": ans_val_str,
        "correct_answer": ans_val_str
    }

def generate_compare_problem():
    """生成比較大小的題目，包含絕對值或負數。"""
    subtype = random.choice(['abs_compare', 'num_compare'])
    
    if subtype == 'abs_compare':
        a = random.randint(-20, 20)
        b = random.randint(-20, 20)
        while a == b or abs(a) == abs(b):
            b = random.randint(-20, 20)
        op = ">" if abs(a) > abs(b) else "<"
        question_text = f"比較 $|{a}|$ 和 $|{b}|$ 的大小。(請填入 $>$、$<$ 或 $=$)"
    else: # num_compare, specifically for negative numbers
        a = -random.randint(1, 25)
        b = -random.randint(1, 25)
        while a == b:
            b = -random.randint(1, 25)
        op = ">" if a > b else "<"
        question_text = f"比較 ${a}$ 和 ${b}$ 的大小。(請填入 $>$、$<$ 或 $=$)"
        
    return {
        "question_text": question_text,
        "answer": op,
        "correct_answer": op
    }

def generate_abs_solve_problem():
    """生成由絕對值反推原數的題目。"""
    k = random.randint(1, 25)
    
    question_text = f"在數線上，有一數 $a$，若 $|a|={k}$，則 $a$ 是多少？ (若有多個答案，請用逗號分隔)"
    correct_answer = f"{-k},{k}"  # Canonical form: sorted, comma-separated
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_abs_range_problem():
    """生成給定絕對值範圍，求所有整數的題目。"""
    k = random.randint(3, 8)
    subtype = random.choice(['all', 'positive', 'negative'])
    
    if subtype == 'all':
        question_text = f"寫出絕對值小於 ${k}$ 的所有整數。(答案請用逗號分隔，由小到大排列)"
        ans_list = list(range(-(k - 1), k))
    elif subtype == 'positive':
        question_text = f"已知 $c$ 為正整數，且 $|c| < {k}$，則 $c$ 可能是多少？(答案請用逗號分隔，由小到大排列)"
        ans_list = list(range(1, k))
    else: # negative
        question_text = f"已知 $c$ 為負整數，且 $|c| < {k}$，則 $c$ 可能是多少？(答案請用逗號分隔，由小到大排列)"
        ans_list = list(range(-(k - 1), 0))
        
    correct_answer = ",".join(map(str, sorted(ans_list)))
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確，可處理數字、比較符號、逗號分隔列表。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    is_correct = False

    # 檢查逗號分隔的答案 (e.g., abs_solve, abs_range)
    if ',' in correct_answer:
        try:
            user_parts = re.split(r'[\s,，或]+', user_answer)
            user_parts_cleaned = [p for p in user_parts if p]
            user_set = set(map(int, user_parts_cleaned))
            correct_set = set(map(int, correct_answer.split(',')))
            is_correct = (user_set == correct_set)
        except (ValueError, AttributeError):
            is_correct = False
    # 檢查其他類型的答案
    else:
        is_correct = (user_answer.upper() == correct_answer.upper())
        if not is_correct:
            try:
                if float(user_answer) == float(correct_answer):
                    is_correct = True
            except (ValueError, TypeError):
                pass

    # 為結果顯示格式化正確答案
    display_answer = correct_answer
    if ',' in correct_answer:
        parts = [int(p) for p in correct_answer.split(',')]
        if len(parts) == 2 and parts[0] == -parts[1]: # For |a|=k case
            display_answer = f"{parts[1]} \\text{{ 或 }} {parts[0]}"
        else: # For range case
            display_answer = ", ".join(map(str, sorted(parts)))

    result_text = f"完全正確！答案是 ${display_answer}$。" if is_correct else f"答案不正確。正確答案應為：${display_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}
