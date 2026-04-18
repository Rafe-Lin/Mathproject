import random
import re

def generate(level=1):
    """
    生成「一元一次應用問題」相關題目 (標準 LaTeX 範本)。
    包含：
    1. 折扣促銷問題
    2. 年齡問題
    3. 分配與盈虧問題
    """
    problem_type = random.choice(['discount', 'age', 'distribution'])
    
    if problem_type == 'discount':
        return generate_discount_problem()
    elif problem_type == 'age':
        return generate_age_problem()
    else:
        return generate_distribution_problem()

def generate_discount_problem():
    """
    生成折扣促銷問題
    題型: 這款[物品]正在促銷，買 N 瓶打 M 折，只比買 1 瓶多 Y 元喔！一瓶原價多少錢？
    """
    # Pre-defined combinations of (price, buy_count, discount_percent) for clean results
    combos = [
        (20, 2, 9),  # The example problem: (1.8-1)*20 = 16
        (50, 3, 8),  # (2.4-1)*50 = 70
        (40, 2, 7),  # (1.4-1)*40 = 16
        (100, 3, 6), # (1.8-1)*100 = 80
        (30, 4, 8),  # (3.2-1)*30 = 66
        (60, 2, 8.5) # (1.7-1)*60 = 42
    ]
    original_price, buy_count, discount_percent = random.choice(combos)
    
    item = random.choice(['汽水', '餅乾', '筆記本', '原子筆', '冰淇淋'])
    discount_rate = discount_percent / 10
    
    # Calculate the extra cost
    extra_cost = round((buy_count * discount_rate - 1) * original_price)
    
    # Handle display of discount (e.g., 8.5折 vs 9折)
    if discount_percent == int(discount_percent):
        discount_str = str(int(discount_percent))
    else:
        discount_str = str(discount_percent)

    question_text = f"這款{item}正在促銷，買 ${buy_count}$ 個打 ${discount_str}$ 折，只比買 $1$ 個多 ${extra_cost}$ 元喔！一個{item}原價多少錢？"
    correct_answer = str(original_price)
    
    # Detailed Solution
    coeff_step1 = buy_count * discount_rate
    coeff_step2 = round(coeff_step1 - 1, 2)
    solution_text = (
        f"設每個{item}的原價為 $x$ 元。<br>"
        f"依題意可列出一元一次方程式為：<br>"
        f"$({buy_count} \\times x \\times {discount_rate}) - x = {extra_cost}$<br>"
        f"${coeff_step1}x - x = {extra_cost}$<br>"
        f"${coeff_step2}x = {extra_cost}$<br>"
        f"$x = \\frac{{{extra_cost}}}{{{coeff_step2}}} = {original_price}$<br>"
        f"所以一個{item}的原價為 ${original_price}$ 元。"
    )
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "solution_text": solution_text
    }

def generate_age_problem():
    """
    生成年齡問題
    題型: [人物A]今年 A 歲，[人物B]今年 B 歲，幾年後 [人物A] 的年齡會是 [人物B] 的 M 倍？
    """
    x_years = random.randint(3, 10)  # This will be the answer
    multiplier = random.choice([2, 3])
    
    # Generate current ages based on the future condition to ensure integer solution
    age_b_current = random.randint(1, 15)
    age_a_current = multiplier * age_b_current + (multiplier - 1) * x_years
    
    # Make sure ages are reasonable
    if age_a_current <= age_b_current or age_a_current > 90:
        # Fallback to a safe combination if generated values are weird
        x_years = 5
        multiplier = 2
        age_b_current = 10
        age_a_current = 25

    names = random.choice([('爸爸', '兒子'), ('媽媽', '女兒'), ('老師', '小明'), ('哥哥', '弟弟')])
    name_a, name_b = names
    
    question_text = f"{name_a}今年 ${age_a_current}$ 歲，{name_b}今年 ${age_b_current}$ 歲，請問幾年後{name_a}的年齡會是{name_b}的 ${multiplier}$ 倍？"
    correct_answer = str(x_years)

    # Detailed Solution
    solution_text = (
        f"設 $x$ 年後{name_a}的年齡會是{name_b}的 ${multiplier}$ 倍。<br>"
        f"$x$ 年後，{name_a}的年齡為 $({age_a_current} + x)$ 歲，{name_b}的年齡為 $({age_b_current} + x)$ 歲。<br>"
        f"依題意可列式：<br>"
        f"${age_a_current} + x = {multiplier}({age_b_current} + x)$<br>"
        f"${age_a_current} + x = {multiplier * age_b_current} + {multiplier}x$<br>"
        f"${age_a_current} - {multiplier * age_b_current} = {multiplier}x - x$<br>"
        f"${age_a_current - multiplier * age_b_current} = {multiplier - 1}x$<br>"
        f"$x = \\frac{{{age_a_current - multiplier * age_b_current}}}{{{multiplier - 1}}} = {x_years}$<br>"
        f"所以答案是 ${x_years}$ 年後。"
    )

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "solution_text": solution_text
    }

def generate_distribution_problem():
    """
    生成分配與盈虧問題
    題型: 將一堆[物品]分給一群人，若每人分 A 個，則剩下 B 個；若每人分 C 個，則不足 D 個。請問有多少人？
    """
    num_people = random.randint(10, 30)  # This will be the answer
    
    dist1 = random.randint(3, 7)
    dist2 = dist1 + random.randint(2, 5)
    leftover = random.randint(1, 20)

    # Ensure (dist2 - dist1) * num_people > leftover to guarantee a shortage
    while (dist2 - dist1) * num_people <= leftover:
        leftover = random.randint(1, (dist2 - dist1) * num_people - 1)

    total_items = dist1 * num_people + leftover
    shortage = dist2 * num_people - total_items
    
    item = random.choice(['糖果', '鉛筆', '貼紙', '蘋果'])
    group = random.choice(['小朋友', '學生', '員工'])

    question_text = f"老師將一袋{item}分給一群{group}。如果每人分 ${dist1}$ 個，會剩下 ${leftover}$ 個；如果每人分 ${dist2}$ 個，就不夠 ${shortage}$ 個。請問{group}有幾位？"
    correct_answer = str(num_people)
    
    # Detailed Solution
    solution_text = (
        f"設{group}有 $x$ 位。<br>"
        f"依題意，「每人分 ${dist1}$ 個，剩下 ${leftover}$ 個」，表示{item}總數為 $({dist1}x + {leftover})$ 個。<br>"
        f"又「每人分 ${dist2}$ 個，不夠 ${shortage}$ 個」，表示{item}總數為 $({dist2}x - {shortage})$ 個。<br>"
        f"{item}總數不變，因此可列式：<br>"
        f"${dist1}x + {leftover} = {dist2}x - {shortage}$<br>"
        f"${leftover} + {shortage} = {dist2}x - {dist1}x$<br>"
        f"${leftover + shortage} = {dist2 - dist1}x$<br>"
        f"$x = \\frac{{{leftover + shortage}}}{{{dist2 - dist1}}} = {num_people}$<br>"
        f"所以{group}共有 ${num_people}$ 位。"
    )

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "solution_text": solution_text
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確，會自動從使用者輸入中提取數字進行比對。
    """
    # Attempt to extract the first number (integer or float) from the user's answer string.
    user_num_str = re.search(r'-?\d+\.?\d*', str(user_answer))
    is_correct = False
    
    if user_num_str:
        try:
            user_val = float(user_num_str.group())
            correct_val = float(correct_answer)
            if user_val == correct_val:
                is_correct = True
        except (ValueError, AttributeError):
            # Handle cases where conversion fails, though regex should prevent most.
            pass

    if is_correct:
        result_text = f"完全正確！答案是 ${correct_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer}$"
    
    return {"correct": is_correct, "result": result_text, "next_question": True}
