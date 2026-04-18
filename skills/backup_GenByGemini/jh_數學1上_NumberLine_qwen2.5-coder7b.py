import random

def generate(level=1):
    """
    生成「數線」相關題目 (標準 LaTeX 範本)。
    包含：
    1. 相對位置
    2. 座標大小比較
    3. 中點座標
    4. 數線讀值
    """
    problem_type = random.choice(['relative_pos', 'comparison', 'midpoint', 'ascii_read'])
    
    if problem_type == 'relative_pos':
        return generate_relative_pos_problem()
    elif problem_type == 'comparison':
        return generate_comparison_problem()
    elif problem_type == 'midpoint':
        return generate_midpoint_problem()
    else:
        return generate_ascii_read_problem()

def generate_relative_pos_problem():
    # 題型：數線上 A 點座標為 val_a，B 點在 A 點的 [方向] val_diff 單位處
    val_a = random.randint(-10, 10)
    val_diff = random.randint(1, 10)
    direction = random.choice(['右', '左'])
    
    if direction == '右':
        val_b = val_a + val_diff
        op_str = "+"
    else:
        val_b = val_a - val_diff
        op_str = "-"
        
    # [教學示範] 注意：數學符號與數字都用 $ 包裹
    question_text = f"數線上 $A$ 點座標為 ${val_a}$，$B$ 點在 $A$ 點的{direction}邊 {val_diff} 單位處，請問 $B$ 點座標為何？"
    correct_answer = str(val_b)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_comparison_problem():
    # 題型：已知 A(a), B(b), C(c)...
    points = {}
    labels = ['A', 'B', 'C', 'D']
    num_points = random.choice([3, 4])
    used_labels = labels[:num_points]
    
    coords = sorted(random.sample(range(-20, 21), num_points))
    
    points_desc = []
    for i, label in enumerate(used_labels):
        points[label] = coords[i]
        # [教學示範] 座標表示法：$A(-5)$
        points_desc.append(f"${label}({coords[i]})$")
        
    target = random.choice(['右', '左'])
    
    if target == '右':
        correct_label = max(points.keys())
    else:
        correct_label = min(points.keys())
    
    question_text = f"比較下列各點的座標，哪個點的位置最 {target}？{', '.join(points_desc)}"
    correct_answer = str(points[correct_label])
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_midpoint_problem():
    # 題型：中點座標計算
    point1 = random.randint(-10, 10)
    point2 = random.randint(point1 + 1, 10)
    
    midpoint = (point1 + point2) / 2
    
    question_text = f"求點 $A({point1})$ 和點 $B({point2})$ 的中點座標。"
    correct_answer = str(midpoint)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_ascii_read_problem():
    # 題型：數線讀值
    start = random.randint(-10, -5)
    end = random.randint(start + 5, 5)
    
    points = [start + i for i in range(6)]
    
    ascii_art = " ".join([f"{point}" if point >= 0 else f" {point} " for point in points])
    question_text = f"根據數線上的標記，請回答下列問題：{ascii_art}"
    correct_answer = str(random.choice(points))
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip().upper()
    correct_answer = correct_answer.strip().upper()
    
    is_correct = (user_answer == correct_answer)
    
    if not is_correct:
        try:
            if float(user_answer) == float(correct_answer):
                is_correct = True
        except ValueError:
            pass

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}