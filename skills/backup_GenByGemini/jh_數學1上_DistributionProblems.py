import random

# List of contexts for word problems to add variety
CONTEXTS = [
    {'item': '人', 'group': '頂帳篷', 'verb': '住'},
    {'item': '顆糖果', 'group': '位小朋友', 'verb': '分給'},
    {'item': '顆蘋果', 'group': '個箱子', 'verb': '裝入'},
    {'item': '位新生', 'group': '個班級', 'verb': '編入'},
    {'item': '位學生', 'group': '間宿舍', 'verb': '分配到'},
]

def generate(level=1):
    """
    生成「分配問題」相關的一元一次方程式應用題。
    題型變化包含：
    1. 盈 vs 虧 (多 vs 少)
    2. 盈 vs 盈 (多 vs 多)
    3. 虧 vs 虧 (少 vs 少)
    4. 總量改變型 (如例題2)
    """
    problem_type = random.choice([
        'surplus_vs_shortage',
        'surplus_vs_surplus',
        'shortage_vs_shortage',
        'total_change'
    ])

    if problem_type == 'surplus_vs_shortage':
        return generate_surplus_vs_shortage_problem()
    elif problem_type == 'surplus_vs_surplus':
        return generate_surplus_vs_surplus_problem()
    elif problem_type == 'shortage_vs_shortage':
        return generate_shortage_vs_shortage_problem()
    else:  # total_change
        return generate_total_change_problem()

def generate_surplus_vs_shortage_problem():
    """
    題型: 每組分 rate1 個, 會多 surplus 個; 每組分 rate2 個, 會少 shortage 個。
    方程式: rate1*x + surplus = rate2*x - shortage (假設 rate2 > rate1)
    => (rate2 - rate1)*x = surplus + shortage
    """
    context = random.choice(CONTEXTS)
    item, group, verb = context['item'], context['group'], context['verb']

    # 1. 決定答案 x (組數)
    x = random.randint(10, 30)

    # 2. 決定 rate 的差值
    rate_diff = random.randint(2, 5)

    # 3. 計算總差額
    total_diff = rate_diff * x

    # 4. 將總差額拆成 surplus 和 shortage, 確保兩者不為零
    # 讓 surplus 和 shortage 不要太懸殊
    if total_diff < 10:
        surplus = random.randint(1, total_diff - 1)
    else:
        surplus = random.randint(max(1, int(total_diff * 0.2)), int(total_diff * 0.8))
    shortage = total_diff - surplus

    # 5. 決定 rate1, 並算出 rate2
    rate1 = random.randint(5, 25)
    rate2 = rate1 + rate_diff

    # 6. 組成題目
    question_text = f"將一批{item}{verb}若干{group}。若每{group}{verb} {rate1} {item}，則會多出 {surplus} {item}；"\
                    f"若每{group}{verb} {rate2} {item}，則會不足 {shortage} {item}。請問共有多少{group}？"

    correct_answer = str(x)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_surplus_vs_surplus_problem():
    """
    題型: 每組分 rate1 個, 會多 surplus1 個; 每組分 rate2 個, 會多 surplus2 個。
    方程式: rate1*x + surplus1 = rate2*x + surplus2 (假設 rate2 > rate1, 則 surplus1 > surplus2)
    => (rate2 - rate1)*x = surplus1 - surplus2
    """
    context = random.choice(CONTEXTS)
    item, group, verb = context['item'], context['group'], context['verb']

    # 1. 決定答案 x (組數)
    x = random.randint(10, 35)

    # 2. 決定 rate 的差值
    rate_diff = random.randint(1, 4)

    # 3. 計算 surplus 的差值
    surplus_diff = rate_diff * x

    # 4. 決定 surplus2, 並算出 surplus1
    surplus2 = random.randint(1, 20)
    surplus1 = surplus2 + surplus_diff
    
    # 5. 決定 rate1, 並算出 rate2
    rate1 = random.randint(5, 30)
    rate2 = rate1 + rate_diff

    # 6. 組成題目
    question_text = f"有一批{item}要{verb}一些{group}。如果每{group}{verb} {rate1} {item}，會剩下 {surplus1} {item}；"\
                    f"如果每{group}{verb} {rate2} {item}，則會剩下 {surplus2} {item}。請問共有多少{group}？"

    correct_answer = str(x)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_shortage_vs_shortage_problem():
    """
    題型: 每組分 rate1 個, 會少 shortage1 個; 每組分 rate2 個, 會少 shortage2 個。
    方程式: rate1*x - shortage1 = rate2*x - shortage2 (假設 rate2 > rate1, 則 shortage2 > shortage1)
    => (rate2 - rate1)*x = shortage2 - shortage1
    """
    context = random.choice(CONTEXTS)
    item, group, verb = context['item'], context['group'], context['verb']

    # 1. 決定答案 x (組數)
    x = random.randint(10, 35)

    # 2. 決定 rate 的差值
    rate_diff = random.randint(1, 4)

    # 3. 計算 shortage 的差值
    shortage_diff = rate_diff * x

    # 4. 決定 shortage1, 並算出 shortage2
    shortage1 = random.randint(1, 20)
    shortage2 = shortage1 + shortage_diff
    
    # 5. 決定 rate1, 並算出 rate2 (確保總數為正: rate1*x > shortage1)
    min_rate1 = (shortage1 // x) + 1
    rate1 = random.randint(min_rate1, min_rate1 + 10)
    rate2 = rate1 + rate_diff

    # 6. 組成題目
    question_text = f"將一群{item}{verb}若干{group}。若每{group}{verb} {rate1} {item}，則會不夠 {shortage1} {item}；"\
                    f"若每{group}{verb} {rate2} {item}，則會不夠 {shortage2} {item}。請問共有多少{group}？"

    correct_answer = str(x)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_total_change_problem():
    """
    題型: 總量改變型, 如例題2
    原總量 = rate1*x + surplus
    新總量 = 原總量 + extra_items = rate2*x (剛好分完)
    => (rate2 - rate1)*x = surplus + extra_items
    """
    context = random.choice(CONTEXTS)
    item, group, verb = context['item'], context['group'], context['verb']

    # 1. 決定答案 x (組數)
    x = random.randint(10, 30)
    
    # 2. 決定 rate 的差值
    rate_diff = random.randint(2, 5)
    
    # 3. 決定 rate1 和 rate2
    rate1 = random.randint(5, 15)
    rate2 = rate1 + rate_diff
    
    # 4. 決定 surplus 和 extra_items
    total_diff = rate_diff * x
    # 確保 surplus 和 extra_items 都是合理的正整數
    if total_diff <= 1:
        total_diff = 2 # 確保可以拆分
    surplus = random.randint(1, total_diff - 1)
    extra_items = total_diff - surplus

    # 5. 組成題目
    question_text = f"將一包{item}{verb}全體{group}，已知每{group}分到 {rate1} {item}時，會多出 {surplus} {item}；"\
                    f"若另外再加入 {extra_items} {item}，則每{group}剛好可以分到 {rate2} {item}且恰好分完。請問共有幾{group}？"

    correct_answer = str(x)

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
    
    is_correct = False
    try:
        # 嘗試將答案轉為數值進行比較
        if int(user_answer) == int(correct_answer):
            is_correct = True
    except ValueError:
        # 如果轉換失敗，則進行字串比較 (備用)
        is_correct = (user_answer.upper() == correct_answer.upper())

    if is_correct:
        result_text = f"完全正確！答案是 {correct_answer}。"
    else:
        result_text = f"答案不正確。正確答案應為：{correct_answer}"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}
