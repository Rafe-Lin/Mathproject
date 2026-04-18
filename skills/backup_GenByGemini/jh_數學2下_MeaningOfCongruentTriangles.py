import random

def generate(level=1):
    """
    生成「全等三角形的意義」相關題目。
    包含：
    1. 從已知的邊長求對應邊長。
    2. 從已知的角度求對應角或利用三角形內角和求其他角。
    """
    problem_type = random.choice(['find_sides', 'find_angles'])
    
    if problem_type == 'find_sides':
        return generate_find_sides_problem()
    else: # find_angles
        return generate_find_angles_problem()

def generate_find_sides_problem():
    """
    題型：已知△ABC ≅ △PQR，給定部分邊長，求指定邊長。
    """
    # 設定頂點名稱
    v1_labels = ['A', 'B', 'C']
    v2_labels = ['P', 'Q', 'R']
    
    # 隨機對應關係
    shuffled_v2_labels = random.sample(v2_labels, 3)
    
    # 產生符合三角形邊長不等式的邊長
    s1 = random.randint(3, 15)
    s2 = random.randint(3, 15)
    # 確保 s3 滿足 a+b > c, a+c > b, b+c > a
    s3 = random.randint(abs(s1 - s2) + 1, s1 + s2 - 1)
    side_values = [s1, s2, s3]
    random.shuffle(side_values)
    
    # 建立邊與邊長的對應字典
    # △ABC 的邊
    abc_sides = [v1_labels[0]+v1_labels[1], v1_labels[1]+v1_labels[2], v1_labels[2]+v1_labels[0]]
    # △PQR 的對應邊
    pqr_sides = [shuffled_v2_labels[0]+shuffled_v2_labels[1], shuffled_v2_labels[1]+shuffled_v2_labels[2], shuffled_v2_labels[2]+shuffled_v2_labels[0]]
    
    all_sides_map = {}
    for i in range(3):
        all_sides_map[abc_sides[i]] = side_values[i]
        all_sides_map[pqr_sides[i]] = side_values[i]
        
    # 從 6 個邊中隨機選 3 個，2 個當已知，1 個當所求
    all_side_labels = list(all_sides_map.keys())
    selected_labels = random.sample(all_side_labels, 3)
    
    given1_label, given2_label, target_label = selected_labels
    
    # 產生題目文字
    congruence_statement = f"$\\triangle {v1_labels[0]}{v1_labels[1]}{v1_labels[2]} \\cong \\triangle {shuffled_v2_labels[0]}{shuffled_v2_labels[1]}{shuffled_v2_labels[2]}$"
    question_text = (
        f"已知 {congruence_statement}，其中 A、B、C 的對應頂點分別為 {shuffled_v2_labels[0]}、{shuffled_v2_labels[1]}、{shuffled_v2_labels[2]}。<br>"
        f"如果 $\\overline{{{given1_label}}} = {all_sides_map[given1_label]}$，"
        f"$\\overline{{{given2_label}}} = {all_sides_map[given2_label]}$，"
        f"則 $\\overline{{{target_label}}}$ 的長度為多少？"
    )
    
    correct_answer = str(all_sides_map[target_label])
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_find_angles_problem():
    """
    題型：已知△ABC ≅ △DEF，給定部分角度，求指定角度。
    """
    # 設定頂點名稱
    v1_labels = ['A', 'B', 'C']
    v2_labels = ['D', 'E', 'F']
    
    # 隨機對應關係
    shuffled_v2_labels = random.sample(v2_labels, 3)
    
    # 產生三角形的三個內角
    a1 = random.randint(20, 80)
    a2 = random.randint(20, 160 - a1)
    a3 = 180 - a1 - a2
    angle_values = [a1, a2, a3]
    random.shuffle(angle_values)
    
    # 建立頂點與角度的對應字典
    all_angles_map = {}
    for i in range(3):
        all_angles_map[v1_labels[i]] = angle_values[i]
        all_angles_map[shuffled_v2_labels[i]] = angle_values[i]
        
    # 從 6 個角中隨機選 2 個不為對應角的角當作已知
    # 1. 隨機選一個 ABC 中的角
    given_v1 = random.choice(v1_labels)
    # 2. 找出它在 DEF 中的對應角
    corresponding_v2 = shuffled_v2_labels[v1_labels.index(given_v1)]
    # 3. 從 DEF 中剩下的兩個角選一個當作第二個已知角
    possible_given_v2 = [v for v in v2_labels if v != corresponding_v2]
    given_v2 = random.choice(possible_given_v2)
    
    # 從剩下的 4 個未知角中，隨機選 1 個當作所求
    known_vertices = [given_v1, given_v2]
    all_vertices = v1_labels + v2_labels
    unknown_vertices = [v for v in all_vertices if v not in known_vertices]
    target_vertex = random.choice(unknown_vertices)
    
    # 產生題目文字
    congruence_statement = f"$\\triangle {v1_labels[0]}{v1_labels[1]}{v1_labels[2]} \\cong \\triangle {shuffled_v2_labels[0]}{shuffled_v2_labels[1]}{shuffled_v2_labels[2]}$"
    question_text = (
        f"已知 {congruence_statement}，其中 A、B、C 的對應頂點分別為 {shuffled_v2_labels[0]}、{shuffled_v2_labels[1]}、{shuffled_v2_labels[2]}。<br>"
        f"若 $\\angle {given_v1} = {all_angles_map[given_v1]}^\\circ$，"
        f"$\\angle {given_v2} = {all_angles_map[given_v2]}^\\circ$，"
        f"則 $\\angle {target_vertex}$ 為多少度？"
    )

    correct_answer = str(all_angles_map[target_vertex])
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    # 移除答案中可能包含的度數符號 (°) 或單位 (度)
    user_answer = user_answer.strip().replace('°', '').replace('度', '')
    correct_answer = correct_answer.strip()
    
    is_correct = (user_answer == correct_answer)
    
    if not is_correct:
        try:
            # 為了穩健性，檢查浮點數是否相等
            if float(user_answer) == float(correct_answer):
                is_correct = True
        except (ValueError, TypeError):
            pass

    if is_correct:
        result_text = f"完全正確！答案是 ${correct_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer}$。"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}