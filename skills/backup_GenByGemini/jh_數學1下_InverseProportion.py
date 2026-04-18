import random

def generate(level=1):
    """
    生成「反比」相關題目 (標準 LaTeX 範本)。
    包含：
    1. 關係判斷
    2. 求關係式與特定值
    3. 應用問題
    """
    problem_type = random.choice(['identification', 'relation_solve', 'word_problem'])
    
    if problem_type == 'identification':
        return generate_identification_problem()
    elif problem_type == 'relation_solve':
        return generate_relation_solve_problem()
    else:
        return generate_word_problem()

def generate_identification_problem():
    """
    題型：給定表格，判斷兩變數是否成反比。
    """
    # 選擇一個有較多因數的數作為乘積 k
    k = random.randint(2, 12) * random.choice([10, 12, 15, 20])
    k *= random.choice([-1, 1])

    # 找出 k 的所有因數，以生成 x 值
    factors = []
    for i in range(1, int(abs(k)**0.5) + 1):
        if k % i == 0:
            factors.append(i)
            if i*i != abs(k):
                factors.append(abs(k) // i)
    
    # 如果因數少於 4 個，重新生成
    if len(factors) < 4:
        return generate_identification_problem()

    x_values = random.sample([f for f in factors if f != 1 and f != abs(k)], 4)
    x_values.sort()
    y_values = [k // x for x in x_values]

    # 隨機決定此題答案為「是」或「否」
    is_inverse_proportion = random.choice([True, False])

    if not is_inverse_proportion:
        # 如果答案為「否」，則修改其中一個 y 值以破壞反比關係
        idx_to_change = random.randint(0, len(y_values) - 1)
        alteration = random.randint(1, 5) * random.choice([-1, 1])
        # 確保修改後的值不為 0
        while y_values[idx_to_change] + alteration == 0:
             alteration = random.randint(1, 5) * random.choice([-1, 1])
        y_values[idx_to_change] += alteration
        correct_answer = "否"
    else:
        correct_answer = "是"

    # 格式化表格字串
    table_x_str = f"x={{ {', '.join(map(str, x_values))} }}"
    table_y_str = f"y={{ {', '.join(map(str, y_values))} }}"

    # 使用 HTML <br> 標籤換行
    question_text = (
        f"已知變數 $x$ 與 $y$ 的關係如下表，判斷 $y$ 與 $x$ 是否成反比？ (請回答「是」或「否」)<br>"
        f"表 1: ${table_x_str}$<br>"
        f"      ${table_y_str}$"
    )

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_relation_solve_problem():
    """
    題型：給定一組 (x, y) 值，求關係式或另一組的未知數。
    """
    k = random.choice(list(range(-50, -5)) + list(range(6, 51)))
    
    # 選擇 x1 作為 k 的因數
    factors = [i for i in range(1, abs(k) + 1) if k % i == 0]
    x1 = random.choice(factors) * random.choice([-1, 1])
    # 確保符號正確後仍可整除
    if k % x1 != 0:
        x1 = -x1
    y1 = k // x1

    # 隨機選擇子題型：求關係式、求 x、或求 y
    sub_problem_type = random.choice(['find_relation', 'solve_for_x', 'solve_for_y'])

    question_prefix = f"設 $y$ 與 $x$ 成反比，且當 $x={x1}$ 時，$y={y1}$，則："

    if sub_problem_type == 'find_relation':
        question_text = f"{question_prefix}<br>⑴ $x$ 與 $y$ 的關係式為何？"
        correct_answer = f"xy={k}"
    else:
        # 找出與 x1 不同的因數來生成新題目
        other_factors = [f for f in factors if abs(f) != abs(x1)]
        if not other_factors:
            return generate_relation_solve_problem() # 重新生成以避免錯誤
        
        new_val_base = random.choice(other_factors)

        if sub_problem_type == 'solve_for_y':
            x2 = new_val_base * random.choice([-1, 1])
            if k % x2 != 0:
                x2 = -x2
            y2 = k // x2
            question_text = f"{question_prefix}<br>⑵ 當 $x={x2}$ 時，$y$ 是多少？"
            correct_answer = str(y2)
        else: # solve_for_x
            y2 = new_val_base * random.choice([-1, 1])
            if k % y2 != 0:
                y2 = -y2
            x2 = k // y2
            question_text = f"{question_prefix}<br>⑵ 當 $y={y2}$ 時，$x$ 是多少？"
            correct_answer = str(x2)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_word_problem():
    """
    題型：反比概念的應用問題。
    """
    scenarios = [
        {
            "context": "參加「自行車挑戰」活動，已知距離固定時，速率與時間成反比",
            "x_var": "速率", "x_unit": "公里/小時", "y_var": "時間", "y_unit": "小時"
        },
        {
            "context": "工程隊要完成一項工程，已知工作總量固定時，人數與所需工作天數成反比",
            "x_var": "人數", "x_unit": "人", "y_var": "天數", "y_unit": "天"
        },
        {
            "context": "一筆固定金額的錢要分給若干人，每人分得的金額與人數成反比",
            "x_var": "人數", "x_unit": "人", "y_var": "每人分得金額", "y_unit": "元"
        }
    ]
    
    scenario = random.choice(scenarios)

    if scenario['x_var'] == "速率":
        x1 = random.randint(20, 60)
        y1 = random.randint(5, 20)
    else: # 人數/天數 或 人數/金額
        x1 = random.randint(5, 20)
        y1 = random.randint(10, 50)

    k = x1 * y1

    # 產生第二組數據，確保 x2 是 k 的因數且不等於 x1
    factors_of_k = [i for i in range(2, k) if k % i == 0 and i != x1]
    if not factors_of_k:
        return generate_word_problem() # 重新生成
    x2 = random.choice(factors_of_k)
    y2 = k // x2

    sub_problem_type = random.choice(['find_relation', 'solve'])
    
    context_text = f"{scenario['context']}，若以 {x1} {scenario['x_unit']} 的{scenario['x_var']}進行，需要花 {y1} {scenario['y_unit']} 的{scenario['y_var']}，試問："
    
    if sub_problem_type == 'find_relation':
        question_text = f"{context_text}<br>⑴ 以 $x$ 表示{scenario['x_var']}、以 $y$ 表示{scenario['y_var']}，則 $x$ 與 $y$ 的關係式為何？"
        correct_answer = f"xy={k}"
    else:
        question_text = f"{context_text}<br>⑵ 若{scenario['x_var']}改為 {x2} {scenario['x_unit']}，則需花幾{scenario['y_unit']}？"
        correct_answer = str(y2)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確，可處理數字、關係式、以及「是/否」。
    """
    # 標準化輸入，去除空白並轉為小寫
    user_ans = user_answer.strip().replace(" ", "").lower()
    correct_ans = correct_answer.strip().replace(" ", "").lower()

    is_correct = False

    # 1. 直接比對 (適用於「是」、「否」)
    if user_ans == correct_ans:
        is_correct = True
    
    # 2. 數值比對
    if not is_correct:
        try:
            if float(user_ans) == float(correct_ans):
                is_correct = True
        except (ValueError, TypeError):
            pass

    # 3. 關係式比對 (xy=k, yx=k, y=k/x, x=k/y)
    if not is_correct and 'xy=' in correct_ans:
        try:
            k_val_str = correct_ans.split('=')[1]
            k_val = float(k_val_str)
            
            if user_ans in [f"xy={k_val_str}", f"yx={k_val_str}"]:
                is_correct = True
            
            if not is_correct and user_ans.startswith('y=') and '/x' in user_ans:
                expr = user_ans.split('=')[1].replace('/x', '')
                if float(expr) == k_val:
                    is_correct = True
                    
            if not is_correct and user_ans.startswith('x=') and '/y' in user_ans:
                expr = user_ans.split('=')[1].replace('/y', '')
                if float(expr) == k_val:
                    is_correct = True
        except (ValueError, IndexError):
            pass

    # 格式化正確答案以供顯示
    display_answer = correct_answer
    try:
        float(correct_answer)
        display_answer = f"${correct_answer}$"
    except ValueError:
        if '=' in correct_answer:
            parts = correct_answer.split('=')
            display_answer = f"${parts[0]} = {parts[1]}$"

    result_text = f"完全正確！答案是 {display_answer}。" if is_correct else f"答案不正確。正確答案應為：${display_answer}"
    
    return {"correct": is_correct, "result": result_text, "next_question": True}
