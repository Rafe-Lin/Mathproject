import random
from fractions import Fraction
import math

# --- Helper Functions ---
def get_coprime_pair(max_val=5):
    """Generates a pair of coprime integers (m, n) with n > m."""
    while True:
        m = random.randint(2, max_val)
        n = random.randint(m + 1, max_val + 2)
        if math.gcd(m, n) == 1:
            return m, n

def generate_aa_proof():
    """
    Generates a problem to determine similarity based on AA property from given angles.
    """
    is_similar = random.choice([True, False])
    
    # Generate angles for the first triangle
    a1 = random.randint(30, 80)
    a2 = random.randint(30, 80)
    while a1 + a2 >= 150: # Ensure the third angle is reasonably large
        a1 = random.randint(30, 80)
        a2 = random.randint(30, 80)
    a3 = 180 - a1 - a2
    
    angles_a = [a1, a2, a3]
    
    if is_similar:
        # For the second triangle, pick two angles from the same set
        angles_b_choices = random.sample(angles_a, 2)
        b1 = angles_b_choices[0]
        b2 = angles_b_choices[1]
        correct_answer = "是"
    else:
        # For a non-similar triangle, ensure angle sets are different
        # One angle might be the same to make it tricky
        b1 = random.choice(angles_a)
        b2 = random.randint(30, 80)
        # Ensure the new set of angles is different from the original
        while set(angles_a) == {b1, b2, 180 - b1 - b2} or b1 + b2 >= 150:
            b2 = random.randint(30, 80)
        correct_answer = "否"

    question_text = f"$\\triangle ABC$ 的其中兩個內角分別為 ${a1}^\\circ$ 與 ${a2}^\\circ$。<br>"
    question_text += f"$\\triangle DEF$ 的其中兩個內角分別為 ${b1}^\\circ$ 與 ${b2}^\\circ$。<br>"
    question_text += f"請問這兩個三角形是否相似？ (請填 是 或 否)"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_sas_proof():
    """
    Generates a problem to determine similarity based on SAS property.
    This is based on the nested triangle configuration.
    """
    is_similar = random.choice([True, False])
    
    # We need to find if △ADE ~ △ABC, which implies AD/AB = AE/AC
    # Or if △ADE ~ △ACB, which implies AD/AC = AE/AB
    # Let's generate for the second case (△ADE ~ △ACB), as in reference example 8.
    
    k_num = random.randint(3, 7)
    k_den = random.randint(2, k_num - 1)
    k = Fraction(k_num, k_den)

    # To ensure integer side lengths after division by k
    ac_base = random.randint(4, 8)
    ab_base = random.randint(4, 8)
    while ac_base == ab_base:
        ab_base = random.randint(4, 8)
        
    val_ac = ac_base * k_num
    val_ab = ab_base * k_num
    
    val_ad = ac_base * k_den
    val_ae = ab_base * k_den
    
    val_bd = val_ab - val_ad

    if not is_similar:
        # Mess up one ratio
        val_ae += random.choice([-2, -1, 1, 2])
        if val_ae <= 0: val_ae = 1 # Ensure side is positive
        correct_answer = "否"
    else:
        correct_answer = "是"

    question_text = f"如圖，D、E 兩點分別在 $\\overline{{AB}}$、$\\overline{{AC}}$ 上。"
    question_text += f"若 $\\overline{{AD}}={val_ad}$、$\\overline{{BD}}={val_bd}$、$\\overline{{AC}}={val_ac}$、$\\overline{{AE}}={val_ae}$，"
    question_text += f"請問 $\\triangle ADE$ 與 $\\triangle ABC$ 是否相似？ (請填 是 或 否)"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_sss_proof():
    """
    Generates a problem to determine similarity based on SSS property.
    """
    is_similar = random.choice([True, False])
    
    # Use Pythagorean triples for valid triangles
    base_triangles = [
        [3, 4, 5],
        [5, 12, 13],
        [8, 15, 17],
        [7, 24, 25]
    ]
    sides1 = random.choice(base_triangles)
    
    k = random.randint(2, 5)
    
    if is_similar:
        sides2 = [s * k for s in sides1]
        correct_answer = "是"
    else:
        sides2 = [s * k for s in sides1]
        # Alter one side to make it not similar
        idx_to_change = random.randint(0, 2)
        sides2[idx_to_change] += random.choice([-1, 1])
        # Ensure it's still a valid triangle
        sides2.sort()
        if sides2[0] + sides2[1] <= sides2[2]:
            sides2[idx_to_change] += 2 # Adjust to maintain triangle inequality
        correct_answer = "否"

    random.shuffle(sides1)
    random.shuffle(sides2)

    s1_str = ', '.join(map(str, sides1))
    s2_str = ', '.join(map(str, sides2))
    
    question_text = f"一個三角形的三邊長為 ${s1_str}$。<br>"
    question_text += f"另一個三角形的三邊長為 ${s2_str}$。<br>"
    question_text += f"請問這兩個三角形是否相似？ (請填 是 或 否)"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_application_calc():
    """
    Generates a problem that requires calculation based on a similarity property.
    Based on the reference example: △ABC ~ △DAC due to AA similarity.
    """
    m, n = get_coprime_pair(max_val=5)
    
    # Let AC = m*n and CD = m*m
    # From similarity CB/AC = AC/CD => CB = AC^2 / CD
    # CB = (m*n)^2 / (m*m) = (m^2 * n^2) / m^2 = n^2
    # Then BD = CB - CD = n^2 - m^2
    
    val_ac = m * n
    val_cd = m * m
    val_bd = n * n - m * m
    
    question_text = f"如圖，$\\triangle ABC$ 中，D 點在 $\\overline{{BC}}$ 上，"
    question_text += f"已知 $\\angle B = \\angle CAD$。若 $\\overline{{AC}} = {val_ac}$ "
    question_text += f"且 $\\overline{{CD}} = {val_cd}$，求 $\\overline{{BD}}$ 的長度。"
                        
    correct_answer = str(val_bd)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    生成「三角形相似性質」相關題目。
    - AA 相似性質判斷
    - SAS 相似性質判斷
    - SSS 相似性質判斷
    - 相似性質的應用計算
    """
    problem_type = random.choice(['aa_proof', 'sas_proof', 'sss_proof', 'application_calc'])
    
    if problem_type == 'aa_proof':
        return generate_aa_proof()
    elif problem_type == 'sas_proof':
        return generate_sas_proof()
    elif problem_type == 'sss_proof':
        return generate_sss_proof()
    else: # application_calc
        return generate_application_calc()

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip()
    correct_answer = str(correct_answer).strip()
    
    # Handle text-based answers (是/否) with synonyms
    is_correct = False
    positive_answers = ["是", "相似"]
    negative_answers = ["否", "不相似"]

    if correct_answer in positive_answers:
        if user_answer in positive_answers:
            is_correct = True
    elif correct_answer in negative_answers:
        if user_answer in negative_answers:
            is_correct = True
    
    # Handle numerical answers
    if not is_correct:
        try:
            # Use Fraction to handle decimals and fractions correctly
            if Fraction(user_answer) == Fraction(correct_answer):
                is_correct = True
        except (ValueError, ZeroDivisionError, TypeError):
            pass # Keep is_correct as False

    if is_correct:
        result_text = f"完全正確！"
        if correct_answer in positive_answers or correct_answer in negative_answers:
            result_text += f" 正確答案是「{correct_answer}」。"
        else:
             result_text += f" 答案是 ${correct_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為「{correct_answer}」。"
        # Format if the answer is numerical
        try:
            float(correct_answer)
            result_text = f"答案不正確。正確答案應為：${correct_answer}$"
        except (ValueError, TypeError):
            pass

    return {"correct": is_correct, "result": result_text, "next_question": True}