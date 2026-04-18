import random
import math
from fractions import Fraction

def generate(level=1):
    """
    生成「常用對數」相關題目。
    包含：
    1. 常用對數的定義應用 ($b = 10^{\log b}$ 或 $\log(10^x) = x$)
    2. 基本常用對數計算 ($\log 1, \log 10^n$)
    3. 常用對數性質應用 (已知 $k = \log b$, 求 $10^{ak}$ 等)
    4. 計算機近似值計算
    5. 位數估計應用
    6. 常用對數概念判斷 (是非題)
    7. 解指數方程式 ($a^k = b$)
    """
    problem_types_l1 = [
        'def_form_10_power',
        'def_log_10_power',
        'calc_simple_log_integer_power',
        'tf_statement_def_b_10logb',
        'tf_statement_def_log_10_x'
    ]
    problem_types_l2 = [
        'def_form_10_power',
        'def_log_10_power',
        'calc_simple_log_integer_power',
        'prop_k_log_b',
        'calc_approx_log',
        'digit_count_application',
        'tf_statement_def_b_10logb',
        'tf_statement_def_log_10_x',
        'tf_statement_digit_count',
        'solve_for_k_in_a_power_k_b'
    ]

    if level == 1:
        problem_type = random.choice(problem_types_l1)
    else: # level 2 or higher
        problem_type = random.choice(problem_types_l2)
    
    if problem_type == 'def_form_10_power':
        return generate_def_form_10_power()
    elif problem_type == 'def_log_10_power':
        return generate_def_log_10_power()
    elif problem_type == 'calc_simple_log_integer_power':
        return generate_calc_simple_log_integer_power()
    elif problem_type == 'prop_k_log_b':
        return generate_prop_k_log_b(level)
    elif problem_type == 'calc_approx_log':
        return generate_calc_approx_log()
    elif problem_type == 'digit_count_application':
        return generate_digit_count_application()
    elif problem_type == 'tf_statement_def_b_10logb':
        return generate_tf_statement_def_b_10logb()
    elif problem_type == 'tf_statement_def_log_10_x':
        return generate_tf_statement_def_log_10_x()
    elif problem_type == 'tf_statement_digit_count':
        return generate_tf_statement_digit_count()
    elif problem_type == 'solve_for_k_in_a_power_k_b':
        return generate_solve_for_k_in_a_power_k_b()
    
    # Fallback in case of an unhandled problem type (should not happen with proper selection)
    return generate_def_form_10_power()

def generate_def_form_10_power():
    """
    生成題目：利用常用對數將 N 表為「10的次方」的形式。
    例：將 2.7 表為 10^log2.7
    """
    num = random.choice([round(random.uniform(0.1, 100), random.randint(1, 2)), random.randint(1, 100)])
    if isinstance(num, float) and num.is_integer(): # 避免出現 2.0 而非 2
        num = int(num)
    
    question_text = f"利用常用對數將 ${num}$ 表為「$10$ 的次方」的形式。"
    correct_answer = f"$10^{{\\log {num}}}$"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "explanation": f"根據常用對數的定義，任意正數 $b$ 皆可表示為 $10^{{\\log b}}$ 的形式。因此，${num} = 10^{{\\log {num}}}$。"
    }

def generate_def_log_10_power():
    """
    生成題目：求 log(10^x) 的值。
    例：求 log(10^3.14) 的值
    """
    exponent_type = random.choice(['int', 'float', 'fraction_root'])
    exponent = 0 # Initialize to avoid UnboundLocalError
    exponent_display = "" # Initialize for display purposes

    if exponent_type == 'int':
        exponent = random.randint(-5, 5)
        exponent_display = str(exponent)
    elif exponent_type == 'float':
        exponent = round(random.uniform(-5.0, 5.0), 2)
        exponent_display = str(exponent)
    else: # fraction_root
        choice = random.choice(['sqrt', 'fraction'])
        if choice == 'sqrt':
            base = random.randint(2, 5)
            exponent_display = f"\\sqrt{{{base}}}"
            exponent = math.sqrt(base) # 實際的數值
        else:
            num_val = random.randint(1, 5)
            den_val = random.randint(num_val + 1, 10)
            exponent_display = f"\\frac{{{num_val}}}{{{den_val}}}"
            exponent = num_val / den_val
    
    question_text = f"求 $\\log(10^{{ {exponent_display} }})$ 的值。"
    # 答案是指數的實際數值
    correct_answer = str(exponent)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "explanation": f"根據常用對數的定義，$\\log(10^{{x}}) = x$。因此，$\\log(10^{{ {exponent_display} }}) = {exponent_display} = {correct_answer}$。"
    }

def generate_calc_simple_log_integer_power():
    """
    生成題目：求 log(N) 的值，其中 N 是 10 的整數次方 (1, 100, 0.001)。
    例：log100, log0.001
    """
    power = random.randint(-4, 4)
    num = 10**power
    
    if power >= 0:
        num_display = str(num)
    else: # 負數次方，顯示為分數或小數
        num_display = str(Fraction(1, 10**abs(power))) if random.random() < 0.5 else str(num)
    
    question_text = f"求 $\\log({num_display})$ 的值。"
    correct_answer = str(power)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "explanation": f"因為 ${num_display} = 10^{{{power}}}$，所以 $\\log({num_display}) = {power}$。"
    }

def generate_prop_k_log_b(level):
    """
    生成題目：已知 k = log b，求 10^{ak} 或 10^{ak} + 10^{bk} 的值。
    例：已知 k = log13，求 10^{2k} 或 10^k + 10^{-k}。
    """
    b_val = random.randint(2, 20)
    
    problem_choice = random.choice(['single_power', 'sum_powers'])
    
    question_text = f"已知 $k = \\log {b_val}$，求下列各數的值：<br>"
    
    if problem_choice == 'single_power':
        a = random.choice([1, 2, 3, -1, -2])
        exponent_expr = f"{a}k" if a != 1 else "k"
        
        result = b_val**a
        
        question_text += f"(1) $10^{{{exponent_expr}}}$。"
        correct_answer = str(result)
        explanation = (
            f"依題意得 ${b_val} = 10^{{\\log {b_val}}} = 10^{{k}}$。<br>"
            f"所以 $10^{{{exponent_expr}}} = (10^{{k}})^{{{a}}} = ({b_val})^{{{a}}} = {result}$。"
        )

    else: # sum_powers
        term1_a = random.choice([1, 2])
        term2_a = -1
        
        exponent_expr_1 = f"{term1_a}k" if term1_a != 1 else "k"
        exponent_expr_2 = f"{term2_a}k" if term2_a != 1 else "-k"
        
        val1 = b_val**term1_a
        val2 = b_val**term2_a
        
        result_frac = Fraction(val1) + Fraction(val2)
        
        question_text += f"(1) $10^{{{exponent_expr_1}}} + 10^{{{exponent_expr_2}}}$。"
        correct_answer = str(result_frac)
        explanation = (
            f"依題意得 ${b_val} = 10^{{\\log {b_val}}} = 10^{{k}}$。<br>"
            f"所以 $10^{{{exponent_expr_1}}} + 10^{{{exponent_expr_2}}} = (10^{{k}})^{{{term1_a}}} + (10^{{k}})^{{{term2_a}}} = ({b_val})^{{{term1_a}}} + ({b_val})^{{{term2_a}}} = {val1} + \\frac{{1}}{{{b_val**abs(term2_a)}}} = {result_frac}$。"
        )
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "explanation": explanation
    }


def generate_calc_approx_log():
    """
    生成題目：求 log N 的值（四捨五入到小數點以下第 X 位）。
    例：求 log1.34 的值（四捨五入到小數點以下第4位）。
    """
    num = round(random.uniform(0.1, 99.9), random.randint(1, 2))
    decimal_places = random.randint(2, 4)
    
    num = max(0.1, num) # 確保 num 為正數

    calculated_log = math.log10(num)
    correct_answer = str(round(calculated_log, decimal_places))
    
    question_text = f"求 $\\log {num}$ 的值（四捨五入到小數點以下第${decimal_places}$位）。"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "explanation": f"利用計算機，依序按下 ${num}$ [log] 可得 $\\log {num} \\approx {calculated_log:.{decimal_places+3}f}$，四捨五入到小數點以下第${decimal_places}$位為 ${correct_answer}$。"
    }

def generate_digit_count_application():
    """
    生成題目：問：$A^{B}$ 是幾位數？ (或 $A^B - 1$)
    例：2^{127}-1 為幾位數？
    """
    base = random.choice([2, 3, 5, 7])
    exponent = random.randint(10, 200)
    
    log_val = exponent * math.log10(base)
    num_digits = math.floor(log_val) + 1
    
    include_minus_one = random.choice([True, False])
    # 避免 N-1 減少位數的情況，例如 100-1 = 99 (3位變2位)
    if include_minus_one and not (base == 10 and log_val.is_integer()):
        question_text = f"問：$ {base}^{{{exponent}}} - 1 $ 是幾位數？"
    else:
        question_text = f"問：$ {base}^{{{exponent}}} $ 是幾位數？"

    correct_answer = str(num_digits)
    
    explanation_base = f"利用 $b = 10^{{\\log b}}$，得 $ {base}^{{{exponent}}} = (10^{{\\log {base}}})^{{{exponent}}} = 10^{{{exponent} \\times \\log {base}}}$。<br>" \
                       f"再使用計算機求得指數部分為 $ {exponent} \\times \\log {base} \\approx {log_val:.3f}$。<br>" \
                       f"可得 $10^{{{math.floor(log_val)}}} < 10^{{{log_val:.3f}}} < 10^{{{math.ceil(log_val)}}}$，即 $10^{{{math.floor(log_val)}}} < {base}^{{{exponent}}} < 10^{{{math.ceil(log_val)}}}$.<br>" \
                       f"因此， $ {base}^{{{exponent}}} $ 是 ${num_digits}$ 位數。"

    if include_minus_one and not (base == 10 and log_val.is_integer()):
         explanation = f"因為 $ {base}^{{{exponent}}} - 1 $ 的個位數不是 $0$ (一般情況下)，所以 $ {base}^{{{exponent}}} - 1 $ 和 $ {base}^{{{exponent}}} $ 位數相同。<br>" \
                       + explanation_base
    else:
        explanation = explanation_base

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "explanation": explanation
    }

def generate_tf_statement_def_b_10logb():
    """
    生成是非題：判斷 b = 10^log b 相關敘述的對錯。
    例：b = 10^log b
    """
    is_correct_statement = random.choice([True, False])
    
    if is_correct_statement:
        b_val = random.randint(1, 100)
        statement = f"$ {b_val} = 10^{{\\log {b_val}}} $"
        correct_answer = "○"
        explanation = f"根據常用對數的定義，任意正數 $b$ 皆可表示為 $10^{{\\log b}}$ 的形式。所以此敘述正確。"
    else:
        b_val = random.randint(2, 100)
        wrong_form = random.choice([
            f"$\\log {b_val} = 10^{{{b_val}}}$",
            f"$ {b_val} = \\log {b_val} $"
        ])
        statement = wrong_form
        correct_answer = "×"
        explanation = f"根據常用對數的定義，${b_val} = 10^{{\\log {b_val}}}$。題目敘述不符合定義，因此錯誤。"
    
    question_text = f"下列敘述對的打「○」，錯的打「×」。<br>(1) {statement}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "explanation": explanation
    }

def generate_tf_statement_def_log_10_x():
    """
    生成是非題：判斷 log(10^x) = x 相關敘述的對錯。
    例：log(10^sqrt(2)) = 2
    """
    is_correct_statement = random.choice([True, False])
    
    exp_val_num = random.choice([random.randint(1, 5), round(random.uniform(1.0, 5.0), 2)])
    exp_val_display = str(exp_val_num)

    if is_correct_statement:
        statement = f"$\\log(10^{{{exp_val_display}}}) = {exp_val_display}$"
        correct_answer = "○"
        explanation = f"根據常用對數的定義，$\\log(10^{{x}}) = x$。所以此敘述正確。"
    else:
        wrong_answer = random.choice([exp_val_num * 2, exp_val_num + 1, exp_val_num - 1])
        if abs(wrong_answer - exp_val_num) < 1e-6: # 確保答案確實是錯的
            wrong_answer += 1
        statement = f"$\\log(10^{{{exp_val_display}}}) = {wrong_answer}$"
        correct_answer = "×"
        explanation = f"根據常用對數的定義，$\\log(10^{{{exp_val_display}}}) = {exp_val_display}$。因此題目敘述錯誤。"
    
    question_text = f"下列敘述對的打「○」，錯的打「×」。<br>(2) {statement}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "explanation": explanation
    }

def generate_tf_statement_digit_count():
    """
    生成是非題：判斷 10^X.Y 的整數部分為 X+1 位數 相關敘述的對錯。
    例：10^18.3 的整數部分為19位數。
    """
    integer_part = random.randint(1, 20)
    fractional_part = round(random.uniform(0.1, 0.9), 1)
    
    exponent_val = integer_part + fractional_part
    
    is_correct_statement = random.choice([True, False])
    
    if is_correct_statement:
        num_digits = integer_part + 1
        statement = f"$10^{{{exponent_val}}}$ 的整數部分為${num_digits}$位數。"
        correct_answer = "○"
        explanation = (
            f"若一個數 $N$ 的位數為 $D$，則 $10^{{D-1}} \\le N < 10^{{D}}$，等價於 $D-1 \\le \\log_{{10}} N < D$。<br>"
            f"題目給定指數為 $10^{{{exponent_val}}}$，則其常用對數為 $\\log_{{10}}(10^{{{exponent_val}}}) = {exponent_val}$。<br>"
            f"因為 ${integer_part} < {exponent_val} < {integer_part + 1}$，所以此數的位數為 ${integer_part + 1}$ 位。<br>"
            f"此敘述正確。"
        )
    else:
        num_digits = integer_part + 1
        wrong_digits = random.choice([num_digits - 1, num_digits + 1, num_digits + random.randint(2, 3)])
        # Ensure it's actually wrong
        if wrong_digits == num_digits:
            wrong_digits += 1
        statement = f"$10^{{{exponent_val}}}$ 的整數部分為${wrong_digits}$位數。"
        correct_answer = "×"
        explanation = (
            f"若一個數 $N$ 的位數為 $D$，則 $10^{{D-1}} \\le N < 10^{{D}}$，等價於 $D-1 \\le \\log_{{10}} N < D$。<br>"
            f"題目給定指數為 $10^{{{exponent_val}}}$，則其常用對數為 $\\log_{{10}}(10^{{{exponent_val}}}) = {exponent_val}$。<br>"
            f"因為 ${integer_part} < {exponent_val} < {integer_part + 1}$，所以此數的位數為 ${integer_part + 1}$ 位。<br>"
            f"題目敘述為 ${wrong_digits}$ 位數，因此錯誤。"
        )
    
    question_text = f"下列敘述對的打「○」，錯的打「×」。<br>(3) {statement}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "explanation": explanation
    }

def generate_solve_for_k_in_a_power_k_b():
    """
    生成題目：設 a^k = b，求 k 的值。（四捨五入到小數點後第 X 位）
    例：設 6^k = 10，求k的值。（四捨五入到小數點後第一位）
    """
    base_a = random.randint(2, 9)
    result_b = random.randint(10, 100)
    decimal_places = random.randint(1, 3)
    
    # a^k = b => k * log(a) = log(b) => k = log(b) / log(a)
    calculated_k = math.log10(result_b) / math.log10(base_a)
    correct_answer = str(round(calculated_k, decimal_places))
    
    question_text = f"設 $ {base_a}^{{k}} = {result_b} $，求 $k$ 的值。（四捨五入到小數點後第${decimal_places}$位）"
    
    explanation = (
        f"對等式 $ {base_a}^{{k}} = {result_b} $ 兩邊取常用對數：<br>"
        f"$\\log({base_a}^{{k}}) = \\log({result_b})$<br>"
        f"$k \\cdot \\log({base_a}) = \\log({result_b})$<br>"
        f"$k = \\frac{{\\log({result_b})}}{{\\log({base_a})}}$<br>"
        f"利用計算機，$k \\approx \\frac{{{math.log10(result_b):.5f}}}{{{math.log10(base_a):.5f}}} \\approx {calculated_k:.{decimal_places+3}f}$。<br>"
        f"四捨五入到小數點後第${decimal_places}$位，得 $k \\approx {correct_answer}$。"
    )

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "explanation": explanation
    }


def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    處理數字（包括浮點數）和字符（'○', '×'）的比較。
    對於浮點數，允許一定的容忍度。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()

    is_correct = False
    feedback = ""

    # 檢查是否為 '○' 或 '×' 的答案
    if correct_answer in ['○', '×']:
        is_correct = (user_answer == correct_answer)
        if is_correct:
            feedback = f"完全正確！答案是「{correct_answer}」。"
        else:
            feedback = f"答案不正確。正確答案應為：「{correct_answer}」。"
    else:
        # 嘗試將答案轉換為浮點數進行數值比較
        try:
            user_num = float(user_answer)
            correct_num = float(correct_answer)
            
            # 使用小於 1e-4 的容忍度進行浮點數比較
            tolerance = 1e-4
            is_correct = abs(user_num - correct_num) < tolerance
            
            if is_correct:
                feedback = f"完全正確！答案是 ${correct_answer}$。"
            else:
                feedback = f"答案不正確。正確答案應為：${correct_answer}$。"
        except ValueError:
            # 如果轉換為浮點數失敗，則可能是含有 LaTeX 格式的字符串答案
            # 在這種情況下，進行精確的字符串比較，並去除可能的數學符號以提高魯棒性
            user_answer_cleaned = user_answer.replace('$', '').replace('{', '').replace('}', '').replace('\\log', 'log').strip()
            correct_answer_cleaned = correct_answer.replace('$', '').replace('{', '').replace('}', '').replace('\\log', 'log').strip()
            
            is_correct = (user_answer_cleaned == correct_answer_cleaned)
            
            if is_correct:
                feedback = f"完全正確！答案是 {correct_answer}。"
            else:
                feedback = f"答案不正確。正確答案應為：{correct_answer}"

    return {"correct": is_correct, "result": feedback, "next_question": True}