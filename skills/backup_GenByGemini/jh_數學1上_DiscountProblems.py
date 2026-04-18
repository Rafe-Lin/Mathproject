import random

def generate(level=1):
    """
    生成「折扣問題」相關題目 (標準 LaTeX 範本)。
    主要題型：
    已知某物原價比預算多 A 元，打折後比預算少 B 元，求預算為多少。
    """
    return generate_budget_discount_problem()

def generate_budget_discount_problem():
    """
    生成基於預算的折扣問題。
    方程式模型：(x + over_budget) * discount = x - under_budget
    """
    # 為了增加題目多樣性，定義一些可替換的詞語
    PEOPLE = ["阿樂", "小華", "志明", "文文", "哥哥", "姊姊"]
    ITEMS = ["一雙限量籃球鞋", "一台最新款的遊戲機", "一台筆記型電腦", "一件名牌外套", "演唱會的門票"]
    SCENES = [
        ("想在網路上購買", "一段時間後，他發現這商品還沒被買走，且變成"),
        ("看中", "剛好店家正在週年慶，這項商品變成"),
        ("的購物清單中有", "幾天後，他收到App通知，該商品正以")
    ]
    
    # 步驟 1: 生成能夠產生漂亮整數解的參數
    # 我們從答案 (預算) 開始反推，確保所有數字都合理
    
    budget = random.randint(40, 200) * 100  # 預算 x, e.g., 4000 ~ 20000
    
    # 決定一個常見的折扣
    discount_percent = random.choice([70, 75, 80, 85, 90])
    discount_decimal = discount_percent / 100
    
    # 根據折扣百分比生成中文說法 (e.g., 8 折, 7.5 折)
    if discount_percent % 10 == 0:
        discount_text = f"{discount_percent // 10} 折"
    else:
        discount_text = f"{discount_percent / 10:.1f} 折"
        
    # 步驟 2: 根據預算和折扣，計算合理的 `over_budget` 和 `under_budget`
    # 方程式: (budget + over_budget) * discount_decimal = budget - under_budget
    # 移項得: under_budget = budget * (1 - discount_decimal) - over_budget * discount_decimal
    # 為了使 under_budget > 0, 必須滿足:
    # budget * (1 - discount_decimal) > over_budget * discount_decimal
    # 亦即 over_budget < budget * (1 - discount_decimal) / discount_decimal
    
    max_over_budget = budget * (1 - discount_decimal) / discount_decimal
    
    over_budget = 0
    under_budget = 0
    
    # 使用迴圈尋找一組漂亮的數字 (例如都是 50 或 100 的倍數)
    attempts = 0
    while attempts < 100:
        # 在合理範圍內隨機選一個 `over_budget`
        # 範圍下限設為 500，上限設為最大值的 90% 以免 `under_budget` 過小
        lower_bound = 500
        upper_bound = max(int(max_over_budget * 0.9), lower_bound + 100)
        
        # 確保隨機範圍有效
        if lower_bound >= upper_bound:
            # 如果範圍無效，可能需要調整 budget 或 discount，但簡單重試即可
            budget = random.randint(40, 200) * 100
            max_over_budget = budget * (1 - discount_decimal) / discount_decimal
            attempts += 1
            continue

        # 選擇一個 100 的倍數
        temp_over_budget = random.randrange(lower_bound, upper_bound, 100)
        
        # 計算對應的 `under_budget`
        temp_under_budget_float = budget * (1 - discount_decimal) - temp_over_budget * discount_decimal
        
        # 檢查 `under_budget` 是否為正數且是漂亮的數字 (e.g., 50 的倍數)
        if temp_under_budget_float > 100 and temp_under_budget_float % 50 == 0:
            over_budget = temp_over_budget
            under_budget = int(temp_under_budget_float)
            break
        attempts += 1
    
    # 如果迴圈 100 次都失敗，就用一個固定的安全備案
    if over_budget == 0 or under_budget <= 0:
        budget = 7000
        over_budget = 1500
        under_budget = 200
        discount_text = "8 折"

    # 步驟 3: 組合題目文字
    person = random.choice(PEOPLE)
    item = random.choice(ITEMS)
    scene_start, scene_middle = random.choice(SCENES)
    
    part1 = f"{person}{scene_start}{item}，但售價比他的預算還多 ${over_budget}$ 元。"
    part2 = f"{scene_middle} ${discount_text}$ 促銷，"
    part3 = f"這樣算下來比他的預算還少 ${under_budget}$ 元。"
    question = f"請問{person}的預算為多少元？"
    
    question_text = f"{part1}<br>{part2}{part3}<br>{question}"
    
    correct_answer = str(budget)
    
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
    
    # 主要比對方法
    if user_answer == correct_answer:
        is_correct = True
    else:
        # 嘗試轉換為數字比對，以處理 "7000" vs "7000.0" 的情況
        try:
            if float(user_answer) == float(correct_answer):
                is_correct = True
        except (ValueError, TypeError):
            pass

    if is_correct:
        result_text = f"完全正確！答案就是 ${correct_answer}$ 元。"
    else:
        result_text = f"答案不正確。正確答案應為 ${correct_answer}$ 元。"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}