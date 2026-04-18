import random
from fractions import Fraction
import math

def generate(level=1):
    """
    生成「相似多邊形」相關題目。
    包含：
    1. 相似定義的概念題
    2. 給定兩個多邊形，判斷是否相似
    3. 已知相似，求對應邊長或角度
    4. 已知相似的應用問題
    """
    problem_type = random.choice(['definition_check', 'rectangle_ratio_check', 'find_unknown', 'multistep_rectangle'])
    
    if problem_type == 'definition_check':
        return generate_definition_check_problem()
    elif problem_type == 'rectangle_ratio_check':
        return generate_rectangle_ratio_check_problem()
    elif problem_type == 'find_unknown':
        return generate_find_unknown_problem()
    else: # multistep_rectangle
        return generate_multistep_rectangle_problem()

def generate_definition_check_problem():
    """
    生成關於相似多邊形定義的概念題。
    """
    q_type = random.choice(['rect_square', 'rhombus_square', 'regular_polygon'])
    
    if q_type == 'rect_square':
        question_text = "長方形與正方形的四個內角都是直角，它們是否一定相似？ (請回答「是」、「否」或「不一定」)"
        correct_answer = "不一定"
    elif q_type == 'rhombus_square':
        question_text = "菱形與正方形的四個邊長都對應成比例，它們是否一定相似？ (請回答「是」、「否」或「不一定」)"
        correct_answer = "不一定"
    else: # regular_polygon
        n = random.choice([5, 6, 7, 8])
        n_map = {5: "五", 6: "六", 7: "七", 8: "八"}
        shape_name = f"正{n_map[n]}邊形"
        question_text = f"任意兩個{shape_name}是否一定相似？ (請回答「是」、「否」或「不一定」)"
        correct_answer = "是"
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_rectangle_ratio_check_problem():
    """
    生成判斷兩個長方形是否相似的題目。
    """
    is_similar = random.choice([True, False])
    
    w1 = random.randint(3, 8)
    l1 = random.randint(w1 + 2, 15)
    ratio1 = Fraction(l1, w1)
    
    if is_similar:
        k = random.choice([2, 3, Fraction(3, 2)])
        if isinstance(k, Fraction):
            # To keep numbers integers, multiply by denominator
            l_temp = l1 * k.numerator
            w_temp = w1 * k.numerator
            l1 = l1 * k.denominator
            w1 = w1 * k.denominator
            l2 = l_temp
            w2 = w_temp
        else:
            l2 = l1 * k
            w2 = w1 * k
        if random.random() < 0.5: # Randomly swap l2, w2
            l2, w2 = w2, l2
        correct_answer = "是"
    else:
        w2 = random.randint(3, 8)
        l2 = random.randint(w2 + 2, 15)
        ratio2 = Fraction(l2, w2)
        # Ensure they are not similar and not identical
        while ratio1 == ratio2 or (l1 == l2 and w1 == w2) or (l1 == w2 and w1 == l2):
            w2 = random.randint(3, 8)
            l2 = random.randint(w2 + 2, 15)
            ratio2 = Fraction(l2, w2)
        correct_answer = "否"
        
    sides1 = sorted([w1, l1])
    sides2 = sorted([w2, l2])

    question_text = (f"一個長方形的兩鄰邊長為 ${sides1[0]}$ 與 ${sides1[1]}$，另一個長方形的兩鄰邊長為 ${sides2[0]}$ 與 ${sides2[1]}$。"
                     f"請問這兩個長方形是否相似？ (請回答「是」或「否」)")

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_find_unknown_problem():
    """
    生成已知多邊形相似，求未知邊長或角度的題目。
    """
    sub_type = random.choice(['find_side', 'find_angle'])
    n = random.choice([4, 5])
    shape_map = {4: "四", 5: "五"}
    labels1 = "ABCDE"[:n]
    labels2 = "PQRST"[:n]
    
    if sub_type == 'find_side':
        scale_num = random.randint(2, 5)
        scale_den = random.randint(2, 5)
        while math.gcd(scale_num, scale_den) != 1:
            scale_den = random.randint(2, 5)
        while scale_num == scale_den:
            scale_num = random.randint(2, 5)
        
        base_sides = [random.randint(2, 8) for _ in range(2)]
        sides1 = [s * scale_den for s in base_sides]
        sides2 = [s * scale_num for s in base_sides]
        
        side1_known_name = f"\\overline{{{labels1[0]}{labels1[1]}}}"
        side2_known_name = f"\\overline{{{labels2[0]}{labels2[1]}}}"
        side1_for_unknown_name = f"\\overline{{{labels1[1]}{labels1[2]}}}"
        unknown_side_name = f"\\overline{{{labels2[1]}{labels2[2]}}}"
        
        question_text = (f"已知{shape_map[n]}邊形 ${labels1} \\sim$ {shape_map[n]}邊形 ${labels2}$，且頂點依序對應。"
                         f"若 ${side1_known_name} = {sides1[0]}$、${side1_for_unknown_name} = {sides1[1]}$、${side2_known_name} = {sides2[0]}$，"
                         f"則 ${unknown_side_name}$ 的長度為何？")
        
        correct_answer = str(sides2[1])

    else: # find_angle
        total_angle = (n - 2) * 180
        if n == 4:
            base_angles = [70, 80, 90, 100, 110]
            random.shuffle(base_angles)
            angles = base_angles[:3]
            angles.append(360 - sum(angles))
            while any(a <= 30 for a in angles): # Recalculate if an angle is too small
                random.shuffle(base_angles)
                angles = base_angles[:3]
                angles.append(360 - sum(angles))
        else: # n == 5
            base_angles = [100, 105, 110, 115, 120]
            random.shuffle(base_angles)
            angles = base_angles[:4]
            angles.append(540 - sum(angles))
            while any(a <= 60 for a in angles): # Recalculate if an angle is too small
                random.shuffle(base_angles)
                angles = base_angles[:4]
                angles.append(540 - sum(angles))

        is_direct_question = random.random() < 0.4
        
        question_text = f"已知{shape_map[n]}邊形 ${labels1} \\sim$ {shape_map[n]}邊形 ${labels2}$，且頂點依序對應。"
        
        if is_direct_question:
            idx = random.randint(0, n - 1)
            question_text += f" 若 $\\angle {labels1[idx]} = {angles[idx]}^{{\\circ}}$，則 $\\angle {labels2[idx]}$ 為多少度？ (請僅填入數字)"
            correct_answer = str(angles[idx])
        else: # Calculate last angle
            given_angles_str = []
            unknown_idx = n - 1
            for i in range(n - 1):
                given_angles_str.append(f"$\\angle {labels1[i]} = {angles[i]}^{{\\circ}}$")
            question_text += f" 其中 {', '.join(given_angles_str)}。則 $\\angle {labels2[unknown_idx]}$ 為多少度？ (請僅填入數字)"
            correct_answer = str(angles[unknown_idx])
            
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_multistep_rectangle_problem():
    """
    生成如例題6的相似長方形多步驟應用問題。
    """
    b = random.randint(2, 5)
    a = random.randint(1, b - 1)
    g = random.randint(2, 4)
    
    # Rectangle EFGH sides: EF = g*a, EH = g*b. Ratio is a:b
    ef = g * a
    eh = g * b
    
    k = random.randint(1, 3)
    # The difference in corresponding sides is chosen to make the math simple
    diff_ad = k * b
    
    # The answer to "how much longer is AB than EF" will be k*a
    answer = k * a
    
    question_text = (f"長方形 $ABCD \\sim$ 長方形 $EFGH$，且 $A, B, C, D$ 的對應點依序為 $E, F, G, H$。"
                     f"若 $\\overline{{EF}} = {ef}$ 公分、$\\overline{{EH}} = {eh}$ 公分，"
                     f"且 $\\overline{{AD}}$ 比 $\\overline{{EH}}$ 長 ${diff_ad}$ 公分，"
                     f"則 $\\overline{{AB}}$ 比 $\\overline{{EF}}$ 多幾公分？ (請僅填入數字)")
    
    correct_answer = str(answer)
    
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
    
    # Handle text-based answers
    if correct_answer in ["是", "否", "不一定"]:
        is_correct = (user_answer == correct_answer)
    else: # Handle numerical answers
        is_correct = (user_answer == correct_answer)
        if not is_correct:
            try:
                # Allow for fractional answers like 1/2 vs 0.5
                if abs(float(Fraction(user_answer)) - float(Fraction(correct_answer))) < 1e-9:
                    is_correct = True
            except (ValueError, ZeroDivisionError):
                pass

    is_numeric = False
    try:
        Fraction(correct_answer)
        is_numeric = True
    except (ValueError, ZeroDivisionError):
        pass

    if is_correct:
        if is_numeric:
            result_text = f"完全正確！答案是 ${correct_answer}$。"
        else:
            result_text = f"完全正確！答案是 {correct_answer}。"
    else:
        if is_numeric:
            result_text = f"答案不正確。正確答案應為：${correct_answer}$"
        else:
            result_text = f"答案不正確。正確答案應為：{correct_answer}"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}