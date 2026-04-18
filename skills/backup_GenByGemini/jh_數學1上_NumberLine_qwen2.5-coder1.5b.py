import random
from fractions import Fraction

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
    direction = random.choice(['左', '右'])
    
    if direction == '右':
        val_b = val_a + val_diff
        op_str = "+"
    else:
        val_b = val_a - val_diff
        op_str = "-"
        
    # [教學示範] 注意：數學符號與數字都用 $ 包裹
    # 這裡示範了如何正確嵌入變數： ${val_a}$
    question_text = f"數線上 $A$ 點座標為 ${val_a}$，$B$ 點在 $A$ 點的{direction}邊 ${val_diff}$ 單位處，請問 $B$ 點座標為何？"
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
    
    coords = random.sample(range(-20, 21), num_points)
    
    points_desc = []
    for i, label in enumerate(used_labels):
        points[label] = coords[i]
        # [教學示範] 座標表示法：$A(-5)$
        # 同時示範了如何在 f-strings 中使用变量
        points_desc.append(f"{label}: {coords[i]}")
    
    question_text = "已知以下點的座標，請比較它们的大小:"
    for i, point in enumerate(points_desc):
        question_text += f"<br>{point}"
    
    correct_answer = str(coords[0])  # Assuming the first point is the smallest
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_midpoint_problem():
    # 題型：已知 A(x1, y1) 和 B(x2, y2)，請計算其中點的座標 (x_m, y_m)
    x1, y1 = random.randint(-10, 10), random.randint(-10, 10)
    x2, y2 = random.randint(-10, 10), random.randint(-10, 10)
    
    question_text = f"已知點 A({x1}, {y1}) 和 B({x2}, {y2})，請計算其中點的座標 (x_m, y_m)："
    correct_answer = f"x_m: {(x1 + x2) / 2}, y_m: {(y1 + y2) / 2}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_ascii_read_problem():
    # 題型：已知以下點的座標，請計算其中點的座標 (x_m, y_m)
    x1, y1 = random.randint(-10, 10), random.randint(-10, 10)
    x2, y2 = random.randint(-10, 10), random.randint(-10, 10)
    
    question_text = f"已知點 A({x1}, {y1}) 和 B({x2}, {y2})，請計算其中點的座標 (x_m, y_m)："
    correct_answer = f"x_m: {(x1 + x2) / 2}, y_m: {(y1 + y2) / 2}"
    
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

    # [教學示範] 回傳結果中也可以包含 LaTeX
    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}