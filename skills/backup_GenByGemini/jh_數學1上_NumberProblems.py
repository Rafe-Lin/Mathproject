import random

def generate(level=1):
    """
    生成「一元一次方程式應用題」相關題目。
    技能: jh_數學1上_NumberProblems
    包含：
    1. 基本型: ax + b = c
    2. 兩邊皆有未知數: ax + b = cx + d
    3. 連續整數問題
    """
    # 調整權重，讓兩邊有未知數的題型出現機率高一些
    problem_type = random.choice(['simple_eq', 'both_sides_eq', 'both_sides_eq', 'consecutive_int'])
    
    if problem_type == 'simple_eq':
        return generate_simple_eq_problem()
    elif problem_type == 'both_sides_eq':
        return generate_both_sides_eq_problem()
    else: # consecutive_int
        return generate_consecutive_int_problem()

def generate_simple_eq_problem():
    # 題型：已知某數的 a 倍 [加/減] b 等於 c，求某數。 (ax + b = c)
    
    # 1. 先決定答案 x
    x = random.randint(-10, 10)
    if x == 0: x = random.randint(1, 10) # 避免答案是 0，讓題目稍微有點計算
    
    # 2. 決定係數 a 和 常數 b
    a = random.randint(2, 6) * random.choice([-1, 1])
    b = random.randint(-20, 20)
    
    # 3. 計算結果 c
    c = a * x + b
    
    # 4. 組成題目文字
    # 處理係數 a 的文字
    if a == 1:
        a_desc = "某數"
    elif a == -1:
        a_desc = "某數的相反數"
    else:
        a_desc = f"某數的 ${a}$ 倍"

    # 處理常數 b 的文字
    b_desc = ""
    if b > 0:
        b_desc = f"加上 ${b}$"
    elif b < 0:
        b_desc = f"減去 ${abs(b)}$"
        
    question_text = f"已知{a_desc}{b_desc}等於 ${c}$，求此數是多少？"
    correct_answer = str(x)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_both_sides_eq_problem():
    # 題型：如課本例題，ax + b = cx + d
    
    # 1. 先決定答案 x
    x = random.randint(-15, 15)
    
    # 2. 決定係數 a, c
    a = random.randint(2, 7)
    c = random.randint(-3, 3)
    if a == c: # 確保 a, c 不相等
        c += random.choice([-1, 1])
        if c == a: c += 1 # 再次確保
    if random.random() > 0.5: # 隨機交換 a, c 增加變化
        a, c = c, a
        
    # 3. 決定常數 b
    b = random.randint(-20, 20)
    
    # 4. 計算常數 d (ax + b = cx + d  => d = ax + b - cx)
    d = (a * x) + b - (c * x)
    
    # 5. 組成題目文字
    var_name = random.choice(["甲數", "乙數", "某數"])
    
    def get_desc(coeff, const, name):
        desc = ""
        # 處理係數
        if coeff == 1:
            desc = name
        elif coeff == -1:
            desc = f"{name}的相反數"
        elif coeff != 0:
            desc = f"{name}的 ${coeff}$ 倍"
            
        # 處理常數
        if const > 0:
            desc += f"加上 ${const}$" if desc else f"${const}$"
        elif const < 0:
            desc += f"減去 ${abs(const)}$" if desc else f"${const}$"
            
        return desc

    left_desc = get_desc(a, b, var_name)
    right_desc = get_desc(c, d, f"此數") # 右式用「此數」避免重複
    
    question_text = f"已知{left_desc}等於{right_desc}，求{var_name}是多少？"
    correct_answer = str(x)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }
    
def generate_consecutive_int_problem():
    # 題型：n 個連續整數/偶數/奇數的和為 S，求其中一數。
    
    num_count = random.choice([3, 4, 5])
    int_type = random.choice(['整數', '偶數', '奇數'])
    
    # 1. 決定最小的數 start_val
    start_val = random.randint(-10, 20)
    
    if int_type == '偶數' and start_val % 2 != 0:
        start_val += 1
    elif int_type == '奇數' and start_val % 2 == 0:
        start_val += 1
        
    # 2. 產生數列並計算總和
    step = 2 if int_type in ['偶數', '奇數'] else 1
    numbers = [start_val + i * step for i in range(num_count)]
    total_sum = sum(numbers)
    
    # 3. 決定要求哪個數
    target_options = ['最小', '最大']
    if num_count % 2 != 0:
        target_options.append('中間')
    target = random.choice(target_options)
    
    # 4. 計算正確答案
    if target == '最小':
        correct_answer_val = numbers[0]
    elif target == '最大':
        correct_answer_val = numbers[-1]
    else: # '中間'
        correct_answer_val = numbers[num_count // 2]
        
    question_text = f"有 {num_count} 個連續{int_type}，它們的和為 ${total_sum}$。請問{target}的數是多少？"
    correct_answer = str(correct_answer_val)
    
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
    
    # 數值容錯 (例如 5 vs 5.0)
    if not is_correct:
        try:
            if float(user_answer) == float(correct_answer):
                is_correct = True
        except (ValueError, TypeError):
            pass

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}
