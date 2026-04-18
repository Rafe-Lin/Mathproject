import random
import math

def generate(level=1):
    """
    生成「點與圓的位置關係」相關題目。
    包含：
    1. 判斷單點位置 (圓內、圓上、圓外)
    2. 比較點到圓心距離與半徑大小
    3. 從多個點中找出特定位置關係的點
    """
    problem_type = random.choice(['classify_single', 'compare_distance', 'classify_multiple'])
    
    if problem_type == 'classify_single':
        return _generate_classify_single_problem()
    elif problem_type == 'compare_distance':
        return _generate_compare_distance_problem()
    else: # 'classify_multiple'
        return _generate_classify_multiple_problem()

def _generate_circle_and_points(num_points=1):
    """
    內部輔助函式，用於生成一個圓和指定數量的點，並確定它們的位置關係。
    """
    center_h = random.randint(-5, 5)
    center_k = random.randint(-5, 5)
    
    # 使用畢氏三元數組來生成半徑和座標，確保「圓上」的點有整數解
    triples = [(3, 4, 5), (5, 12, 13), (6, 8, 10), (8, 15, 17), (7, 24, 25)]
    base_a, base_b, radius = random.choice(triples)
    
    r_squared = radius**2
    
    points = []
    
    # 為了在生成多個點時增加多樣性，預先定義好位置關係
    available_relations = ['in', 'on', 'out']
    random.shuffle(available_relations)
    
    for i in range(num_points):
        # 決定這個點的位置關係
        if num_points > 1:
            # 生成多點時，輪流使用不同關係
            relation_type = available_relations[i % len(available_relations)]
        else:
            # 生成單點時，隨機選取
            relation_type = random.choice(available_relations)

        # 根據所需的位置關係生成座標
        if relation_type == 'on':
            # 創建一個剛好在圓上的點
            dx, dy = random.choice([(base_a, base_b), (base_b, base_a)])
            px = center_h + dx * random.choice([-1, 1])
            py = center_k + dy * random.choice([-1, 1])
        elif relation_type == 'in':
            # 創建一個在圓內的點
            # 將距離圓心的 x, y 位移稍微縮短
            factor = random.uniform(0.5, 0.9)
            dx = int(base_a * factor)
            dy = int(base_b * factor)
            # 避免點剛好是圓心
            if dx == 0 and dy == 0: dx = 1
            px = center_h + dx * random.choice([-1, 1])
            py = center_k + dy * random.choice([-1, 1])
        else: # 'out'
            # 創建一個在圓外的點
            # 將距離圓心的 x, y 位移稍微拉長
            factor = random.uniform(1.1, 1.5)
            dx = int(base_a * factor)
            dy = int(base_b * factor)
            px = center_h + dx * random.choice([-1, 1])
            py = center_k + dy * random.choice([-1, 1])

        # 由於取整數可能導致位置關係改變，重新計算並確認
        dist_sq = (px - center_h)**2 + (py - center_k)**2
        if dist_sq < r_squared:
            actual_relation = 'in'
        elif dist_sq == r_squared:
            actual_relation = 'on'
        else:
            actual_relation = 'out'

        points.append({
            'coords': (px, py),
            'relation': actual_relation # 使用重新計算後的真實關係
        })
        
    circle_info = {
        'center': (center_h, center_k),
        'radius': radius
    }
    
    return circle_info, points

def _generate_classify_single_problem():
    """
    題型一：給定圓心、半徑和一點座標，判斷點在圓內、圓上或圓外。
    """
    circle_info, points = _generate_circle_and_points(num_points=1)
    
    center_h, center_k = circle_info['center']
    radius = circle_info['radius']
    point_px, point_py = points[0]['coords']
    relation = points[0]['relation']
    
    relation_map = {
        'in': '圓內',
        'on': '圓上',
        'out': '圓外'
    }
    correct_answer = relation_map[relation]

    question_text = (f"坐標平面上有一圓，圓心為 $O({center_h}, {center_k})$，半徑為 ${radius}$。"
                     f"請問點 $P({point_px}, {point_py})$ 的位置是在圓內、圓上、還是圓外？")
                     
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def _generate_compare_distance_problem():
    """
    題型二：給定圓心、半徑和一點座標，比較點到圓心距離與半徑的大小。
    """
    circle_info, points = _generate_circle_and_points(num_points=1)
    
    center_h, center_k = circle_info['center']
    radius = circle_info['radius']
    point_px, point_py = points[0]['coords']
    relation = points[0]['relation']
    
    relation_map = {
        'in': '<',
        'on': '=',
        'out': '>'
    }
    correct_answer = relation_map[relation]

    question_text = (f"坐標平面上有一圓，圓心為 $O({center_h}, {center_k})$，半徑 $r = {radius}$。"
                     f"若點 $P$ 的座標為 $({point_px}, {point_py})$，且其到圓心的距離為 $\\overline{{OP}}$，"
                     f"請比較 $\\overline{{OP}}$ 與 $r$ 的大小關係。(請填入 >、< 或 =)")
                     
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def _generate_classify_multiple_problem():
    """
    題型三：給定一個圓和多個點，找出符合特定位置關係的所有點。
    """
    while True:
        num_points = random.randint(3, 4)
        circle_info, points_data = _generate_circle_and_points(num_points=num_points)
        
        center_h, center_k = circle_info['center']
        radius = circle_info['radius']
        
        labels = ['A', 'B', 'C', 'D']
        
        points_desc = []
        for i in range(num_points):
            px, py = points_data[i]['coords']
            points_desc.append(f"${labels[i]}({px}, {py})$")
        
        relation_map = {
            'in': '圓內',
            'on': '圓上',
            'out': '圓外'
        }
        target_relation_key = random.choice(list(relation_map.keys()))
        target_relation_text = relation_map[target_relation_key]
        
        correct_labels = []
        for i in range(num_points):
            if points_data[i]['relation'] == target_relation_key:
                correct_labels.append(labels[i])
                
        # 確保題目至少有一個答案，若沒有則重新生成
        if correct_labels:
            break
            
    correct_labels.sort()
    correct_answer = ",".join(correct_labels)
    
    question_text = (f"坐標平面上有一圓，圓心為 $O({center_h}, {center_k})$，半徑為 ${radius}$。<br>"
                     f"平面上有數點：{', '.join(points_desc)}。<br>"
                     f"請問哪些點在{target_relation_text}？ (若有多點，請依字母順序以逗號分隔，例如 A,C)")
                     
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    def normalize(ans_str):
        # 標準化答案格式，以應對多點答案的順序和大小寫問題
        # e.g., " C, a " -> "A,C"
        # 也適用於單一答案，如 '圓內' or '>'
        parts = [p.strip().upper() for p in ans_str.split(',')]
        parts = [p for p in parts if p] # 移除因多餘逗號產生的空字串
        parts.sort()
        return ",".join(parts)

    user_ans_norm = normalize(user_answer)
    correct_ans_norm = normalize(correct_answer)
    
    is_correct = (user_ans_norm == correct_ans_norm)

    if is_correct:
        result_text = f"完全正確！答案是 ${correct_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer}$"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}