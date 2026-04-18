import random
from fractions import Fraction
from math import gcd

# Helper function to format numbers, avoiding unnecessary decimals
def format_number(num):
    """Formats a number as an integer if possible, otherwise as a fraction string."""
    if isinstance(num, Fraction):
        if num.denominator == 1:
            return str(num.numerator)
        else:
            return f"{num.numerator}/{num.denominator}"
    if isinstance(num, float) and num.is_integer():
        return str(int(num))
    return str(num)

def generate(level=1):
    """
    生成「平行線截比例線段性質」相關題目。
    """
    # Based on the reference examples, we can create several types of problems.
    problem_type = random.choice([
        'basic_proportion_find_segment',
        'parallel_line_length',
        'converse_property_find_angle',
        'midpoint_theorem',
        'area_ratio',
        'multiple_parallel_lines'
    ])

    if problem_type == 'basic_proportion_find_segment':
        return generate_basic_proportion_find_segment()
    elif problem_type == 'parallel_line_length':
        return generate_parallel_line_length()
    elif problem_type == 'converse_property_find_angle':
        return generate_converse_property_find_angle()
    elif problem_type == 'midpoint_theorem':
        return generate_midpoint_theorem()
    elif problem_type == 'area_ratio':
        return generate_area_ratio()
    else: # 'multiple_parallel_lines'
        return generate_multiple_parallel_lines()


def generate_basic_proportion_find_segment():
    """
    題型：DE // BC，已知 AD, DB, AE, EC 其中三段，求第四段。
    性質：AD:DB = AE:EC
    """
    # Generate a simple ratio k1:k2
    k1 = random.randint(2, 8)
    k2 = random.randint(2, 8)
    while k1 == k2:
        k2 = random.randint(2, 8)
    
    # Generate two different scales for the two sides
    m = random.randint(1, 4)
    n = random.randint(1, 4)
    
    ad = Fraction(k1 * m)
    db = Fraction(k2 * m)
    ae = Fraction(k1 * n)
    ec = Fraction(k2 * n)
    
    segments = {'AD': ad, 'DB': db, 'AE': ae, 'EC': ec}
    
    # Choose which segment to be the unknown
    unknown_key = random.choice(list(segments.keys()))
    answer_val = segments[unknown_key]
    
    # Set up knowns
    knowns = segments.copy()
    del knowns[unknown_key]
    
    known_strs = [f"$\\overline{{{key}}}={format_number(value)}$" for key, value in knowns.items()]
    
    question_text = f"如圖，在 $\\triangle ABC$ 中，D、E 分別為 $\\overline{{AB}}$、$\\overline{{AC}}$ 上一點，且 $\\overline{{DE}} // \\overline{{BC}}$。<br>"\
                    f"若 {', '.join(known_strs)}，則 $\\overline{{{unknown_key}}}$ 的長度為何？"

    correct_answer = format_number(answer_val)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_parallel_line_length():
    """
    題型：DE // BC，已知 AD, AB, DE, BC 其中三段，求第四段。
    性質：AD:AB = DE:BC
    """
    # Generate ratio k1:(k1+k2)
    k1 = random.randint(2, 7)
    k2 = random.randint(2, 7)
    
    # Generate scales
    m = random.randint(2, 5) # scale for parallel lines
    n = random.randint(1, 4) # scale for side AB

    de = Fraction(k1 * m)
    bc = Fraction((k1 + k2) * m)
    ad = Fraction(k1 * n)
    db = Fraction(k2 * n)
    ab = ad + db
    
    segments = {'AD': ad, 'DB': db, 'AB': ab, 'DE': de, 'BC': bc}
    
    # Choose a setup
    # Case 1: Find DE or BC. Knowns: AD, DB (or AB), and one of DE/BC
    # Case 2: Find AD or DB. Knowns: DE, BC, and one of AB/DB/AD
    case = random.choice([1, 2])
    
    if case == 1: # Find DE
        unknown_key = 'DE'
        known_keys = ['AD', 'DB', 'BC']
    else: # Find AD
        unknown_key = 'AD'
        known_keys = ['DB', 'DE', 'BC']

    answer_val = segments[unknown_key]
    
    knowns = {key: segments[key] for key in known_keys}
    known_strs = [f"$\\overline{{{key}}}={format_number(value)}$" for key, value in knowns.items()]

    question_text = f"如圖，在 $\\triangle ABC$ 中，D 為 $\\overline{{AB}}$ 上一點，E 為 $\\overline{{AC}}$ 上一點，且 $\\overline{{DE}} // \\overline{{BC}}$。<br>"\
                    f"若 {', '.join(known_strs)}，則 $\\overline{{{unknown_key}}}$ 的長度為何？"

    correct_answer = format_number(answer_val)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_converse_property_find_angle():
    """
    題型：已知 AD, DB, AE, EC，判斷 DE 是否平行 BC，並求角度。
    性質：若 AD:DB = AE:EC，則 DE // BC
    """
    # Generate a simple ratio k1:k2
    k1 = random.randint(2, 9)
    k2 = random.randint(2, 9)
    while k1 == k2:
        k2 = random.randint(2, 9)

    m = random.randint(1, 4)
    n = random.randint(1, 4)

    ad = k1 * m
    db = k2 * m
    
    # 90% chance for parallel case
    if random.random() < 0.9:
        ae = k1 * n
        ec = k2 * n
        is_parallel = True
    else:
        ae = k1 * n
        # Make it not proportional
        ec = (k2 + random.choice([-1, 1])) * n
        if ec <= 0: ec = (k2 + 1) * n
        is_parallel = False
        
    angle_b = random.randint(30, 80)
    
    if is_parallel:
        answer_val = angle_b
        question_text = f"如圖，在 $\\triangle ABC$ 中，D、E 分別在 $\\overline{{AB}}$、$\\overline{{AC}}$ 上。已知 $\\overline{{AD}}={ad}$、$\\overline{{DB}}={db}$、$\\overline{{AE}}={ae}$、$\\overline{{EC}}={ec}$，且 $\\angle B={angle_b}^\\circ$。<br>"\
                        f"請問 $\\angle ADE$ 的度數為何？"
        correct_answer = str(answer_val)
    else:
        answer_val = "不一定"
        question_text = f"如圖，在 $\\triangle ABC$ 中，D、E 分別在 $\\overline{{AB}}$、$\\overline{{AC}}$ 上。已知 $\\overline{{AD}}={ad}$、$\\overline{{DB}}={db}$、$\\overline{{AE}}={ae}$、$\\overline{{EC}}={ec}$。<br>"\
                        f"請問 $\\overline{{DE}}$ 是否與 $\\overline{{BC}}$ 平行？ (請回答 '是' 或 '不一定')"
        correct_answer = answer_val

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_midpoint_theorem():
    """
    題型：D, E 為中點，相關線段長度計算。
    性質：DE = 1/2 BC，DE // BC
    """
    # Generate sides of the smaller triangle △ADE
    de = random.randint(3, 8)
    ad = random.randint(de, 10)
    ae = random.randint(de, 10)
    
    # Ensure triangle inequality for △ABC (and thus △ADE)
    # 2*ad, 2*ae, 2*de must form a triangle => ad, ae, de must form a triangle
    while not (ad + ae > de and ad + de > ae and ae + de > ad):
        ad = random.randint(de, 10)
        ae = random.randint(de, 10)
        
    # Calculate sides of the larger triangle △ABC
    bc = 2 * de
    ab = 2 * ad
    ac = 2 * ae
    
    # Choose problem type
    ptype = random.choice(['find_sum', 'find_perimeter', 'find_single_side'])
    
    if ptype == 'find_sum':
        # Given AD, DE, find AB + BC
        question_text = f"如圖，在 $\\triangle ABC$ 中，D、E 分別為 $\\overline{{AB}}$、$\\overline{{AC}}$ 的中點。若 $\\overline{{AD}}={ad}$，$\\overline{{DE}}={de}$，則 $\\overline{{AB}} + \\overline{{BC}}$ 的值為何？"
        answer_val = ab + bc
    elif ptype == 'find_perimeter':
        # Given AB, BC, AC, find perimeter of △ADE
        question_text = f"如圖，在 $\\triangle ABC$ 中，D、E 分別為 $\\overline{{AB}}$、$\\overline{{AC}}$ 的中點。若 $\\overline{{AB}}={ab}$、$\\overline{{BC}}={bc}$、$\\overline{{AC}}={ac}$，則 $\\triangle ADE$ 的周長為多少？"
        answer_val = ad + ae + de
    else: # find_single_side
        # Given AC and BC, find DE, and D is midpoint
        question_text = f"如圖，在 $\\triangle ABC$ 中，D 為 $\\overline{{AB}}$ 的中點，且過 D 點作 $\\overline{{DE}} // \\overline{{BC}}$ 交 $\\overline{{AC}}$ 於 E 點。若 $\\overline{{BC}}={bc}$，則 $\\overline{{DE}}$ 的長度為何？"
        answer_val = de
        
    correct_answer = format_number(answer_val)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_area_ratio():
    """
    題型：利用等高三角形面積比等於底邊比。
    """
    b1 = random.randint(2, 9)
    b2 = random.randint(2, 9)
    while b1 == b2:
        b2 = random.randint(2, 9)

    # Scale factor for area
    scale = random.randint(2, 10)
    area1 = b1 * scale
    area2 = b2 * scale
    total_area = (b1 + b2) * scale
    
    # Choose problem type
    ptype = random.choice([1, 2])
    
    if ptype == 1:
        # Given area of a part, find area of another part
        question_text = f"如圖，在 $\\triangle ABC$ 中，D 為 $\\overline{{BC}}$ 上一點，且 $\\overline{{BD}}={b1}$、$\\overline{{DC}}={b2}$。若 $\\triangle ABD$ 的面積為 ${area1}$，則 $\\triangle ADC$ 的面積為何？"
        answer_val = area2
    else:
        # Given area of a part, find area of the whole
        question_text = f"如圖，在 $\\triangle ABC$ 中，E 為 $\\overline{{AC}}$ 上一點，且 $\\overline{{AE}}={b1}$、$\\overline{{EC}}={b2}$。若 $\\triangle ABE$ 的面積為 ${area1}$，則 $\\triangle ABC$ 的面積為何？"
        answer_val = total_area
        
    correct_answer = format_number(answer_val)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_multiple_parallel_lines():
    """
    題型：多條平行線截兩邊，求線段長度。
    性質：AD:DF:FB = AE:EG:GC, 且 DE:FG:BC = AD:AF:AB
    """
    k1 = random.randint(1, 4)
    k2 = random.randint(1, 4)
    k3 = random.randint(1, 4)
    
    m = random.randint(2, 6) # scale for parallel lines
    
    ktot = k1 + k2 + k3
    
    bc = ktot * m
    de = k1 * m
    fg_len = (k1 + k2) * m
    
    # Choose unknown
    unknown_key = random.choice(['DE', 'FG', 'BC'])
    
    if unknown_key == 'DE':
        answer_val = de
        known_val = bc
        known_key = 'BC'
    elif unknown_key == 'FG':
        answer_val = fg_len
        known_val = bc
        known_key = 'BC'
    else: # unknown_key == 'BC'
        answer_val = bc
        known_val = random.choice([de, fg_len])
        known_key = 'DE' if known_val == de else 'FG'

    question_text = f"如圖，$\\triangle ABC$ 中，D、F 兩點在 $\\overline{{AB}}$ 上，E、G 兩點在 $\\overline{{AC}}$ 上，且 $\\overline{{DE}} // \\overline{{FG}} // \\overline{{BC}}$。<br>"\
                    f"若 $\\overline{{AD}}：\\overline{{DF}}：\\overline{{FB}}={k1}：{k2}：{k3}$，且 $\\overline{{{known_key}}}={known_val}$，則 $\\overline{{{unknown_key}}}$ 的長度為何？"
    
    correct_answer = format_number(answer_val)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    # Normalize answers by removing whitespace and making them uppercase (for text answers)
    user_answer = user_answer.strip().upper()
    correct_answer = str(correct_answer).strip().upper()
    
    is_correct = (user_answer == correct_answer)
    
    # If not a perfect string match, try numerical comparison
    if not is_correct:
        try:
            # Use Fraction to handle integers, decimals, and fraction strings like "8/3"
            if Fraction(user_answer) == Fraction(correct_answer):
                is_correct = True
        except (ValueError, ZeroDivisionError):
            # The user answer is not a valid number, so it's wrong.
            pass

    # Provide feedback
    if is_correct:
        # Use the original correct_answer format for display
        result_text = f"完全正確！答案是 ${str(correct_answer).lower()}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${str(correct_answer).lower()}$"
    
    return {"correct": is_correct, "result": result_text, "next_question": True}