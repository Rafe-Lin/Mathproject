import random

# Helper function for LaTeX arc notation
def arc(points):
    """Generates the LaTeX string for an arc over points."""
    return f"\\overset{{\\frown}}{{{points}}}"

def generate(level=1):
    """
    Generates a question about inscribed angles, parallel chords, and cyclic quadrilaterals.
    """
    problem_types = [
        'basic_angle_arc',
        'diameter_and_arcs',
        'cyclic_quadrilateral',
        'parallel_chords',
        'semicircle_triangle',
        'multi_arc_angle'
    ]
    problem_type = random.choice(problem_types)

    if problem_type == 'basic_angle_arc':
        return generate_basic_angle_arc_problem()
    elif problem_type == 'diameter_and_arcs':
        return generate_diameter_problem()
    elif problem_type == 'cyclic_quadrilateral':
        return generate_cyclic_quad_problem()
    elif problem_type == 'parallel_chords':
        return generate_parallel_chords_problem()
    elif problem_type == 'semicircle_triangle':
        return generate_semicircle_triangle_problem()
    else: # 'multi_arc_angle'
        return generate_multi_arc_angle_problem()

def generate_basic_angle_arc_problem():
    """
    Problem type: Basic relationships between central angle, inscribed angle, and arc measure.
    """
    sub_type = random.choice(['c_to_i', 'i_to_c', 'major_arc'])

    if sub_type == 'c_to_i':
        central_angle = random.randrange(40, 170, 2)
        inscribed_angle = central_angle // 2
        question_text = f"已知一圓心角為 ${central_angle}^\\circ$，求其所對應的圓周角度數。"
        correct_answer = str(inscribed_angle)
    elif sub_type == 'i_to_c':
        inscribed_angle = random.randint(20, 85)
        central_angle = inscribed_angle * 2
        question_text = f"已知一圓周角為 ${inscribed_angle}^\\circ$，求其所對應的圓心角度數。"
        correct_answer = str(central_angle)
    else: # 'major_arc'
        central_angle = random.randrange(80, 170, 2)
        major_arc = 360 - central_angle
        major_inscribed_angle = major_arc // 2
        question_text = f"已知一劣弧所對的圓心角為 ${central_angle}^\\circ$，求其對應的優弧所對的圓周角度數。"
        correct_answer = str(major_inscribed_angle)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_diameter_problem():
    """
    Problem type: Using the diameter and given arcs/angles to find others.
    """
    angle_adc = random.randint(30, 70)
    arc_ac = 2 * angle_adc
    # Ensure arc_bd is valid and leaves space for arc_ac
    arc_bd = random.randrange(20, 180 - arc_ac, 2)
    arc_ad = 180 - arc_bd
    
    # Calculate potential answers
    ans_angle_abc = angle_adc  # Subtends the same arc AC
    ans_angle_acd = arc_ad // 2  # Subtends arc AD
    ans_arc_ad = arc_ad
    ans_arc_bc = 180 - arc_ac # Semicircle - arc_ac

    choices = [
        (f"$\\angle ABC$", ans_angle_abc),
        (f"$\\angle ACD$", ans_angle_acd),
        (f"劣弧 ${arc('AD')}$", ans_arc_ad),
        (f"劣弧 ${arc('BC')}$", ans_arc_bc)
    ]
    
    chosen_question, correct_answer = random.choice(choices)
    
    question_text = f"如圖，已知 $AB$ 是圓 $O$ 的直徑，若 $\\angle ADC={angle_adc}^\\circ$ 且 ${arc('BD')}={arc_bd}^\\circ$，求 {chosen_question} 的度數。"
    
    return {
        "question_text": question_text,
        "answer": str(correct_answer),
        "correct_answer": str(correct_answer)
    }

def generate_cyclic_quad_problem():
    """
    Problem type: Properties of a cyclic quadrilateral (opposite angles, exterior angle).
    """
    sub_type = random.choice(['opposite', 'exterior', 'combined'])
    
    if sub_type == 'opposite':
        angle_a = random.randint(70, 110)
        angle_c = 180 - angle_a
        question_text = f"圓內接四邊形 $ABCD$ 中，若 $\\angle A = {angle_a}^\\circ$，求 $\\angle C$ 的度數。"
        correct_answer = str(angle_c)
    elif sub_type == 'exterior':
        angle_bad = random.randint(70, 110)
        question_text = f"如圖，四邊形 $ABCD$ 為圓內接四邊形，且 $B、C、E$ 三點共線。若 $\\angle BAD = {angle_bad}^\\circ$，求外角 $\\angle DCE$ 的度數。"
        correct_answer = str(angle_bad)
    else: # 'combined'
        angle_abc = random.randint(65, 85)
        angle_bad = random.randint(105, 125)
        
        ans_adc = 180 - angle_abc
        ans_dce = angle_bad

        if random.random() < 0.5:
            asked_angle = "\\angle ADC"
            correct_answer = str(ans_adc)
        else:
            asked_angle = "\\angle DCE"
            correct_answer = str(ans_dce)
        
        question_text = f"如圖，四邊形 $ABCD$ 為圓內接四邊形，且 $B、C、E$ 三點共線。若 $\\angle ABC={angle_abc}^\\circ$，$\\angle BAD={angle_bad}^\\circ$，求 ${asked_angle}$ 的度數？"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_parallel_chords_problem():
    """
    Problem type: Properties of parallel chords intercepting arcs.
    """
    # Ensure remaining arc is positive
    arc_ad = random.randrange(50, 82, 2)
    arc_cd = random.randrange(60, 102, 2)
    # 360 - 102 - 2*82 = 360 - 102 - 164 = 94. OK.
    
    arc_bc = arc_ad
    
    # Calculate angles
    angle_abc = (arc_ad + arc_cd) // 2
    angle_bad = (arc_bc + arc_cd) // 2
    
    if random.random() < 0.5:
        asked_entity = f"$\\angle ABC$"
        correct_answer = str(angle_abc)
    else:
        asked_entity = f"$\\angle BAD$"
        correct_answer = str(angle_bad)

    question_text = f"圓中有兩平行弦 $AB$ 與 $CD$。若劣弧 ${arc('AD')} = {arc_ad}^\\circ$，且劣弧 ${arc('CD')} = {arc_cd}^\\circ$，求 {asked_entity} 的度數。"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_semicircle_triangle_problem():
    """
    Problem type: Angle in a semicircle is a right angle.
    """
    angle_a = random.randint(20, 70)
    angle_b = 90 - angle_a
    
    if random.random() < 0.5:
        # Given A, find B
        known_angle_name = "\\angle CAB"
        known_angle_val = angle_a
        unknown_angle_name = "\\angle ABC"
        correct_answer = str(angle_b)
    else:
        # Given B, find A
        known_angle_name = "\\angle ABC"
        known_angle_val = angle_b
        unknown_angle_name = "\\angle CAB"
        correct_answer = str(angle_a)
        
    question_text = f"如圖，一個半圓的直徑為 $AB$，C 為圓弧上的一點。若 ${known_angle_name}={known_angle_val}^\\circ$，則 ${unknown_angle_name}$ 是幾度？"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_multi_arc_angle_problem():
    """
    Problem type: Complex problem involving multiple given arcs and angles.
    """
    while True:
        arc_ad = random.randrange(50, 82, 2)
        central_cod = random.randrange(60, 92, 2) # This is also arc_cd
        arc_cd = central_cod
        
        angle_dab = random.randint(100, 130)
        arc_dcb = 2 * angle_dab
        
        arc_bc = arc_dcb - arc_cd
        arc_ab = 360 - arc_ad - arc_cd - arc_bc
        
        if arc_bc > 0 and arc_ab > 10: # Ensure valid geometry
            break
            
    # Potential questions and answers
    ans_angle_abc = (arc_ad + arc_cd) // 2
    ans_arc_bc = arc_bc
    ans_angle_bce = angle_dab # Exterior angle of cyclic quad
    ans_angle_adc = (arc_ab + arc_bc) // 2

    choices = [
        (f"$\\angle ABC$ 的度數", ans_angle_abc),
        (f"劣弧 ${arc('BC')}$ 的度數", ans_arc_bc),
        (f"$\\angle ADC$ 的度數", ans_angle_adc)
    ]
    
    chosen_question, correct_answer = random.choice(choices)
    
    question_text = (f"如圖，A、B、C、D 為圓 O 上相異四點，已知劣弧 ${arc('AD')}={arc_ad}^\\circ$，"
                     f"$\\angle COD={central_cod}^\\circ$，且 $\\angle DAB={angle_dab}^\\circ$，求 {chosen_question}。")

    return {
        "question_text": question_text,
        "answer": str(correct_answer),
        "correct_answer": str(correct_answer)
    }


def check(user_answer, correct_answer):
    """
    Checks if the user's answer is correct.
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    
    is_correct = False
    # Allow for answers like "60度" or "60"
    user_answer_val = "".join(filter(str.isdigit or (lambda c: c in '.'), user_answer))

    if user_answer_val == correct_answer:
        is_correct = True
    else:
        try:
            if float(user_answer_val) == float(correct_answer):
                is_correct = True
        except (ValueError, TypeError):
            # Cannot convert to float, comparison fails
            pass

    if is_correct:
        result_text = f"完全正確！答案是 ${correct_answer}^\\circ$。"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer}^\\circ$。"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}