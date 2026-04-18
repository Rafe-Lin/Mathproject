import random
from fractions import Fraction
import math

def generate(level=1):
    """
    生成「相似三角形的邊長與面積關係」相關題目。
    包含：
    1. 相似三角形的對應高與對應邊長成正比。
    2. 相似三角形的面積比等於對應邊長的平方比。
    3. 三角形各邊中點連線所形成新三角形的周長與面積關係。
    """
    problem_type = random.choice([
        'side_from_altitude',
        'area_from_ratio',
        'midpoint_triangle_property',
        'embedded_triangle_ratio'
    ])
    
    if problem_type == 'side_from_altitude':
        return generate_side_from_altitude_problem()
    elif problem_type == 'area_from_ratio':
        return generate_area_from_ratio_problem()
    elif problem_type == 'midpoint_triangle_property':
        return generate_midpoint_triangle_property_problem()
    else: # 'embedded_triangle_ratio'
        return generate_embedded_triangle_ratio_problem()

def generate_side_from_altitude_problem():
    """
    題型：已知相似三角形對應高的比與其中一個對應邊長，求另一個對應邊長。
    參考例題 2。
    """
    r1 = random.randint(2, 8)
    r2 = random.randint(2, 8)
    while r1 == r2:
        r2 = random.randint(2, 8)
    
    k = random.randint(2, 6)
    
    # 隨機決定哪一組是已知的
    if random.choice([True, False]):
        side1 = k * r1
        side2 = k * r2
        # Fix: removed extra } after DEF
        question_text = f"已知 $\\triangle ABC \\sim \\triangle DEF$，其對應高 $\\overline{{AH}}$ 與 $\\overline{{DK}}$ 的比為 ${r1}:{r2}$。若對應邊 $\\overline{{BC}} = {side1}$，則 $\\overline{{EF}}$ 的長度為何？"
        correct_answer = str(side2)
    else:
        side1 = k * r2
        side2 = k * r1
        # Fix: removed extra } after DEF
        question_text = f"已知 $\\triangle ABC \\sim \\triangle DEF$，其對應高 $\\overline{{AH}}$ 與 $\\overline{{DK}}$ 的比為 ${r1}:{r2}$。若對應邊 $\\overline{{EF}} = {side1}$，則 $\\overline{{BC}}$ 的長度為何？"
        correct_answer = str(side2)
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_area_from_ratio_problem():
    """
    題型：已知相似三角形的對應邊長比(或對應高比)與其中一個面積，求另一個面積。
    參考例題 3。
    """
    r1 = random.randint(2, 7)
    r2 = random.randint(2, 7)
    while r1 == r2:
        r2 = random.randint(2, 7)
    
    ratio_type = random.choice(['對應邊長', '對應高'])
    
    # 為了可能產生分數的答案
    area1 = random.randint(5, 30)
    
    result_area = Fraction(area1 * r2**2, r1**2)
    
    if result_area.denominator == 1:
        correct_answer = str(result_area.numerator)
    else:
        correct_answer = f"{result_area.numerator}/{result_area.denominator}"

    if random.choice([True, False]):
        # Fix: removed extra } after DEF
        question_text = f"已知 $\\triangle ABC \\sim \\triangle DEF$，且其{ratio_type}的比為 ${r1}:{r2}$。若 $\\triangle ABC$ 的面積為 ${area1}$，則 $\\triangle DEF$ 的面積為多少？"
    else:
        # 交換一下角色，讓問題更多樣
        temp_area = area1
        area1 = correct_answer
        correct_answer = str(temp_area)
        # Fix: removed extra } after DEF
        question_text = f"已知 $\\triangle ABC \\sim \\triangle DEF$，且其{ratio_type}的比為 ${r1}:{r2}$。若 $\\triangle DEF$ 的面積為 ${area1}$，則 $\\triangle ABC$ 的面積為多少？"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_midpoint_triangle_property_problem():
    """
    題型：關於各邊中點連成的三角形，求周長或面積。
    參考例題 5。
    """
    direction = random.choice(['mid_to_orig', 'orig_to_mid'])
    prop_to_find = random.choice(['周長', '面積'])
    
    base_text = f"$\\triangle ABC$ 中，$D、E、F$ 分別為 $\\overline{{BC}}$、$\\overline{{AC}}$、$\\overline{{AB}}$ 的中點。"

    if direction == 'mid_to_orig':
        if prop_to_find == '周長':
            p_def = random.randint(10, 30)
            p_abc = 2 * p_def
            question_text = f"{base_text} 已知 $\\triangle DEF$ 的周長為 ${p_def}$，求 $\\triangle ABC$ 的周長。"
            correct_answer = str(p_abc)
        else: # 面積
            area_def = random.randint(5, 25)
            area_abc = 4 * area_def
            question_text = f"{base_text} 已知 $\\triangle DEF$ 的面積為 ${area_def}$，求 $\\triangle ABC$ 的面積。"
            correct_answer = str(area_abc)
    else: # 'orig_to_mid'
        if prop_to_find == '周長':
            p_abc = 2 * random.randint(15, 40)
            p_def = p_abc // 2
            question_text = f"{base_text} 已知 $\\triangle ABC$ 的周長為 ${p_abc}$，求 $\\triangle DEF$ 的周長。"
            correct_answer = str(p_def)
        else: # 面積
            area_abc = 4 * random.randint(10, 50)
            area_def = area_abc // 4
            question_text = f"{base_text} 已知 $\\triangle ABC$ 的面積為 ${area_abc}$，求 $\\triangle DEF$ 的面積。"
            correct_answer = str(area_def)
            
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_embedded_triangle_ratio_problem():
    """
    題型：直角三角形中，從一股的中點作斜邊的垂線，求小三角形與原三角形的面積比。
    參考例題 4。
    """
    pythagorean_triples = [(3, 4, 5), (5, 12, 13), (8, 15, 17)]
    k = random.randint(1, 4)
    a, b, c = [k * x for x in random.choice(pythagorean_triples)]
    
    # 隨機分配兩股
    leg1_len, leg2_len = random.sample([a, b], 2)
    hyp_len = c

    # 隨機選擇中點在哪一股上
    if random.choice([True, False]):
        # 中點在 AB 上
        midpoint_leg_label = "AB"
        other_leg_label = "BC"
        midpoint_leg_len = leg1_len
        other_leg_len = leg2_len
        small_triangle_name = "\\triangle ADE"
        num = leg1_len**2
    else:
        # 中點在 BC 上
        midpoint_leg_label = "BC"
        other_leg_label = "AB"
        midpoint_leg_len = leg2_len
        other_leg_len = leg1_len
        small_triangle_name = "\\triangle CDE"
        num = leg2_len**2
        
    den = hyp_len**2
    common_divisor = math.gcd(num, den)
    
    num_s = num // common_divisor
    den_s = den // common_divisor
    
    question_text = f"在直角三角形 $\\triangle ABC$ 中，$\\angle B = 90^\\circ$，$\\overline{{{other_leg_label}}} = {other_leg_len}$，$\\overline{{{midpoint_leg_label}}} = {midpoint_leg_len}$。"
    question_text += f" 若 $D$ 為 $\\overline{{{midpoint_leg_label}}}$ 的中點，且過 $D$ 點作 $\\overline{{DE}} \\perp \\overline{{AC}}$ 於 $E$ 點，求 ${small_triangle_name}$ 面積與 $\\triangle ABC$ 面積的比？（請以 a:b 的最簡整數比表示）"

    correct_answer = f"{num_s}:{den_s}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def check(user_answer, correct_answer):
    """
    檢查答案是否正確，可處理整數、分數、比例。
    """
    user_answer = user_answer.strip().replace('：', ':') # 將全形冒號轉為半形
    correct_answer = str(correct_answer).strip()
    is_correct = False

    # 檢查比例格式 (e.g., "4:25")
    if ':' in correct_answer:
        try:
            c_parts = [int(p) for p in correct_answer.split(':')]
            u_parts = [int(p) for p in user_answer.split(':')]
            
            if len(c_parts) == 2 and len(u_parts) == 2 and u_parts[1] != 0 and c_parts[1] != 0:
                # 使用分數比較來處理未化簡的比例
                is_correct = (Fraction(u_parts[0], u_parts[1]) == Fraction(c_parts[0], c_parts[1]))
        except (ValueError, ZeroDivisionError, IndexError):
            is_correct = False
    # 檢查分數格式 (e.g., "20/3")
    elif '/' in correct_answer:
        try:
            is_correct = (Fraction(user_answer) == Fraction(correct_answer))
        except (ValueError, ZeroDivisionError):
            is_correct = (user_answer == correct_answer) # 若無法轉換為分數，則進行字串比較
    # 標準數值比較
    else:
        try:
            # 比較浮點數以處理像 5.0 和 5 的情況
            is_correct = (abs(float(user_answer) - float(correct_answer)) < 1e-9)
        except ValueError:
            is_correct = (user_answer.upper() == correct_answer.upper())

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}