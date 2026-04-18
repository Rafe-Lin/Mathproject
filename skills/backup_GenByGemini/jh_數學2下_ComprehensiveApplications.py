import random
from fractions import Fraction

def generate(level=1):
    """
    生成綜合應用中垂線、角平分線、等腰三角形性質的題目。
    """
    problem_type = random.choice([
        'isosceles_angles',
        'chained_isosceles',
        'angle_bisector_pythagorean',
        'perpendicular_bisector_pythagorean',
        'identify_isosceles'
    ])

    if problem_type == 'isosceles_angles':
        return generate_isosceles_angles_problem()
    elif problem_type == 'chained_isosceles':
        return generate_chained_isosceles_problem()
    elif problem_type == 'angle_bisector_pythagorean':
        return generate_angle_bisector_pythagorean_problem()
    elif problem_type == 'perpendicular_bisector_pythagorean':
        return generate_perpendicular_bisector_pythagorean_problem()
    else:  # 'identify_isosceles'
        return generate_identify_isosceles_problem()

def generate_isosceles_angles_problem():
    """
    基於例題：△ABC 中，D、E、F 分別在 BC、AB、AC 上。若 BD=BE、CD=CF，且∠B=70°、∠C=40°，則∠EDF=？
    """
    angle_b = random.randrange(40, 81, 2)
    angle_c = random.randrange(40, 81, 2)
    while angle_b + angle_c >= 160:
        angle_c = random.randrange(40, 81, 2)

    # In △BDE, ∠BDE = (180 - angle_b) / 2
    # In △CDF, ∠CDF = (180 - angle_c) / 2
    # ∠EDF = 180 - ∠BDE - ∠CDF = 180 - (90 - b/2) - (90 - c/2) = (b+c)/2
    answer = (angle_b + angle_c) / 2
    answer_str = str(int(answer)) if answer.is_integer() else str(answer)

    question_text = f"在 $\\triangle ABC$ 中，D、E、F 三點分別在 $\\overline{{BC}}$、$\\overline{{AB}}$、$\\overline{{AC}}$ 上。<br>"
    question_text += f"若 $\\overline{{BD}}=\\overline{{BE}}$、$\\overline{{CD}}=\\overline{{CF}}$，且 $\\angle B = {angle_b}^\\circ$、$\\angle C = {angle_c}^\\circ$，則 $\\angle EDF$ 的度數為何？"

    return {
        "question_text": question_text,
        "answer": answer_str,
        "correct_answer": answer_str
    }

def generate_chained_isosceles_problem():
    """
    基於例題：△ABC 中，D 為 BC 上一點，若 AB=AD=CD，且∠C=32°，則∠B=？
    """
    angle_c = random.randint(20, 40)
    # In △ACD, AD=CD => ∠CAD = ∠C = angle_c
    # Exterior angle ∠ADB = ∠CAD + ∠C = 2 * angle_c
    # In △ABD, AB=AD => ∠B = ∠ADB = 2 * angle_c
    answer = 2 * angle_c

    question_text = f"在 $\\triangle ABC$ 中，已知 D 為 $\\overline{{BC}}$ 上一點，若 $\\overline{{AB}}=\\overline{{AD}}=\\overline{{CD}}$，且 $\\angle C = {angle_c}^\\circ$，則 $\\angle B$ 的度數為何？"

    return {
        "question_text": question_text,
        "answer": str(answer),
        "correct_answer": str(answer)
    }

def generate_angle_bisector_pythagorean_problem():
    """
    基於例題：梯形 ABCD 中，AD||BC, ∠A=∠B=90°, AB=18, AD=6, CE平分∠BCD, DE⊥CD, 則BE=?
    """
    triples = [(3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25), (6, 8, 10)]
    a, b, c = random.choice(triples)
    k = random.randint(1, 2)
    a, b, c = k * a, k * b, k * c

    # Let AD = a, AE = b, DE = c
    # By angle bisector theorem, BE = DE = c
    # So AB = AE + BE = b + c
    ad = a
    ab = b + c
    answer = c

    question_text = f"在梯形 ABCD 中，$\\overline{{AD}} \\parallel \\overline{{BC}}$，$\\angle A=\\angle B=90^\\circ$。<br>"
    question_text += f"若 $\\overline{{AB}}={ab}$，$\\overline{{AD}}={ad}$，且 $\\overline{{CE}}$ 平分 $\\angle BCD$ 並交 $\\overline{{AB}}$ 於 E 點，又 $\\overline{{DE}} \\perp \\overline{{CD}}$，則 $\\overline{{BE}}$ 的長度為何？"

    return {
        "question_text": question_text,
        "answer": str(answer),
        "correct_answer": str(answer)
    }

def generate_perpendicular_bisector_pythagorean_problem():
    """
    基於例題：△ABC 中，∠C=90°, AB=10, BC=8, AC=6, 直線 L 為 AB 的中垂線, L交BC於E, 則CE=?
    """
    triples = [(3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25)]
    l1, l2, h = random.choice(triples)
    k = random.randint(1, 2)
    if k==2 and (l1,l2,h)==(7,24,25): # Avoid large numbers
        k=1
    l1, l2, h = k * l1, k * l2, k * h

    # Randomly assign legs and decide which one the bisector intersects
    if random.choice([True, False]):
        ac, bc = l1, l2
    else:
        ac, bc = l2, l1

    # Place E on the longer leg to ensure positive length for CE
    if ac > bc:
        intersect_side = "\\overline{AC}"
        # Let CE = x, AE = ac - x. BE = AE = ac - x.
        # In right △BCE: BC^2 + CE^2 = BE^2 => bc^2 + x^2 = (ac-x)^2
        # bc^2 = ac^2 - 2*ac*x => x = (ac^2 - bc^2) / (2*ac)
        num = ac**2 - bc**2
        den = 2 * ac
    else:
        intersect_side = "\\overline{BC}"
        # Let CE = x, BE = bc - x. AE = BE = bc - x.
        # In right △ACE: AC^2 + CE^2 = AE^2 => ac^2 + x^2 = (bc-x)^2
        # ac^2 = bc^2 - 2*bc*x => x = (bc^2 - ac^2) / (2*bc)
        num = bc**2 - ac**2
        den = 2 * bc

    ans_frac = Fraction(num, den)
    answer_str = str(ans_frac.numerator)
    if ans_frac.denominator != 1:
        answer_str = f"{ans_frac.numerator}/{ans_frac.denominator}"

    question_text = f"在直角 $\\triangle ABC$ 中，$\\angle C=90^\\circ$，$\\overline{{AC}}={ac}$，$\\overline{{BC}}={bc}$。<br>"
    question_text += f"若直線 L 為斜邊 $\\overline{{AB}}$ 的中垂線，且 L 交 ${intersect_side}$ 於 E 點，則 $\\overline{{CE}}$ 的長度為何？"

    return {
        "question_text": question_text,
        "answer": answer_str,
        "correct_answer": answer_str
    }

def generate_identify_isosceles_problem():
    """
    基於例題：△ABC 中，∠A=58°, ∠B=64°, 則哪兩個邊長相等？
    """
    labels = ['A', 'B', 'C']
    random.shuffle(labels)
    equal_label1, equal_label2, other_label = labels[0], labels[1], labels[2]
    
    equal_angle = random.randint(30, 85)
    other_angle = 180 - 2 * equal_angle

    angles = {
        equal_label1: equal_angle,
        equal_label2: equal_angle,
        other_label: other_angle
    }

    opposite_sides = {'A': 'BC', 'B': 'AC', 'C': 'AB'}
    side1 = opposite_sides[equal_label1]
    side2 = opposite_sides[equal_label2]

    answer = f"\\overline{{{side1}}}=\\overline{{{side2}}}"
    
    q_labels = random.sample(list(angles.keys()), 2)
    q_angle1_label, q_angle2_label = q_labels[0], q_labels[1]
    q_angle1_val = angles[q_angle1_label]
    q_angle2_val = angles[q_angle2_label]

    question_text = f"在 $\\triangle ABC$ 中，若 $\\angle {q_angle1_label}={q_angle1_val}^\\circ$，$\\angle {q_angle2_label}={q_angle2_val}^\\circ$，則此三角形中哪兩條邊的長度相等？<br>(請以 $\\overline{{AB}}=\\overline{{BC}}$ 的格式作答)"

    return {
        "question_text": question_text,
        "answer": answer,
        "correct_answer": answer
    }


def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip()
    is_correct = False

    # Case 1: Side equality answer, e.g., \\overline{AB}=\\overline{BC}
    if '=' in correct_answer and '\\overline' in correct_answer:
        def parse_equality(s):
            try:
                # Clean up string: remove latex, spaces, make upper case
                s = s.replace('\\overline', '').replace('{', '').replace('}', '').replace(' ', '').upper()
                parts = s.split('=')
                if len(parts) != 2 or not all(parts):
                    return None
                # Sort characters in side names to handle AB vs BA
                return frozenset([''.join(sorted(p)) for p in parts])
            except:
                return None

        user_set = parse_equality(user_answer)
        correct_set = parse_equality(correct_answer)
        if user_set and user_set == correct_set:
            is_correct = True
    
    # Case 2: Numerical answer
    else:
        try:
            # Using eval to handle fractions like "7/4" from user
            user_val = float(eval(user_answer))
            correct_val = float(eval(correct_answer))
            # Compare with a small tolerance for floating point issues
            if abs(user_val - correct_val) < 1e-9:
                is_correct = True
        except (SyntaxError, NameError, TypeError, ZeroDivisionError):
            # Fallback for direct string comparison if eval fails
            if user_answer == correct_answer:
                is_correct = True
        except:
             # Catch any other eval error
             pass

    if is_correct:
        result_text = f"完全正確！答案是 ${correct_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer}$"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}