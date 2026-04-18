import random
import re

# Item pool: (more_expensive_item, cheaper_item, unit)
ITEM_POOL = [
    ('全票', '學生票', '張'),
    ('筆記本', '原子筆', '枝'),
    ('蛋', '豆腐', '盒'),
    ('蘋果', '橘子', '個'),
    ('漢堡', '薯條', '份'),
    ('外套', 'T恤', '件')
]

# Name pool
NAME_POOL = ['小明', '小華', '心怡', '志成', '曉君', '家豪']

def generate(level=1):
    """
    生成「成本問題」相關的一元一次方程式應用題。
    包含：
    1. 基本加法關係成本問題
    2. 找零錢相關的成本問題
    3. 倍數關係成本問題
    """
    problem_type = random.choice(['basic_additive', 'change_calculation', 'multiplicative_relationship'])

    if problem_type == 'basic_additive':
        return generate_basic_additive_problem()
    elif problem_type == 'change_calculation':
        return generate_change_calculation_problem()
    else: # multiplicative_relationship
        return generate_multiplicative_relationship_problem()

def generate_basic_additive_problem():
    """
    題型：A 比 B 貴 d 元，買 n_a 個 A 和 n_b 個 B 共 C 元，求 A 和 B 的單價。
    """
    # 1. 選擇素材
    name = random.choice(NAME_POOL)
    item_a, item_b, unit = random.choice(ITEM_POOL)

    # 2. 生成數值 (反向計算以確保答案為整數)
    # 設 item_b (便宜的) 單價為 x
    price_b = random.randint(10, 80) * 5 # 讓價格是 5 的倍數，較常見
    # A 比 B 貴 d 元
    diff = random.randint(2, 10) * 5
    price_a = price_b + diff

    # 購買數量
    n_a = random.randint(1, 5)
    n_b = random.randint(1, 5)
    # 避免總數太少或其中一方為零
    while n_a + n_b < 3:
        n_a = random.randint(1, 5)
        n_b = random.randint(1, 5)
    
    # 總金額
    total_cost = n_a * price_a + n_b * price_b

    # 3. 組合題目文字
    question_text = (
        f"{name}買了 {n_a} {unit}{item_a}和 {n_b} {unit}{item_b}，共花了 {total_cost} 元。"
        f"已知 1 {unit}{item_a}比 1 {unit}{item_b}貴 {diff} 元，"
        f"請問 1 {unit}{item_a}和 1 {unit}{item_b}的價錢分別為多少元？"
    )

    # 4. 產生答案
    # 格式：便宜的在前，貴的在後
    correct_answer = f"1 {unit}{item_b} {price_b} 元,1 {unit}{item_a} {price_a} 元"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_change_calculation_problem():
    """
    題型：拿 P 元買 A 和 B，找回 R 元。A 比 B 貴 d 元，求 A 和 B 的單價。
    """
    # 1. 選擇素材
    name = random.choice(NAME_POOL)
    item_a, item_b, unit = random.choice(ITEM_POOL)

    # 2. 生成數值
    price_b = random.randint(15, 100)
    diff = random.randint(10, 50)
    price_a = price_b + diff

    n_a = random.randint(1, 4)
    n_b = random.randint(1, 4)
    while n_a + n_b < 3:
        n_a = random.randint(1, 4)
        n_b = random.randint(1, 4)

    total_cost = n_a * price_a + n_b * price_b
    
    # 生成支付金額和找零
    # 支付金額需為百元或五十元鈔的倍數，且比總價高
    if total_cost < 450:
        payment = 500
    elif total_cost < 950:
        payment = 1000
    else:
        payment = (total_cost // 500 + 1) * 500
    
    # 確保找零不是0
    if payment == total_cost:
        payment += 100

    change = payment - total_cost

    # 3. 組合題目文字
    question_text = (
        f"{name}拿 {payment} 元買了 {n_a} {unit}{item_a}和 {n_b} {unit}{item_b}，找回 {change} 元。"
        f"已知 1 {unit}{item_a}比 1 {unit}{item_b}貴 {diff} 元，"
        f"請問 1 {unit}{item_a}和 1 {unit}{item_b}的價錢分別為多少元？"
    )
    
    # 4. 產生答案
    correct_answer = f"1 {unit}{item_b} {price_b} 元,1 {unit}{item_a} {price_a} 元"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_multiplicative_relationship_problem():
    """
    題型：A 的價錢是 B 的 k 倍，買 n_a 個 A 和 n_b 個 B 共 C 元，求 A 和 B 的單價。
    """
    # 1. 選擇素材
    name = random.choice(NAME_POOL)
    item_a, item_b, unit = random.choice(ITEM_POOL)

    # 2. 生成數值
    # 設 item_b (便宜的) 單價為 x
    price_b = random.randint(10, 50) * 5
    # A 的價錢是 B 的 k 倍
    multiple = random.choice([2, 3, 4])
    price_a = price_b * multiple

    # 購買數量
    n_a = random.randint(1, 4)
    n_b = random.randint(1, 5)
    while n_a + n_b < 3:
        n_a = random.randint(1, 4)
        n_b = random.randint(1, 5)
        
    # 總金額
    total_cost = n_a * price_a + n_b * price_b
    
    # 3. 組合題目文字
    question_text = (
        f"{name}買了 {n_a} {unit}{item_a}和 {n_b} {unit}{item_b}，共花了 {total_cost} 元。"
        f"已知 1 {unit}{item_a}的價錢剛好是 1 {unit}{item_b}的 {multiple} 倍，"
        f"請問 1 {unit}{item_a}和 1 {unit}{item_b}的價錢分別為多少元？"
    )
    
    # 4. 產生答案
    correct_answer = f"1 {unit}{item_b} {price_b} 元,1 {unit}{item_a} {price_a} 元"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    答案格式為「商品A 價格A 元, 商品B 價格B 元」。
    檢查時會忽略單位、商品名稱、順序，只比對數字是否正確。
    """
    # 從正確答案中提取數字
    correct_numbers = set(re.findall(r'\d+', correct_answer))
    
    # 從使用者答案中提取數字
    user_numbers = set(re.findall(r'\d+', user_answer))
    
    is_correct = (correct_numbers == user_numbers) and (len(correct_numbers) > 0)
    
    if is_correct:
        result_text = f"完全正確！答案是 {correct_answer}。"
    else:
        result_text = f"答案不正確。正確答案應為：{correct_answer}"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}
