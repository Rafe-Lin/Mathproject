import random
from fractions import Fraction
import traceback

def _format_latex_fraction(frac, parenthesize=True):
    """
    格式化分數為 LaTeX 字串的輔助函式
    """
    if not isinstance(frac, Fraction):
        frac = Fraction(frac)

    if frac.denominator == 1:
        val_str = str(frac.numerator)
        if parenthesize and frac.numerator < 0:
             return f"({val_str})"
        return val_str

    num, den = abs(frac.numerator), frac.denominator
    sign = "-" if frac.numerator < 0 else ""
    latex_str = f"{sign}\\frac{{{num}}}{{{den}}}"
    
    if parenthesize:
        return f"({latex_str})"
    else:
        return latex_str

def generate(level=1):
    """
    生成「數的乘方」相關題目 (標準 LaTeX 範本)。
    包含：分數乘方律、同底數大小比較、不同底數大小比較、乘方計算
    """
    try:
        problem_type = random.choice(['power_rule', 'comparison_same_base', 'comparison_different_base', 'calculation'])
        
        if problem_type == 'power_rule':
            return generate_power_rule_problem()
        elif problem_type == 'comparison_same_base':
            return generate_comparison_same_base_problem()
        elif problem_type == 'comparison_different_base':
            return generate_comparison_different_base_problem()
        else: # calculation
            return generate_calculation_problem()
            
    except Exception as e:
        print(f"❌ 生成題目時發生錯誤: {e}")
        traceback.print_exc()
        return {
            "question_text": "題目生成發生錯誤，請查看後端終端機日誌。",
            "answer": "0",
            "correct_answer": "0"
        }

def generate_power_rule_problem():
    """題型：(a/b)^n = a^□ / b^□"""
    num = random.randint(2, 9)
    den = random.randint(2, 9)
    while den == num:
        den = random.randint(2, 9)
        
    if random.random() < 0.5:
        num = -num
        
    # 決定負號顯示位置
    if num < 0 and random.random() < 0.5:
        # Case: (-a)/b 轉寫為 a/(-b)
        base_frac_str = f"\\frac{{{abs(num)}}}{{{-den}}}"
        rhs_num_str = f"{abs(num)}"
        rhs_den_str = f"({-den})"
    else:
        # 一般情況
        base_frac_str = f"\\frac{{{num}}}{{{den}}}"
        rhs_num_str = f"({num})" if num < 0 else f"{num}"
        rhs_den_str = f"{den}"
            
    exponent = random.randint(3, 5)
    
    # 拆解字串
    lhs = f"({base_frac_str})^{{{exponent}}}"
    rhs_numerator = f"{rhs_num_str}^{{□}}"
    rhs_denominator = f"{rhs_den_str}^{{□}}"
    rhs = f"\\frac{{{rhs_numerator}}}{{{rhs_denominator}}}"
    
    # [修正] 將 \\\\ 改為 <br> 以避免顯示反斜線
    question_text = f"在下列□中填入適當的數，使等號成立。<br>${lhs} = {rhs}$"
    correct_answer = str(exponent)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_comparison_same_base_problem():
    """題型：比較 a^m 和 a^n 的大小"""
    if random.random() < 0.5:
        is_base_greater_than_one = True
        if random.random() < 0.5: # 分數
            den = random.randint(2, 5)
            num = den + random.randint(1, 3)
            base_str = _format_latex_fraction(Fraction(num, den))
        else: # 小數
            base_val = random.randint(11, 25) / 10.0
            base_str = str(base_val)
    else:
        is_base_greater_than_one = False
        if random.random() < 0.5: # 分數
            den = random.randint(3, 8)
            num = random.randint(1, den - 1)
            base_str = _format_latex_fraction(Fraction(num, den))
        else: # 小數
            base_val = random.randint(2, 9) / 10.0
            base_str = str(base_val)

    exp1 = random.randint(2, 10)
    exp2 = exp1 + random.randint(1, 10)
    
    if random.random() < 0.5:
        exp1, exp2 = exp2, exp1
            
    if is_base_greater_than_one:
        correct_op = ">" if exp1 > exp2 else "<"
    else:
        correct_op = "<" if exp1 > exp2 else ">"
        
    # [修正] 將 \\\\ 改為 <br>
    question_text = f"比較下列各組數的大小，請在 __ 中填入 > 或 <：<br>$ {base_str}^{{{exp1}}} $ __ $ {base_str}^{{{exp2}}} $"
    
    return {
        "question_text": question_text,
        "answer": correct_op,
        "correct_answer": correct_op
    }

def generate_comparison_different_base_problem():
    """題型：比較 a^m 和 b^n (a > 1, 0 < b < 1)"""
    base1_val = random.randint(101, 120) / 100.0
    base1_str = str(base1_val)
    
    base2_val = random.randint(80, 99) / 100.0
    base2_str = str(base2_val)
    
    exp1 = random.randint(10, 30)
    exp2 = random.randint(10, 30)
    
    term1 = f"{base1_str}^{{{exp1}}}"
    term2 = f"{base2_str}^{{{exp2}}}"
    correct_op = ">"
    
    if random.random() < 0.5:
        term1, term2 = term2, term1
        correct_op = "<"
        
    # [修正] 將 \\\\ 改為 <br>
    question_text = f"比較下列各組數的大小，請在 __ 中填入 > 或 <：<br>$ {term1} $ __ $ {term2} $"
    
    return {
        "question_text": question_text,
        "answer": correct_op,
        "correct_answer": correct_op
    }

def generate_calculation_problem():
    """題型：計算含乘方的算式"""
    if random.random() < 0.6: 
        n1 = random.choice([-2, -1])
        d1 = random.randint(abs(n1) + 1, 4)
        f1 = Fraction(n1, d1)
        exp1 = random.randint(2, 4)

        n2 = random.choice([-3, -2, -1, 1, 2, 3])
        d2 = random.randint(abs(n2) + 1, 5)
        f2 = Fraction(n2, d2)
        exp2 = random.randint(2, 3)

        op_choice = random.choice(['multiply', 'divide'])
        
        term1_val = f1**exp1
        term2_val = f2**exp2
        
        f1_str = _format_latex_fraction(f1)
        f2_str = _format_latex_fraction(f2)

        if op_choice == 'multiply':
            op_str = "\\times"
            result = term1_val * term2_val
        else: # divide
            op_str = "\\div"
            if term2_val == 0: return generate_calculation_problem()
            result = term1_val / term2_val

        # [修正] 將 \\\\ 改為 <br>
        question_text = f"計算下列各式的值。<br>$ {f1_str}^{{{exp1}}} {op_str} {f2_str}^{{{exp2}}} $"
        
    else:
        # Combined operations
        d1 = random.choice([2, 3])
        n1 = random.choice([-1, 1])
        f1 = Fraction(n1, d1)
        exp1 = d1 
        C = d1**exp1
        term1_val = (f1**exp1) * C
        f1_str = _format_latex_fraction(f1)
        term1_q_str = f"{f1_str}^{{{exp1}}} \\times {C}"
        
        d2 = random.choice([3, 5])
        n2 = random.choice([-1, 1])
        f2 = Fraction(n2, d2)
        exp2 = 2
        d3 = random.choice([2, 3])
        n3 = random.choice([-1, 1])
        f3 = Fraction(n3, d3)
        exp3 = 2
        term2_val = (f2**exp2) / (f3**exp3)
        f2_str = _format_latex_fraction(f2)
        f3_str = _format_latex_fraction(f3)
        term2_q_str = f"{f2_str}^{{{exp2}}} \\div {f3_str}^{{{exp3}}}"
        
        op_choice = random.choice(['add', 'subtract'])
        if op_choice == 'add':
            result = term1_val + term2_val
            op_str = "+"
        else:
            result = term1_val - term2_val
            op_str = "-"

        # [修正] 將 \\\\ 改為 <br>
        question_text = f"計算下列各式的值。<br>$ {term1_q_str} {op_str} {term2_q_str} $"

    if result.denominator == 1:
        correct_answer = str(result.numerator)
    else:
        correct_answer = f"{result.numerator}/{result.denominator}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    is_correct = False

    if correct_answer in ['<', '>']:
        is_correct = (user_answer == correct_answer)
        display_answer = correct_answer
        result_text = f"完全正確！答案是 {display_answer}。" if is_correct else f"答案不正確。正確答案應為：${display_answer}$"
    else:
        try:
            user_val = Fraction(user_answer).limit_denominator()
            correct_val = Fraction(correct_answer)
            if user_val == correct_val:
                is_correct = True
        except (ValueError, ZeroDivisionError):
            is_correct = (user_answer.lower() == correct_answer.lower())
        
        frac_ans = Fraction(correct_answer)
        if frac_ans.denominator == 1:
            display_answer = str(frac_ans.numerator)
        else:
            num_str = abs(frac_ans.numerator)
            den_str = frac_ans.denominator
            sign = "-" if frac_ans.numerator < 0 else ""
            display_answer = f"{sign}\\frac{{{num_str}}}{{{den_str}}}"

        if is_correct:
            result_text = f"完全正確！答案是 ${display_answer}$。"
        else:
            result_text = f"答案不正確。正確答案應為：${display_answer}$"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}