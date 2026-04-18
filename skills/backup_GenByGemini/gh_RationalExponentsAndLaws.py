import random
from fractions import Fraction
import math

def get_prime_factors(n):
    factors = {}
    d = 2
    temp = n
    while d * d <= temp:
        while temp % d == 0:
            factors[d] = factors.get(d, 0) + 1
            temp //= d
        d += 1
    if temp > 1:
        factors[temp] = factors.get(temp, 0) + 1
    return factors

def get_base_and_power(n):
    if n <= 1:
        return (n, 1)
    for base in range(2, int(n**0.5) + 2):
        temp_n = n
        power = 0
        while temp_n > 0 and temp_n % base == 0:
            temp_n //= base
            power += 1
        if temp_n == 1:
            return (base, power)
    return (n, 1)

def simplify_radical(num, root_n):
    if num == 1:
        return 1, 1
    if root_n == 1:
        return num, 1
    if num == 0:
        return 0, 1

    coeff_sign = 1
    if num < 0:
        if root_n % 2 == 1:
            coeff_sign = -1
            num = abs(num)
        else:
            return None, None # Invalid for even roots of negative numbers
    
    factors = get_prime_factors(num)
    
    out_coeff = 1
    in_radicand = 1
    
    for prime, count in factors.items():
        extracted_power = count // root_n
        remaining_power = count % root_n
        
        out_coeff *= (prime ** extracted_power)
        in_radicand *= (prime ** remaining_power)
        
    return coeff_sign * out_coeff, in_radicand

def format_radical(coeff, radicand_in, root_n):
    if radicand_in == 1 and root_n >= 1:
        return str(coeff)
    
    if root_n == 2:
        if coeff == 1:
            return f"\\sqrt{{{radicand_in}}}"
        elif coeff == -1:
            return f"-\\sqrt{{{radicand_in}}}"
        else:
            return f"{coeff}\\sqrt{{{radicand_in}}}"
    else:
        if coeff == 1:
            return f"\\sqrt[{{{root_n}}}]{{{{ {radicand_in} }}}}"
        elif coeff == -1:
            return f"-\\sqrt[{{{root_n}}}]{{{{ {radicand_in} }}}}"
        else:
            return f"{coeff}\\sqrt[{{{root_n}}}]{{{{ {radicand_in} }}}}"

def generate_rad_conversion_problem(level):
    base_choices = [2, 3, 4, 5, 6, 7, 8, 9, 10, 16, 25, 27, 32]
    base = random.choice(base_choices)
    
    numerator = random.randint(1, 4)
    denominator = random.randint(2, 5)

    frac = Fraction(numerator, denominator)
    numerator = frac.numerator
    denominator = frac.denominator

    is_negative_exponent = False
    if level >= 2 and random.random() < 0.4:
        is_negative_exponent = True
    
    exponent_val = Fraction(numerator, denominator)
    exponent_str = f"\\frac{{{numerator}}}{{{denominator}}}"
    if is_negative_exponent:
        exponent_val = -exponent_val
        exponent_str = f"-\\frac{{{numerator}}}{{{denominator}}}"
        
    question_text = f"以根式表示下列各數： ${base}^{{{exponent_str}}}$。"
    
    rad_base_val = base ** abs(exponent_val.numerator)
    rad_coeff, rad_val = simplify_radical(rad_base_val, exponent_val.denominator)

    if rad_coeff is None: # Should not happen with positive base, but defensive
        return generate_rad_conversion_problem(level)

    radical_form = format_radical(rad_coeff, rad_val, exponent_val.denominator)
    
    if is_negative_exponent:
        if rad_coeff == 0: # 0^(-x) is undefined, but base is chosen positive
            correct_answer = "undefined" 
        elif rad_coeff == 1 and rad_val == 1: # base is 1
            correct_answer = "1"
        else:
            correct_answer = f"\\frac{{1}}{{{radical_form}}}"
    else:
        correct_answer = radical_form

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_exp_simplification_problem(level):
    problem_template = random.choice([1, 2, 3])
    
    if problem_template == 1: # (A^p)^(-q/r) or A^(p/q) where A is a power
        base_val = random.choice([4, 8, 9, 16, 25, 27, 32, 64, 81, 100])
        base_of_base, power_of_base = get_base_and_power(base_val)

        target_final_exp = random.randint(-3, 3)
        while target_final_exp == 0:
            target_final_exp = random.randint(-3, 3)
        
        outer_exp = Fraction(target_final_exp, power_of_base)
        
        question_text = f"利用指數律，求下列各式的值： ${base_val}^{{{outer_exp}}}$。"
        
        if target_final_exp < 0:
            correct_answer = f"\\frac{{1}}{{{base_of_base ** (-target_final_exp)}}}"
        else:
            correct_answer = str(base_of_base ** target_final_exp)

    elif problem_template == 2: # (A/B)^(-p/q) type
        common_power = random.randint(2, 4)
        base_val1 = random.choice([2, 3, 5])
        base_val2 = random.choice([2, 3, 4, 5])
        while base_val1 == base_val2:
             base_val2 = random.choice([2, 3, 4, 5])
        
        num1 = base_val1 ** common_power
        num2 = base_val2 ** common_power
        
        target_final_exp = random.randint(-3, 3)
        while target_final_exp == 0:
            target_final_exp = random.randint(-3, 3)
        
        outer_exp = Fraction(target_final_exp, common_power)
        
        question_text = f"利用指數律，求下列各式的值： $({num1}/{num2})^{{{outer_exp}}}$。"
        
        base_fraction = Fraction(base_val1, base_val2)
        result_frac = base_fraction ** target_final_exp
        
        if result_frac.denominator == 1:
            correct_answer = str(result_frac.numerator)
        else:
            if result_frac.numerator < 0: # Should not happen with positive bases
                correct_answer = f"-\\frac{{{-result_frac.numerator}}}{{{result_frac.denominator}}}"
            else:
                correct_answer = f"\\frac{{{result_frac.numerator}}}{{{result_frac.denominator}}}"

    elif problem_template == 3: # a^p * a^q type
        base = random.choice([2, 3, 5, 7])
        
        exp1_num = random.randint(-3, 3)
        exp1_den = random.randint(2, 4)
        while exp1_num == 0: exp1_num = random.randint(-3, 3)
        exp1 = Fraction(exp1_num, exp1_den)

        exp2_num = random.randint(-3, 3)
        exp2_den = random.randint(2, 4)
        while exp2_num == 0: exp2_num = random.randint(-3, 3)
        exp2 = Fraction(exp2_num, exp2_den)

        sum_exp = exp1 + exp2
        while sum_exp.denominator not in [1, 2, 3, 4] or sum_exp.numerator == 0:
            exp1_num = random.randint(-3, 3)
            exp1_den = random.randint(2, 4)
            while exp1_num == 0: exp1_num = random.randint(-3, 3)
            exp1 = Fraction(exp1_num, exp1_den)

            exp2_num = random.randint(-3, 3)
            exp2_den = random.randint(2, 4)
            while exp2_num == 0: exp2_num = random.randint(-3, 3)
            exp2 = Fraction(exp2_num, exp2_den)
            sum_exp = exp1 + exp2
            
        question_text = f"利用指數律，求下列各式的值： ${base}^{{{exp1}}} \\times {base}^{{{exp2}}}$。"

        if sum_exp.denominator == 1:
            final_exponent_int = sum_exp.numerator
            if final_exponent_int < 0:
                correct_answer = f"\\frac{{1}}{{{base ** (-final_exponent_int)}}}"
            else:
                correct_answer = str(base ** final_exponent_int)
        else:
            rad_base_val = base ** sum_exp.numerator
            if sum_exp.numerator < 0:
                rad_coeff, rad_val = simplify_radical(abs(rad_base_val), sum_exp.denominator)
                if rad_coeff is None:
                    return generate_exp_simplification_problem(level) # Regenerate if invalid
                radical_form = format_radical(abs(rad_coeff), rad_val, sum_exp.denominator)
                if abs(rad_coeff) == 1 and rad_val == 1:
                    correct_answer = str(rad_coeff) # e.g. 1/1
                else:
                    correct_answer = f"\\frac{{1}}{{{radical_form}}}"
            else:
                rad_coeff, rad_val = simplify_radical(rad_base_val, sum_exp.denominator)
                if rad_coeff is None:
                    return generate_exp_simplification_problem(level) # Regenerate if invalid
                correct_answer = format_radical(rad_coeff, rad_val, sum_exp.denominator)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_alg_manipulation_problem(level):
    k = random.randint(2, 5)
    
    question_text = f"已知 $a > 0$ 且 $a^{{1/2}} + a^{{-1/2}} = {k}$，求 $a + a^{{-1}}$ 的值。"
    correct_answer = str(k*k - 2)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_find_exponent_problem(level):
    base = random.choice([2, 3, 5, 7, 11])
    numerator = random.randint(1, 5)
    denominator = random.randint(2, 6)
    
    frac = Fraction(numerator, denominator)
    numerator = frac.numerator
    denominator = frac.denominator
    
    question_text = f"已知 $r$ 為有理數，且 ${base}^r = \\sqrt[{{{denominator}}}]{{{{ {base}^{{{numerator}}} }}}}`，求 $r$ 的值。"
    correct_answer = f"\\frac{{{numerator}}}{{{denominator}}}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_word_problem(level):
    possible_exponents = [Fraction(1,2), Fraction(2,3), Fraction(3,2), Fraction(3,4), Fraction(4,3)]
    exp = random.choice(possible_exponents)
    a, b = exp.numerator, exp.denominator

    factor_x_candidates = []
    if b == 2:
        factor_x_candidates = [4, 9, 16, 25, 36, 49, 64, 81, 100, 400]
    elif b == 3:
        factor_x_candidates = [8, 27, 64, 125, 1000]
    elif b == 4:
        factor_x_candidates = [16, 81, 256, 625, 10000]
    
    factor_x = random.choice(factor_x_candidates)

    ans1_val_frac = factor_x ** exp
    ans1_val_float = float(ans1_val_frac)

    options = []
    if ans1_val_float >= 10:
        ans1_option_int = round(ans1_val_float / 10) * 10
        if ans1_option_int == 0: ans1_option_int = 10
        ans1_option_str = str(ans1_option_int)

        options_base = [ans1_option_int - 20, ans1_option_int - 10, ans1_option_int, ans1_option_int + 10, ans1_option_int + 20]
        options_base = [str(o) for o in options_base if o > 0]
        options_base = list(set(options_base))
        options_base.sort(key=int)
        
        while len(options_base) < 5:
            options_base.append(str(int(options_base[-1]) + 10))
        options = random.sample(options_base, min(5, len(options_base)))
        options.sort(key=int)
        if ans1_option_str not in options:
            options[random.randint(0, len(options)-1)] = ans1_option_str
            options.sort(key=int)
        
    else:
        ans1_option_str = str(int(round(ans1_val_float)))
        
        options_base = [int(ans1_val_float) + i for i in range(-2, 3)]
        options_base = [str(o) for o in options_base if o > 0]
        options_base = list(set(options_base))
        options_base.sort(key=int)

        while len(options_base) < 5:
            options_base.append(str(int(options_base[-1]) + 1))
        options = random.sample(options_base, min(5, len(options_base)))
        options.sort(key=int)
        if ans1_option_str not in options:
            options[random.randint(0, len(options)-1)] = ans1_option_str
            options.sort(key=int)

    exp_inv = Fraction(b, a)
    
    factor_q_candidates = []
    if a == 1:
        factor_q_candidates = [10, 100, 1000, 10000]
    elif a == 2:
        factor_q_candidates = [4, 9, 16, 25, 36, 100, 400]
    elif a == 3:
        factor_q_candidates = [8, 27, 64, 125, 1000]
    
    factor_q = random.choice(factor_q_candidates)
    
    ans2_val_frac = factor_q ** exp_inv
    ans2_val_str = str(ans2_val_frac.numerator)

    animal1 = random.choice(["貓", "狗", "羊"])
    animal2 = random.choice(["老鼠", "兔子", "松鼠"])
    while animal1 == animal2:
        animal2 = random.choice(["老鼠", "兔子", "松鼠"])

    measure_unit_q = "千卡/天"
    measure_unit_m = "公斤"
    
    question_text = (
        f"生物學家發現多數哺乳動物的基礎代謝率 $Q$（{measure_unit_q}）與其體重 $M$（{measure_unit_m}）會滿足關係式 $Q = k M^{{{exp}}}$，其中 $k$ 為大於0的常數。<br>"
        f"設一隻 {animal2} 的基礎代謝率為 $q$（{measure_unit_q}），體重為 $m$（{measure_unit_m}）。試回答下列問題：<br>"
        f"(1) 設一隻 {animal1} 的體重約為一隻 {animal2} 的 ${factor_x}$ 倍，試問：{animal1} 的基礎代謝率 $Q_{{ {animal1} }}$（{measure_unit_q}）約為 {animal2} 的幾倍？試選出最接近的選項。（單選）<br>"
        f"{"　".join([f"${opt}$倍" for opt in options])}<br>"
        f"(2) 設一頭牛的基礎代謝率約為一隻 {animal2} 的 ${factor_q}$ 倍，試問：牛的體重 $M_{{牛}}$（{measure_unit_m}）約為 {animal2} 的幾倍？"
    )
    
    correct_answer = f"(1) {ans1_option_str}倍<br>(2) {ans2_val_str}倍"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    problem_type = random.choice([
        'rad_conversion',
        'exp_simplification',
        'alg_manipulation',
        'find_exponent'
    ])
    
    if level >= 3 and random.random() < 0.3:
        problem_type = 'word_problem'

    if problem_type == 'rad_conversion':
        return generate_rad_conversion_problem(level)
    elif problem_type == 'exp_simplification':
        return generate_exp_simplification_problem(level)
    elif problem_type == 'alg_manipulation':
        return generate_alg_manipulation_problem(level)
    elif problem_type == 'find_exponent':
        return generate_find_exponent_problem(level)
    elif problem_type == 'word_problem':
        return generate_word_problem(level)

def check(user_answer, correct_answer):
    user_answer = user_answer.strip().replace(" ", "")
    correct_answer = correct_answer.strip().replace(" ", "")

    is_correct = False
    feedback = ""

    if "<br>" in correct_answer:
        try:
            user_parts = user_answer.split("<br>")
            correct_parts = correct_answer.split("<br>")

            if len(user_parts) != len(correct_parts):
                feedback = "請確保您的答案格式與題目要求一致，包含所有小題的答案，並使用 `<br>` 分隔。"
            else:
                all_parts_correct = True
                for i in range(len(correct_parts)):
                    u_p = user_parts[i]
                    c_p = correct_parts[i]
                    
                    u_val_str = u_p.split(')')[1].replace("倍", "") if ')' in u_p else u_p.replace("倍", "")
                    c_val_str = c_p.split(')')[1].replace("倍", "") if ')' in c_p else c_p.replace("倍", "")
                    
                    try:
                        u_val_num = float(u_val_str)
                        c_val_num = float(c_val_str)
                        
                        if abs(u_val_num - c_val_num) < 0.01:
                            pass
                        else:
                            all_parts_correct = False
                            feedback += f"第{i+1}小題答案不正確。您輸入：${u_val_str}$，正確答案應為：${c_val_str}$。<br>"
                    except ValueError:
                        all_parts_correct = False
                        feedback += f"第{i+1}小題答案格式不正確或含有非數字字元。您輸入：{u_p}，正確答案應為：{c_p}。<br>"
                
                if all_parts_correct:
                    is_correct = True
                elif not feedback:
                    feedback = f"答案不正確。正確答案應為：${correct_answer}$"

        except Exception as e:
            feedback = f"處理答案時發生錯誤：{e}。請檢查您的輸入格式是否正確。"
            
    else:
        if user_answer == correct_answer:
            is_correct = True
        else:
            try:
                user_val = float(user_answer)
                correct_val = float(correct_answer)
                if abs(user_val - correct_val) < 0.001:
                    is_correct = True
            except ValueError:
                try:
                    user_frac = Fraction(user_answer)
                    correct_frac = Fraction(correct_answer)
                    if user_frac == correct_frac:
                        is_correct = True
                except ValueError:
                    pass

    if is_correct:
        result_text = f"完全正確！答案是 ${correct_answer}$。"
    else:
        if not feedback:
            result_text = f"答案不正確。正確答案應為：${correct_answer}$"
        else:
            result_text = f"部分答案不正確或格式有誤。<br>{feedback}正確答案應為：${correct_answer}$"

    return {"correct": is_correct, "result": result_text, "next_question": True}