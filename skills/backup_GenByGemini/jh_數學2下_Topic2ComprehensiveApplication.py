import random
from fractions import Fraction
import math

# 使用 raw string 定義 LaTeX 指令
ANGLE_CMD = r"\angle"
FRAC_CMD = r"\frac"
OVERLINE_CMD = r"\overline"
CIRC_CMD = r"^{\circ}" 
TRIANGLE_CMD = r"\triangle"

def generate(level=1):
    """
    生成「中垂線、角平分線、等腰三角形性質」相關題目。
    """
    problem_type = random.choice([
        'angle_bisector_trapezoid',
        'perpendicular_bisector_triangle',
        'isosceles_triangle_angles',
        'isosceles_triangle_exterior_angle'
    ])
    
    if problem_type == 'angle_bisector_trapezoid':
        return generate_angle_bisector_trapezoid_problem()
    elif problem_type == 'perpendicular_bisector_triangle':
        return generate_perpendicular_bisector_triangle_problem()
    elif problem_type == 'isosceles_triangle_angles':
        return generate_isosceles_triangle_angles_problem()
    else: 
        return generate_isosceles_triangle_exterior_angle_problem()

def generate_angle_bisector_trapezoid_problem():
    """
    題目：梯形中角平分線與直角三角形。
    """
    while True:
        ab_height = random.randint(10, 20)
        ad_base = random.randint(5, ab_height - 1)
        
        numerator = ad_base**2 + ab_height**2
        denominator = 2 * ab_height
        
        if numerator % denominator == 0:
            be_length = numerator // denominator
            if 0 < be_length < ab_height:
                break
        
    # [Fix] 補上空格：\angle A, \angle B, \angle BCD
    question_text = (
        f"如右圖，在梯形 $ABCD$ 中，${OVERLINE_CMD}{{AD}}$ 平行 ${OVERLINE_CMD}{{BC}}$，"
        f"${ANGLE_CMD} A = {ANGLE_CMD} B = 90{CIRC_CMD}$。若 ${OVERLINE_CMD}{{AB}} = {ab_height}$，"
        f"${OVERLINE_CMD}{{AD}} = {ad_base}$，且 ${OVERLINE_CMD}{{CE}}$ 平分 ${ANGLE_CMD} BCD$ 交 ${OVERLINE_CMD}{{AB}}$ 於 $E$ 點，"
        f"${ANGLE_CMD} CDE = 90{CIRC_CMD}$，則 ${OVERLINE_CMD}{{BE}}$ 的長度為何？"
    )
    
    return {
        "question_text": question_text,
        "answer": str(be_length),
        "correct_answer": str(be_length)
    }

def generate_perpendicular_bisector_triangle_problem():
    """
    題目：直角三角形中垂線。
    """
    while True:
        bc_side = random.randint(6, 15)
        ac_side = random.randint(3, bc_side - 1)
        
        numerator = bc_side**2 - ac_side**2
        denominator = 2 * bc_side
        
        if numerator > 0:
            ce_length_frac = Fraction(numerator, denominator)
            if ce_length_frac < bc_side:
                break
                
    # [Fix] 補上空格：\triangle ABC, \angle C
    question_text = (
        f"如右圖，${TRIANGLE_CMD} ABC$ 中，${ANGLE_CMD} C = 90{CIRC_CMD}$，"
        f"${OVERLINE_CMD}{{BC}} = {bc_side}$，${OVERLINE_CMD}{{AC}} = {ac_side}$。"
        f"直線 $L$ 為 ${OVERLINE_CMD}{{AB}}$ 的中垂線，且交 ${OVERLINE_CMD}{{BC}}$ 於 $E$ 點，則 ${OVERLINE_CMD}{{CE}}$ 的長度為何？"
    )
    
    return {
        "question_text": question_text,
        "answer": str(ce_length_frac),
        "correct_answer": str(ce_length_frac)
    }

def generate_isosceles_triangle_angles_problem():
    """
    題目：等腰三角形角度。
    """
    while True:
        angle_b = random.randrange(40, 81, 2)
        angle_c = random.randrange(40, 81, 2)
        if angle_b + angle_c < 180:
            break

    angle_bde = (180 - angle_b) // 2
    angle_cdf = (180 - angle_c) // 2
    angle_edf = 180 - angle_bde - angle_cdf
    
    # [Fix] 補上空格：\triangle ABC, \angle B, \angle C, \angle EDF
    question_text = (
        f"如右圖，${TRIANGLE_CMD} ABC$ 中，$D$、 $E$、 $F$ 分別在 ${OVERLINE_CMD}{{BC}}$、${OVERLINE_CMD}{{AB}}$、${OVERLINE_CMD}{{AC}}$ 上。"
        f"若 ${OVERLINE_CMD}{{BD}} = {OVERLINE_CMD}{{BE}}$、${OVERLINE_CMD}{{CD}} = {OVERLINE_CMD}{{CF}}$，"
        f"且 ${ANGLE_CMD} B = {angle_b}{CIRC_CMD}$、${ANGLE_CMD} C = {angle_c}{CIRC_CMD}$，"
        f"則 ${ANGLE_CMD} EDF$ 的度數為何？"
    )
    
    return {
        "question_text": question_text,
        "answer": str(angle_edf),
        "correct_answer": str(angle_edf)
    }

def generate_isosceles_triangle_exterior_angle_problem():
    """
    題目：等腰三角形與外角。
    """
    while True:
        bac_angle = random.randrange(60, 150, 10)
        
        k_numerator = random.choice([1, 2])
        k_denominator = random.choice([2, 3])
        if k_numerator >= k_denominator: continue
        
        k_val_frac = Fraction(k_numerator, k_denominator)
        bad_angle_exact = k_val_frac * bac_angle
        
        if bad_angle_exact.denominator == 1:
            bad_angle = int(bad_angle_exact)
            d_angle = bac_angle - bad_angle
            if d_angle > 0 and bad_angle > 0:
                break
            
    # 建構分數 LaTeX 字串，使用 {{}} 轉義
    k_val_str = f"{FRAC_CMD}{{{k_numerator}}}{{{k_denominator}}}"
            
    # [Fix] 補上空格：\triangle ABC, \angle BAD, \angle BAC, \angle D
    question_text = (
        f"如右圖，點 $D, B, C$ 共線且 $B$ 在 ${OVERLINE_CMD}{{DC}}$ 上。${TRIANGLE_CMD} ABC$ 中，"
        f"若 ${OVERLINE_CMD}{{AC}} = {OVERLINE_CMD}{{BC}}$，且 ${ANGLE_CMD} BAD = {k_val_str}{ANGLE_CMD} BAC$。"
        f"若 ${ANGLE_CMD} BAC = {bac_angle}{CIRC_CMD}$，則 ${ANGLE_CMD} D$ 的度數為何？"
    )
    
    return {
        "question_text": question_text,
        "answer": str(d_angle),
        "correct_answer": str(d_angle)
    }

def check(user_answer, correct_answer):
    user_answer = str(user_answer).strip().lower()
    correct_answer = str(correct_answer).strip().lower()
    
    is_correct = False
    try:
        if Fraction(user_answer) == Fraction(correct_answer):
            is_correct = True
    except ValueError:
        if user_answer == correct_answer:
            is_correct = True

    feedback = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": feedback, "next_question": True}