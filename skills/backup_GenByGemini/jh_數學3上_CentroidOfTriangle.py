import random
from fractions import Fraction
import math

def generate_median_segment_length_problem():
    """
    Generates a problem about the 2:1 ratio of median segments.
    Example: Given lengths of medians, find segment lengths.
    """
    ad = random.randint(4, 12) * 3
    be = random.randint(4, 12) * 3
    cf = random.randint(4, 12) * 3
    
    ag = ad * 2 // 3
    bg = be * 2 // 3
    cg = cf * 2 // 3
    gd = ad // 3
    
    # Randomly choose what to ask
    choice = random.randint(0, 3)
    if choice == 0:
        question_text = f"△ABC 的三中線 AD、BE、CF 相交於重心 G 點。若 AD=${ad}$、BE=${be}$、CF=${cf}$，則 AG＋BG＋CG 的長度為何？"
        correct_answer = str(ag + bg + cg)
    elif choice == 1:
        question_text = f"△ABC 的中線 AD 長度為 ${ad}$，且 G 為重心，則 AG 的長度為何？"
        correct_answer = str(ag)
    elif choice == 2:
        question_text = f"△ABC 的中線 BE 長度為 ${be}$，且 G 為重心，則 GE 的長度為何？"
        correct_answer = str(be // 3)
    else:
        question_text = f"△ABC 的中線 AD 長度為 ${ad}$，且 G 為重心，則 GD 的長度為何？"
        correct_answer = str(gd)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_area_division_problem():
    """
    Generates a problem about area division by the centroid.
    Covers right and isosceles triangles.
    """
    sub_type = random.choice(['right', 'isosceles'])
    
    if sub_type == 'right':
        # To ensure total_area = (l1*l2)/2 is divisible by 6, l1*l2 must be divisible by 12.
        k = random.randint(1, 3)
        leg1 = random.choice([3, 6, 9]) * k
        leg2 = random.choice([4, 8, 12]) * k
        if random.random() < 0.5:
            leg1, leg2 = leg2, leg1

        total_area = (leg1 * leg2) // 2
        question_start = f"一個直角三角形 ABC，其中 $\\angle B=90°$，G 點為其重心。若兩股長 AB=${leg1}$、BC=${leg2}$"
    
    else: # isosceles
        triples = [(3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25)]
        k = random.randint(1, 2)
        # h*half_base must be divisible by 6, which is true for all common triples
        h, half_base, side = [val * k for val in random.choice(triples)]
        base = 2 * half_base
        
        total_area = h * half_base
        question_start = f"一個等腰三角形 ABC，其中 AB=AC=${side}$，底邊 BC=${base}$，G 點為其重心"

    ask_for_one_third = random.choice([True, False])
    
    if ask_for_one_third:
        area = total_area // 3
        triangle_name = random.choice(["ABG", "BCG", "ACG"])
        question_text = f"{question_start}，則 △{triangle_name} 的面積為何？"
    else:
        area = total_area // 6
        # The names of the small triangles depend on the median labels (D, E, F)
        question_text = f"{question_start}，且三條中線將三角形面積平分成六個相等的小三角形。請問其中一個小三角形的面積為何？"
        
    correct_answer = str(area)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_parallelogram_problem():
    """
    Generates problems combining parallelogram and centroid properties.
    """
    sub_type = random.choice(['length', 'area'])
    
    if sub_type == 'length':
        # Setup: G is centroid of △ABC
        # OG:BG = 1:2, BO = 3*OG, BD = 2*BO = 6*OG
        if random.random() < 0.5: # Give small, ask big
            og = random.randint(2, 8)
            bd = 6 * og
            question_text = f"平行四邊形 ABCD 中，兩對角線 AC 與 BD 交於 O 點，E 為 BC 的中點，AE 與 BD 相交於 G 點。若 OG=${og}$，則對角線 BD 的長度為多少？"
            correct_answer = str(bd)
        else: # Give big, ask small
            bd = random.randint(5, 12) * 6
            og = bd // 6
            question_text = f"平行四邊形 ABCD 中，兩對角線 AC 與 BD 交於 O 點，E 為 BC 的中點，AE 與 BD 相交於 G 點。若對角線 BD=${bd}$，則 OG 的長度為多少？"
            correct_answer = str(og)
    
    else: # area
        # Setup: G is centroid of △ACD
        # Area(△GDE) = 1/6 Area(△ACD) = 1/12 Area(Parallelogram)
        if random.random() < 0.5: # Give small, ask big
            gde_area = random.randint(2, 10)
            abcd_area = 12 * gde_area
            question_text = f"平行四邊形 ABCD 中，兩對角線 AC 與 BD 相交於 O 點，E 為 CD 的中點，AE 與 BD 相交於 G 點。若 △GDE 的面積為 ${gde_area}$，則平行四邊形 ABCD 的面積為何？"
            correct_answer = str(abcd_area)
        else: # Give big, ask small
            abcd_area = random.randint(4, 10) * 12
            gde_area = abcd_area // 12
            question_text = f"平行四邊形 ABCD 中，兩對角線 AC 與 BD 相交於 O 點，E 為 CD 的中點，AE 與 BD 相交於 G 點。若平行四邊形 ABCD 的面積為 ${abcd_area}$，則 △GDE 的面積為何？"
            correct_answer = str(gde_area)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }
    
def generate_right_triangle_hypotenuse_median_problem():
    """
    Generates problems about the centroid and the median to the hypotenuse.
    """
    # Let E be the midpoint of hypotenuse AC. BE is the median.
    # BE = 1/2 * AC. G is on BE. EG = 1/3 BE.
    # So EG = 1/3 * (1/2 * AC) = 1/6 AC.
    if random.random() < 0.5: # Give EG, ask AC
        eg = random.randint(2, 7)
        ac = 6 * eg
        question_text = f"直角△ABC 中，$\\angle B=90°$，G 為其重心，BG 的延長線交斜邊 AC 於 E 點。若 EG=${eg}$，則斜邊 AC 的長度為何？"
        correct_answer = str(ac)
    else: # Give AC, ask EG
        ac = random.randint(5, 12) * 6
        eg = ac // 6
        question_text = f"直角△ABC 中，$\\angle B=90°$，G 為其重心，BG 的延長線交斜邊 AC 於 E 點。若斜邊 AC=${ac}$，則 EG 的長度為何？"
        correct_answer = str(eg)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def generate(level=1):
    """
    Generates a problem related to the centroid of a triangle.
    """
    problem_type = random.choice([
        'median_segment_length', 
        'area_division',
        'parallelogram',
        'right_triangle_hypotenuse_median'
    ])
    
    if problem_type == 'median_segment_length':
        return generate_median_segment_length_problem()
    elif problem_type == 'area_division':
        return generate_area_division_problem()
    elif problem_type == 'parallelogram':
        return generate_parallelogram_problem()
    else: # right_triangle_hypotenuse_median
        return generate_right_triangle_hypotenuse_median_problem()

def check(user_answer, correct_answer):
    """
    Checks if the user's answer is correct.
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    
    is_correct = False
    try:
        # Compare as floats to handle cases like "8" vs "8.0"
        if abs(float(user_answer) - float(correct_answer)) < 1e-9:
            is_correct = True
    except ValueError:
        is_correct = (user_answer.upper() == correct_answer.upper())

    if is_correct:
        result_text = f"完全正確！答案是 ${correct_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer}$"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}