import random
from fractions import Fraction
import math

# --- Helper Functions ---

def is_prime(n):
    """Checks if a number is prime."""
    if n <= 1:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

def is_composite(n):
    """Checks if a number is composite."""
    if n <= 3:
        return False
    return not is_prime(n)

# --- Problem Generation Functions ---

def generate_coin_toss_problem():
    """
    Generates a question about tossing a coin multiple times.
    """
    n_tosses = random.choice([2, 3])
    total_outcomes = 2 ** n_tosses

    if n_tosses == 2:
        event_type = random.choice(['one_each', 'both_same'])
        if event_type == 'one_each':
            event_desc = "一次出現正面，另一次出現反面"
            favorable_outcomes = 2 # (正, 反), (反, 正)
        else: # both_same
            face = random.choice(['正面', '反面'])
            event_desc = f"兩次均出現{face}"
            favorable_outcomes = 1 # (正, 正) or (反, 反)
    else: # n_tosses == 3
        event_type = random.choice(['exact_one', 'exact_two', 'at_least_one_H', 'all_same'])
        if event_type == 'exact_one':
            face = random.choice(['正面', '反面'])
            event_desc = f"恰好一次出現{face}"
            favorable_outcomes = 3 # e.g., HTT, THT, TTH
        elif event_type == 'exact_two':
            face = random.choice(['正面', '反面'])
            event_desc = f"恰好兩次出現{face}"
            favorable_outcomes = 3 # e.g., HHT, HTH, THH
        elif event_type == 'at_least_one_H':
            event_desc = "至少出現一次正面"
            favorable_outcomes = 7 # All except (反, 反, 反)
        else: # all_same
            event_desc = "三次均為同一面"
            favorable_outcomes = 2 # (正, 正, 正) and (反, 反, 反)

    question_text = f"投擲一枚公正硬幣 ${n_tosses}$ 次，則{event_desc}的機率是多少？"
    
    answer_fraction = Fraction(favorable_outcomes, total_outcomes)
    correct_answer = f"{answer_fraction.numerator}/{answer_fraction.denominator}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_dice_roll_problem():
    """
    Generates a question about rolling two dice.
    """
    total_outcomes = 36
    
    problem_subtype = random.choice(['sum_value', 'sum_property', 'dice_property'])

    if problem_subtype == 'sum_value':
        target_sum = random.randint(3, 11)
        event_desc = f"兩顆骰子點數和為 ${target_sum}$"
        favorable_outcomes = 0
        for i in range(1, 7):
            for j in range(1, 7):
                if i + j == target_sum:
                    favorable_outcomes += 1
    
    elif problem_subtype == 'sum_property':
        prop = random.choice(['質數', '合數', '偶數', '大於9'])
        event_desc = f"兩顆骰子點數和為{prop}"
        favorable_outcomes = 0
        for i in range(1, 7):
            for j in range(1, 7):
                s = i + j
                is_favorable = False
                if prop == '質數' and is_prime(s): is_favorable = True
                if prop == '合數' and is_composite(s): is_favorable = True
                if prop == '偶數' and s % 2 == 0: is_favorable = True
                if prop == '大於9' and s > 9: is_favorable = True
                if is_favorable:
                    favorable_outcomes += 1
    
    else: # dice_property
        prop = random.choice(['質數', '合數', '偶數', '奇數'])
        event_desc = f"兩顆骰子點數皆為{prop}"
        
        count = 0
        for i in range(1, 7):
            is_favorable = False
            if prop == '質數' and is_prime(i): is_favorable = True
            if prop == '合數' and is_composite(i): is_favorable = True
            if prop == '偶數' and i % 2 == 0: is_favorable = True
            if prop == '奇數' and i % 2 != 0: is_favorable = True
            if is_favorable:
                count += 1
        favorable_outcomes = count * count

    question_text = f"投擲兩顆公正骰子一次，則{event_desc}的機率是多少？"
    
    answer_fraction = Fraction(favorable_outcomes, total_outcomes)
    correct_answer = f"{answer_fraction.numerator}/{answer_fraction.denominator}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_rock_paper_scissors_problem():
    """
    Generates a question about a rock-paper-scissors game.
    """
    p1 = random.choice(["阿輝", "小妍", "小明"])
    p2 = random.choice(["小華", "小翊", "小美"])
    while p1 == p2:
        p2 = random.choice(["小華", "小翊", "小美"])

    total_outcomes = 9
    event_type = random.choice(['win', 'lose', 'tie', 'decided'])

    if event_type == 'win':
        event_desc = f"{p1}贏"
        favorable_outcomes = 3
    elif event_type == 'lose':
        event_desc = f"{p1}輸"
        favorable_outcomes = 3
    elif event_type == 'tie':
        event_desc = "兩人平手"
        favorable_outcomes = 3
    else: # decided
        event_desc = "分出勝負"
        favorable_outcomes = 6

    question_text = (
        f"{p1}和{p2}玩猜拳遊戲，若兩人出剪刀、石頭、布的機會都相同，"
        f"且僅猜拳一次，則{event_desc}的機率是多少？"
    )

    answer_fraction = Fraction(favorable_outcomes, total_outcomes)
    correct_answer = f"{answer_fraction.numerator}/{answer_fraction.denominator}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_set_drawing_problem():
    """
    Generates a question about drawing items from two different sets.
    """
    if random.random() < 0.5:
        # Number card game variation
        p1_name = "小妍"
        p2_name = "小翊"
        
        all_cards = list(range(1, 12))
        random.shuffle(all_cards)
        
        p1_cards = sorted(all_cards[:4])
        p2_cards = sorted(all_cards[4:8])
        
        total_outcomes = len(p1_cards) * len(p2_cards)
        
        favorable_outcomes = sum(1 for c1 in p1_cards for c2 in p2_cards if c1 > c2)
        
        question_text = (
            f"{p1_name}、{p2_name}兩人各有 4 張數字牌，{p1_name}的牌是 ${', '.join(map(str, p1_cards))}$，"
            f"{p2_name}的牌是 ${', '.join(map(str, p2_cards))}$。兩人玩數字比大小遊戲，每次雙方各出一張牌，"
            f"數字較大者獲勝。試問第一次出牌時，{p1_name}獲勝的機率為多少？"
        )

        answer_fraction = Fraction(favorable_outcomes, total_outcomes)
        correct_answer = f"{answer_fraction.numerator}/{answer_fraction.denominator}"
        
    else:
        # Drawing numbered balls from two bags
        num_a = random.randint(2, 5)
        num_b = random.randint(2, 5)
        color_a = "紅"
        color_b = random.choice(["綠", "藍", "黃"])
        
        total_outcomes = num_a * num_b
        favorable_outcomes = min(num_a, num_b)

        question_text = (
            f"有甲、乙兩袋，甲袋中有 ${num_a}$ 顆{color_a}球，分別編號 1 到 ${num_a}$；"
            f"乙袋中有 ${num_b}$ 顆{color_b}球，也分別編號 1 到 ${num_b}$。"
            "今從甲、乙兩袋中各取一球，若每一袋中每顆球被取出的機會都相等，"
            "則兩袋所取出的球編號相同的機率是多少？"
        )
        answer_fraction = Fraction(favorable_outcomes, total_outcomes)
        correct_answer = f"{answer_fraction.numerator}/{answer_fraction.denominator}"
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    Generates a question about tree diagrams and probability.
    """
    problem_type = random.choice([
        'coin_toss', 'dice_roll', 'rock_paper_scissors', 'set_drawing'
    ])
    
    if problem_type == 'coin_toss':
        return generate_coin_toss_problem()
    elif problem_type == 'dice_roll':
        return generate_dice_roll_problem()
    elif problem_type == 'rock_paper_scissors':
        return generate_rock_paper_scissors_problem()
    else: # 'set_drawing'
        return generate_set_drawing_problem()

def check(user_answer, correct_answer):
    """
    Checks if the user's answer is correct for probability questions.
    Handles fractions, decimals, and whole numbers.
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    is_correct = False

    try:
        # Compare as fractions to handle equivalent forms (e.g., 2/4 vs 1/2)
        user_frac = Fraction(user_answer)
        correct_frac = Fraction(correct_answer)
        if user_frac == correct_frac:
            is_correct = True
    except (ValueError, ZeroDivisionError):
        # Fallback for non-fractional input, though unlikely for this skill
        if user_answer.upper() == correct_answer.upper():
            is_correct = True
    
    # Format the correct answer nicely using LaTeX for feedback
    final_frac = Fraction(correct_answer)
    if final_frac.denominator == 1:
        correct_answer_str = str(final_frac.numerator)
    else:
        # Use double backslashes for LaTeX commands in Python strings
        correct_answer_str = f"\\frac{{{final_frac.numerator}}}{{{final_frac.denominator}}}"

    if is_correct:
        result_text = f"完全正確！答案是 ${correct_answer_str}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer_str}$"

    return {"correct": is_correct, "result": result_text, "next_question": True}