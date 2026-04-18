import random
from fractions import Fraction
import math

def format_number(num):
    """
    Helper function to format numbers for display, especially mixed fractions.
    """
    if isinstance(num, Fraction):
        if num.denominator == 1:
            return str(num.numerator)
        # Handle mixed fractions
        if abs(num.numerator) > num.denominator:
            sign = "-" if num.numerator < 0 else ""
            abs_num = abs(num)
            integer_part = abs_num.numerator // abs_num.denominator
            frac_part = abs_num - integer_part
            if frac_part.numerator > 0:
                # Use f-string with double curly braces for LaTeX
                return f"{sign}{integer_part} \\frac{{{frac_part.numerator}}}{{{frac_part.denominator}}}"
            else:
                return f"{sign}{integer_part}"
        else:
            return f"\\frac{{{num.numerator}}}{{{num.denominator}}}"
    elif isinstance(num, float):
        # Avoid unnecessary .0
        if num == int(num):
            return str(int(num))
        return str(num)
    return str(num)

def generate_relative_representation_problem():
    """
    例題 1 & 2: 以基準點表示正負數
    """
    scenarios = [
        {'context': '位置', 'positive': '東邊', 'negative': '西邊', 'unit': '公里', 'base': '學校'},
        {'context': '成績', 'positive': '進步', 'negative': '退步', 'unit': '分', 'base': '基準分數'},
        {'context': '交易', 'positive': '賺', 'negative': '賠', 'unit': '元', 'base': '成本'},
        {'context': '溫度', 'positive': '零上', 'negative': '零下', 'unit': '度C', 'base': '攝氏零'},
        {'context': '海拔', 'positive': '高於海平面', 'negative': '低於海平面', 'unit': '公尺', 'base': '海平面'}
    ]
    scenario = random.choice(scenarios)
    
    problem_subtype = random.choice(['direct', 'calculation'])
    
    if problem_subtype == 'direct' or scenario['context'] in ['位置', '溫度', '海拔']:
        val_pos = random.randint(1, 20)
        val_neg = random.randint(1, 20)
        
        question_text = (
            f"以{scenario['base']}為基準，若其{scenario['positive']} {val_pos} {scenario['unit']} "
            f"記為「$+ {val_pos}$」，則其{scenario['negative']} {val_neg} {scenario['unit']} 應該怎麼記錄？"
        )
        correct_answer = f"-{val_neg}"
        
    else: # Calculation type (成績, 交易)
        if scenario['context'] == '成績':
            base_score = random.randint(60, 90)
            change = random.randint(1, 10)
            
            new_score = base_score - change
            pos_change = random.randint(1, 10)
            pos_score = base_score + pos_change

            question_text = (
                f"以 {base_score} 分為基準，成績進步為正向，退步為負向。"
                f"若小華考 {pos_score} 分，記為「$+ {pos_change}$」，"
                f"則小明考 {new_score} 分，應該怎麼記錄？"
            )
            correct_answer = f"-{change}"
            
        elif scenario['context'] == '交易':
            cost = random.randint(10, 50) * 10
            change = random.randint(1, 9) * 10
            
            sell_price = cost - change
            pos_change = random.randint(1, 9) * 10
            pos_price = cost + pos_change

            question_text = (
                f"以「+」表示賺錢，「-」表示賠錢。"
                f"若一項成本為 {cost} 元的商品，以 {pos_price} 元售出，記為「$+ {pos_change}$」。"
                f"則同樣成本的商品，若以 {sell_price} 元售出，應該怎麼記錄？"
            )
            correct_answer = f"-{change}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "input_type": "text"
    }

def generate_number_classification_problem():
    """
    例題 3: 辨識正數、負數、整數、同號數
    """
    numbers = set()
    numbers.update(random.sample(range(1, 31), 2))
    numbers.update(random.sample(range(-30, 0), 2))
    numbers.add(0)
    numbers.add(round(random.uniform(0.1, 10.0), 1))
    numbers.add(round(random.uniform(-10.0, -0.1), 1))
    num, den = random.randint(1, 9), random.randint(2, 10)
    while math.gcd(num, den) != 1 or num >= den:
        num, den = random.randint(1, 9), random.randint(2, 10)
    numbers.add(Fraction(num, den))
    int_part = random.randint(1, 5)
    num, den = random.randint(1, 9), random.randint(2, 10)
    while math.gcd(num, den) != 1 or num >= den:
        num, den = random.randint(1, 9), random.randint(2, 10)
    numbers.add(-Fraction(int_part * den + num, den))
    
    number_list = list(numbers)
    random.shuffle(number_list)
    
    display_list = [format_number(n) for n in number_list]
    question_prefix = f"下列各數中： ${', '.join(display_list)}$"
    
    task = random.choice(['find_negative', 'find_integer', 'find_same_sign'])
    
    if task == 'find_negative':
        question_text = f"{question_prefix}\n\n請問哪些是負數？(請用逗號分隔)"
        correct_nums = [n for n in number_list if (isinstance(n, (int, float)) and n < 0) or (isinstance(n, Fraction) and n.numerator < 0)]
    elif task == 'find_integer':
        question_text = f"{question_prefix}\n\n請問哪些是整數？(請用逗號分隔)"
        correct_nums = [n for n in number_list if isinstance(n, int) or (isinstance(n, Fraction) and n.denominator == 1)]
    else: # find_same_sign
        target_num = random.choice([n for n in number_list if n != 0])
        target_sign_is_pos = (isinstance(target_num, (int, float)) and target_num > 0) or (isinstance(target_num, Fraction) and target_num.numerator > 0)
        
        question_text = f"{question_prefix}\n\n請問哪些與 ${format_number(target_num)}$ 是同號數？(請用逗號分隔)"
        if target_sign_is_pos:
            correct_nums = [n for n in number_list if (isinstance(n, (int, float)) and n > 0) or (isinstance(n, Fraction) and n.numerator > 0)]
        else:
            correct_nums = [n for n in number_list if (isinstance(n, (int, float)) and n < 0) or (isinstance(n, Fraction) and n.numerator < 0)]

    correct_answer_list = sorted([format_number(n) for n in correct_nums])
    correct_answer = ", ".join(correct_answer_list)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "input_type": "text"
    }

def generate_opposite_and_absolute_problem():
    """
    延伸題型：相反數與絕對值
    """
    num_type = random.choice(['int', 'decimal', 'fraction'])
    if num_type == 'int':
        val = random.randint(-20, 20)
        while val == 0:
            val = random.randint(-20, 20)
    elif num_type == 'decimal':
        val = round(random.uniform(-15.0, 15.0), 1)
        while val == 0.0:
            val = round(random.uniform(-15.0, 15.0), 1)
    else: # fraction
        den = random.randint(2, 9)
        num = random.randint(1, den * 3)
        if random.choice([True, False]):
            num = -num
        val = Fraction(num, den)

    task = random.choice(['opposite', 'absolute', 'opposite_of_absolute', 'absolute_of_opposite'])
    
    val_str = format_number(val)
    
    if task == 'opposite':
        question_text = f"請問 ${val_str}$ 的相反數為何？"
        correct_answer = format_number(-val)
    elif task == 'absolute':
        question_text = f"請問 ${val_str}$ 的絕對值為何？(或寫為 $\\left| {val_str} \\right|$)"
        correct_answer = format_number(abs(val))
    elif task == 'opposite_of_absolute':
        question_text = f"請問 $\\left| {val_str} \\right|$ 的相反數為何？"
        correct_answer = format_number(-abs(val))
    else: # absolute_of_opposite
        opposite_val = -val
        opposite_str = format_number(opposite_val)
        question_text = f"請問 ${val_str}$ 的相反數（即 ${opposite_str}$）的絕對值為何？"
        correct_answer = format_number(abs(-val))

    is_handwriting = isinstance(val, Fraction) and val.denominator != 1

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "input_type": "handwriting" if is_handwriting else "text"
    }
    
def generate_number_comparison_problem():
    """
    延伸題型：數的大小比較
    """
    numbers = set()
    while len(numbers) < 3:
        num_type = random.choice(['int', 'decimal', 'fraction'])
        if num_type == 'int':
            numbers.add(random.randint(-10, 10))
        elif num_type == 'decimal':
            numbers.add(round(random.uniform(-10.0, 10.0), 1))
        else: 
            den = random.randint(2, 5)
            num = random.randint(-10, 10)
            if num != 0:
                numbers.add(Fraction(num, den))
    
    num_list = list(numbers)
    random.shuffle(num_list)
    display_list = [format_number(n) for n in num_list]

    task = random.choice(['greatest', 'smallest', 'order'])
    
    if task == 'greatest':
        question_text = f"比較下列各數的大小： ${', '.join(display_list)}$，請問何者最大？"
        correct_num = max(num_list)
        correct_answer = format_number(correct_num)
    elif task == 'smallest':
        question_text = f"比較下列各數的大小： ${', '.join(display_list)}$，請問何者最小？"
        correct_num = min(num_list)
        correct_answer = format_number(correct_num)
    else: 
        direction = random.choice(['大到小', '小到大'])
        question_text = f"請將下列各數由{direction}排列： ${', '.join(display_list)}$。(請用 > 或 < 連接)"
        
        sorted_nums = sorted(num_list, reverse=(direction == '大到小'))
        sorted_display = [format_number(n) for n in sorted_nums]
        
        separator = " > " if direction == '大到小' else " < "
        correct_answer = separator.join(sorted_display)

    is_handwriting = any(isinstance(n, Fraction) and n.denominator != 1 for n in num_list)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "input_type": "handwriting" if is_handwriting else "text"
    }

def generate(level=1):
    """
    生成「正負數」相關題目。
    包含：
    1. 相對概念表示 (東/西, 賺/賠)
    2. 數的分類 (正數, 負數, 整數)
    3. 相反數與絕對值
    4. 數的大小比較
    """
    problem_type = random.choice([
        'relative_representation', 
        'number_classification', 
        'opposite_and_absolute',
        'number_comparison'
    ])
    
    if problem_type == 'relative_representation':
        return generate_relative_representation_problem()
    elif problem_type == 'number_classification':
        return generate_number_classification_problem()
    elif problem_type == 'opposite_and_absolute':
        return generate_opposite_and_absolute_problem()
    else: 
        return generate_number_comparison_problem()

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer_norm = user_answer.strip().replace(' ', '').replace('$', '')
    user_answer_norm = user_answer_norm.replace('，', ',')
    
    correct_answer_norm = correct_answer.strip().replace(' ', '').replace('$', '')

    is_correct = False

    if ',' in correct_answer_norm or '>' in correct_answer_norm or '<' in correct_answer_norm:
        if ',' in correct_answer_norm:
            user_parts = sorted(user_answer_norm.split(','))
            correct_parts = sorted(correct_answer_norm.split(','))
            is_correct = (user_parts == correct_parts)
        else:
            sep = '>' if '>' in correct_answer_norm else '<'
            user_parts = user_answer_norm.split(sep)
            correct_parts = correct_answer_norm.split(sep)
            is_correct = (user_parts == correct_parts)
    else:
        if user_answer_norm == correct_answer_norm:
            is_correct = True
        else:
            try:
                user_val = Fraction(user_answer_norm)
                correct_val = Fraction(correct_answer_norm)
                if user_val == correct_val:
                    is_correct = True
            except (ValueError, ZeroDivisionError):
                pass
    
    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    
    return {"correct": is_correct, "result": result_text, "next_question": True}
