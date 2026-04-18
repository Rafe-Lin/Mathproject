import random

def _num_to_str(n):
    """Formats an integer for display in a math expression."""
    return f"({n})" if n < 0 else str(n)

def generate_basic_ops_problem():
    """
    生成一個基本的兩步驟整數四則運算問題。
    涵蓋運算順序（先乘除後加減）。
    - 類型 1: a + b * c (加減與乘法)
    - 類型 2: a / b * c (乘法與除法，由左至右)
    """
    problem_subtype = random.choice(['add_mul', 'mul_div'])
    
    if problem_subtype == 'add_mul':
        a = random.randint(-20, 20)
        b = random.randint(-9, 9)
        if b == 0: b = 1
        c = random.randint(-9, 9)
        if c == 0: c = 1
        op1 = random.choice(['+', '-'])
        
        question_text = f"計算 ${a} {op1} {_num_to_str(b)} \\times {_num_to_str(c)}$ 的值。"
        if op1 == '+':
            correct_answer = str(a + b * c)
        else:
            correct_answer = str(a - b * c)
    else: # 'mul_div'
        # 生成 a / b * c，其中 a 可被 b 整除
        b = random.choice([-6, -5, -4, -3, -2, 2, 3, 4, 5, 6])
        a = b * random.randint(-5, 5)
        c = random.randint(-7, 7)
        if c == 0: c = 1
        
        if random.random() < 0.5:
            # a / b * c
            question_text = f"計算 ${_num_to_str(a)} \\div {_num_to_str(b)} \\times {_num_to_str(c)}$ 的值。"
            correct_answer = str(a // b * c)
        else:
            # a * c / b
            question_text = f"計算 ${_num_to_str(a)} \\times {_num_to_str(c)} \\div {_num_to_str(b)}$ 的值。"
            correct_answer = str(a * c // b)
            
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_parentheses_ops_problem():
    """
    生成包含括號或絕對值的問題。
    - 類型 1: 包含括號的運算式，例如 a / (b*c - d)
    - 類型 2: 包含絕對值的運算式，例如 a*b + |c*d - e|
    """
    problem_subtype = random.choice(['brackets', 'abs_val'])

    if problem_subtype == 'brackets':
        # 例如：(-60)÷[ (-7)×2-1 ]
        op_inner = random.choice(['+', '-', '\\times'])
        b = random.randint(-9, 9)
        if b == 0: b = 2
        c = random.randint(-9, 9)
        if c == 0: c = -2

        if op_inner == '+': val_inner = b + c
        elif op_inner == '-': val_inner = b - c
        else: val_inner = b * c

        if val_inner == 0: val_inner = 1 # 避免除以零
        
        a = val_inner * random.randint(-8, 8)
        if a == 0: a = val_inner

        question_text = f"計算 ${_num_to_str(a)} \\div [ {_num_to_str(b)} {op_inner} {_num_to_str(c)} ]$ 的值。"
        correct_answer = str(a // val_inner)
    
    else: # 'abs_val'
        # 例如：(-8)×6＋｜(-5)×10-1｜
        a = random.randint(-10, 10)
        b = random.randint(-10, 10)
        c = random.randint(-10, 10)
        d = random.randint(-10, 10)
        e = random.randint(-20, 20)

        # 為了避免過於簡單的題目，確保部分數值不為零
        if a == 0: a = random.choice([-1, 1])
        if b == 0: b = random.choice([-2, 2])
        if c == 0: c = random.choice([-3, 3])
        if d == 0: d = random.choice([-4, 4])
        
        op_outer = random.choice(['+', '-'])
        
        question_text = f"計算 ${_num_to_str(a)} \\times {_num_to_str(b)} {op_outer} \\left| {_num_to_str(c)} \\times {_num_to_str(d)} - {_num_to_str(e)} \\right|$ 的值。"
        val_abs = abs(c * d - e)
        if op_outer == '+':
            correct_answer = str(a * b + val_abs)
        else:
            correct_answer = str(a * b - val_abs)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_distributive_law_problem():
    """
    生成可以使用分配律簡化的問題。
    - 類型 1 (提出公因數): a*c + b*c，其中 a+b 為整數。
    - 類型 2 (展開): a*b，其中 a 接近一個整數。
    """
    problem_subtype = random.choice(['factoring', 'expanding'])
    
    if problem_subtype == 'factoring':
        # a*c + b*c = (a+b)*c
        op = random.choice(['+', '-'])
        c = random.randint(-25, 25)
        if c == 0: c = 1

        if op == '+':
            round_sum = random.choice([100, 1000])
            a = random.randint(round_sum // 10, round_sum - 1)
            b = round_sum - a
            question_text = f"計算 ${a} \\times {_num_to_str(c)} + {b} \\times {_num_to_str(c)}$ 的值。"
            correct_answer = str((a + b) * c)
        else: # op == '-'
            round_diff = random.choice([100, 1000])
            a = random.randint(round_diff + 1, round_diff + 100)
            b = a - round_diff
            question_text = f"計算 ${a} \\times {_num_to_str(c)} - {b} \\times {_num_to_str(c)}$ 的值。"
            correct_answer = str((a - b) * c)
    else: # expanding
        # a * b，其中 a 接近 100, 1000 等
        round_num = random.choice([100, 200, 1000])
        offset = random.randint(1, 3) * random.choice([-1, 1])
        a = round_num + offset
        b = random.randint(-25, 25)
        if b == 0: b = 1
        
        question_text = f"計算 ${a} \\times {_num_to_str(b)}$ 的值。"
        correct_answer = str(a * b)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_word_problem():
    """
    生成一個可轉化為整數運算的應用問題。
    - 情境 1: 在數線上移動。
    - 情境 2: 計算遊戲得分。
    """
    scenario = random.choice(['number_line', 'scoring_game'])
    
    if scenario == 'number_line':
        start_pos = 0
        total_events = random.randint(10, 20)
        event1_name = random.choice(["偶數點", "正面", "抽中紅球"])
        event2_name = random.choice(["奇數點", "反面", "抽中白球"])
        event1_move = random.randint(2, 6) # 向右移動
        event2_move = random.randint(2, 6) # 向左移動
        
        event1_count = random.randint(3, total_events - 3)
        event2_count = total_events - event1_count
        
        final_pos = start_pos + event1_count * event1_move - event2_count * event2_move
        
        question_text = (
            f"小翊將一個棋子放在數線上的原點，並依照下列規則移動。<br>"
            f"規則：擲出{event1_name}，棋子往數線右方移動 ${event1_move}$ 個單位；"
            f"擲出{event2_name}，棋子往數線左方移動 ${event2_move}$ 個單位。<br>"
            f"已知小翊共投擲了 ${total_events}$ 次，其中出現 ${event1_count}$ 次{event1_name}，"
            f"則棋子最後的位置在哪個坐標上？"
        )
        correct_answer = str(final_pos)
    else: # scoring_game
        person1 = "小妍"
        person2 = "小美"
        win_score = random.randint(2, 5)
        lose_score = -random.randint(1, 3)
        draw_score = random.choice([0, 1])
        
        total_games = random.randint(9, 15)
        p1_wins = random.randint(2, total_games - 3)
        p2_wins = random.randint(1, total_games - p1_wins - 1)
        if p2_wins < 0 : p2_wins = 0
        draws = total_games - p1_wins - p2_wins
        p1_losses = p2_wins
        
        final_score = p1_wins * win_score + p1_losses * lose_score + draws * draw_score
        
        question_text = (
            f"{person1}與{person2}玩猜拳遊戲，計分方式為：贏得 ${win_score}$ 分，"
            f"平手得 ${draw_score}$ 分，輸了扣 ${-lose_score}$ 分。<br>"
            f"已知兩人共猜了 ${total_games}$ 次拳，其中{person1}贏 ${p1_wins}$ 次，"
            f"{person2}贏 ${p2_wins}$ 次，其餘為平手。<br>"
            f"請問{person1}最後得到幾分？"
        )
        correct_answer = str(final_score)
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    主生成函式，隨機選擇一種整數四則運算的題型。
    """
    problem_type = random.choice([
        'basic_ops', 
        'parentheses_ops', 
        'distributive_law', 
        'word_problem'
    ])
    
    if problem_type == 'basic_ops':
        return generate_basic_ops_problem()
    elif problem_type == 'parentheses_ops':
        return generate_parentheses_ops_problem()
    elif problem_type == 'distributive_law':
        return generate_distributive_law_problem()
    else: # 'word_problem'
        return generate_word_problem()

def check(user_answer, correct_answer):
    """
    檢查使用者答案是否正確（純數值）。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    
    is_correct = False
    try:
        # 比較數值是否相等 (允許 '12' == '12.0')
        if float(user_answer) == float(correct_answer):
            is_correct = True
    except (ValueError, TypeError):
        # 如果無法轉換為浮點數，則進行字串比較
        if user_answer == correct_answer:
            is_correct = True
            
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}
