import random

def generate(level=1):
    """
    生成「乘法分配律」相關計算題。
    題型包含：
    1. a * (b +/- c) 形式的簡化計算
    2. (a +/- b) * (c +/- d) 形式的簡化計算
    """
    # 隨機選擇一種題型
    problem_type = random.choice(['simple', 'complex'])
    
    if problem_type == 'simple':
        return generate_simple_distributive_problem()
    else: # 'complex'
        return generate_complex_distributive_problem()

def generate_simple_distributive_problem():
    """
    生成 a * (b +/- c) 形式的題目。
    此題型對應 a(b+c) = ab+ac 或 a(b-c) = ab-ac。
    例如：計算 25 x 103，可想成 25 * (100 + 3)。
    """
    # 生成第一個數字 n1，為一個二位數且非 10 的倍數，使分配律更有意義
    n1 = random.randint(11, 49)
    while n1 % 10 == 0:
        n1 = random.randint(11, 49)
        
    # 生成第二個數字 n2，使其接近一個整十或整百的數 (base)
    base = random.choice([k * 10 for k in range(2, 11)] + [200, 300, 400, 500])
    delta = random.randint(1, 4)
    
    # 隨機決定 n2 是比 base 大還是小
    if random.random() < 0.5 and base > delta:
        # 減法情況 (e.g., base=100, delta=2 -> n2=98)
        n2 = base - delta
    else:
        # 加法情況 (e.g., base=100, delta=2 -> n2=102)
        n2 = base + delta
        
    correct_answer = n1 * n2
    
    # [教學示範] 在 f-string 中使用 LaTeX，乘號 `\\times` 需寫成 `\\times`
    question_text = f"利用分配律，計算 ${n1} \\times {n2}$ 的值。"
    
    return {
        "question_text": question_text,
        "answer": str(correct_answer),
        "correct_answer": str(correct_answer)
    }

def generate_complex_distributive_problem():
    """
    生成 (a +/- b) * (c +/- d) 形式的題目。
    此題型對應 (a+b)(c+d) = ac+ad+bc+bd 的應用。
    例如：計算 99 x 501, 可想成 (100 - 1) * (500 + 1)。
    """
    # 生成第一個數字 n1，使其接近一個整十或整百的數
    base1 = random.choice([k * 10 for k in range(5, 51)]) # 50, 60, ..., 500
    delta1 = random.randint(1, 4)
    if random.random() < 0.5 and base1 > delta1:
        n1 = base1 - delta1
    else:
        n1 = base1 + delta1
        
    # 生成第二個數字 n2，使其也接近一個整十或整百的數
    base2 = random.choice([k * 10 for k in range(2, 21)]) # 20, 30, ..., 200
    delta2 = random.randint(1, 4)
    if random.random() < 0.5 and base2 > delta2:
        n2 = base2 - delta2
    else:
        n2 = base2 + delta2
            
    # 避免 n1 和 n2 相同 (這會變成平方公式問題，是另一個單元的重點)
    if n1 == n2:
        # 如果相同，最簡單的方式是重新生成一題
        return generate_complex_distributive_problem()

    correct_answer = n1 * n2
    
    # [教學示範] 數學表達式應完整放在一個 `$...$` 區塊內
    question_text = f"利用分配律，計算 ${n1} \\times {n2}$ 的值。"
    
    return {
        "question_text": question_text,
        "answer": str(correct_answer),
        "correct_answer": str(correct_answer)
    }

def check(user_answer, correct_answer):
    """
    檢查使用者答案是否正確。
    """
    user_answer = user_answer.strip()
    
    is_correct = (user_answer == correct_answer)
    
    # 為了穩健性，也嘗試用浮點數比較，以處理像 "123" vs "123.0" 這樣的情況
    if not is_correct:
        try:
            if float(user_answer) == float(correct_answer):
                is_correct = True
        except (ValueError, TypeError):
            # 如果使用者輸入的不是數字，則忽略此檢查
            pass

    # [教學示範] 回傳結果中也可以包含 LaTeX
    if is_correct:
        result_text = f"完全正確！答案是 ${correct_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer}$"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}