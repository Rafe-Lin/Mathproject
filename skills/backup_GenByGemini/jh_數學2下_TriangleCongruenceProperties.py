import random
from fractions import Fraction
import uuid

# Helper to generate side lengths
def generate_side_length():
    """Generates a random integer side length."""
    return random.randint(5, 20)

# Helper to generate angles for non-right triangles
def generate_angle(min_val=30, max_val=120):
    """Generates a random integer angle within a specified range."""
    return random.randint(min_val, max_val)

# Helper to ensure triangle inequality (sum of any two sides > third side)
def check_triangle_inequality(s1, s2, s3):
    return (s1 + s2 > s3 and s1 + s3 > s2 and s2 + s3 > s1)

# Helper to generate a leg and a hypotenuse for right triangles
def generate_hypotenuse_and_leg():
    """Generates a leg length and a hypotenuse length, ensuring hypotenuse > leg."""
    leg = random.randint(6, 15)
    hyp = random.randint(leg + 2, leg + 10) # Hypotenuse must be longer than the leg
    return leg, hyp

def generate_sss_problem():
    s1 = generate_side_length()
    s2 = generate_side_length()
    s3 = generate_side_length()
    
    # Ensure triangle inequality holds for ABC
    while not check_triangle_inequality(s1, s2, s3):
        s1 = generate_side_length()
        s2 = generate_side_length()
        s3 = generate_side_length()

    is_congruent = random.choice([True, False]) # 50% chance of being congruent

    question_text = ""
    correct_answer_str = ""

    if is_congruent:
        # Congruent case: sides are the same, can be listed in any order for DEF
        sides_def = [s1, s2, s3]
        random.shuffle(sides_def) # Shuffle to make mapping non-obvious if desired
        s1_prime, s2_prime, s3_prime = sides_def[0], sides_def[1], sides_def[2]

        question_text = (
            f"已知在 $\\triangle ABC$ 中，$\\overline{{AB}}={s1}$，$\\overline{{BC}}={s2}$，$\\overline{{CA}}={s3}$；"
            f"在 $\\triangle DEF$ 中，$\\overline{{DE}}={s1_prime}$，$\\overline{{EF}}={s2_prime}$，$\\overline{{FD}}={s3_prime}$。"
            f"<br>請問 $\\triangle ABC$ 和 $\\triangle DEF$ 是否全等？若是，請說明是根據哪一個全等性質。"
        )
        correct_answer_str = "是, SSS"
    else:
        # Not congruent case: one side length is different
        s1_prime = s1
        s2_prime = s2
        
        s3_prime_candidate = s3
        attempts = 0
        max_attempts = 10
        # Try to find a different s3_prime that still forms a valid triangle
        while (s3_prime_candidate == s3 or 
               not check_triangle_inequality(s1, s2, s3_prime_candidate)) and attempts < max_attempts:
            s3_prime_candidate = s3 + random.choice([-2, -1, 1, 2, 3])
            if s3_prime_candidate < 1: s3_prime_candidate = 1 # Prevent non-positive side
            attempts += 1
        
        # Fallback: if after attempts, still can't find a valid different triangle,
        # or if the initial choice was for a clearly different value
        if s3_prime_candidate == s3 or not check_triangle_inequality(s1, s2, s3_prime_candidate):
            s3_prime_candidate = s3 + random.randint(3, 5) # Guaranteed different, clear mismatch
        
        s3_prime = s3_prime_candidate

        question_text = (
            f"已知在 $\\triangle ABC$ 中，$\\overline{{AB}}={s1}$，$\\overline{{BC}}={s2}$，$\\overline{{CA}}={s3}$；"
            f"在 $\\triangle DEF$ 中，$\\overline{{DE}}={s1_prime}$，$\\overline{{EF}}={s2_prime}$，$\\overline{{FD}}={s3_prime}$。"
            f"<br>請問 $\\triangle ABC$ 和 $\\triangle DEF$ 是否全等？若是，請說明是根據哪一個全等性質。"
        )
        correct_answer_str = "否"

    return {
        "question_text": question_text,
        "answer": correct_answer_str,
        "correct_answer": correct_answer_str
    }

def generate_sas_problem():
    s1 = generate_side_length()
    angle = generate_angle(min_val=30, max_val=120) # Included angle
    s2 = generate_side_length()

    is_congruent = random.choice([True, False])

    question_text = ""
    correct_answer_str = ""
    
    # Ensure a valid triangle can be formed (rough check: two sides and an angle)
    # The triangle inequality needs to hold for the implied third side, which is complex.
    # For now, rely on angle limits (less than 180) and side length positivity.

    if is_congruent:
        # Congruent: AB=DE, BC=EF, angle B=angle E
        question_text = (
            f"已知在 $\\triangle ABC$ 中，$\\overline{{AB}}={s1}$，$\\overline{{BC}}={s2}$，$\\angle B={angle}\\circ$；"
            f"在 $\\triangle DEF$ 中，$\\overline{{DE}}={s1}$，$\\overline{{EF}}={s2}$，$\\angle E={angle}\\circ$。"
            f"<br>請問 $\\triangle ABC$ 和 $\\triangle DEF$ 是否全等？若是，請說明是根據哪一個全等性質。"
        )
        correct_answer_str = "是, SAS"
    else:
        # Not congruent case:
        choice = random.choice(['mismatch', 'ssa_like'])

        if choice == 'mismatch':
            # One side or angle is different
            mismatched_part = random.choice(['s1', 'angle', 's2'])
            s1_prime, angle_prime, s2_prime = s1, angle, s2
            
            if mismatched_part == 's1':
                s1_prime = s1 + random.choice([-1, 1])
                if s1_prime < 1: s1_prime = 1
            elif mismatched_part == 'angle':
                angle_prime = angle + random.choice([-5, 5])
                if angle_prime <= 0 or angle_prime >= 180: angle_prime = 45 # Fallback
            else: # mismatched_part == 's2'
                s2_prime = s2 + random.choice([-1, 1])
                if s2_prime < 1: s2_prime = 1
            
            # Ensure it's actually a mismatch
            if s1_prime == s1 and angle_prime == angle and s2_prime == s2:
                s1_prime = s1 + 1 # Force a mismatch if random led to same values
                if s1_prime < 1: s1_prime = 1

            question_text = (
                f"已知在 $\\triangle ABC$ 中，$\\overline{{AB}}={s1}$，$\\overline{{BC}}={s2}$，$\\angle B={angle}\\circ$；"
                f"在 $\\triangle DEF$ 中，$\\overline{{DE}}={s1_prime}$，$\\overline{{EF}}={s2_prime}$，$\\angle E={angle_prime}\\circ$。"
                f"<br>請問 $\\triangle ABC$ 和 $\\triangle DEF$ 是否全等？若是，請說明是根據哪一個全等性質。"
            )
        else: # ssa_like (Angle not included, SSA is not a congruence criterion)
            # Present AB, AC, angle B for ABC (SSA)
            s3 = generate_side_length()
            while not check_triangle_inequality(s1, s2, s3): # Ensure ABC is a valid triangle
                s3 = generate_side_length() # s3 represents AC here, s2 represents BC
            
            # To make it SSA, side s3 (AC) should be opposite angle B, and side s1 (AB) is adjacent.
            # Triangle ABC: AB=s1, AC=s3, Angle B=angle.
            # Triangle DEF: DE=s1, DF=s3, Angle E=angle.
            question_text = (
                f"已知在 $\\triangle ABC$ 中，$\\overline{{AB}}={s1}$，$\\overline{{AC}}={s3}$，$\\angle B={angle}\\circ$；" 
                f"在 $\\triangle DEF$ 中，$\\overline{{DE}}={s1}$，$\\overline{{DF}}={s3}$，$\\angle E={angle}\\circ$。" 
                f"<br>請問 $\\triangle ABC$ 和 $\\triangle DEF$ 是否全等？若是，請說明是根據哪一個全等性質。"
            )
        correct_answer_str = "否" # SSA is not a congruence criterion

    return {
        "question_text": question_text,
        "answer": correct_answer_str,
        "correct_answer": correct_answer_str
    }

def generate_rhs_problem():
    leg, hyp = generate_hypotenuse_and_leg()
    
    # Ensure leg < hypotenuse
    while leg >= hyp:
        leg, hyp = generate_hypotenuse_and_leg()

    is_congruent = random.choice([True, False])

    question_text = ""
    correct_answer_str = ""

    if is_congruent:
        # Congruent:
        question_text = (
            f"已知在直角 $\\triangle ABC$ 中 ($\\angle B=90\\circ$)，斜邊 $\\overline{{AC}}={hyp}$，一股 $\\overline{{AB}}={leg}$；"
            f"在直角 $\\triangle DEF$ 中 ($\\angle E=90\\circ$)，斜邊 $\\overline{{DF}}={hyp}$，一股 $\\overline{{DE}}={leg}$。"
            f"<br>請問 $\\triangle ABC$ 和 $\\triangle DEF$ 是否全等？若是，請說明是根據哪一個全等性質。"
        )
        correct_answer_str = "是, RHS"
    else:
        # Not congruent:
        choice = random.choice(['mismatch_hyp', 'mismatch_leg', 'non_right_angle_ssa_like'])

        if choice == 'mismatch_hyp':
            hyp_prime = hyp + random.choice([-1, 1])
            while hyp_prime <= leg: # Hypotenuse must still be longer than leg
                hyp_prime = hyp + random.choice([-2, -1, 1, 2])
                if hyp_prime <= leg: hyp_prime = leg + 1 # Fallback
            
            question_text = (
                f"已知在直角 $\\triangle ABC$ 中 ($\\angle B=90\\circ$)，斜邊 $\\overline{{AC}}={hyp}$，一股 $\\overline{{AB}}={leg}$；"
                f"在直角 $\\triangle DEF$ 中 ($\\angle E=90\\circ$)，斜邊 $\\overline{{DF}}={hyp_prime}$，一股 $\\overline{{DE}}={leg}$。"
                f"<br>請問 $\\triangle ABC$ 和 $\\triangle DEF$ 是否全等？若是，請說明是根據哪一個全等性質。"
            )
        elif choice == 'mismatch_leg':
            leg_prime = leg + random.choice([-1, 1])
            while leg_prime >= hyp or leg_prime < 1: # Leg must be shorter than hypotenuse
                leg_prime = leg + random.choice([-2, -1, 1, 2])
                if leg_prime >= hyp: leg_prime = hyp - 1 # Fallback
                if leg_prime < 1: leg_prime = 1 # Fallback

            question_text = (
                f"已知在直角 $\\triangle ABC$ 中 ($\\angle B=90\\circ$)，斜邊 $\\overline{{AC}}={hyp}$，一股 $\\overline{{AB}}={leg}$；"
                f"在直角 $\\triangle DEF$ 中 ($\\angle E=90\\circ$)，斜邊 $\\overline{{DF}}={hyp}$，一股 $\\overline{{DE}}={leg_prime}$。"
                f"<br>請問 $\\triangle ABC$ 和 $\\triangle DEF$ 是否全等？若是，請說明是根據哪一個全等性質。"
            )
        else: # non_right_angle_ssa_like: Present SSA conditions, which is not RHS nor a congruence
            # Example: AB=leg, AC=hyp, angle C=some_angle (SSA)
            angle_c = generate_angle(min_val=30, max_val=80)
            
            question_text = (
                f"已知在 $\\triangle ABC$ 中，$\\overline{{AB}}={leg}$，$\\overline{{AC}}={hyp}$，$\\angle C={angle_c}\\circ$；"
                f"在 $\\triangle DEF$ 中，$\\overline{{DE}}={leg}$，$\\overline{{DF}}={hyp}$，$\\angle F={angle_c}\\circ$。"
                f"<br>請問 $\\triangle ABC$ 和 $\\triangle DEF$ 是否全等？若是，請說明是根據哪一個全等性質。"
            )
        correct_answer_str = "否"

    return {
        "question_text": question_text,
        "answer": correct_answer_str,
        "correct_answer": correct_answer_str
    }

def generate_asa_problem():
    angle1 = generate_angle(min_val=30, max_val=70)
    angle2 = generate_angle(min_val=30, max_val=70)
    # Ensure sum of angles for third angle to be positive
    while angle1 + angle2 >= 150: 
        angle1 = generate_angle(min_val=30, max_val=70)
        angle2 = generate_angle(min_val=30, max_val=70)
    
    side = generate_side_length()

    is_congruent = random.choice([True, False])

    question_text = ""
    correct_answer_str = ""

    if is_congruent:
        # Congruent: Angle A, Side AB, Angle B (included side)
        question_text = (
            f"已知在 $\\triangle ABC$ 中，$\\angle A={angle1}\\circ$，$\\overline{{AB}}={side}$，$\\angle B={angle2}\\circ$；"
            f"在 $\\triangle DEF$ 中，$\\angle D={angle1}\\circ$，$\\overline{{DE}}={side}$，$\\angle E={angle2}\\circ$。"
            f"<br>請問 $\\triangle ABC$ 和 $\\triangle DEF$ 是否全等？若是，請說明是根據哪一個全等性質。"
        )
        correct_answer_str = "是, ASA"
    else:
        # Not congruent:
        choice = random.choice(['mismatch_angle', 'mismatch_side', 'aas_mismatch'])

        if choice == 'mismatch_angle':
            angle1_prime = angle1 + random.choice([-5, 5])
            while angle1_prime <= 0 or angle1_prime + angle2 >= 170: # Ensure valid angle
                angle1_prime = angle1 + random.choice([-10, -5, 5, 10])
            
            question_text = (
                f"已知在 $\\triangle ABC$ 中，$\\angle A={angle1}\\circ$，$\\overline{{AB}}={side}$，$\\angle B={angle2}\\circ$；"
                f"在 $\\triangle DEF$ 中，$\\angle D={angle1_prime}\\circ$，$\\overline{{DE}}={side}$，$\\angle E={angle2}\\circ$。"
                f"<br>請問 $\\triangle ABC$ 和 $\\triangle DEF$ 是否全等？若是，請說明是根據哪一個全等性質。"
            )
        elif choice == 'mismatch_side':
            side_prime = side + random.choice([-1, 1])
            while side_prime < 1: side_prime = 1
            question_text = (
                f"已知在 $\\triangle ABC$ 中，$\\angle A={angle1}\\circ$，$\\overline{{AB}}={side}$，$\\angle B={angle2}\\circ$；"
                f"在 $\\triangle DEF$ 中，$\\angle D={angle1}\\circ$，$\\overline{{DE}}={side_prime}$，$\\angle E={angle2}\\circ$。"
                f"<br>請問 $\\triangle ABC$ 和 $\\triangle DEF$ 是否全等？若是，請說明是根據哪一個全等性質。"
            )
        else: # aas_mismatch: Present AAS conditions, but with a mismatch, so not congruent
            # For ABC: Angle A, Angle B, Side AC (AAS configuration)
            # For DEF: Angle D, Angle E, Side DF (AAS configuration)
            side_ac = generate_side_length()
            side_df_prime = side_ac + random.choice([-1, 1])
            while side_df_prime < 1 or side_df_prime == side_ac:
                side_df_prime = side_ac + random.choice([-2, -1, 1, 2])
                if side_df_prime < 1: side_df_prime = 1 # Fallback

            question_text = (
                f"已知在 $\\triangle ABC$ 中，$\\angle A={angle1}\\circ$，$\\angle B={angle2}\\circ$，$\\overline{{AC}}={side_ac}$；"
                f"在 $\\triangle DEF$ 中，$\\angle D={angle1}\\circ$，$\\angle E={angle2}\\circ$，$\\overline{{DF}}={side_df_prime}$。"
                f"<br>請問 $\\triangle ABC$ 和 $\\triangle DEF$ 是否全等？若是，請說明是根據哪一個全等性質。"
            )
        correct_answer_str = "否"

    return {
        "question_text": question_text,
        "answer": correct_answer_str,
        "correct_answer": correct_answer_str
    }

def generate_aas_problem():
    angle1 = generate_angle(min_val=30, max_val=70)
    angle2 = generate_angle(min_val=30, max_val=70)
    while angle1 + angle2 >= 150: # Leave room for 3rd angle
        angle1 = generate_angle(min_val=30, max_val=70)
        angle2 = generate_angle(min_val=30, max_val=70)
    
    side = generate_side_length() # This will be a non-included side

    is_congruent = random.choice([True, False])

    question_text = ""
    correct_answer_str = ""
    
    # AAS: Angle-Angle-Side (side not included)
    # Example: Angle A, Angle B, Side BC (opposite Angle A, not included by A and B)
    
    if is_congruent:
        # Congruent:
        question_text = (
            f"已知在 $\\triangle ABC$ 中，$\\angle A={angle1}\\circ$，$\\angle B={angle2}\\circ$，$\\overline{{BC}}={side}$；"
            f"在 $\\triangle DEF$ 中，$\\angle D={angle1}\\circ$，$\\angle E={angle2}\\circ$，$\\overline{{EF}}={side}$。"
            f"<br>請問 $\\triangle ABC$ 和 $\\triangle DEF$ 是否全等？若是，請說明是根據哪一個全等性質。"
        )
        correct_answer_str = "是, AAS"
    else:
        # Not congruent:
        choice = random.choice(['mismatch_angle', 'mismatch_side', 'aaa_like'])

        if choice == 'mismatch_angle':
            angle1_prime = angle1 + random.choice([-5, 5])
            while angle1_prime <= 0 or angle1_prime + angle2 >= 170:
                angle1_prime = angle1 + random.choice([-10, -5, 5, 10])
            
            question_text = (
                f"已知在 $\\triangle ABC$ 中，$\\angle A={angle1}\\circ$，$\\angle B={angle2}\\circ$，$\\overline{{BC}}={side}$；"
                f"在 $\\triangle DEF$ 中，$\\angle D={angle1_prime}\\circ$，$\\angle E={angle2}\\circ$，$\\overline{{EF}}={side}$。"
                f"<br>請問 $\\triangle ABC$ 和 $\\triangle DEF$ 是否全等？若是，請說明是根據哪一個全等性質。"
            )
        elif choice == 'mismatch_side':
            side_prime = side + random.choice([-1, 1])
            while side_prime < 1: side_prime = 1
            question_text = (
                f"已知在 $\\triangle ABC$ 中，$\\angle A={angle1}\\circ$，$\\angle B={angle2}\\circ$，$\\overline{{BC}}={side}$；"
                f"在 $\\triangle DEF$ 中，$\\angle D={angle1}\\circ$，$\\angle E={angle2}\\circ$，$\\overline{{EF}}={side_prime}$。"
                f"<br>請問 $\\triangle ABC$ 和 $\\triangle DEF$ 是否全等？若是，請說明是根據哪一個全等性質。"
            )
        else: # aaa_like (Angle-Angle-Angle implies similarity, not congruence)
            angle3 = 180 - angle1 - angle2
            
            question_text = (
                f"已知在 $\\triangle ABC$ 中，$\\angle A={angle1}\\circ$，$\\angle B={angle2}\\circ$，$\\angle C={angle3}\\circ$；"
                f"在 $\\triangle DEF$ 中，$\\angle D={angle1}\\circ$，$\\angle E={angle2}\\circ$，$\\angle F={angle3}\\circ$。"
                f"<br>請問 $\\triangle ABC$ 和 $\\triangle DEF$ 是否全等？若是，請說明是根據哪一個全等性質。"
            )
        correct_answer_str = "否"

    return {
        "question_text": question_text,
        "answer": correct_answer_str,
        "correct_answer": correct_answer_str
    }

def generate(level=1):
    """
    生成「三角形全等性質」相關題目。
    包含：
    SSS、SAS、RHS、ASA、AAS 等不同全等性質。
    """
    problem_type = random.choice(['SSS', 'SAS', 'RHS', 'ASA', 'AAS'])
    
    if problem_type == 'SSS':
        return generate_sss_problem()
    elif problem_type == 'SAS':
        return generate_sas_problem()
    elif problem_type == 'RHS':
        return generate_rhs_problem()
    elif problem_type == 'ASA':
        return generate_asa_problem()
    elif problem_type == 'AAS':
        return generate_aas_problem()
    else: # Fallback, should not be reached with random.choice above
        return generate_sss_problem()

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    user_answer 預期格式: "是, SSS", "否", "YES, SAS", "No", "SSS" 等
    """
    # Normalize user answer: remove spaces, convert to uppercase, normalize Chinese comma
    user_answer_normalized = user_answer.strip().upper().replace('，', ',').replace(' ', '')
    # Normalize correct answer:
    correct_answer_normalized = correct_answer.strip().upper().replace('，', ',').replace(' ', '')

    is_correct = False
    feedback_message = ""

    if correct_answer_normalized == "否":
        # Accept "否", "NO", "N"
        if user_answer_normalized in ["否", "NO", "N"]:
            is_correct = True
            feedback_message = f"完全正確！答案是 {correct_answer_normalized}。"
        else:
            feedback_message = f"答案不正確。正確答案應為：{correct_answer_normalized}"
    elif correct_answer_normalized.startswith("是,"):
        # Correct answer is like "是,SSS"
        property_part = correct_answer_normalized.split(',')[1] # e.g., "SSS"
        
        # Accept "是,SSS", "YES,SSS", or just "SSS"
        if user_answer_normalized == correct_answer_normalized or \
           user_answer_normalized == f"YES,{property_part}" or \
           user_answer_normalized == property_part:
            is_correct = True
            feedback_message = f"完全正確！答案是 {correct_answer_normalized}。"
        else:
            feedback_message = f"答案不正確。正確答案應為：{correct_answer_normalized}"
    else: # Fallback for unexpected correct_answer formats (should not happen based on generate)
        if user_answer_normalized == correct_answer_normalized:
            is_correct = True
            feedback_message = f"完全正確！答案是 {correct_answer_normalized}。"
        else:
            feedback_message = f"答案不正確。正確答案應為：{correct_answer_normalized}"

    return {"correct": is_correct, "result": feedback_message, "next_question": True}