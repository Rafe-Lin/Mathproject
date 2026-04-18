import random

def generate_perp_bisector_perimeter_problem():
    """
    基於中垂線性質，求周長或邊長問題。
    對應例題1: 直線 L 為 BC 的中垂線...若△AEC 的周長為 26，AC=8，則 AB 的長度為多少？
    """
    ac = random.randint(5, 12)
    ab = random.randint(ac + 3, 25)
    
    # Perimeter of △AEC = AE + CE + AC
    # Since L is the perpendicular bisector of BC, BE = CE
    # Perimeter of △AEC = AE + BE + AC = AB + AC
    perimeter_aec = ab + ac
    
    question_text = (f"如圖（此處省略圖形），直線 $L$ 為 $\\overline{{BC}}$ 的中垂線，且交 $\\overline{{AB}}$ 於 $E$ 點。<br>"
                       f"若 $\\triangle AEC$ 的周長為 ${perimeter_aec}$，$\\overline{{AC}} = {ac}$，則 $\\overline{{AB}}$ 的長度為多少？")
    
    correct_answer = str(ab)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_perp_bisector_pythagorean_problem():
    """
    結合中垂線性質與畢氏定理。
    對應例題3: △ABC 中，∠A=90°，DE⊥BC，且 BE=CE...
    """
    triples = [(5, 12, 13), (8, 15, 17), (7, 24, 25), (9, 40, 41)]
    triple = random.choice(triples)
    
    # Randomly assign legs
    ab, ac, bc = triple[0], triple[1], triple[2]
    if random.random() < 0.5:
        ab, ac = ac, ab
        
    # Perimeter of △ABE = AB + AE + BE
    # Since DE is the perpendicular bisector of BC (with E on AC), BE = CE.
    # Perimeter = AB + AE + CE = AB + (AE + CE) = AB + AC
    perimeter_abe = ab + ac
    
    question_text = (f"如圖（此處省略圖形），在直角 $\\triangle ABC$ 中，$\\angle A=90^\\circ$。<br>"
                       f"若直線 $L$ 為斜邊 $\\overline{{BC}}$ 的中垂線，且交 $\\overline{{AC}}$ 於 $E$ 點。<br>"
                       f"已知 $\\overline{{AB}}={ab}$、$\\overline{{BC}}={bc}$，則 $\\triangle ABE$ 的周長為何？")
    
    correct_answer = str(perimeter_abe)
                       
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_angle_bisector_distance_area_problem():
    """
    基於角平分線性質，求點到邊的距離或三角形面積。
    對應例題4: △ABC 中，∠ACB=90°，BD 為∠ABC 的角平分線...
    """
    cd = random.randint(3, 7)
    # Ensure AB is even so area is an integer
    ab = random.randint(6, 12) * 2 
    
    # By angle bisector property, DE = CD
    de = cd
    area_abd = int(0.5 * ab * de)
    
    question_type = random.choice(['distance', 'area'])

    if question_type == 'distance':
        question_text = (f"如圖（此處省略圖形），在 $\\triangle ABC$ 中，$\\angle C=90^\\circ$，$\\overline{{BD}}$ 為 $\\angle ABC$ 的角平分線，交 $\\overline{{AC}}$ 於 $D$ 點。<br>"
                           f"若自 $D$ 點作 $\\overline{{DE}} \\perp \\overline{{AB}}$ 於 $E$ 點，且 $\\overline{{CD}}={cd}$，則 $\\overline{{DE}}$ 的長度為多少？")
        correct_answer = str(de)
    else: # area
        question_text = (f"如圖（此處省略圖形），在 $\\triangle ABC$ 中，$\\angle C=90^\\circ$，$\\overline{{BD}}$ 為 $\\angle ABC$ 的角平分線，交 $\\overline{{AC}}$ 於 $D$ 點。<br>"
                           f"若自 $D$ 點作 $\\overline{{DE}} \\perp \\overline{{AB}}$ 於 $E$ 點，且 $\\overline{{AB}}={ab}$、$\\overline{{CD}}={cd}$，則 $\\triangle ABD$ 的面積為多少？")
        correct_answer = str(area_abd)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_angle_bisector_find_angle_problem():
    """
    基於角平分線的判別性質，求角度。
    對應例題6: △ABC 中，DE⊥AB、DF⊥AC，且 DE=DF...
    """
    # Generate angles such that the sum is less than 180 and result is positive
    while True:
        angle_bad = random.randint(20, 40)
        angle_c = random.randint(30, 75)
        angle_bac = 2 * angle_bad
        
        # Ensure the third angle is positive and reasonably sized
        if angle_bac + angle_c < 160: 
            break
            
    angle_b = 180 - angle_bac - angle_c
    
    question_text = (f"如圖（此處省略圖形），在 $\\triangle ABC$ 中，點 $D$ 在 $\\overline{{BC}}$ 上，$\\overline{{DE}} \\perp \\overline{{AB}}$ 於 $E$ 點，$\\overline{{DF}} \\perp \\overline{{AC}}$ 於 $F$ 點。<br>"
                       f"若 $\\overline{{DE}} = \\overline{{DF}}$，且 $\\angle BAD={angle_bad}^\\circ$，$\\angle C={angle_c}^\\circ$，則 $\\angle B$ 的度數為多少？")
    
    correct_answer = str(angle_b)
                   
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def generate(level=1):
    """
    生成「中垂線與角平分線性質」相關題目。
    - Perpendicular Bisector Property:
      1. Finding perimeter/length.
      2. Combined with Pythagorean theorem.
    - Angle Bisector Property:
      1. Finding distance from a point to a side, or area.
      2. Finding an angle in a triangle using the converse property.
    """
    problem_type = random.choice([
        'perp_bisector_perimeter', 
        'perp_bisector_pythagorean', 
        'angle_bisector_distance_area', 
        'angle_bisector_find_angle'
    ])
    
    if problem_type == 'perp_bisector_perimeter':
        return generate_perp_bisector_perimeter_problem()
    elif problem_type == 'perp_bisector_pythagorean':
        return generate_perp_bisector_pythagorean_problem()
    elif problem_type == 'angle_bisector_distance_area':
        return generate_angle_bisector_distance_area_problem()
    else: # 'angle_bisector_find_angle'
        return generate_angle_bisector_find_angle_problem()

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    # Attempt to convert both answers to float for comparison, if possible
    try:
        user_float = float(user_answer.strip())
        correct_float = float(correct_answer.strip())
        is_correct = abs(user_float - correct_float) < 1e-9
    except (ValueError, TypeError):
        # Fallback to string comparison if conversion fails
        is_correct = user_answer.strip().upper() == correct_answer.strip().upper()

    if is_correct:
        result_text = f"完全正確！答案是 ${correct_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer}$"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}