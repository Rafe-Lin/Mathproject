import random
from fractions import Fraction

def generate(level=1):
    """
    生成「解的合理性」相關題目。
    題型包含：
    1. 購物情境：購買數量必須為正整數。
    2. 分物情境：平分後必須可以整除。
    3. 存錢情境：存錢天數/週數必須為正整數。
    """
    problem_type = random.choice(['shopping', 'grouping', 'saving'])

    if problem_type == 'shopping':
        return generate_shopping_problem()
    elif problem_type == 'grouping':
        return generate_grouping_problem()
    else:  # saving
        return generate_saving_problem()

def generate_shopping_problem():
    """
    生成購物情境題。
    例：買了 4 張全票和 x 張優待票，總花費是否合理。
    """
    # Contexts: (item1, item2, scenario_verb)
    contexts = [
        ("全票", "優待票", "去游泳池游泳"),
        ("原子筆", "鉛筆", "去文具店買文具"),
        ("大杯紅茶", "中杯奶茶", "去飲料店買飲料")
    ]
    person = random.choice(["琦瑋", "巴奈", "小華", "小明"])
    item1, item2, scenario_verb = random.choice(contexts)

    price1 = random.randint(5, 15) * 10
    price_diff = random.randint(1, 4) * 10
    price2 = price1 - price_diff
    qty1 = random.randint(2, 5)

    is_reasonable = random.choice([True, False])

    if is_reasonable:
        # 變數 x (item2 的數量) 必須是正整數
        x = random.randint(2, 8)
        total_cost = price1 * qty1 + price2 * x
        correct_answer = "合理"
    else:
        # 變數 x (item2 的數量) 會是分數或小數
        # 為了確保這一點，我們先用一個整數 x 算出基準總價，再加上一個無法被 price2 整除的餘數
        base_x = random.randint(2, 8)
        base_total = price1 * qty1 + price2 * base_x
        offset = random.randint(1, price2 - 1)
        total_cost = base_total + offset
        correct_answer = "不合理"

    question_text = (
        f"{person}和家人{scenario_verb}，買了 {qty1} 張{item1}和若干張{item2}。"
        f"已知一張{item1} {price1} 元，比一張{item2}貴 {price_diff} 元。"
        f"{person}計算後認為應付 {total_cost} 元，請問這個付費金額是否合理？"
        f"（提示：購買的物品數量必須是正整數）"
    )

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_grouping_problem():
    """
    生成分物情境題。
    例：將 M 個糖果平分給 N 個人，每人拿 K 個，是否能剛好分完。
    """
    contexts = [
        ("老師", "糖果", "學生", "顆", "位"),
        ("媽媽", "果凍", "盤子", "個", "個"),
        ("農夫", "橘子", "箱子", "顆", "個")
    ]
    person, item, group, item_unit, group_unit = random.choice(contexts)

    group_size = random.randint(4, 12)
    num_groups = random.randint(5, 20)

    is_reasonable = random.choice([True, False])

    if is_reasonable:
        # 總數可以被每組數量整除
        total_items = group_size * num_groups
        correct_answer = "合理"
    else:
        # 總數除以每組數量會有餘數
        remainder = random.randint(1, group_size - 1)
        total_items = group_size * num_groups + remainder
        correct_answer = "不合理"

    question_text = (
        f"{person}有 {total_items} {item_unit}{item}，想平分給若干{group_unit}{group}，"
        f"且每個{group}要分到 {group_size} {item_unit}。"
        f"{person}認為剛好可以分完，請問這個想法是否合理？"
    )

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_saving_problem():
    """
    生成儲蓄情境題。
    例：原有 A 元，每天存 B 元，若干天後是否可能剛好有 C 元。
    """
    person = random.choice(["小明", "小華", "志玲", "承旭"])
    initial_money = random.randint(20, 100) * 10
    saving_rate = random.randint(2, 10) * 10
    time_unit = random.choice(['天', '週'])

    is_reasonable = random.choice([True, False])

    if is_reasonable:
        # 時間單位 x 是正整數
        x = random.randint(5, 25)
        target_amount = initial_money + saving_rate * x
        correct_answer = "合理"
    else:
        # 時間單位 x 不是整數
        base_x = random.randint(5, 25)
        base_total = initial_money + saving_rate * base_x
        offset = random.randint(1, saving_rate - 1)
        target_amount = base_total + offset
        correct_answer = "不合理"

    question_text = (
        f"{person}原本有 {initial_money} 元，他決定每{time_unit}存 {saving_rate} 元。"
        f"他認為經過若干{time_unit}後，他的存款總額可以剛好達到 {target_amount} 元。"
        f"請問{person}的這個目標設定是否合理？"
        f"（提示：存款的{time_unit}數必須是正整數）"
    )

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

    is_correct = (user_answer == correct_answer)

    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"

    return {"correct": is_correct, "result": result_text, "next_question": True}
