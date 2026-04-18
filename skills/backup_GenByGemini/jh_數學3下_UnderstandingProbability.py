import random
from fractions import Fraction

# Helper function
def is_prime(n):
    """Checks if a number is prime."""
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

def generate_bag_draw_problem():
    """Generates a problem about drawing items from a bag."""
    item_types = [
        ("黑球", "黃球"),
        ("巧克力", "糖果"),
        ("紅筆", "藍筆"),
        ("蘋果", "橘子")
    ]
    container_types = ["盒子中", "袋中有"]

    item_type1, item_type2 = random.choice(item_types)
    container = random.choice(container_types)

    count1 = random.randint(2, 25)
    count2 = random.randint(2, 25)

    # Ensure counts are different to avoid 50/50 probability every time
    while count1 == count2:
        count2 = random.randint(2, 25)

    total = count1 + count2

    # Choose which item to ask for
    if random.random() < 0.5:
        target_name = item_type1
        favorable_outcomes = count1
    else:
        target_name = item_type2
        favorable_outcomes = count2

    question_text = f"{container}有 {count1} 顆{item_type1}、{count2} 顆{item_type2}，從{container[:-1]}中任取一顆，每顆球被取出的機會都相等，則取出{target_name}的機率是多少？"

    prob = Fraction(favorable_outcomes, total)
    correct_answer = f"{prob.numerator}/{prob.denominator}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_numbered_items_problem():
    """Generates a problem about drawing numbered lots."""
    total_items = random.choice([10, 12, 15, 20, 25, 30])

    question_base = f"籤筒中有 {total_items} 支籤，將它們逐一標上 $1～{total_items}$ 的號碼，從籤筒中任意抽出一支籤，每一支籤被抽中的機會都相等，則"

    sub_type = random.choice(['multiple', 'comparison', 'property'])

    if sub_type == 'multiple':
        divisor = random.randint(2, 10)
        favorable_outcomes = total_items // divisor
        question_text = f"{question_base}抽到編號是 ${divisor}$ 的倍數的機率是多少？"

    elif sub_type == 'comparison':
        # val can be outside the range 1-total_items to create impossible/certain events
        comparison_val = random.randint(0, total_items + 1)
        direction = random.choice(['大於', '小於', '大於或等於', '小於或等於'])

        outcomes = range(1, total_items + 1)
        if direction == '大於':
            favorable_outcomes = len([x for x in outcomes if x > comparison_val])
        elif direction == '小於':
            favorable_outcomes = len([x for x in outcomes if x < comparison_val])
        elif direction == '大於或等於':
            favorable_outcomes = len([x for x in outcomes if x >= comparison_val])
        else:  # '小於或等於'
            favorable_outcomes = len([x for x in outcomes if x <= comparison_val])

        question_text = f"{question_base}抽到編號{direction} ${comparison_val}$ 的機率是多少？"

    else:  # 'property'
        prop = random.choice(['質數', '奇數', '偶數'])

        if prop == '質數':
            primes = [i for i in range(1, total_items + 1) if is_prime(i)]
            favorable_outcomes = len(primes)
        elif prop == '奇數':
            favorable_outcomes = (total_items + 1) // 2
        else:  # '偶數'
            favorable_outcomes = total_items // 2

        question_text = f"{question_base}抽到編號是{prop}的機率是多少？"

    if favorable_outcomes == 0:
        correct_answer = "0"
    elif favorable_outcomes == total_items:
        correct_answer = "1"
    else:
        prob = Fraction(favorable_outcomes, total_items)
        correct_answer = f"{prob.numerator}/{prob.denominator}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_dice_roll_problem():
    """Generates a problem about rolling a standard die."""
    total_outcomes = 6
    question_base = "投擲一顆均勻骰子，每一面出現的機會都相等，則"

    sub_type = random.choice(['specific_number', 'comparison', 'property'])

    if sub_type == 'specific_number':
        target_num = random.randint(1, 6)
        favorable_outcomes = 1
        question_text = f"{question_base}出現點數 ${target_num}$ 的機率是多少？"

    elif sub_type == 'comparison':
        # val from 0 to 7 to include impossible/certain events
        comparison_val = random.randint(0, 7)
        direction = random.choice(['大於', '小於', '大於或等於', '小於或等於'])

        outcomes = range(1, 7)
        if direction == '大於':
            favorable_outcomes = len([x for x in outcomes if x > comparison_val])
        elif direction == '小於':
            favorable_outcomes = len([x for x in outcomes if x < comparison_val])
        elif direction == '大於或等於':
            favorable_outcomes = len([x for x in outcomes if x >= comparison_val])
        else:  # '小於或等於'
            favorable_outcomes = len([x for x in outcomes if x <= comparison_val])

        question_text = f"{question_base}出現點數{direction} ${comparison_val}$ 的機率是多少？"

    else:  # 'property'
        prop = random.choice(['質數', '奇數', '偶數', '合數'])  # 合數=composite

        if prop == '質數':
            # {2, 3, 5}
            favorable_outcomes = 3
        elif prop == '奇數':
            # {1, 3, 5}
            favorable_outcomes = 3
        elif prop == '偶數':
            # {2, 4, 6}
            favorable_outcomes = 3
        else:  # '合數'
            # {4, 6}
            favorable_outcomes = 2

        question_text = f"{question_base}出現點數為{prop}的機率是多少？"

    if favorable_outcomes == 0:
        correct_answer = "0"
    elif favorable_outcomes == total_outcomes:
        correct_answer = "1"
    else:
        prob = Fraction(favorable_outcomes, total_outcomes)
        correct_answer = f"{prob.numerator}/{prob.denominator}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_card_draw_problem():
    """Generates a problem about drawing from a deck of cards."""
    total_outcomes = 52
    question_base = "從一副 52 張（不含鬼牌）的撲克牌中任意抽出一張，若每一張牌被抽中的機會均相等，則"

    sub_type = random.choice(['color', 'suit', 'rank', 'combo', 'number_vs_letter'])

    if sub_type == 'color':
        color = random.choice(['紅色', '黑色'])
        favorable_outcomes = 26
        question_text = f"{question_base}抽出的牌為{color}的機率是多少？"

    elif sub_type == 'suit':
        suit = random.choice(['黑桃', '紅心', '方塊', '梅花'])
        favorable_outcomes = 13
        question_text = f"{question_base}抽出的牌為{suit}的機率是多少？"

    elif sub_type == 'rank':
        rank = random.choice(['A', 'K', 'Q', 'J'] + [str(i) for i in range(2, 11)])
        favorable_outcomes = 4
        question_text = f"{question_base}抽出的牌為 ${rank}$ 的機率是多少？"

    elif sub_type == 'combo':
        color = random.choice(['紅色', '黑色'])
        rank = random.choice(['A', 'K', 'Q', 'J'])
        favorable_outcomes = 2
        question_text = f"{question_base}抽出的牌為{color} ${rank}$ 的機率是多少？"

    else:  # 'number_vs_letter'
        card_type = random.choice(['數字', '字母'])
        if card_type == '數字':
            # Ranks 2-10 are numbers (9 ranks) * 4 suits = 36 cards
            favorable_outcomes = 36
            question_text = f"{question_base}抽出的牌為{card_type}的機率是多少？"
        else:  # '字母' (A, K, Q, J)
            # 4 ranks * 4 suits = 16 cards
            favorable_outcomes = 16
            question_text = f"{question_base}抽出的牌為{card_type}的機率是多少？"

    prob = Fraction(favorable_outcomes, total_outcomes)
    correct_answer = f"{prob.numerator}/{prob.denominator}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def generate(level=1):
    """
    生成「機率」相關題目。
    包含：
    1. 從袋中抽物
    2. 抽數字籤
    3. 擲骰子
    4. 抽撲克牌
    """
    problem_type = random.choice(['bag_draw', 'numbered_items', 'dice_roll', 'card_draw'])

    if problem_type == 'bag_draw':
        return generate_bag_draw_problem()
    elif problem_type == 'numbered_items':
        return generate_numbered_items_problem()
    elif problem_type == 'dice_roll':
        return generate_dice_roll_problem()
    else:  # 'card_draw'
        return generate_card_draw_problem()


def check(user_answer, correct_answer):
    """
    檢查答案是否正確。答案可以是分數 (e.g., "3/5") 或數字 (e.g., "0", "1", "0.5")。
    """
    user_answer = user_answer.strip()
    is_correct = False

    try:
        # Evaluate correct answer as a float
        if '/' in correct_answer:
            num, den = map(int, correct_answer.split('/'))
            correct_val = num / den
        else:
            correct_val = float(correct_answer)

        # Evaluate user answer as a float. It could be a fraction or a decimal.
        if '/' in user_answer:
            num, den = map(int, user_answer.split('/'))
            if den == 0:  # Avoid division by zero
                user_val = float('inf') # Mark as incorrect
            else:
                user_val = num / den
        else:
            user_val = float(user_answer)

        # Compare the float values with a small tolerance
        if abs(user_val - correct_val) < 1e-9:
            is_correct = True

    except (ValueError, ZeroDivisionError):
        is_correct = False

    # Format the correct answer for display using LaTeX
    if correct_answer == "0":
        latex_answer = "0"
    elif correct_answer == "1":
        latex_answer = "1"
    elif '/' in correct_answer:
        num, den_str = correct_answer.split('/')
        if den_str == '1':
            latex_answer = num
        else:
            latex_answer = f"\\frac{{{num}}}{{{den_str}}}"
    else:
        latex_answer = correct_answer

    if is_correct:
        result_text = f"完全正確！答案是 ${latex_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${latex_answer}$"

    return {"correct": is_correct, "result": result_text, "next_question": True}