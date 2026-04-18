import random
from fractions import Fraction

def generate(level=1):
    """
    生成「應用等差級數」相關題目。
    包含：
    1. 堆疊物品求總數 (給定首項、公差、項數 或 首項、末項、項數)
    2. 堆疊物品求項 (給定總和、項數、公差，求首項或末項)
    3. 規律圖形求總數 (給定規律，求前n項和)
    """
    problem_type = random.choice(['stacking_find_total', 'stacking_find_term', 'pattern_find_total'])
    
    if problem_type == 'stacking_find_total':
        return generate_stacking_find_total_problem()
    elif problem_type == 'stacking_find_term':
        return generate_stacking_find_term_problem()
    else: # pattern_find_total
        return generate_pattern_find_total_problem()

def generate_stacking_find_total_problem():
    """
    題型：堆疊物品或連續過程，已知項的資訊，求總和。
    """
    # 隨機選擇給定 (a1, d, n) 或 (a1, an, n)
    if random.random() < 0.5:
        # 子題型: 給定 a1, d, n 求 Sn
        # 範例：學校排座位
        a1 = random.randint(5, 20)
        d = random.randint(2, 5)
        n = random.randint(10, 25)
        
        # 公式 Sn = n * [2*a1 + (n-1)*d] / 2
        sn = n * (2 * a1 + (n - 1) * d) // 2
        
        scenario = random.choice([
            {"item": "座位", "location": "體育館", "verb": "排了", "unit": "排", "first": "第一排", "each": "每一排", "prev": "前一排"},
            {"item": "積木", "location": "展示牆", "verb": "堆了", "unit": "層", "first": "最上層", "each": "每一層", "prev": "上一層"},
            {"item": "書本", "location": "書架上", "verb": "放了", "unit": "層", "first": "最上層", "each": "每一層", "prev": "上一層"}
        ])
        
        question_text = f"在{scenario['location']}{scenario['verb']} ${n}$ {scenario['unit']}的{scenario['item']}。" \
                        f"{scenario['first']}有 ${a1}$ 個，之後{scenario['each']}都比{scenario['prev']}多 ${d}$ 個。" \
                        f"請問總共有多少個{scenario['item']}？"
        correct_answer = str(sn)

    else:
        # 子題型: 給定 a1, an, n 求 Sn
        # 範例：織布、儲蓄
        n = random.randint(10, 30)
        a1 = random.randint(20, 50)

        if random.random() < 0.5:
            # 遞減數列
            # 確保 d 的值能讓 an > 0
            d = -random.randint(1, a1 // n if n > 0 else a1)
            if d == 0: d = -1
            an = a1 + (n - 1) * d
            scenario = random.choice([
                {"subject": "女子織布", "unit": "尺", "verb": "織了"},
                {"subject": "跑者每日訓練", "unit": "公里", "verb": "跑了"}
            ])
            story = f"有一{scenario['subject']}，每天的進度都比前一天少固定的長度。已知第一天{scenario['verb']} ${a1}$ {scenario['unit']}，最後一天{scenario['verb']} ${an}$ {scenario['unit']}。若總共持續了 ${n}$ 天，請問總共{scenario['verb']}多少{scenario['unit']}？"
        else:
            # 遞增數列
            d = random.randint(2, 10)
            an = a1 + (n - 1) * d
            scenario = random.choice([
                {"subject": "小華存錢", "unit": "元", "verb": "存了"},
                {"subject": "工人鋪路", "unit": "公尺", "verb": "鋪設"}
            ])
            story = f"{scenario['subject']}，每天的進度都比前一天多固定的長度。已知第一天{scenario['verb']} ${a1}$ {scenario['unit']}，最後一天{scenario['verb']} ${an}$ {scenario['unit']}。若總共持續了 ${n}$ 天，請問總共{scenario['verb']}多少{scenario['unit']}？"

        # 公式 Sn = n * (a1 + an) / 2
        sn = n * (a1 + an) // 2
        question_text = story
        correct_answer = str(sn)
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_stacking_find_term_problem():
    """
    題型：堆疊物品，已知總和，求首項或末項。
    """
    # 隨機選擇求 a1 或 an
    if random.random() < 0.5:
        # 子題型: 給定 Sn, n, d 求 a1
        # 範例：已知總座位數，求第一排座位數
        n = random.randint(10, 20)
        d = random.randint(2, 5)
        
        # 為了確保 a1 是整數，我們先生成 a1，再反推出 Sn
        a1 = random.randint(10, 30)
        sn = n * (2 * a1 + (n - 1) * d) // 2
        
        scenario = random.choice([
            {"item": "座位", "unit": "排", "first": "第一排"},
            {"item": "罐頭", "unit": "排", "first": "第一排"}
        ])

        question_text = f"預計要排 ${sn}$ 個{scenario['item']}，一共 ${n}$ {scenario['unit']}，且每一{scenario['unit']}都比前一{scenario['unit']}多 ${d}$ 個{scenario['item']}，則{scenario['first']}要放多少個{scenario['item']}？"
        correct_answer = str(a1)
        
    else:
        # 子題型: 給定 Sn, n, d 求 an
        # 範例：已知總公仔數，求最底層公仔數
        n = random.randint(7, 15)
        d = random.randint(2, 5)
        
        # 為了確保解是整數，我們先生成 a1，再推出 Sn 和 an
        a1 = random.randint(5, 20)
        sn = n * (2 * a1 + (n - 1) * d) // 2
        an = a1 + (n - 1) * d

        scenario = random.choice([
            {"item": "公仔", "location": "展示架"},
            {"item": "積木", "location": "堆疊作品"}
        ])
        
        question_text = f"{scenario['location']}上堆疊著一層層的{scenario['item']}，依次每層都比上一層多 ${d}$ 個{scenario['item']}。已知共使用了 ${sn}$ 個{scenario['item']}堆疊出 ${n}$ 層，則最底層（第 ${n}$ 層）要放多少個{scenario['item']}？"
        correct_answer = str(an)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_pattern_find_total_problem():
    """
    題型：規律圖形，求前 n 個圖形的棋子總數。
    """
    a1 = random.randint(3, 8)
    d = random.randint(2, 6) * 2 # 公差通常是偶數
    n = random.randint(10, 25)
    
    # 計算 Sn
    sn = n * (2 * a1 + (n - 1) * d) // 2
    
    # 產生前三項來展示規律
    terms = [str(a1 + i * d) for i in range(3)]
    
    question_text = f"用棋子依某種規律排成一系列的圖形。觀察發現，各圖形的棋子數依序為 ${', '.join(terms)}, \\dots$，" \
                    f"形成一個等差數列。如果要排出從第 1 個到第 ${n}$ 個圖形，總共需要幾顆棋子？"
    
    correct_answer = str(sn)
    
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
    
    # 移除答案中的單位，例如 "個" 或 "元"
    for unit in ['個', '元', '尺', '公尺', '公里', '顆']:
        user_answer = user_answer.replace(unit, '')

    is_correct = (user_answer == correct_answer)
    
    if not is_correct:
        try:
            if float(user_answer) == float(correct_answer):
                is_correct = True
        except (ValueError, TypeError):
            pass

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}