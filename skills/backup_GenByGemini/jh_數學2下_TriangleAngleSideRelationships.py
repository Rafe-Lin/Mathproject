import random
import math

def generate(level=1):
    """
    生成「三角形邊角關係」相關題目。
    包含：
    1. 給定兩邊長，比較對應兩角大小。
    2. 給定兩角大小，比較對應兩邊長。
    3. 等腰三角形特性與邊角比較。
    4. 綜合比較題 (如已知最長/最短邊)。
    """
    problem_type = random.choice([
        'side_to_angle_comparison',
        'angle_to_side_comparison',
        'isosceles_triangle_comparison',
        'combined_comparison'
    ])
    
    if problem_type == 'side_to_angle_comparison':
        return generate_side_to_angle_comparison()
    elif problem_type == 'angle_to_side_comparison':
        return generate_angle_to_side_comparison()
    elif problem_type == 'isosceles_triangle_comparison':
        return generate_isosceles_triangle_comparison()
    else: # combined_comparison
        return generate_combined_comparison()

def generate_side_to_angle_comparison():
    """
    題目類型：給定兩邊長，比較對應兩角大小。
    """
    side1_len = random.randint(10, 25)
    
    # 決定第二邊長 (80%機率不同，20%機率相同)
    if random.random() < 0.8:
        side2_len = random.randint(10, 25)
        while side2_len == side1_len:
            side2_len = random.randint(10, 25)
    else:
        side2_len = side1_len

    # 隨機分配長度給 AB 和 AC
    if random.random() < 0.5:
        ab_len = side1_len
        ac_len = side2_len
    else:
        ab_len = side2_len
        ac_len = side1_len
    
    # 題目：比較角B 與 角C
    # 角B 對邊是 AC, 角C 對邊是 AB
    if ac_len > ab_len:
        correct_answer = ">"
    elif ac_len < ab_len:
        correct_answer = "<"
    else:
        correct_answer = "="

    # 使用雙反斜線 \\ 避免跳脫字元問題
    question_text = f"在 $\\triangle ABC$ 中，已知 $\\overline{{AB}} = {ab_len}$，$\\overline{{AC}} = {ac_len}$。<br>請問 $\\angle B$ 與 $\\angle C$ 的大小關係為何？<br>(請填入 '$>$'、'$<$' 或 '$=$')"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_angle_to_side_comparison():
    """
    題目類型：給定兩角大小，比較對應兩邊長。
    """
    angle_b = random.randint(30, 80)
    angle_c = random.randint(30, 80)
    
    # 確保兩角和 < 180 且盡量不相等
    while angle_b + angle_c >= 170 or angle_b == angle_c:
        angle_b = random.randint(30, 80)
        angle_c = random.randint(30, 80)
    
    # 題目：比較 AC 與 AB
    # AC 對角是 角B, AB 對角是 角C
    if angle_b > angle_c:
        correct_answer = ">"
    elif angle_b < angle_c:
        correct_answer = "<"
    else:
        correct_answer = "="

    question_text = f"在 $\\triangle ABC$ 中，已知 $\\angle B = {angle_b}^\\circ$，$\\angle C = {angle_c}^\\circ$。<br>請問 $\\overline{{AC}}$ 與 $\\overline{{AB}}$ 的大小關係為何？<br>(請填入 '$>$'、'$<$' 或 '$=$')"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_isosceles_triangle_comparison():
    """
    題目類型：等腰三角形特性與邊角比較。
    """
    # 假設 AB = AC (等腰)，則 角B = 角C
    angle_a = random.randint(40, 100)
    
    # 計算底角 (180 - 頂角) / 2
    angle_b_c = (180 - angle_a) / 2 

    choice = random.choice(['side_comparison', 'angle_comparison'])
    
    if choice == 'side_comparison':
        # 比較 AB (對角C) 與 BC (對角A)
        # 其實就是比較 角C 與 角A
        if angle_b_c > angle_a:
            correct_answer = ">"
        elif angle_b_c < angle_a:
            correct_answer = "<"
        else: # 正三角形
            correct_answer = "="
            
        question_text = f"在等腰三角形 $\\triangle ABC$ 中，已知 $\\overline{{AB}} = \\overline{{AC}}$ 且 $\\angle A = {angle_a}^\\circ$。<br>請問 $\\overline{{AB}}$ 與 $\\overline{{BC}}$ 的大小關係為何？<br>(請填入 '$>$'、'$<$' 或 '$=$')"
            
    else: # angle_comparison
        # 比較 角B 與 角A
        if angle_b_c > angle_a:
            correct_answer = ">"
        elif angle_b_c < angle_a:
            correct_answer = "<"
        else:
            correct_answer = "="

        question_text = f"在等腰三角形 $\\triangle ABC$ 中，已知 $\\overline{{AB}} = \\overline{{AC}}$ 且 $\\angle A = {angle_a}^\\circ$。<br>請問 $\\angle B$ 與 $\\angle A$ 的大小關係為何？<br>(請填入 '$>$'、'$<$' 或 '$=$')"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_combined_comparison():
    """
    題目類型：綜合比較題 (如已知最長/最短邊，推導角度)。
    """
    # 已知 AB = BC (角A = 角C)
    
    scenario = random.choice(['shortest', 'longest'])
    
    if scenario == 'shortest':
        # 若 AC 最短 -> 角B (對邊AC) 最小 -> 角B < 角C
        question_text = f"在 $\\triangle ABC$ 中，已知 $\\overline{{AB}} = \\overline{{BC}}$。如果 $\\overline{{AC}}$ 是三角形中的最短邊，<br>請問 $\\angle B$ 與 $\\angle C$ 的大小關係為何？<br>(請填入 '$>$'、'$<$' 或 '$=$')"
        correct_answer = "<"
    else: 
        # 若 AC 最長 -> 角B (對邊AC) 最大 -> 角B > 角C
        question_text = f"在 $\\triangle ABC$ 中，已知 $\\overline{{AB}} = \\overline{{BC}}$。如果 $\\overline{{AC}}$ 是三角形中的最長邊，<br>請問 $\\angle B$ 與 $\\angle C$ 的大小關係為何？<br>(請填入 '$>$'、'$<$' 或 '$=$')"
        correct_answer = ">"
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = str(user_answer).strip()
    correct_answer = str(correct_answer).strip()
    
    is_correct = (user_answer == correct_answer)
    
    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}