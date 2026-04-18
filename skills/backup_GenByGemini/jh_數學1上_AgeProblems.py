import random
import math

# --- 全域設定 ---
YOUNGER_NAMES = ["小妍", "小智", "阿光", "小櫻", "小翔", "小宇", "志明", "小傑"]
OLDER_NAMES = ["媽媽", "爸爸", "老師", "叔叔", "爺爺", "伯伯", "阿姨"]

def generate(level=1):
    """
    生成「年齡問題」相關題目。
    包含：
    1. 給定年齡和與未來關係
    2. 給定年齡差與過去關係
    3. 給定現在關係與未來關係
    """
    problem_type = random.choice([
        'sum_and_future_relation',
        'diff_and_past_relation',
        'current_and_future_relation'
    ])
    
    if problem_type == 'sum_and_future_relation':
        return generate_sum_and_future_relation()
    elif problem_type == 'diff_and_past_relation':
        return generate_diff_and_past_relation()
    else: # 'current_and_future_relation'
        return generate_current_and_future_relation()

def generate_sum_and_future_relation():
    """
    題型：今年兩人年齡和為 S，Y 年後，一人年齡是另一人的 K 倍多 C 歲，求現在年齡或年齡差。
    類似例題 1。
    """
    person1 = random.choice(YOUNGER_NAMES)
    person2 = random.choice(OLDER_NAMES)
    
    child_age = random.randint(8, 15)
    age_diff = random.randint(20, 35)
    parent_age = child_age + age_diff
    
    age_sum = parent_age + child_age
    years_later = random.randint(3, 10)
    k = random.randint(2, 3)
    
    # 計算關係中的常數 c
    # (parent_age + years_later) = k * (child_age + years_later) + c
    c = (parent_age + years_later) - k * (child_age + years_later)
    
    c_str = ""
    if c > 0:
        c_str = f"多 ${c}$ 歲"
    elif c < 0:
        c_str = f"少 ${-c}$ 歲"
    # 如果 c == 0, c_str 為空，表示「正好是 K 倍」
    
    # 隨機決定要問什麼
    question_target = random.choice(['child', 'parent', 'diff'])
    
    if question_target == 'child':
        question_part = f"請問{person1}今年幾歲？"
        correct_answer = str(child_age)
    elif question_target == 'parent':
        question_part = f"請問{person2}今年幾歲？"
        correct_answer = str(parent_age)
    else: # 'diff'
        question_part = f"請問{person2}和{person1}相差多少歲？"
        correct_answer = str(age_diff)
        
    question_text = f"今年{person1}和{person2}的年齡和是 ${age_sum}$ 歲，${years_later}$ 年後，{person2}的年齡是{person1}年齡的 ${k}$ 倍{c_str}，{question_part}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_diff_and_past_relation():
    """
    題型：兩人年齡差為 D，Y 年前，一人年齡是另一人的 K 倍，求現在年齡。
    類似例題 2。
    """
    person1 = random.choice(YOUNGER_NAMES)
    person2 = random.choice(OLDER_NAMES)
    
    # 從過去的年齡反推，確保倍數為整數
    past_child_age = random.randint(3, 10)
    k = random.randint(3, 8)
    past_parent_age = k * past_child_age
    
    # 確保回到現在後，小孩的年紀是合理的
    years_ago = random.randint(4, 15 - past_child_age)
    
    child_age = past_child_age + years_ago
    parent_age = past_parent_age + years_ago
    age_diff = parent_age - child_age # 年齡差是固定的
    
    # 隨機決定要問誰的年齡
    question_target = random.choice(['child', 'parent'])
    
    if question_target == 'child':
        target_person_str = person1
        correct_answer = str(child_age)
    else:
        target_person_str = person2
        correct_answer = str(parent_age)
        
    question_text = f"已知{person1}與{person2}的年齡相差 ${age_diff}$ 歲，且 ${years_ago}$ 年前，{person2}的年齡恰好是{person1}年齡的 ${k}$ 倍，則{target_person_str}現在幾歲？"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_current_and_future_relation():
    """
    題型：現在一人年齡是另一人的 k1 倍，Y 年後，將變為 k2 倍，求現在年齡。
    """
    while True:
        person1 = random.choice(YOUNGER_NAMES)
        person2 = random.choice(OLDER_NAMES)

        # 未來的倍數 (較小)
        k_future = random.randint(2, 3)
        # 經過的年數
        years_later = random.randint(4, 12)
        
        # 求解方程式: x = Y * (k2 - 1) / (k1 - k2)
        # 我們需要找到 k1，使得 x (child_age) 是個合理的整數
        numerator = years_later * (k_future - 1)
        
        # 找出所有可能的除數 (代表 k1 - k2)
        possible_divisors = [d for d in range(1, numerator + 1) if numerator % d == 0]
        
        valid_params = []
        for d in possible_divisors:
            k_current = k_future + d
            # 限制現在的倍數，讓題目合理
            if k_current > k_future and k_current <= 8:
                child_age = numerator // d
                # 限制小孩的年齡，讓題目合理
                if 5 <= child_age <= 15:
                    valid_params.append((k_current, child_age))
        
        if valid_params:
            k_current, child_age = random.choice(valid_params)
            parent_age = k_current * child_age
            break # 找到合適參數，跳出迴圈

    # 隨機決定要問誰的年齡
    question_target = random.choice(['child', 'parent'])
    if question_target == 'child':
        question_part = f"請問{person1}現在幾歲？"
        correct_answer = str(child_age)
    else:
        question_part = f"請問{person2}現在幾歲？"
        correct_answer = str(parent_age)

    question_text = f"現在{person2}的年齡是{person1}的 ${k_current}$ 倍，${years_later}$ 年後，{person2}的年齡將會是{person1}的 ${k_future}$ 倍。{question_part}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。答案通常是純數字。
    """
    # 去除前後空白，並移除「歲」等單位
    user_answer = user_answer.strip()
    for unit in ['歲', 'years', 'year old']:
        user_answer = user_answer.replace(unit, '')

    correct_answer = correct_answer.strip()
    
    is_correct = (user_answer == correct_answer)
    
    # 數值容錯 (例如 25 vs 25.0)
    if not is_correct:
        try:
            if float(user_answer) == float(correct_answer):
                is_correct = True
        except (ValueError, TypeError):
            pass

    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}
