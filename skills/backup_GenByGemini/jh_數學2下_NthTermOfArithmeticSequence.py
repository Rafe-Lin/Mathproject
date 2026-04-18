import random

def generate(level=1):
    """
    生成「等差數列第 n 項」相關題目。
    包含：
    1. 給首項、公差，求第 n 項。
    2. 給數列，求項數。
    3. 圖形規律應用問題。
    """
    problem_type = random.choice(['find_nth_term', 'find_num_terms', 'pattern_problem'])
    
    if problem_type == 'find_nth_term':
        return generate_find_nth_term()
    elif problem_type == 'find_num_terms':
        return generate_find_num_terms()
    else: # pattern_problem
        return generate_pattern_problem()

def generate_find_nth_term():
    """
    題型：若等差數列的首項為 a1，公差為 d，求此等差數列的第 n 項。
    """
    a1 = random.randint(-50, 50)
    d = random.choice([i for i in range(-15, 16) if i != 0])
    n = random.randint(5, 25)
    
    an = a1 + (n - 1) * d
    
    question_text = f"若一等差數列的首項為 ${a1}$，公差為 ${d}$，求此等差數列的第 ${n}$ 項。"
    correct_answer = str(an)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_find_num_terms():
    """
    題型：已知 a1, a2, ..., an 為等差數列，求此等差數列共有幾項？
    """
    a1 = random.randint(-30, 30)
    d = random.choice([i for i in range(-10, 11) if i != 0])
    n = random.randint(10, 30)
    
    an = a1 + (n - 1) * d
    
    # 顯示前兩項以建立公差
    a2 = a1 + d
    
    question_text = f"已知一等差數列為 ${a1}, {a2}, \dots$，若此數列的末項為 ${an}$，請問此數列共有幾項？"
    correct_answer = str(n)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_pattern_problem():
    """
    題型：與圖形規律相關的應用問題。
    """
    scenarios = [
        {'name': 'squares', 'desc': '用等長的吸管排出相連的正方形', 'a1': 4, 'd': 3, 'unit': '根吸管'},
        {'name': 'triangles', 'desc': '用牙籤排出相連的正三角形', 'a1': 3, 'd': 2, 'unit': '根牙籤'},
        {'name': 'tables', 'desc': '將正方形餐桌併攏排列，一張餐桌可坐4人，兩張可坐6人，依此類推', 'a1': 4, 'd': 2, 'unit': '人'}
    ]
    scenario = random.choice(scenarios)
    a1 = scenario['a1']
    d = scenario['d']
    desc = scenario['desc']
    unit = scenario['unit']

    sub_type = random.choice(['find_an', 'find_n', 'check_feasibility'])
    
    if sub_type == 'find_an':
        n_val = random.randint(8, 25)
        an_val = a1 + (n_val - 1) * d
        if scenario['name'] == 'tables':
             question = f"如果排列 ${n_val}$ 張桌子，總共可以坐幾人？"
        else:
             unit_q = unit[:-1] if unit.endswith('根') else unit
             question = f"如果要排出第 ${n_val}$ 個圖形，需要幾{unit_q}？"
        correct_answer = str(an_val)
    elif sub_type == 'find_n':
        n_val = random.randint(8, 25)
        an_val = a1 + (n_val - 1) * d
        if scenario['name'] == 'tables':
             question = f"如果要安排 ${an_val}$ 人入座，需要排列幾張桌子？"
        else:
             question = f"如果總共用了 ${an_val}$ {unit}，可以排出第幾個圖形？"
        correct_answer = str(n_val)
    else: # check_feasibility
        is_feasible = random.choice([True, False])
        if is_feasible:
            n_val = random.randint(10, 40)
            num = a1 + (n_val - 1) * d
            correct_answer = "是"
        else:
            n_val_base = random.randint(10, 40)
            base_num = a1 + (n_val_base - 1) * d
            # 產生一個不是 d 的倍數的偏移量
            offset = random.choice([i for i in range(-abs(d) + 1, abs(d)) if i != 0])
            num = base_num + offset
            correct_answer = "否"
        
        if scenario['name'] == 'tables':
            question = f"是否剛好可以用數張桌子安排 ${num}$ 人入座？(請回答是或否)"
        else:
            question = f"是否剛好可用 ${num}$ {unit}排出一個完整的圖形？(請回答是或否)"

    question_text = f"{desc}。依此規律，回答下列問題：<br>{question}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    
    is_correct = (user_answer == correct_answer)
    
    # 對於數字答案，允許不同的格式 (例如 "20" vs "20.0")
    if not is_correct and correct_answer not in ["是", "否"]:
        try:
            if float(user_answer) == float(correct_answer):
                is_correct = True
        except (ValueError, TypeError):
            pass

    if is_correct:
        result_text = f"完全正確！答案是 ${correct_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer}$"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}