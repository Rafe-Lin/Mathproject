import random
import math
from fractions import Fraction

# --- Problem Generation Functions ---

def generate_acute_angle_from_vertex_angle():
    """
    例題1: 在銳角△ABC 中，O 點為外心，若∠A=65°，則∠BOC 的度數為何？
    """
    angle_A = random.randint(51, 89)
    angle_BOC = 2 * angle_A
    question_text = f"在銳角$\\triangle ABC$ 中，$O$ 點為外心，若 $\\angle A={angle_A}\\circ$，則 $\\angle BOC$ 的度數為何？"
    return {
        "question_text": question_text,
        "answer": str(angle_BOC),
        "correct_answer": str(angle_BOC)
    }

def generate_acute_angle_from_central_angle():
    """
    例題2: 在銳角△ABC 中，O 點為外心，若∠AOC=100°，則∠ABC 的度數為何？
    """
    angle_B = random.randint(51, 89)
    angle_AOC = 2 * angle_B
    question_text = f"在銳角$\\triangle ABC$ 中，$O$ 點為外心，若 $\\angle AOC={angle_AOC}\\circ$，則 $\\angle ABC$ 的度數為何？"
    return {
        "question_text": question_text,
        "answer": str(angle_B),
        "correct_answer": str(angle_B)
    }

def generate_obtuse_angle_from_vertex_angle():
    """
    例題3: 在鈍角△ABC 中，O 點為外心，若∠BAC=110°，則∠BOC 的度數為何？
    """
    angle_A = random.randint(91, 149)
    angle_BOC = 360 - 2 * angle_A
    question_text = f"在鈍角$\\triangle ABC$ 中，$O$ 點為外心，若 $\\angle BAC={angle_A}\\circ$，則 $\\angle BOC$ 的度數為何？"
    return {
        "question_text": question_text,
        "answer": str(angle_BOC),
        "correct_answer": str(angle_BOC)
    }

def generate_ambiguous_angle_from_central_angle():
    """
    例題4: 在△ABC 中，O 點為外心，若∠BOC=140°，則∠BAC 的度數為何？
    """
    angle_BOC = 2 * random.randint(20, 89) # Ensures even number between 40 and 178
    acute_A = angle_BOC // 2
    obtuse_A = (360 - angle_BOC) // 2
    question_text = f"在 $\\triangle ABC$ 中，$O$ 點為外心，若 $\\angle BOC={angle_BOC}\\circ$，則 $\\angle BAC$ 的度數可能為何？ (提示：須考慮銳角與鈍角兩種情況，請填入兩個答案並以逗號分隔)"
    # The check function will sort the answers, so order doesn't matter
    correct_answer = f"{acute_A},{obtuse_A}"
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_right_triangle_radius():
    """
    例題5: 直角△ABC 中，∠C=90°，若 AC=8、BC=6，則其外接圓半徑為多少？
    """
    triples = [(3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25), (6, 8, 10)]
    k = random.randint(1, 2)
    a, b, c = random.choice(triples)
    leg1, leg2, hyp = a*k, b*k, c*k
    
    if random.random() < 0.5:
        leg1, leg2 = leg2, leg1
        
    radius = hyp / 2
    radius_str = str(int(radius)) if radius.is_integer() else str(radius)
    
    question_text = f"直角$\\triangle ABC$ 中，$\\angle C=90\\circ$，若兩股長分別為 ${leg1}$ 與 ${leg2}$，則其外接圓半徑為多少？"
    return {
        "question_text": question_text,
        "answer": radius_str,
        "correct_answer": radius_str
    }

def generate_right_triangle_special_area():
    """
    例題6: 直角△ABC 中，∠C=90°，O 點為外心，若 OC=BC=6，則△ABC 的面積為多少？
    """
    s = random.choice([4, 6, 8, 10]) # Even numbers for nice integer coefficients
    area_coeff = s*s // 2
    
    question_text = f"直角$\\triangle ABC$ 中，$\\angle C=90\\circ$，$O$ 點為外心。若外接圓半徑 $OC$ 恰好等於一股長 $BC$，且 $OC={s}$，則 $\\triangle ABC$ 的面積為多少？"
    correct_answer = f"{area_coeff}\\sqrt{{3}}"
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_isosceles_triangle_radius():
    """
    例題7/8: O 點為等腰△ABC 的外心，AB=AC=5，BC=6，則其外接圓半徑為多少？
    """
    # h, b/2, a -> height, base/2, equal_side
    sets = [ (4, 3, 5), (5, 12, 13), (12, 5, 13), (8, 15, 17), (15, 8, 17) ]
    h, b_half, a_side = random.choice(sets)
    base = 2 * b_half
    side = a_side
    
    radius = Fraction(side**2, 2*h)
    
    if radius.denominator == 1:
        radius_str = str(radius.numerator)
    elif radius.numerator / radius.denominator in [16.9]: # For specific examples from reference
        radius_str = str(radius.numerator / radius.denominator)
    else:
        radius_str = f"{radius.numerator}/{radius.denominator}"

    question_text = f"$O$ 點為等腰$\\triangle ABC$ 的外心，$AB=AC={side}$，$BC={base}$，則其外接圓半徑為多少？"
    return {
        "question_text": question_text,
        "answer": radius_str,
        "correct_answer": radius_str
    }

# --- Main Functions ---

def generate(level=1):
    """
    生成「三角形的外心」相關題目。
    - 依據三角形類型（銳角、鈍角、直角）與已知條件，生成不同題型。
    """
    # Problem Types based on Reference Examples:
    # 1. generate_acute_angle_from_vertex_angle: Given ∠A in acute triangle, find ∠BOC. (Ex 1)
    # 2. generate_acute_angle_from_central_angle: Given ∠BOC in acute triangle, find ∠A. (Ex 2)
    # 3. generate_obtuse_angle_from_vertex_angle: Given obtuse ∠A, find ∠BOC. (Ex 3)
    # 4. generate_ambiguous_angle_from_central_angle: Given ∠BOC, find the two possible values for ∠A. (Ex 4)
    # 5. generate_right_triangle_radius: Given legs of a right triangle, find circumradius. (Ex 5)
    # 6. generate_right_triangle_special_area: Given special conditions (30-60-90), find area. (Ex 6)
    # 7. generate_isosceles_triangle_radius: Given sides of an isosceles triangle, find circumradius. (Ex 7, 8)
    
    problem_type_map = {
        'acute_angle_from_vertex_angle': generate_acute_angle_from_vertex_angle,
        'acute_angle_from_central_angle': generate_acute_angle_from_central_angle,
        'obtuse_angle_from_vertex_angle': generate_obtuse_angle_from_vertex_angle,
        'ambiguous_angle_from_central_angle': generate_ambiguous_angle_from_central_angle,
        'right_triangle_radius': generate_right_triangle_radius,
        'right_triangle_special_area': generate_right_triangle_special_area,
        'isosceles_triangle_radius': generate_isosceles_triangle_radius
    }
    
    problem_type = random.choice(list(problem_type_map.keys()))
    return problem_type_map[problem_type]()

def check(user_answer, correct_answer):
    """
    檢查答案是否正確，支援純數字、分數、根號及多答案格式。
    """
    user_answer = user_answer.strip()
    correct_answer = str(correct_answer).strip()

    is_correct = False

    # 1. Handle ambiguous case (e.g., "70,110") by sorting
    if ',' in correct_answer:
        try:
            correct_parts = sorted([p.strip() for p in correct_answer.split(',')])
            user_parts = sorted([p.strip() for p in user_answer.split(',')])
            is_correct = (user_parts == correct_parts)
        except:
            is_correct = False
    # 2. Handle sqrt case (e.g., "18\\sqrt{3}") by normalized string comparison
    elif '\\sqrt' in correct_answer:
        is_correct = (user_answer.replace(" ", "") == correct_answer.replace(" ", ""))
    # 3. Handle numeric/fraction case
    else:
        # First, try direct string match for fractions like "25/8"
        if user_answer == correct_answer:
            is_correct = True
        else:
            # Fallback to float comparison for formats like "5.0" vs "5" or "3.125" vs "25/8"
            try:
                user_val = float(Fraction(user_answer))
                correct_val = float(Fraction(correct_answer))
                if math.isclose(user_val, correct_val):
                    is_correct = True
            except (ValueError, TypeError):
                # If conversion fails, it's not a valid number in the expected format
                pass

    if is_correct:
        result_text = f"完全正確！答案是 ${correct_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer}$"

    return {"correct": is_correct, "result": result_text, "next_question": True}