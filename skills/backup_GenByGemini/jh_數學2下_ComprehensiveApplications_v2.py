import random
from fractions import Fraction

def generate_trapezoid_pythagorean():
    """
    Type 1: Trapezoid with Angle Bisector and Pythagorean Theorem.
    In a right trapezoid ABCD, CE bisects angle BCD. With specific perpendicularity conditions,
    this leads to a right triangle where sides can be formed from a Pythagorean triple.
    """
    pythagorean_triples = [(6, 8, 10), (5, 12, 13), (7, 24, 25), (8, 15, 17), (12, 35, 37)]
    b, a, c = random.choice(pythagorean_triples)
    if random.random() < 0.5:
        a, b = b, a  # Swap to randomize which side is which leg

    # Setup:
    # In right triangle ADE (formed by construction/problem statement), let AE=a, AD=b, DE=c.
    # From angle bisector properties and the given ∠CDE=90°, we deduce BE = DE.
    # Therefore, BE = c.
    # The total length of the perpendicular side is AB = AE + BE = a + c.
    ab_len = a + c
    ad_len = b
    be_len = c

    # Fix: replace \degree with ^\circ
    question_text = f"如圖，在梯形 $ABCD$ 中，$AD \\parallel BC$，$\\angle A=\\angle B=90^\\circ$。若 $\\overline{{AB}}={ab_len}$，$\\overline{{AD}}={ad_len}$，且 $\\overline{{CE}}$ 平分 $\\angle BCD$ 交 $\\overline{{AB}}$ 於 $E$ 點，$\\angle CDE=90^\\circ$，則 $\\overline{{BE}}$ 的長度為何？<br><br><small>(此為示意圖，各邊長比例不一定完全精準)</small>"
    
    correct_answer = str(be_len)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_perp_bisector_pythagorean():
    """
    Type 2: Right Triangle Perpendicular Bisector and Pythagorean Theorem.
    The perpendicular bisector of the hypotenuse of a right triangle intersects one of the legs.
    This creates smaller triangles and allows for solving a length using the Pythagorean theorem.
    """
    triples = [(3, 4, 5), (6, 8, 10), (9, 12, 15), (5, 12, 13)]
    b, a, c = random.choice(triples)  # (short leg, long leg, hypotenuse)
    
    # Setup: In right triangle ABC (∠C=90°), AC=b, BC=a, AB=c.
    # The perpendicular bisector of AB intersects the longer leg BC at point E.
    # By definition of a perpendicular bisector, AE = BE.
    # Let CE = x. Then BE = BC - CE = a - x. Thus, AE = a - x.
    # In right triangle ACE: AE² = AC² + CE²  =>  (a - x)² = b² + x².
    # Solving for x gives: x = (a² - b²) / (2a).
    
    numerator = a**2 - b**2
    denominator = 2 * a
    
    ans = Fraction(numerator, denominator)
    
    # Fix: replace \degree with ^\circ
    question_text = f"如圖，$\\triangle ABC$ 中，$\\angle C=90^\\circ$，$\\overline{{AB}}={c}$，$\\overline{{BC}}={a}$，$\\overline{{AC}}={b}$。若直線 $L$ 為 $\\overline{{AB}}$ 的中垂線，且 $L$ 交 $\\overline{{BC}}$ 於 $E$ 點，則 $\\overline{{CE}}$ 的長度為何？<br><br><small>(此為示意圖，各邊長比例不一定完全精準)</small>"
    
    if ans.denominator == 1:
        correct_answer = str(ans.numerator)
    else:
        correct_answer = f"{ans.numerator}/{ans.denominator}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_isosceles_angle_sum():
    """
    Type 3: Isosceles Angle Sum on a Line.
    Two isosceles triangles are constructed on the base of a larger triangle.
    The angle between them can be found using angle sum properties.
    """
    angle_b_half = random.randint(20, 35)
    angle_c_half = random.randint(20, 35)
    while angle_b_half == angle_c_half or (angle_b_half + angle_c_half) >= 80:
        angle_b_half = random.randint(20, 35)
        angle_c_half = random.randint(20, 35)
        
    angle_b = angle_b_half * 2
    angle_c = angle_c_half * 2
    
    # Logic: ∠EDF = 180 - ∠BDE - ∠CDF
    # ∠BDE = (180 - ∠B) / 2 = 90 - ∠B/2
    # ∠CDF = (180 - ∠C) / 2 = 90 - ∠C/2
    # ∠EDF = 180 - (90 - ∠B/2) - (90 - ∠C/2) = (∠B + ∠C) / 2
    answer = angle_b_half + angle_c_half
    
    # Fix: replace \degree with ^\circ
    question_text = f"如圖，$\\triangle ABC$ 中，$D$、$E$、$F$ 分別在 $\\overline{{BC}}$、$\\overline{{AB}}$、$\\overline{{AC}}$ 上。若 $\\overline{{BD}}=\\overline{{BE}}$、$\\overline{{CD}}=\\overline{{CF}}$，且 $\\angle B={angle_b}^\\circ$、$\\angle C={angle_c}^\\circ$，則 $\\angle EDF$ 的度數為何？<br><br><small>(此為示意圖，各邊長比例不一定完全精準)</small>"
    
    correct_answer = str(answer)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_chained_isosceles():
    """
    Type 4: Chained Isosceles & Exterior Angle Theorem.
    A chain of equalities (AB=AD=CD) creates two connected isosceles triangles.
    The exterior angle theorem links their angles.
    """
    if random.random() < 0.5:
        # Given ∠C, find ∠B. Logic: ∠B = 2 * ∠C
        angle_c = random.randint(25, 40)
        angle_b = 2 * angle_c
        
        # Fix: replace \degree with ^\circ
        question_text = f"如圖，$\\triangle ABC$ 中，已知 $D$ 為 $\\overline{{BC}}$ 上一點，若 $\\overline{{AB}}=\\overline{{AD}}=\\overline{{CD}}$，且 $\\angle C={angle_c}^\\circ$，則 $\\angle B$ 的度數為何？<br><br><small>(此為示意圖，各邊長比例不一定完全精準)</small>"
        correct_answer = str(angle_b)
    else:
        # Given ∠B, find ∠C. Logic: ∠C = ∠B / 2
        angle_b = random.choice([50, 54, 60, 68, 70, 76, 80])
        angle_c = angle_b // 2

        # Fix: replace \degree with ^\circ
        question_text = f"如圖，$\\triangle ABC$ 中，已知 $D$ 為 $\\overline{{BC}}$ 上一點，若 $\\overline{{AB}}=\\overline{{AD}}=\\overline{{CD}}$，且 $\\angle B={angle_b}^\\circ$，則 $\\angle C$ 的度數為何？<br><br><small>(此為示意圖，各邊長比例不一定完全精準)</small>"
        correct_answer = str(angle_c)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_find_equal_sides():
    """
    Type 5: Find Equal Sides from Angles.
    Given two angles of a triangle, the student must find the third and then use the property
    that sides opposite equal angles are equal.
    """
    equal_angle = random.randint(40, 80)
    # Ensure the third angle is not equal to the first two (i.e., not equilateral)
    while (180 - 2 * equal_angle) == equal_angle:
        equal_angle = random.randint(40, 80)
        
    third_angle = 180 - 2 * equal_angle
    
    angles = [equal_angle, equal_angle, third_angle]
    random.shuffle(angles)
    
    angle_a, angle_b, angle_c = angles
    
    given_angles_dict = {'A': angle_a, 'B': angle_b, 'C': angle_c}
    # Give the two different angles as knowns
    given_keys = ['A', 'B', 'C']
    if angle_a == angle_b:
        known_keys = random.sample(['A', 'C'], 2) if random.random() < 0.5 else random.sample(['B', 'C'], 2)
    elif angle_a == angle_c:
        known_keys = random.sample(['A', 'B'], 2) if random.random() < 0.5 else random.sample(['C', 'B'], 2)
    else: # B==C
        known_keys = random.sample(['B', 'A'], 2) if random.random() < 0.5 else random.sample(['C', 'A'], 2)

    # Fix: replace \degree with ^\circ
    q_str = f"$\\triangle ABC$ 中，已知 $\\angle {known_keys[0]}={given_angles_dict[known_keys[0]]}^\\circ$，$\\angle {known_keys[1]}={given_angles_dict[known_keys[1]]}^\\circ$，則此三角形的邊長中，哪兩個邊的長度相等？(請以 $\\overline{{AB}}=\\overline{{BC}}$ 的格式作答)"

    if angle_a == angle_b:
        answer = "\\overline{AC}=\\overline{BC}"
    elif angle_a == angle_c:
        answer = "\\overline{AB}=\\overline{BC}"
    else:  # angle_b == angle_c
        answer = "\\overline{AB}=\\overline{AC}"
    
    return {
        "question_text": q_str,
        "answer": answer,
        "correct_answer": answer
    }

def generate_corrected_double_isosceles():
    """
    Type 6: Double Isosceles Problem for side length.
    Two angle equalities create two isosceles triangles, allowing for a side length calculation.
    """
    bc_len = random.randint(3, 10)
    ab_len = random.randint(bc_len + 2, bc_len + 10)
    
    bd_len = ab_len - bc_len
    
    # Logic:
    # ∠A = ∠ACD  =>  AD = CD (in ΔACD)
    # ∠B = ∠BDC  =>  BC = CD (in ΔBCD)
    # Therefore, AD = BC.
    # BD = AB - AD = AB - BC.
    
    question_text = f"如圖，$\\triangle ABC$ 中，$D$ 為 $\\overline{{AB}}$ 上一點。若 $\\overline{{AB}}={ab_len}$、$\\overline{{BC}}={bc_len}$，且 $\\angle A=\\angle ACD$、$\\angle B=\\angle BDC$，則 $\\overline{{BD}}$ 的長度為何？<br><br><small>(此為示意圖，各邊長比例不一定完全精準)</small>"
    
    correct_answer = str(bd_len)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    生成「中垂線、角平分線、等腰三角形」綜合應用題。
    """
    problem_types = [
        generate_trapezoid_pythagorean,
        generate_perp_bisector_pythagorean,
        generate_isosceles_angle_sum,
        generate_chained_isosceles,
        generate_find_equal_sides,
        generate_corrected_double_isosceles
    ]
    
    gen_func = random.choice(problem_types)
    return gen_func()

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    
    is_correct = False
    
    if "\\overline" in correct_answer:
        try:
            cleaned_user_answer = user_answer.replace(" ", "").upper()
            cleaned_user_answer = cleaned_user_answer.replace("\\OVERLINE", "").replace("{", "").replace("}", "")
            
            parts_correct = correct_answer.replace("\\overline", "").replace("{", "").replace("}", "").split("=")
            side1_correct = set(parts_correct[0])
            side2_correct = set(parts_correct[1])
            
            parts_user = cleaned_user_answer.split("=")
            if len(parts_user) == 2:
                side1_user = set(parts_user[0])
                side2_user = set(parts_user[1])
                
                is_correct = (side1_correct == side1_user and side2_correct == side2_user) or \
                             (side1_correct == side2_user and side2_correct == side1_user)
        except (ValueError, IndexError):
            is_correct = False
    else:
        try:
            user_frac = Fraction(user_answer)
            correct_frac = Fraction(correct_answer)
            is_correct = (user_frac == correct_frac)
        except (ValueError, ZeroDivisionError):
            is_correct = False

    if is_correct:
        result_text = f"完全正確！答案是 ${correct_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer}$"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}