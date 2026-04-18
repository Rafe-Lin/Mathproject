import random

def generate(level=1):
    """
    生成一道「空間直線參數式」的題目。
    """
    point = [random.randint(-5, 5) for _ in range(3)]
    direction = [random.randint(-4, 4) for _ in range(3)]
    # 確保方向向量不是零向量
    while all(c == 0 for c in direction):
        direction = [random.randint(-4, 4) for _ in range(3)]
    
    if level == 1:
        question_text = f"已知空間中一條直線通過點 {tuple(point)}，且方向向量為 {tuple(direction)}，請寫出此直線的參數式。\n(這是一道觀念題，請在紙上作答)"
        correct_answer = "觀念題"
    else: # level 2
        q_type = random.choice(['calc_point', 'check_point'])
        if q_type == 'calc_point':
            t = random.randint(2, 5)
            question_text = f"已知直線 L 的參數式為 x={point[0]}+{direction[0]}t, y={point[1]}+{direction[1]}t, z={point[2]}+{direction[2]}t (t為實數)。當 t={t} 時，直線上的點坐標為何？"
            p_on_line = [point[i] + direction[i]*t for i in range(3)]
            correct_answer = str(tuple(p_on_line))
        else: # check_point
            test_point = [point[i] + direction[i]*2 for i in range(3)] # 構造一個在線上的點
            if random.choice([True, False]): # 隨機決定測試點是否真的在線上
                correct_answer = "是"
            else:
                test_point[random.randint(0,2)] += 1 # 讓點偏離直線
                correct_answer = "否"
            question_text = f"已知直線 L 的參數式為 x={point[0]}+{direction[0]}t, y={point[1]}+{direction[1]}t, z={point[2]}+{direction[2]}t (t為實數)。請問點 {tuple(test_point)} 是否在直線 L 上？ (是/否)"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    if correct_answer == "觀念題": return {"correct": True, "result": "觀念正確！參數式表示為 (x,y,z) = (x₀+at, y₀+bt, z₀+ct)。", "next_question": True}
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip().replace(" ", "")
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}