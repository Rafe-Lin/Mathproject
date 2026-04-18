import random
from fractions import Fraction

def generate(level=1):
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
    val_a = random.randint(-10, 10)
    val_diff = random.randint(1, 10)
    direction = random.choice(['左', '右'])
    
    if direction == '右':
        val_b = val_a + val_diff
        op_str = "+"
    else:
        val_b = val_a - val_diff
        op_str = "-"
        
    question_text = f"數線上 $A$ 點座標為 ${val_a}$，$B$ 點在 $A$ 點的{direction}邊 ${val_diff}$ 單位處，請問 $B$ 點座標為何？"
    correct_answer = str(val_b)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_comparison_problem():
    points = {}
    labels = ['A', 'B', 'C', 'D']
    num_points = random.choice([3, 4])
    used_labels = labels[:num_points]
    
    coords = random.sample(range(-20, 21), num_points)
    
    points_desc = []
    for i, label in enumerate(used_labels):
        points[label] = coords[i]
        points_desc.append(f"${label}({coords[i]})$")
        
    target = random.choice(['左', '右'])
    
    if target == '右':
        correct_label = max(points, key=points.get)
    else:
        correct_label = min(points, key=points.get)
        
    question_text = f"已知數線上 {', '.join(points_desc)}，請問哪一點在最{target}邊？(請填代號)"
    correct_answer = correct_label
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_midpoint_problem():
    val_a = random.randint(-15, 15)
    diff = random.randint(1, 10) * 2 
    
    if random.random() < 0.3:
        diff = random.randint(1, 10) * 2
    
    val_b = val_a + diff
    midpoint = (val_a + val_b) / 2
    
    question_text = f"已知 $A$ 點座標為 ${val_a}$，$B$ 點座標為 ${val_b}$，請問 $AB$ 的中點是何？"
    correct_answer = str(midpoint)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_ascii_read_problem():
    ascii_art = r"""
     _______
    |       |
    |   A  |
    |_______|
    """
    missing_value = random.randint(1, 5)
    
    question_text = f"{ascii_art}請問 $A$ 點的值是何？"
    correct_answer = str(missing_value)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
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