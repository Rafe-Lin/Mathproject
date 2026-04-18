import random
from fractions import Fraction

def generate(level=1):
    """
    生成「正比」相關題目 (標準 LaTeX 範本)。
    包含：
    1. 判斷是否成正比
    2. 求特定值
    3. 求比例常數
    4. 應用問題
    """
    problem_type = random.choice(['is_proportional_table', 'find_value', 'word_problem', 'find_constant'])
    
    if problem_type == 'is_proportional_table':
        return generate_is_proportional_table_problem()
    elif problem_type == 'find_value':
        return generate_find_value_problem()
    elif problem_type == 'word_problem':
        return generate_word_problem()
    else: # find_constant
        return generate_find_constant_problem()

def generate_is_proportional_table_problem():
    """題型：從表格數據判斷是否成正比"""
    is_proportional = random.choice([True, False])
    num_points = random.randint(4, 5)

    den = random.randint(1, 4)
    num = random.randint(1, 5)
    # 確保 k 不是 1
    while num == den:
        num = random.randint(1, 5)
        
    k = Fraction(num, den)

    # 選擇 x 的基底值，並確保 x 都是 k 的分母的倍數，這樣 y 就會是整數
    base_x = random.sample(range(2, 10), num_points)
    x_values = sorted([val * k.denominator for val in base_x])
    y_values = [int(x * k) for x in x_values]

    if not is_proportional:
        # 隨機修改其中一個 y 值，使其不成正比
        idx_to_change = random.randint(0, num_points - 1)
        # 確保改變的值不會剛好又成比例，或變成 0 或負數
        change = random.randint(1, 5) * random.choice([-1, 1])
        y_values[idx_to_change] += change
        if y_values[idx_to_change] <= 0:
             y_values[idx_to_change] += 5 # 確保為正數

    x_str = ', '.join(map(str, x_values))
    y_str = ', '.join(map(str, y_values))
    
    question_text = f"判斷下列數據中，$y$ 與 $x$ 是否成正比？<br>$x = \{{{x_str}\}}$<br>$y = \{{{y_str}\}}$<br>(請填 是 或 否)"
    correct_answer = '是' if is_proportional else '否'
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_find_value_problem():
    """題型：已知 y 與 x 成正比及一組對應值，求另一特定值"""
    # 隨機決定比例常數 k 是整數還是分數
    if random.random() < 0.5:
        # k 為整數
        k_val = random.randint(2, 10)
        k = Fraction(k_val, 1)
        x1 = random.randint(3, 15)
        y1 = k_val * x1
        x2 = random.randint(3, 15)
        while x2 == x1:
            x2 = random.randint(3, 15)
    else:
        # k 為分數
        den = random.randint(2, 5)
        num = random.randint(2, 7)
        while num % den == 0 or den % num == 0:
            num = random.randint(2, 7)
        k = Fraction(num, den)
        
        mult1 = random.randint(2, 5)
        x1 = k.denominator * mult1
        y1 = k.numerator * mult1
        
        mult2 = random.randint(2, 5)
        while mult2 == mult1:
            mult2 = random.randint(2, 5)
        x2 = k.denominator * mult2
        
    y2 = k * x2

    if y2.denominator == 1:
        correct_answer = str(y2.numerator)
    else:
        correct_answer = f"{y2.numerator}/{y2.denominator}"

    question_text = f"設 $y$ 與 $x$ 成正比，且當 $x={x1}$ 時，$y={y1}$。請問當 $x={x2}$ 時，$y$ 的值是多少？"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_find_constant_problem():
    """題型：已知一組對應值，求比例常數 k"""
    den = random.randint(2, 7)
    num = random.randint(2, 9)
    k = Fraction(num, den)
    
    mult = random.randint(2, 5)
    x1 = k.denominator * mult
    y1 = k.numerator * mult
    
    # 重新計算以確保分數已化為最簡
    correct_k = Fraction(y1, x1)
    
    if correct_k.denominator == 1:
        correct_answer = str(correct_k.numerator)
    else:
        correct_answer = f"{correct_k.numerator}/{correct_k.denominator}"
        
    question_text = f"設 $y$ 與 $x$ 成正比，其關係式為 $y=kx$。若當 $x={x1}$ 時，$y={y1}$，請問比例常數 $k$ 的值是多少？"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_word_problem():
    """題型：正比的應用問題"""
    contexts = [
        {
            'story': '阿賢到某便利商店打工，薪資與工作時數成正比。',
            'y_name': '薪資', 'y_unit': '元',
            'x_name': '工作時數', 'x_unit': '小時',
            'k_range': (180, 250)
        },
        {
            'story': '一個水龍頭以固定速率注水到一個空的游泳池，注入池中的水量與注水時間成正比。',
            'y_name': '水量', 'y_unit': '公升',
            'x_name': '注水時間', 'x_unit': '分鐘',
            'k_range': (5, 25)
        },
        {
            'story': '一輛火車以等速行駛，其行駛的距離與所花的時間成正比。',
            'y_name': '距離', 'y_unit': '公里',
            'x_name': '時間', 'x_unit': '小時',
            'k_range': (60, 120)
        }
    ]
    context = random.choice(contexts)
    
    k = random.randint(*context['k_range'])
    x1 = random.randint(2, 10)
    y1 = k * x1
    x2 = random.randint(2, 10)
    while x1 == x2:
        x2 = random.randint(2, 10)
    y2 = k * x2
    
    question_text = f"{context['story']}已知當{context['x_name']}為 ${x1}$ {context['x_unit']}時，{context['y_name']}為 ${y1}$ {context['y_unit']}。試問當{context['x_name']}為 ${x2}$ {context['x_unit']}時，{context['y_name']}是多少{context['y_unit']}？"
    correct_answer = str(y2)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_ans = user_answer.strip()
    correct_ans = correct_answer.strip()

    is_correct = False
    
    # 1. 直接字串比對 (適用於 '是', '否' 等文字答案)
    if user_ans.upper() == correct_ans.upper():
        is_correct = True
    else:
        # 2. 數值比對 (適用於整數、分數、小數)
        try:
            # 使用 Fraction 進行穩健的比對，可處理 '1.5' vs '3/2' 的情況
            if Fraction(user_ans) == Fraction(correct_ans):
                is_correct = True
        except (ValueError, ZeroDivisionError):
            # 若轉換失敗，表示不是有效的數字格式，判定為錯誤
            pass

    result_text = f"完全正確！答案是 ${correct_ans}$。" if is_correct else f"答案不正確。正確答案應為：${correct_ans}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}
