import random
import math
import re

def generate(level=1):
    """
    生成「一元一次不等式應用問題」相關題目。
    包含：
    1. 存款與目標問題
    2. 預算與折扣問題
    3. 分級折扣問題
    """
    problem_type = random.choice(['savings', 'budget', 'discount'])
    
    if problem_type == 'savings':
        return generate_savings_problem()
    elif problem_type == 'budget':
        return generate_budget_problem()
    else: # discount
        return generate_discount_problem()

def generate_savings_problem():
    """
    生成存款問題 (範例：筆電問題)
    情境：已有部分存款，每天固定存錢，要達到某個金額目標，求最少天數。
    """
    item = random.choice(['筆記型電腦', '智慧型手機', '遊戲機', '平板電腦'])
    total_cost = random.randint(150, 350) * 100
    initial_savings = random.randint(30, 80) * 100
    # 確保初始存款明顯少於目標金額
    while initial_savings >= total_cost * 0.7:
        initial_savings = random.randint(30, 80) * 100
        
    daily_savings = random.randint(5, 25) * 10
    
    # 不等式: initial_savings + daily_savings * x >= total_cost
    needed = total_cost - initial_savings
    min_x_float = needed / daily_savings
    
    # 天數 x 必須是整數，所以取無條件進位
    correct_x = math.ceil(min_x_float)
    
    question_text = (
        f"小妍想要購買一臺價值 ${total_cost}$ 元的{item}，"
        f"但現有存款僅 ${initial_savings}$ 元，若從今天開始每天存 ${daily_savings}$ 元，"
        f"至少需要存幾天，他才有足夠的錢購買這臺{item}？"
    )
    
    correct_answer = f"{correct_x} 天"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_budget_problem():
    """
    生成預算與折扣問題 (範例：蛋糕店問題)
    情境：在有折扣的情況下購買多樣商品，且總花費不超過預算，求最後一樣商品有幾種選擇。
    """
    max_attempts = 10
    for _ in range(max_attempts):
        discount_map = {90: '九', 85: '八五', 80: '八', 75: '七五'}
        discount_percent = random.choice(list(discount_map.keys()))
        discount_factor = discount_percent / 100
        discount_str = discount_map[discount_percent]

        budget = random.randint(300, 600)
        
        item1_price = random.randint(5, 9) * 10
        item2_price = random.randint(5, 9) * 10
        if item1_price == item2_price:
            continue
        item1_qty = 1
        item2_qty = random.randint(2, 3)
        
        fixed_cost = item1_price * item1_qty + item2_price * item2_qty
        
        # x <= (budget / discount_factor) - fixed_cost
        max_price = (budget / discount_factor) - fixed_cost
        if max_price < 40: # 確保有足夠空間給選項
            continue

        all_possible_prices = [p * 5 for p in range(8, 21)] # 40, 45, ..., 100
        options_pool = [p for p in all_possible_prices if p not in [item1_price, item2_price]]
        
        if len(options_pool) < 4: continue

        options = sorted(random.sample(options_pool, k=random.randint(4, 5)))
        valid_options_count = sum(1 for p in options if p <= max_price)
        
        # 確保題目有意義 (至少一個可選，一個不可選)
        if valid_options_count > 0 and valid_options_count < len(options):
            options_str = '、'.join([f"${p}$" for p in options])

            question_text = (
                f"蛋糕店週年慶，所有品項均享有{discount_str}折優惠。珊珊買了 {item1_qty} 片 ${item1_price}$ 元的黑森林、"
                f"{item2_qty} 片 ${item2_price}$ 元的法式草莓後，想再買 1 片不同品項的蛋糕，且總花費不超過 ${budget}$ 元，"
                f"則珊珊第 4 片蛋糕最多有幾種選擇？<br>"
                f"（店內其他蛋糕品項與價格為：${options_str}）"
            )

            correct_answer = f"{valid_options_count} 種"
            
            return {
                "question_text": question_text,
                "answer": correct_answer,
                "correct_answer": correct_answer
            }
    # 若多次嘗試失敗，則生成另一種題型
    return generate_savings_problem()

def generate_discount_problem():
    """
    生成分級折扣問題 (範例：書本折扣問題)
    情境：購買達一定數量有折扣，但買更多以取得更低折扣反而更便宜，求最少購買量。
    """
    max_attempts = 10
    discount_map_tier1 = {90: '九', 85: '八五', 80: '八'}
    discount_map_tier2 = {70: '七', 65: '六五', 60: '六'}
    
    for _ in range(max_attempts):
        item = random.choice(['書', 'T-shirt', '紀念品', '門票'])
        base_price = random.randint(20, 50) * 10
        
        tier2_threshold = random.choice([50, 60, 100])
        tier1_threshold = tier2_threshold - random.randint(20, 30)
        
        tier2_discount_percent = random.choice(list(discount_map_tier2.keys()))
        tier1_discount_percent_choices = [p for p in discount_map_tier1.keys() if p > tier2_discount_percent]
        if not tier1_discount_percent_choices: continue
        tier1_discount_percent = random.choice(tier1_discount_percent_choices)
        
        tier2_discount_str = discount_map_tier2[tier2_discount_percent]
        tier1_discount_str = discount_map_tier1[tier1_discount_percent]
            
        # x * tier1_discount > tier2_threshold * tier2_discount
        result_float = (tier2_threshold * tier2_discount_percent) / tier1_discount_percent
        correct_x = math.floor(result_float) + 1
        
        # 確保答案落在 tier1 的區間內，問題才有意義
        if tier1_threshold < correct_x < tier2_threshold:
            if item == '書': unit = '本'
            elif item == 'T-shirt': unit = '件'
            elif item == '門票': unit = '張'
            else: unit = '個'

            question_text = (
                f"某出版社優惠：購買數量超過 ${tier1_threshold}$ {unit}不足 ${tier2_threshold}$ {unit}，每{unit}打 {tier1_discount_str} 折；"
                f"${tier2_threshold}$ {unit}以上(含)每{unit}打 {tier2_discount_str} 折。"
                f"若學校想購買定價 ${base_price}$ 元的{item}，原預計購買數量在 ${tier1_threshold}$ 到 ${tier2_threshold}$ {unit}之間，"
                f"但發現一次購買 ${tier2_threshold}$ {unit}反而更便宜。問學校原本至少想購買幾{unit}{item}？"
            )
            
            correct_answer = f"{correct_x} {unit}"
            
            return {
                "question_text": question_text,
                "answer": correct_answer,
                "correct_answer": correct_answer
            }
    
    # 若多次嘗試失敗，則生成另一種題型
    return generate_savings_problem()

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    此版本會從答案中提取數字進行比較，以容納單位詞。
    """
    # 從使用者答案和正確答案中提取所有數字(包含小數點)
    user_num_str = ".".join(re.findall(r'\d+', user_answer))
    correct_num_str = ".".join(re.findall(r'\d+', correct_answer))
    
    is_correct = False
    # 只有在兩者都成功提取到數字時才進行比較
    if user_num_str and correct_num_str:
        try:
            if float(user_num_str) == float(correct_num_str):
                is_correct = True
        except ValueError:
            # 如果轉換失敗，則保持 is_correct 為 False
            pass
            
    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}