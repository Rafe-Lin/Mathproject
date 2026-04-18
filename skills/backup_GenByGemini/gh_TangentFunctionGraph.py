import random
from fractions import Fraction
import math

def generate(level=1):
    """
    生成「正切函數圖形」相關題目。
    包含：
    1. 週期性
    2. 定義域與漸近線
    3. 值域
    4. 對稱性
    5. 象限內正負號
    """
    problem_types = [
        'periodicity',
        'domain_asymptote',
        'range',
        'symmetry',
        'sign_quadrant'
    ]
    
    problem_type = random.choice(problem_types)

    if problem_type == 'periodicity':
        return generate_periodicity_problem(level)
    elif problem_type == 'domain_asymptote':
        return generate_domain_asymptote_problem(level)
    elif problem_type == 'range':
        return generate_range_problem()
    elif problem_type == 'symmetry':
        return generate_symmetry_problem()
    else: # sign_quadrant
        return generate_sign_quadrant_problem()

def generate_periodicity_problem(level):
    """
    生成關於正切函數週期的問題，例如 $y = \\tan(bx)$ 的週期。
    """
    # y = tan(bx) 的週期為 pi/|b|
    # b_val choices can include integers and simple fractions
    if level == 1:
        b_val = random.choice([1, 2, 3, Fraction(1, 2)])
    else: # level >= 2, introduce more complex coefficients
        b_val = random.choice([1, 2, 3, 4, -1, -2, Fraction(1, 2), Fraction(-1, 2), Fraction(2, 3), Fraction(-3, 4)])
    
    abs_b = abs(b_val)
    
    func_str_b = ""
    if b_val == 1:
        func_str_b = "x"
    elif b_val == -1:
        func_str_b = "-x"
    elif isinstance(b_val, Fraction):
        if b_val.numerator == 1:
            func_str_b = fr"\\frac{{x}}{{{b_val.denominator}}}" if b_val > 0 else fr"-\\frac{{x}}{{{abs(b_val.denominator)}}}"
        elif b_val.numerator == -1:
            func_str_b = fr"-\\frac{{x}}{{{b_val.denominator}}}"
        else:
            func_str_b = fr"\\frac{{{b_val.numerator}x}}{{{b_val.denominator}}}" if b_val > 0 else fr"-\\frac{{{abs(b_val.numerator)}x}}{{{abs(b_val.denominator)}}}"
    else: # integer
        func_str_b = fr"{b_val}x"

    function_text = fr"$y = \\tan({func_str_b})$"

    # Calculate correct period for checking
    period_numerator = math.pi
    period_denominator = abs_b

    if period_denominator == 1:
        correct_period_check = "pi"
        correct_period_latex = r"$\\pi$"
    elif isinstance(period_denominator, Fraction):
        # Period = pi / (num/den) = pi * den / num
        actual_num = period_denominator.denominator
        actual_den = period_denominator.numerator
        if actual_den == 1:
            correct_period_check = f"{actual_num}pi"
            correct_period_latex = fr"${{{actual_num}}}\\pi$"
        else:
            correct_period_check = f"{actual_num}pi/{actual_den}"
            correct_period_latex = fr"$\\frac{{{actual_num}\\pi}}{{{actual_den}}}$"
    else: # integer
        correct_period_check = f"pi/{abs_b}"
        correct_period_latex = fr"$\\frac{{\\pi}}{{{abs_b}}}$"

    question_text = f"請問函數 {function_text} 的週期是多少？"
    
    return {
        "question_text": question_text,
        "answer": correct_period_check,
        "correct_answer": correct_period_check
    }

def generate_domain_asymptote_problem(level):
    """
    生成關於正切函數定義域或漸近線的問題。
    """
    problem_subtype = random.choice(['undefined_value', 'asymptote_equation'])
    
    if problem_subtype == 'undefined_value':
        # Question about a specific value not in the domain of tan(x)
        # Undefined values for tan(x) are x = pi/2 + n*pi
        n_val = random.choice([-2, -1, 0, 1, 2])
        undefined_value_num = 1 + 2 * n_val # numerator of pi/2, 3pi/2, etc.
        
        if undefined_value_num == 1:
            correct_value_latex = r"$\\frac{{\\pi}}{2}$"
            correct_value_check = "pi/2"
        elif undefined_value_num == -1:
            correct_value_latex = r"$-\\frac{{\\pi}}{2}$"
            correct_value_check = "-pi/2"
        else:
            correct_value_latex = fr"$\\frac{{{undefined_value_num}\\pi}}{2}$"
            correct_value_check = f"{undefined_value_num}pi/2"

        question_text = f"下列哪個 $x$ 值不在函數 $y = \\tan(x)$ 的定義域中？<br>(請以 ${correct_value_latex}$ 的形式回答)"
        
        return {
            "question_text": question_text,
            "answer": correct_value_check, # Hinting with the answer itself for specific format
            "correct_answer": correct_value_check
        }

    else: # asymptote_equation
        # Question about vertical asymptotes in a given interval for y = tan(bx)
        
        b_val = 1
        func_str = r"$y = \\tan(x)$"
        
        # Interval for tan(x)
        interval_start_factor = 0
        interval_end_factor = random.choice([2, 3, 4]) 
        
        if level >= 2 and random.random() < 0.6: # More complex functions for level 2
            b_val = random.choice([2, 3, Fraction(1, 2), Fraction(2, 3)])
            
            if b_val == 2:
                func_str = r"$y = \\tan(2x)$"
                interval_end_factor = random.choice([1, 1.5, 2]) # Shorter interval due to smaller period
            elif b_val == 3:
                func_str = r"$y = \\tan(3x)$"
                interval_end_factor = random.choice([1, 2]) / 3 * random.choice([1, 2]) * 3
            elif b_val == Fraction(1, 2):
                func_str = r"$y = \\tan(\\frac{{1}}{2}x)$"
                interval_end_factor = random.choice([3, 4, 5]) 
            elif b_val == Fraction(2, 3):
                func_str = r"$y = \\tan(\\frac{{2}}{3}x)$"
                interval_end_factor = random.choice([2, 3, 4])
        
        interval_start = interval_start_factor * math.pi
        interval_end = interval_end_factor * math.pi

        # Asymptotes are x = (pi/2 + n*pi) / b_val
        asymptotes = []
        # Iterate n to find asymptotes within the interval
        n_min = math.floor((interval_start * b_val - math.pi/2) / math.pi) -1
        n_max = math.ceil((interval_end * b_val - math.pi/2) / math.pi) +1
        
        for n in range(n_min, n_max):
            candidate_x = (math.pi/2 + n * math.pi) / b_val
            if candidate_x > interval_start and candidate_x < interval_end:
                asymptotes.append(candidate_x)
        
        if not asymptotes:
            # Fallback if no asymptotes are found (e.g., very small interval)
            # This should be rare with the chosen intervals
            question_text = f"請問函數 {func_str} 在區間 $(0, \\pi)$ 內有幾條垂直漸近線？"
            correct_answer_str = "0"
            
            return {
                "question_text": question_text,
                "answer": correct_answer_str,
                "correct_answer": correct_answer_str
            }
        else:
            asymptote_strs_latex = []
            asymptote_strs_check = []
            
            for a in sorted(asymptotes):
                # Convert float 'a' (like 1.57 for pi/2) back to symbolic fraction of pi
                fraction_of_pi = Fraction(a / math.pi).limit_denominator(100)
                
                if fraction_of_pi.denominator == 1:
                    if fraction_of_pi.numerator == 1:
                        asymptote_latex = r"\\pi"
                        asymptote_check = "pi"
                    else:
                        asymptote_latex = fr"{fraction_of_pi.numerator}\\pi"
                        asymptote_check = f"{fraction_of_pi.numerator}pi"
                elif fraction_of_pi.numerator == 1:
                    asymptote_latex = fr"\\frac{{\\pi}}{{{fraction_of_pi.denominator}}}"
                    asymptote_check = f"pi/{fraction_of_pi.denominator}"
                else:
                    asymptote_latex = fr"\\frac{{{fraction_of_pi.numerator}\\pi}}{{{fraction_of_pi.denominator}}}"
                    asymptote_check = f"{fraction_of_pi.numerator}pi/{fraction_of_pi.denominator}"
                
                asymptote_strs_latex.append(fr"$x = {asymptote_latex}$")
                asymptote_strs_check.append(asymptote_check)

            # Format interval end for display
            interval_end_latex_val = Fraction(interval_end_factor).limit_denominator(100)
            if interval_end_latex_val.denominator == 1:
                interval_end_latex = fr"${{{interval_end_latex_val.numerator}}}\\pi$"
            else:
                interval_end_latex = fr"$\\frac{{{interval_end_latex_val.numerator}\\pi}}{{{interval_end_latex_val.denominator}}}$"
            
            question_text = f"請問函數 {func_str} 在區間 $(0, {interval_end_latex})$ 內的垂直漸近線方程式為何？<br>(請以逗號分隔，由小到大排列，例如：'pi/4, 3pi/4')"
            correct_answer_str = ", ".join(asymptote_strs_check)
            
            return {
                "question_text": question_text,
                "answer": correct_answer_str,
                "correct_answer": correct_answer_str
            }


def generate_range_problem():
    """
    生成關於正切函數值域的問題。
    """
    func_str = r"$y = \\tan(x)$"
    question_text = f"請問函數 {func_str} 的值域為何？"
    correct_answer = r"$(-\\infty, \\infty)$" # LaTeX interval notation
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_symmetry_problem():
    """
    生成關於正切函數對稱性的問題。
    """
    func_str = r"$y = \\tan(x)$"
    question_text = f"請問函數 {func_str} 是奇函數、偶函數、還是兩者皆非？"
    correct_answer = "奇函數"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_sign_quadrant_problem():
    """
    生成關於正切函數在特定象限內正負號的問題。
    """
    quadrants = {
        1: "第一",
        2: "第二",
        3: "第三",
        4: "第四"
    }
    
    quadrant_num = random.choice([1, 2, 3, 4])
    quadrant_text = quadrants[quadrant_num]
    
    if quadrant_num in [1, 3]:
        correct_sign = "正"
    else:
        correct_sign = "負"
        
    question_text = f"如果 $x$ 落在{quadrant_text}象限，請問 $\\tan(x)$ 的值是正還是負？"
    
    return {
        "question_text": question_text,
        "answer": correct_sign,
        "correct_answer": correct_sign
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip().replace(" ", "").lower()
    correct_answer = correct_answer.strip().replace(" ", "").lower()

    is_correct = False
    
    # 1. Direct string match (for text answers like "奇函數", "正", "負")
    if user_answer == correct_answer:
        is_correct = True
    
    # 2. Handle specific keywords and variations (case-insensitive, sometimes simplified)
    if not is_correct:
        if correct_answer == "奇函數":
            if user_answer in ["奇函數", "odd", "oddfunction"]:
                is_correct = True
        elif correct_answer == "偶函數": 
            if user_answer in ["偶函數", "even", "evenfunction"]:
                is_correct = True
        elif correct_answer == "正":
            if user_answer in ["正", "positive"]:
                is_correct = True
        elif correct_answer == "負":
            if user_answer in ["負", "negative"]:
                is_correct = True
        elif correct_answer in [r"$(-\\infty, \\infty)$".replace(" ", "").lower(), "(-inf,inf)", "(-infinity,infinity)", "r", "實數"]: # Range
            if user_answer in [r"$(-\\infty, \\infty)$".replace(" ", "").lower(), "(-inf,inf)", "(-infinity,infinity)", "r", "實數"]:
                is_correct = True

    # 3. Handle numerical/mathematical expressions involving pi
    if not is_correct:
        # Substitute 'pi' with its numerical value for evaluation
        # This allows eval to correctly calculate expressions like "pi/2", "2*pi"
        user_answer_for_eval = user_answer.replace("pi", str(math.pi)) 
        correct_answer_for_eval = correct_answer.replace("pi", str(math.pi))

        try:
            # If multiple parts (e.g., for asymptotes, comma-separated values)
            if "," in correct_answer_for_eval:
                user_parts = [p.strip() for p in user_answer_for_eval.split(',')]
                correct_parts = [p.strip() for p in correct_answer_for_eval.split(',')]
                
                if len(user_parts) == len(correct_parts):
                    user_floats = sorted([float(eval(p)) for p in user_parts])
                    correct_floats = sorted([float(eval(p)) for p in correct_parts])
                    
                    # Compare floats with a small relative tolerance
                    if all(math.isclose(u, c, rel_tol=1e-9) for u, c in zip(user_floats, correct_floats)):
                        is_correct = True
            # Single numerical expression
            else:
                if math.isclose(float(eval(user_answer_for_eval)), float(eval(correct_answer_for_eval)), rel_tol=1e-9):
                    is_correct = True
        except (ValueError, NameError, SyntaxError):
            pass # Not a valid mathematical expression for eval, fall back to string comparison

    # Final feedback message
    if is_correct:
        # Replace 'pi' back with LaTeX \\pi for display in feedback
        feedback_text = f"完全正確！答案是 ${correct_answer.replace('pi', r'\\pi')}$。"
    else:
        feedback_text = f"答案不正確。正確答案應為：${correct_answer.replace('pi', r'\\pi')}$"
        
    return {"correct": is_correct, "result": feedback_text, "next_question": True}