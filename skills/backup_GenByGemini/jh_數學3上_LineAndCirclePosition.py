import random
import uuid
from fractions import Fraction
import re

def generate(level=1):
    """
    生成「直線與圓的位置關係」相關題目。
    包含：
    1. 已知半徑與距離，判斷關係。
    2. 已知半徑與關係，選出可能的距離。
    3. 平行線與圓的綜合問題。
    """
    problem_type = random.choice(['find_relationship', 'find_distance', 'parallel_lines'])
    
    if problem_type == 'find_relationship':
        return generate_find_relationship_problem()
    elif problem_type == 'find_distance':
        return generate_find_distance_problem()
    else: # 'parallel_lines'
        return generate_parallel_lines_problem()

def generate_find_relationship_problem():
    """
    題型：已知半徑與多條直線的距離，判斷其關係或交點數。
    參考例題 2。
    """
    # 1. 生成圓的半徑
    use_diameter = random.choice([True, False])
    radius = random.randint(5, 15)
    if use_diameter:
        diameter = radius * 2
        radius_info = f"直徑為 ${diameter}$ 公分"
    else:
        radius_info = f"半徑為 ${radius}$ 公分"

    # 2. 生成不同關係的距離
    all_distances = set()
    # d < r (割線)
    d_secant = round(random.uniform(1, radius - 1), 1)
    if d_secant == int(d_secant): d_secant = int(d_secant)
    all_distances.add(d_secant)
    # d = r (切線)
    d_tangent = radius
    all_distances.add(d_tangent)
    # d > r (不相交)
    d_no_intersect = round(random.uniform(radius + 1, radius + 10), 1)
    if d_no_intersect == int(d_no_intersect): d_no_intersect = int(d_no_intersect)
    all_distances.add(d_no_intersect)

    # 3. 創建直線與距離的組合
    # Add a fourth line for variety, ensuring it's unique
    while len(all_distances) < 4:
        extra_choice = random.choice(['secant', 'no_intersect'])
        if extra_choice == 'secant':
            d_extra = round(random.uniform(1, radius - 1), 1)
            if d_extra == int(d_extra): d_extra = int(d_extra)
        else: # no_intersect
            d_extra = round(random.uniform(radius + 1, radius + 10), 1)
            if d_extra == int(d_extra): d_extra = int(d_extra)
        all_distances.add(d_extra)
            
    distances = list(all_distances)
    random.shuffle(distances)

    line_labels = ['L', 'M', 'N', 'H']
    line_data = dict(zip(line_labels, distances))

    # 4. 構建問題
    distances_str = "、".join([str(d) for d in distances])
    question_part1 = f"已知圓 $O$ 的{radius_info}，而圓心 $O$ 到四條直線 $L$、$M$、$N$、$H$ 的距離分別為 ${distances_str}$ 公分。"
    
    # 5. 決定要問什麼
    question_type = random.choice(['ask_tangent', 'ask_secant', 'ask_no_intersect', 'ask_intersections'])
    
    correct_answers = []
    if question_type == 'ask_tangent':
        question_text = f"{question_part1}<br>請問哪一條直線是圓 $O$ 的切線？"
        for label, d in line_data.items():
            if d == radius:
                correct_answers.append(label)
    elif question_type == 'ask_secant':
        question_text = f"{question_part1}<br>請問哪幾條直線是圓 $O$ 的割線？"
        for label, d in line_data.items():
            if d < radius:
                correct_answers.append(label)
    elif question_type == 'ask_no_intersect':
        question_text = f"{question_part1}<br>請問哪幾條直線與圓 $O$ 不相交？"
        for label, d in line_data.items():
            if d > radius:
                correct_answers.append(label)
    else: # ask_intersections
        target_line = random.choice(line_labels)
        target_dist = line_data[target_line]
        question_text = f"{question_part1}<br>請問直線 ${target_line}$ 和圓 $O$ 有幾個交點？"
        if target_dist < radius:
            correct_answers.append('2')
        elif target_dist == radius:
            correct_answers.append('1')
        else: # d > r
            correct_answers.append('0')

    correct_answer = ", ".join(sorted(correct_answers))

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_find_distance_problem():
    """
    題型：已知半徑與關係，從選項中選出可能的距離。
    參考例題 1。
    """
    # 1. 生成圓的半徑
    radius = random.randint(5, 20)
    
    # 2. 隨機選擇一種關係
    relationship_map = {
        '不相交': 'd > r',
        '相切': 'd = r',
        '相交於兩點': 'd < r'
    }
    relationship_text = random.choice(list(relationship_map.keys()))
    condition = relationship_map[relationship_text]

    # 3. 生成選項
    options = set()
    correct_options_labels = []
    
    # Add the tangent case as a guaranteed option
    options.add(radius)
    
    # Add some secant cases
    for _ in range(2):
        d = random.randint(1, radius - 1)
        options.add(d)

    # Add some no-intersection cases
    for _ in range(2):
        d = random.randint(radius + 1, radius + 20)
        options.add(d)
        
    # Ensure we have at least 4 unique options, regenerate if needed
    while len(options) < 4:
        options.add(random.randint(1, radius + 20))
        
    option_list = sorted(list(options))
    if len(option_list) > 5:
        option_list = random.sample(option_list, 5)
        option_list.sort()

    option_labels = ['A', 'B', 'C', 'D', 'E']
    
    # 4. 構建問題和答案
    question_text = f"已知圓 $O$ 的半徑為 ${radius}$ 公分，直線 $M$ 和圓 $O$ {relationship_text}，則圓心 $O$ 到直線 $M$ 的距離可能是下列哪些選項？"
    
    options_str_parts = []
    for i, val in enumerate(option_list):
        label = option_labels[i]
        options_str_parts.append(f"{label}) ${val}$ 公分")
        
        # Check if this option is correct
        is_correct = False
        if condition == 'd > r' and val > radius:
            is_correct = True
        elif condition == 'd = r' and val == radius:
            is_correct = True
        elif condition == 'd < r' and val < radius:
            is_correct = True
        
        if is_correct:
            correct_options_labels.append(label)
    
    question_text += "<br>" + " ".join(options_str_parts)
    
    # Ensure there is at least one correct answer
    if not correct_options_labels:
        # This case is very unlikely but good to handle. Let's regenerate.
        return generate_find_distance_problem()
        
    correct_answer = ", ".join(sorted(correct_options_labels))
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_parallel_lines_problem():
    """
    題型：給定一組平行線與圓，判斷各線與圓的關係。
    參考例題 3。
    """
    # 1. 設定平行線
    num_lines = 5
    line_labels = [f"L{i}" for i in range(1, num_lines + 1)] # L1, L2, ...
    
    # 2. 設定相鄰距離和圓心位置
    dist_adj = random.randint(1, 3)
    center_line_index = random.randint(1, num_lines - 2) # Center on L2, L3, or L4
    center_line_label = f"L{center_line_index + 1}"
    
    # 3. 設定半徑
    # Make radius a multiple of dist_adj to guarantee a tangent line
    radius_multiplier = random.randint(1, num_lines - 1 - center_line_index)
    radius = radius_multiplier * dist_adj
    if random.random() < 0.2:
        radius += dist_adj / 2.0
    if radius == int(radius): radius = int(radius)
    
    # 4. 構建問題
    question_part1 = f"有五條平行線，相鄰兩條平行線的距離皆為 ${dist_adj}$ 公分，由上至下依序為 $L1, L2, L3, L4, L5$。若圓心 $O$ 在直線 ${center_line_label}$ 上，並以半徑 ${radius}$ 公分畫圓，則："
    
    # 5. 計算各線的關係並選擇一個問題來問
    line_relations = {'no_intersect': [], 'tangent': [], 'secant': []}
    for i in range(num_lines):
        line_idx = i + 1
        dist_to_center = abs(line_idx - (center_line_index + 1)) * dist_adj
        
        if dist_to_center > radius:
            line_relations['no_intersect'].append(f"L{line_idx}")
        elif dist_to_center == radius:
            line_relations['tangent'].append(f"L{line_idx}")
        else: # dist_to_center < radius
            line_relations['secant'].append(f"L{line_idx}")

    # 6. 隨機選擇要問的問題類型
    possible_questions = [key for key, val in line_relations.items() if val]
    if not possible_questions:
        return generate_parallel_lines_problem()
        
    q_type = random.choice(possible_questions)
    
    if q_type == 'no_intersect':
        question_text = f"{question_part1}<br>哪些直線與圓 $O$ 不相交？"
        correct_answers = line_relations['no_intersect']
    elif q_type == 'tangent':
        question_text = f"{question_part1}<br>哪些直線是切線？"
        correct_answers = line_relations['tangent']
    else: # secant
        question_text = f"{question_part1}<br>哪些直線是割線？"
        correct_answers = line_relations['secant']
        
    correct_answer = ", ".join(sorted(correct_answers))

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。能處理單一答案、多重選項 (A,B)、多重標籤 (L1,L3)。
    """
    def normalize(ans_str):
        """Cleans up strings like "A, B", "L1,L3", "AB", "L1 L3" into a canonical form."""
        s = ans_str.strip().upper().replace(',', ' ').replace('_', '')
        
        # Pattern 1: L followed by digits (e.g., L1, L23)
        l_parts = re.findall(r'L\d+', s)
        if l_parts and ''.join(l_parts) == s.replace(' ', ''):
            return sorted(l_parts)
            
        # Pattern 2: Single capital letters (e.g., A, B)
        a_parts = re.findall(r'[A-Z]', s)
        if a_parts and ''.join(a_parts) == s.replace(' ', ''):
            return sorted(a_parts)
        
        # Default split for general cases or single numbers
        return sorted(s.split())

    user_ans_normalized = normalize(user_answer)
    correct_ans_normalized = normalize(correct_answer)
    
    # Handle empty user input
    if not user_ans_normalized:
        is_correct = False
    else:
        is_correct = (user_ans_normalized == correct_ans_normalized)

    # Fallback for simple numeric comparison for cases like "2" vs "2.0"
    if not is_correct and len(user_ans_normalized) == 1 and len(correct_ans_normalized) == 1:
        try:
            if float(user_ans_normalized[0]) == float(correct_ans_normalized[0]):
                is_correct = True
        except (ValueError, IndexError):
            pass

    if is_correct:
        result_text = f"完全正確！答案是 ${correct_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer}$。"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}