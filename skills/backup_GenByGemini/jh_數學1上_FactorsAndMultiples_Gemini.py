import random

def _get_factors(n):
    """Helper function to get all positive factors of a number n."""
    factors = set()
    for i in range(1, int(n**0.5) + 1):
        if n % i == 0:
            factors.add(i)
            factors.add(n // i)
    return sorted(list(factors))

def generate(level=1):
    """
    生成「因數與倍數」相關題目。
    包含：
    1. 寫出一個數的所有因數。
    2. 從不完整的因數列表中，找出缺少的因數。
    3. 寫出一個數的倍數。
    """
    problem_type = random.choice(['find_all_factors', 'find_missing_factors', 'list_multiples'])
    
    if problem_type == 'find_all_factors':
        return generate_find_all_factors_problem()
    elif problem_type == 'find_missing_factors':
        return generate_find_missing_factors_problem()
    else: # list_multiples
        return generate_list_multiples_problem()

def generate_find_all_factors_problem():
    """
    題型：寫出一個數的所有正因數 (對應例題 1, 2)。
    """
    while True:
        # 選擇一個有適量因數的數字 (4到12個之間)
        n = random.randint(20, 120)
        factors = _get_factors(n)
        if 4 <= len(factors) <= 12:
            break

    question_text = f"請由小到大寫出 ${n}$ 的所有正因數。(請用逗號分隔)"
    correct_answer = ",".join(map(str, factors))
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_find_missing_factors_problem():
    """
    題型：從不完整的因數列表中，找出缺少的因數 (對應例題 3, 4)。
    """
    while True:
        # 選擇一個有6到10個因數的數字，這樣挖空後仍有足夠線索
        n = random.randint(30, 150)
        factors = _get_factors(n)
        if 6 <= len(factors) <= 10:
            break
    
    # 決定要隱藏幾個因數 (1 或 2 個)
    num_to_hide = random.choice([1, 2])
    # 不隱藏 1 和 n 本身
    hidable_indices = list(range(1, len(factors) - 1))
    indices_to_hide = sorted(random.sample(hidable_indices, num_to_hide))
    
    labels = ['a', 'b'][:num_to_hide]
    hidden_values = [factors[i] for i in indices_to_hide]
    num_variable = random.choice(['M', 'N'])
    
    display_list = []
    label_idx = 0
    for i, factor in enumerate(factors):
        if i in indices_to_hide:
            display_list.append(labels[label_idx])
            label_idx += 1
        elif i == len(factors) - 1:
            display_list.append(num_variable)
        else:
            display_list.append(str(factor))
            
    q_list_str = ", ".join(display_list)
    
    # 決定要問哪些未知數
    ask_items = labels.copy()
    answer_values = hidden_values.copy()
    
    # 約 40% 的機率會加問 M 或 N 本身是多少
    if random.random() < 0.4:
        ask_items.append(num_variable)
        answer_values.append(n)
        
    q_ask_str = "、".join(ask_items)
    
    question_text = f"有一正整數 ${num_variable}$ 的所有因數由小到大排列為 ${q_list_str}$，則 ${q_ask_str}$ 的值為何？(請依序回答，並用逗號分隔)"
    correct_answer = ",".join(map(str, answer_values))
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_list_multiples_problem():
    """
    題型：寫出一個數的倍數。
    """
    sub_type = random.choice(['first_n', 'within_limit'])
    
    if sub_type == 'first_n':
        base = random.randint(6, 15)
        count = random.randint(4, 7)
        multiples = [base * i for i in range(1, count + 1)]
        question_text = f"請寫出 ${base}$ 的前 ${count}$ 個正倍數。(請用逗號分隔)"
    else: # within_limit
        base = random.randint(11, 25)
        limit = random.choice([50, 100, 150, 200])
        multiples = [base * i for i in range(1, limit // base + 1)]
        # 確保有足夠的倍數可寫
        if len(multiples) < 3:
            return generate_list_multiples_problem() # 重新生成一個
        question_text = f"請寫出所有小於 ${limit}$ 的 ${base}$ 的正倍數。(請用逗號分隔)"
        
    correct_answer = ",".join(map(str, multiples))

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。答案是逗號分隔的數字列表。
    """
    # 清理使用者輸入和正確答案中的空格
    user_parts = [part.strip() for part in user_answer.split(',')]
    correct_parts = [part.strip() for part in correct_answer.split(',')]
    
    # 比較清理後的列表是否相同
    is_correct = (user_parts == correct_parts)
    
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    
    return {"correct": is_correct, "result": result_text, "next_question": True}
