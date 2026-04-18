import random
from fractions import Fraction
import math

def generate_angle_relation_forward_problem():
    """
    題型：已知頂點角度，求內心對應角。
    公式：∠BIC = 90° + 1/2 * ∠A
    """
    angle_A = random.randrange(40, 140, 2)
    angle_BIC = 90 + angle_A // 2
    
    question_text = f"在△ABC 中，I 點為內心，若$\\angle A = {angle_A}^\\circ$，則$\\angle BIC$ 的度數為何？"
    correct_answer = str(angle_BIC)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_angle_relation_backward_problem():
    """
    題型：已知內心對應角，求頂點角度。
    公式：∠A = (∠BIC - 90°) * 2
    """
    # 確保 0 < angle_A < 180
    # (angle_BIC - 90) * 2 < 180 => angle_BIC - 90 < 90 => angle_BIC < 180
    # (angle_BIC - 90) * 2 > 0 => angle_BIC > 90
    angle_BIC = random.randint(100, 170)
    angle_A = (angle_BIC - 90) * 2
    
    question_text = f"在△ABC 中，I 點為內心，若$\\angle BIC = {angle_BIC}^\\circ$，則$\\angle BAC$ 的度數為何？"
    correct_answer = str(angle_A)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_inradius_right_triangle_problem():
    """
    題型：已知直角三角形邊長，求內切圓半徑。
    公式：r = (a + b - c) / 2
    """
    base_triples = [(3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25)]
    a, b, c = random.choice(base_triples)
    k = random.randint(1, 5)
    leg1, leg2, hyp = a * k, b * k, c * k
    
    r = (leg1 + leg2 - hyp) // 2
    
    given_type = random.choice(['two_legs', 'leg_and_hyp'])
    
    # Randomly assign right angle to B or C
    right_angle_vertex = random.choice(['B', 'C'])

    if given_type == 'two_legs':
        question_text = f"已知 I 點為直角△ABC 的內心，其中$\\angle {right_angle_vertex}=90^\\circ$。若兩股長分別為 ${leg1}$、${leg2}$，則其內切圓半徑為何？"
    else: # leg_and_hyp
        legs = [leg1, leg2]
        random.shuffle(legs)
        given_leg = legs[0]
        question_text = f"已知 I 點為直角△ABC 的內心，其中$\\angle {right_angle_vertex}=90^\\circ$。若一股長為 ${given_leg}$，斜邊長為 ${hyp}$，則其內切圓半徑為何？"
        
    correct_answer = str(r)
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_inradius_isosceles_triangle_problem():
    """
    題型：已知特定等腰三角形邊長，求內切圓半徑。
    公式：面積 = 1/2 * r * s
    """
    k = random.randint(1, 5)
    equal_side = 10 * k
    base = 12 * k
    
    # Calculation for answer:
    # height h = sqrt((10k)^2 - (6k)^2) = 8k
    # area = 1/2 * base * h = 1/2 * 12k * 8k = 48k^2
    # perimeter s = 10k + 10k + 12k = 32k
    # r = 2 * area / s = 2 * 48k^2 / 32k = 3k
    r = 3 * k
    
    question_text = f"△ABC 中，$AB=AC={equal_side}$、$BC={base}$，I 點為其內心，則其內切圓半徑為多少？"
    correct_answer = str(r)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_sub_triangle_area_problem():
    """
    題型：已知直角三角形邊長，求內心構成的子三角形面積。
    概念：△AIB:△BIC:△CIA = c:a:b
    """
    # Use the (3,4,5) triple scaled by an even number to ensure integer areas
    m = random.randint(1, 4)
    k = 2 * m
    leg_short, leg_long, hyp = 3 * k, 4 * k, 5 * k

    # Let C be the right angle. AB is hypotenuse.
    # AC and BC are legs. Randomly assign them.
    if random.random() < 0.5:
        AC, BC, AB = leg_short, leg_long, hyp
    else:
        AC, BC, AB = leg_long, leg_short, hyp

    # We will give one leg and the hypotenuse, which is a common setup.
    given_leg_name = random.choice(['AC', 'BC'])
    given_leg_val = AC if given_leg_name == 'AC' else BC

    # We ask for the area of one of the three sub-triangles.
    sub_triangles = {'AIB': AB, 'BIC': BC, 'CIA': AC}
    target_sub_triangle_name = random.choice(list(sub_triangles.keys()))

    # Calculate the answer
    total_area = (AC * BC) // 2
    perimeter = AC + BC + AB
    target_side_length = sub_triangles[target_sub_triangle_name]
    area = (total_area * target_side_length) // perimeter
    
    question_text = f"已知 I 點為直角△ABC 的內心，其中$\\angle C=90^\\circ$。若 ${given_leg_name}={given_leg_val}$，斜邊 $AB={AB}$，則△{target_sub_triangle_name} 的面積為何？"
    correct_answer = str(area)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    生成「三角形的內心」相關題目。
    包含：
    1. 內心相關角度計算 (正向與反向)
    2. 直角三角形內切圓半徑
    3. 特定等腰三角形內切圓半徑
    4. 內心分割之子三角形面積
    """
    problem_types = [
        'angle_relation_forward',
        'angle_relation_backward',
        'inradius_right_triangle',
        'inradius_isosceles_triangle',
        'sub_triangle_area'
    ]
    problem_type = random.choice(problem_types)
    
    if problem_type == 'angle_relation_forward':
        return generate_angle_relation_forward_problem()
    elif problem_type == 'angle_relation_backward':
        return generate_angle_relation_backward_problem()
    elif problem_type == 'inradius_right_triangle':
        return generate_inradius_right_triangle_problem()
    elif problem_type == 'inradius_isosceles_triangle':
        return generate_inradius_isosceles_triangle_problem()
    else: # 'sub_triangle_area'
        return generate_sub_triangle_area_problem()

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    # Clean up user answer and correct answer for comparison
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    
    # Attempt to compare as floats to handle cases like "15" vs "15.0"
    try:
        is_correct = math.isclose(float(user_answer), float(correct_answer))
    except (ValueError, TypeError):
        # Fallback to string comparison if conversion fails
        is_correct = (user_answer.upper() == correct_answer.upper())

    if is_correct:
        result_text = f"完全正確！答案是 ${correct_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer}$"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}