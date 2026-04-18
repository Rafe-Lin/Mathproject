import random
from fractions import Fraction
import math
import re

def generate(level=1):
    """
    生成「數據伸縮與平移」相關題目。
    包含：
    1. 數據線性變換後平均數與標準差的計算。
    2. 數據標準化 (Z分數) 的計算。
    3. 比較不同數據組的Z分數。
    4. 反向推導線性變換參數或原始數據統計量。
    5. 概念性判斷題。
    """
    problem_type_options = {
        1: ['linear_transform_basic'],
        2: ['linear_transform_basic', 'standardization_calc'],
        3: ['standardization_calc', 'standardization_compare', 'reverse_linear_transform'],
        4: ['standardization_compare', 'reverse_linear_transform', 'conceptual_tf']
    }
    
    # Ensure level is within bounds
    if level < 1: level = 1
    if level > max(problem_type_options.keys()): level = max(problem_type_options.keys())
    
    problem_type = random.choice(problem_type_options[level])

    if problem_type == 'linear_transform_basic':
        return generate_linear_transform_basic()
    elif problem_type == 'standardization_calc':
        return generate_standardization_calc()
    elif problem_type == 'standardization_compare':
        return generate_standardization_compare()
    elif problem_type == 'reverse_linear_transform':
        return generate_reverse_linear_transform()
    elif problem_type == 'conceptual_tf':
        return generate_conceptual_tf()

def generate_linear_transform_basic():
    # y = ax + b
    # mu_y = a * mu_x + b
    # sigma_y = |a| * sigma_x

    # Generate a (can be int or fraction, positive or negative)
    a_type = random.choice(['integer', 'fraction'])
    if a_type == 'integer':
        a_val = random.randint(-5, 5)
        while a_val == 0: # a cannot be 0 for standard deviation to make sense
            a_val = random.randint(-5, 5)
        
        if a_val == 1:
            a_str_coeff = "" # For equation y = x + b
        elif a_val == -1:
            a_str_coeff = "-" # For equation y = -x + b
        else:
            a_str_coeff = str(a_val)
        a_str_full = a_str_coeff # This is what will be used in LaTeX for 'a'
        
    else: # fraction
        num_raw = random.randint(1, 10)
        den_raw = random.randint(2, 5)
        frac_val_positive = Fraction(num_raw, den_raw)
        
        # Ensure it's not an integer, simplify fraction
        while frac_val_positive.denominator == 1:
            num_raw = random.randint(1, 10)
            den_raw = random.randint(2, 5)
            frac_val_positive = Fraction(num_raw, den_raw)
        
        if random.random() < 0.5:
            a_val = -float(frac_val_positive)
            a_str_full = r"-\\frac{{{}}}{{{}}}".format(frac_val_positive.numerator, frac_val_positive.denominator)
        else:
            a_val = float(frac_val_positive)
            a_str_full = r"\\frac{{{}}}{{{}}}".format(frac_val_positive.numerator, frac_val_positive.denominator)

    # Generate b (integer)
    b = random.randint(-20, 50)
    b_str = f"{'+ ' if b >= 0 else ''}{b}" # Format for y = ax + b string

    # Generate mu_x and sigma_x
    mu_x = random.randint(20, 80)
    sigma_x_int = random.randint(2, 10)
    sigma_x_dec = random.choice([0, 0.5]) # Add a .5 sometimes
    sigma_x = sigma_x_int + sigma_x_dec
    
    # Calculate mu_y and sigma_y
    mu_y = a_val * mu_x + b
    sigma_y = abs(a_val) * sigma_x

    # Format for question text
    # Ensure y = ax + b is nicely formatted, especially if b is negative or a is 1/-1
    if a_type == 'integer' and (a_val == 1 or a_val == -1):
        equation_str = f"$y = {a_str_full}x {b_str}$" # e.g. $y = x + 5$ or $y = -x + 5$
    else:
        equation_str = f"$y = {a_str_full}x {b_str}$" # e.g. $y = 2x + 5$ or $y = \\frac{{1}}{{2}}x + 5$
    
    # Round answers to a reasonable decimal place if they are floats
    mu_y_str = f"{mu_y:.1f}" if not mu_y.is_integer() else str(int(mu_y))
    sigma_y_str = f"{sigma_y:.1f}" if not sigma_y.is_integer() else str(int(sigma_y))

    question_text = (
        f"已知一組數據 $x$ 經過線性變換後得到新數據 $y$，其關係為 {equation_str}。<br>"
        f"若原始數據 $x$ 的平均數 $\\mu_x$ 為 ${mu_x}$，標準差 $\\sigma_x$ 為 ${sigma_x}$，<br>"
        f"請問新數據 $y$ 的平均數 $\\mu_y$ 與標準差 $\\sigma_y$ 各為何？"
        f"(答案四捨五入至小數點後第一位)"
    )
    # To make check easier, provide a structured answer for comparison
    internal_answer = f"mu:{mu_y_str},sigma:{sigma_y_str}"
    correct_answer_feedback = f"平均數: ${mu_y_str}$，標準差: ${sigma_y_str}$"

    return {
        "question_text": question_text,
        "answer": internal_answer, # Store structured answer for robust checking
        "correct_answer": correct_answer_feedback # Store human-readable answer for feedback
    }

def generate_standardization_calc():
    # Z = (x - mu) / sigma
    mu = random.randint(40, 80)
    sigma = random.randint(5, 15)
    
    # Ensure score x is within a reasonable range of mu
    # Make sure it's not too far out, e.g., within 3 standard deviations
    min_x = int(mu - 2.5 * sigma)
    max_x = int(mu + 2.5 * sigma)
    x = random.randint(max(0, min_x), min(100, max_x)) # Scores usually 0-100

    z_score = (x - mu) / sigma
    z_score_str = f"{z_score:.2f}" # Round to 2 decimal places

    question_text = (
        f"某次考試，全班的平均分數 $\\mu$ 為 ${mu}$ 分，標準差 $\\sigma$ 為 ${sigma}$ 分。<br>"
        f"若甲生在這次考試中得到 ${x}$ 分，請問甲生的標準化成績（Z分數）為何？"
        f"(四捨五入至小數點後第二位)"
    )
    correct_answer = z_score_str

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_standardization_compare():
    subjects = ['數學', '英文', '物理', '化學', '國文']
    sub1, sub2 = random.sample(subjects, 2)

    # Subject 1
    mu1 = random.randint(50, 80)
    sigma1 = random.randint(5, 12)
    x1_offset = random.uniform(-1.5, 1.5) * sigma1 # Student score offset from mean
    x1 = int(round(mu1 + x1_offset))
    x1 = max(0, min(100, x1)) # Ensure score is within 0-100

    # Subject 2
    mu2 = random.randint(50, 80)
    sigma2 = random.randint(5, 12)
    x2_offset = random.uniform(-1.5, 1.5) * sigma2
    x2 = int(round(mu2 + x2_offset))
    x2 = max(0, min(100, x2))

    # Calculate Z-scores
    z1 = (x1 - mu1) / sigma1
    z2 = (x2 - mu2) / sigma2

    if z1 > z2:
        better_subject = sub1
    elif z2 > z1:
        better_subject = sub2
    else:
        # If Z-scores are very close, consider them equal or re-generate
        if abs(z1 - z2) < 0.01:
            better_subject = "兩科表現一樣好" 
        else: # Unlikely, but for strictness re-generate. For now, pick one.
            better_subject = random.choice([sub1, sub2])

    question_text = (
        f"某班級 {sub1} 與 {sub2} 成績的平均數與標準差如下：<br>"
        f"- {sub1}：平均數 $\\mu_{{\\text{{{sub1}}}}}$ 為 ${mu1}$ 分，標準差 $\\sigma_{{\\text{{{sub1}}}}}$ 為 ${sigma1}$ 分。<br>"
        f"- {sub2}：平均數 $\\mu_{{\\text{{{sub2}}}}}$ 為 ${mu2}$ 分，標準差 $\\sigma_{{\\text{{{sub2}}}}}$ 為 ${sigma2}$ 分。<br>"
        f"已知班上某生在 {sub1} 考了 ${x1}$ 分，在 {sub2} 考了 ${x2}$ 分。<br>"
        f"相對於全班，該生在哪一科的表現比較好？"
        f"(請填寫科目名稱，如 '{sub1}')"
    )
    correct_answer = better_subject

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_reverse_linear_transform():
    # y = ax + b
    # Generate a full set first and then ask for one component
    a_val = random.randint(-4, 4)
    while a_val == 0:
        a_val = random.randint(-4, 4)
    
    b_val = random.randint(-30, 30)

    mu_x = random.randint(20, 80)
    sigma_x_int = random.randint(2, 10)
    sigma_x_dec = random.choice([0, 0.5])
    sigma_x = sigma_x_int + sigma_x_dec
    
    mu_y = a_val * mu_x + b_val
    sigma_y = abs(a_val) * sigma_x

    # Choose what to ask for
    question_target = random.choice(['mu_x', 'sigma_x', 'a', 'b'])

    # Prepare string representations for the equation
    a_str = ""
    if a_val == 1:
        a_str = ""
    elif a_val == -1:
        a_str = "-"
    else:
        a_str = str(a_val)
    
    b_str = f"{'+ ' if b_val >= 0 else ''}{b_val}"
    
    # Format for question text and correct answer
    correct_ans_val = None
    question_text = ""
    
    if question_target == 'mu_x':
        # Given mu_y, a, b, find mu_x
        equation_str = f"$y = {a_str}x {b_str}$"
        mu_y_str = f"{mu_y:.1f}" if not mu_y.is_integer() else str(int(mu_y))
        
        question_text = (
            f"一組數據 $x$ 經過線性變換得到 $y$，關係為 {equation_str}。<br>"
            f"若新數據 $y$ 的平均數 $\\mu_y$ 為 ${mu_y_str}$，<br>"
            f"請問原始數據 $x$ 的平均數 $\\mu_x$ 為何？"
            f"(答案四捨五入至小數點後第一位)"
        )
        correct_ans_val = mu_x

    elif question_target == 'sigma_x':
        # Given sigma_y, a, find sigma_x (b is irrelevant here)
        equation_str = f"$y = {a_str}x {b_str}$"
        sigma_y_str = f"{sigma_y:.1f}" if not sigma_y.is_integer() else str(int(sigma_y))

        question_text = (
            f"一組數據 $x$ 經過線性變換得到 $y$，關係為 {equation_str}。<br>"
            f"若新數據 $y$ 的標準差 $\\sigma_y$ 為 ${sigma_y_str}$，<br>"
            f"請問原始數據 $x$ 的標準差 $\\sigma_x$ 為何？"
            f"(答案四捨五入至小數點後第一位)"
        )
        correct_ans_val = sigma_x
    
    elif question_target == 'a':
        # Given mu_x, mu_y, b, find a
        # mu_y = a * mu_x + b => a = (mu_y - b) / mu_x
        # Make sure mu_x is not 0 for this formula.
        while mu_x == 0:
            mu_x = random.randint(20, 80)
        
        a_calc = (mu_y - b_val) / mu_x
        
        mu_x_str = str(mu_x)
        mu_y_str = f"{mu_y:.1f}" if not mu_y.is_integer() else str(int(mu_y))
        
        question_text = (
            f"一組數據 $x$ 經過線性變換得到 $y$，關係為 $y = ax {b_str}$。<br>"
            f"若原始數據 $x$ 的平均數 $\\mu_x$ 為 ${mu_x_str}$，新數據 $y$ 的平均數 $\\mu_y$ 為 ${mu_y_str}$，<br>"
            f"請問轉換常數 $a$ 的值為何？"
        )
        correct_ans_val = a_calc

    elif question_target == 'b':
        # Given mu_x, mu_y, a, find b
        # b = mu_y - a * mu_x
        
        mu_x_str = str(mu_x)
        mu_y_str = f"{mu_y:.1f}" if not mu_y.is_integer() else str(int(mu_y))

        b_calc = mu_y - a_val * mu_x
        
        question_text = (
            f"一組數據 $x$ 經過線性變換得到 $y$，關係為 $y = {a_str}x + b$。<br>"
            f"若原始數據 $x$ 的平均數 $\\mu_x$ 為 ${mu_x_str}$，新數據 $y$ 的平均數 $\\mu_y$ 為 ${mu_y_str}$，<br>"
            f"請問轉換常數 $b$ 的值為何？"
        )
        correct_ans_val = b_calc
    
    # Format correct_ans_val for output
    if isinstance(correct_ans_val, float):
        if correct_ans_val.is_integer():
            ans_str = str(int(correct_ans_val))
        else:
            # Try to convert to simple fraction if possible, otherwise use 2 decimal places
            frac_val = Fraction(correct_ans_val).limit_denominator(100)
            if abs(float(frac_val) - correct_ans_val) < 1e-6: # Check if fraction approximation is very close
                if frac_val.denominator == 1:
                    ans_str = str(frac_val.numerator)
                else:
                    ans_str = r"\\frac{{{}}}{{{}}}".format(frac_val.numerator, frac_val.denominator)
            else:
                ans_str = f"{correct_ans_val:.2f}"
    else: # Should be integer from initial generation, but good practice
        ans_str = str(correct_ans_val)

    return {
        "question_text": question_text,
        "answer": ans_str,
        "correct_answer": ans_str
    }

def generate_conceptual_tf():
    statements = [
        {
            "text": r"若將一組數據中的每個數值都加上一個常數 $k$ (其中 $k \neq 0$)，則其平均數會改變，而標準差保持不變。",
            "correct": True
        },
        {
            "text": r"若將一組數據中的每個數值都乘以一個非零常數 $c$，則其平均數會乘以 $c$，標準差也會乘以 $c$。",
            "correct": False, # Standard deviation multiplies by |c|, not c
            "explanation": r"正確的說法是：標準差會乘以 $|c|$。"
        },
        {
            "text": r"若數據 $y_i$ 與數據 $x_i$ 的關係式為 $y_i = -2x_i+5$，則 $\\sigma_y = -2\\sigma_x$。",
            "correct": False, # Should be sigma_y = |-2|sigma_x = 2sigma_x
            "explanation": r"正確的關係式應為 $\\sigma_y = |-2|\\sigma_x = 2\\sigma_x$。"
        },
        {
            "text": r"數據標準化 (Z分數) 是將數據轉換為平均數為 $0$、標準差為 $1$ 的新數據。",
            "correct": True
        },
        {
            "text": r"若兩個學生在不同科目中的 Z 分數相同，表示他們在這兩科中的原始分數也相同。",
            "correct": False,
            "explanation": r"Z 分數相同表示相對於各自班級的表現一樣好，但原始分數可能不同。"
        },
        {
            "text": r"在十個數據中加入一個新的數據 $20$ 後，所得的算術平均數一定會增加 $2$。",
            "correct": False, # Depends on original mean and values
            "explanation": r"平均數的變化取決於新加入數據與原有數據平均數的關係，不一定增加 $2$。"
        }
    ]

    chosen_statement = random.choice(statements)
    
    question_text = f"判斷下列敘述是否正確。請回答「是」或「否」。<br>{chosen_statement['text']}"
    correct_answer = "是" if chosen_statement['correct'] else "否"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def check(user_answer, correct_answer):
    user_ans_processed = user_answer.strip().lower().replace(" ", "").replace("，", ",").replace(":", "=")
    correct_ans_processed = correct_answer.strip().lower().replace(" ", "").replace("，", ",").replace(":", "=")

    is_correct = False
    feedback_msg = ""
    tolerance = 1e-2 # For floating point comparisons

    # Specific handling for linear_transform_basic (structured answer "mu:X,sigma:Y")
    if "mu=" in correct_ans_processed and "sigma=" in correct_ans_processed:
        try:
            user_mu_part = next((p for p in user_ans_processed.split(',') if 'mu' in p), None)
            user_sigma_part = next((p for p in user_ans_processed.split(',') if 'sigma' in p), None)

            correct_mu_part = next((p for p in correct_ans_processed.split(',') if 'mu' in p), None)
            correct_sigma_part = next((p for p in correct_ans_processed.split(',') if 'sigma' in p), None)

            if user_mu_part and user_sigma_part and correct_mu_part and correct_sigma_part:
                user_mu = float(user_mu_part.split('=')[1])
                user_sigma = float(user_sigma_part.split('=')[1])
                
                correct_mu = float(correct_mu_part.split('=')[1])
                correct_sigma = float(correct_sigma_part.split('=')[1])
                
                if abs(user_mu - correct_mu) < tolerance and abs(user_sigma - correct_sigma) < tolerance:
                    is_correct = True
                    feedback_msg = f"完全正確！平均數是 ${correct_mu_part.split('=')[1]}$，標準差是 ${correct_sigma_part.split('=')[1]}$。"
                else:
                    feedback_msg = f"答案不正確。正確答案應為：平均數: ${correct_mu_part.split('=')[1]}$，標準差: ${correct_sigma_part.split('=')[1]}$"
            else:
                feedback_msg = f"答案格式不符或計算錯誤。正確答案應為：平均數: ${correct_mu_part.split('=')[1]}$，標準差: ${correct_sigma_part.split('=')[1]}$"
        except (ValueError, IndexError, AttributeError):
            feedback_msg = f"答案格式不符或計算錯誤。正確答案應為：{correct_answer}" # Use original correct_answer for feedback

    # For numerical answers (standardization_calc, reverse_linear_transform)
    else:
        # Determine if the user's answer can be parsed as a numerical value (float or fraction)
        user_is_numerical = False
        user_val = None
        if user_ans_processed.replace('.', '', 1).replace('-', '', 1).isdigit(): # Can be parsed as float
            try:
                user_val = float(user_ans_processed)
                user_is_numerical = True
            except ValueError:
                pass
        elif r"\\frac{" in user_ans_processed: # Looks like a LaTeX fraction
            match = re.match(r"\\frac\{(-?\d+)\}\{(-?\d+)\}", user_ans_processed)
            if match:
                try:
                    user_val = float(Fraction(int(match.group(1)), int(match.group(2))))
                    user_is_numerical = True
                except (ValueError, ZeroDivisionError):
                    pass

        # Determine if the correct answer is numerical
        correct_is_numerical = False
        correct_val = None
        if correct_ans_processed.replace('.', '', 1).replace('-', '', 1).isdigit():
            try:
                correct_val = float(correct_ans_processed)
                correct_is_numerical = True
            except ValueError:
                pass
        elif r"\\frac{" in correct_ans_processed:
            match = re.match(r"\\frac\{(-?\d+)\}\{(-?\d+)\}", correct_ans_processed)
            if match:
                try:
                    correct_val = float(Fraction(int(match.group(1)), int(match.group(2))))
                    correct_is_numerical = True
                except (ValueError, ZeroDivisionError):
                    pass
        
        if user_is_numerical and correct_is_numerical:
            if abs(user_val - correct_val) < tolerance:
                is_correct = True
                feedback_msg = f"完全正確！答案是 ${correct_answer}$。"
            else:
                feedback_msg = f"答案不正確。正確答案應為：${correct_answer}$"
        # For string answers (standardization_compare, conceptual_tf)
        else:
            if user_ans_processed == correct_ans_processed:
                is_correct = True
                feedback_msg = f"完全正確！答案是 ${correct_answer}$。"
            else:
                feedback_msg = f"答案不正確。正確答案應為：${correct_answer}$"

    return {"correct": is_correct, "result": feedback_msg, "next_question": True}