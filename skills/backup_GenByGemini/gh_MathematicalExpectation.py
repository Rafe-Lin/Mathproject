import random
from fractions import Fraction
import math

# Helper function for combinations C(n, k)
def combinations(n, k):
    """
    Calculates the number of combinations C(n, k).
    """
    if k < 0 or k > n:
        return 0
    if k == 0 or k == n:
        return 1
    if k > n // 2:
        k = n - k
    res = 1
    for i in range(k):
        res = res * (n - i) // (i + 1)
    return res

def generate_dice_problem(level):
    """
    Generates a mathematical expectation problem based on a dice roll.
    Presents different payouts based on the outcome of a fair die.
    """
    dice_sides = 6
    outcomes = list(range(1, dice_sides + 1))
    
    # Use 2 groups for level 1, 3 groups for higher levels to increase complexity
    num_groups = random.choice([2, 3]) if level < 2 else 3 
    
    payouts = []
    probabilities = []
    
    if num_groups == 2:
        # Split dice outcomes into two groups
        split_point = random.randint(1, dice_sides - 1)
        group1 = outcomes[:split_point]
        group2 = outcomes[split_point:]
        
        value1 = random.randint(5, 50) * 10 # Payouts in multiples of 10
        value2 = random.randint(5, 50) * 10
        # Ensure values are distinct for a more interesting problem
        while value1 == value2:
            value2 = random.randint(5, 50) * 10
            
        payouts.append(value1)
        probabilities.append(Fraction(len(group1), dice_sides))
        payouts.append(value2)
        probabilities.append(Fraction(len(group2), dice_sides))
        
        question_text = (f"擲一粒公正骰子。已知擲出點數為 ${{', '.join(map(str, group1))}}$ 時可得 ${value1}$ 元；"
                         f"擲出點數為 ${{', '.join(map(str, group2))}}$ 時可得 ${value2}$ 元，"
                         f"求擲骰子一次所得金額的期望值。")
        
    else: # num_groups == 3
        # Split dice outcomes into three groups
        split1 = random.randint(1, dice_sides - 2)
        split2 = random.randint(split1 + 1, dice_sides - 1)
        
        group1 = outcomes[:split1]
        group2 = outcomes[split1:split2]
        group3 = outcomes[split2:]
        
        value1 = random.randint(5, 50) * 10
        value2 = random.randint(5, 50) * 10
        value3 = random.randint(5, 50) * 10
        
        # Ensure values are unique
        while len(set([value1, value2, value3])) < 3:
            value1 = random.randint(5, 50) * 10
            value2 = random.randint(5, 50) * 10
            value3 = random.randint(5, 50) * 10

        payouts.append(value1)
        probabilities.append(Fraction(len(group1), dice_sides))
        payouts.append(value2)
        probabilities.append(Fraction(len(group2), dice_sides))
        payouts.append(value3)
        probabilities.append(Fraction(len(group3), dice_sides))
        
        question_text = (f"擲一粒公正骰子。已知擲出點數為 ${{', '.join(map(str, group1))}}$ 時可得 ${value1}$ 元；"
                         f"擲出點數為 ${{', '.join(map(str, group2))}}$ 時可得 ${value2}$ 元；"
                         f"擲出點數為 ${{', '.join(map(str, group3))}}$ 時可得 ${value3}$ 元，"
                         f"求擲骰子一次所得金額的期望值。")

    expected_value = sum(p * x for p, x in zip(probabilities, payouts))
    correct_answer = f"{expected_value:.2f}".rstrip('0').rstrip('.')

    return {
        "question_text": question_text,
        "answer": str(expected_value),
        "correct_answer": correct_answer
    }

def generate_coin_flip_problem(level):
    """
    Generates a mathematical expectation problem based on flipping multiple coins.
    Payouts are determined by the number of heads.
    """
    num_coins = random.randint(2, 3) if level < 3 else random.randint(3, 4) # More coins for higher levels
    total_outcomes = 2**num_coins
    
    possible_heads = list(range(num_coins + 1)) # Outcomes: 0, 1, ..., num_coins heads
    
    payout_conditions = []
    payouts_values = []
    
    # Generate payouts, allowing negative ones for higher levels (representing losses)
    min_payout = -100 if level >= 2 else 0
    max_payout = 150
    
    for _ in range(num_coins + 1):
        payouts_values.append(random.randint(min_payout // 5, max_payout // 5) * 5)
    
    # Ensure payouts are distinct where possible for more varied problems
    if num_coins > 1 and len(set(payouts_values)) < num_coins + 1:
        unique_payouts = set()
        for i in range(len(payouts_values)):
            original_payout = payouts_values[i]
            while payouts_values[i] in unique_payouts:
                payouts_values[i] = random.randint(min_payout // 5, max_payout // 5) * 5
                if payouts_values[i] == original_payout: # Avoid infinite loop if range too small
                    payouts_values[i] += 5 # Perturb to find a unique value
            unique_payouts.add(payouts_values[i])
            
    expected_value = 0
    
    for k_heads in possible_heads:
        prob = Fraction(combinations(num_coins, k_heads), total_outcomes)
        payout = payouts_values[k_heads]
        
        expected_value += payout * prob
        
        if payout >= 0:
            payout_conditions.append(f"出現 ${k_heads}$ 個正面時可得 ${payout}$ 元")
        else:
            payout_conditions.append(f"出現 ${k_heads}$ 個正面時須付給莊家 ${abs(payout)}$ 元")
            
    question_text = f"同時丟 ${num_coins}$ 枚均勻的硬幣。已知" + "；".join(payout_conditions) + "。求丟一次所得金額的期望值為多少？"
    
    correct_answer = f"{expected_value:.2f}".rstrip('0').rstrip('.')

    return {
        "question_text": question_text,
        "answer": str(expected_value),
        "correct_answer": correct_answer
    }

def generate_bag_draw_problem(level):
    """
    Generates a mathematical expectation problem involving drawing items from a bag.
    Can either ask for expected money/value or expected count of a specific item.
    """
    num_type_A = random.randint(2, 5)
    num_type_B = random.randint(2, 5)
    
    total_items = num_type_A + num_type_B
    
    # Number of items to draw
    k_draw = random.randint(2, min(total_items -1, num_type_A + num_type_B -1))
    while k_draw == 1 or k_draw == total_items: # Regenerate if k_draw is trivial (draw 1 or all)
         k_draw = random.randint(2, min(total_items -1, num_type_A + num_type_B -1))

    # Ensure there are at least two distinct outcomes possible for the number of items drawn
    if (min(k_draw, num_type_A) - max(0, k_draw - num_type_B) + 1) < 2:
        return generate_bag_draw_problem(level)
        
    # Define various item types and their associated properties (container, action, units, problem focus)
    item_type_data = [
        {"item_A": "紅球", "item_B": "白球", "focus": "money", "container": "箱中", "action": "同時取出", "unit_plural": "顆球", "unit_base": "顆"}, 
        {"item_A": "200元商品卡", "item_B": "100元商品卡", "focus": "money", "container": "袋中", "action": "任取", "unit_plural": "張商品卡", "unit_base": "張"}, 
        {"item_A": "芝麻湯圓", "item_B": "花生湯圓", "focus": "count", "container": "鍋中", "action": "任意舀取", "unit_plural": "顆湯圓", "unit_base": "顆"}, 
        {"item_A": "黃肉哈密瓜", "item_B": "綠肉哈密瓜", "focus": "count", "container": "盤中", "action": "選出", "unit_plural": "顆哈密瓜", "unit_base": "顆"}, 
        {"item_A": "土雞蛋", "item_B": "普通雞蛋", "focus": "count", "container": "盤中", "action": "任取", "unit_plural": "顆滷蛋", "unit_base": "顆"}
    ]
    
    selected_item_data = random.choice(item_type_data)
    item_A_name = selected_item_data["item_A"]
    item_B_name = selected_item_data["item_B"]
    problem_focus = selected_item_data["focus"]
    container = selected_item_data["container"]
    action = selected_item_data["action"]
    unit_plural = selected_item_data["unit_plural"]
    unit_base = selected_item_data["unit_base"]

    total_combinations = combinations(total_items, k_draw)
    
    outcomes_desc = []
    expected_value = 0
    
    # Possible counts of item A that can be drawn
    possible_A_counts = range(max(0, k_draw - num_type_B), min(k_draw, num_type_A) + 1)
    
    if problem_focus == "money":
        payouts = {}
        payout_base = 50 if level == 1 else 100 # Payout base scales with level
        for k_A in possible_A_counts:
            payouts[k_A] = random.randint(1, 10) * payout_base
        
        # Ensure payouts are distinct where possible
        if len(set(payouts.values())) < len(payouts): 
            unique_payouts = set()
            for k_A in possible_A_counts:
                original_payout = payouts[k_A]
                while payouts[k_A] in unique_payouts:
                    payouts[k_A] = random.randint(1, 10) * payout_base
                    if payouts[k_A] == original_payout: # Avoid infinite loop
                        payouts[k_A] += payout_base // 2
                unique_payouts.add(payouts[k_A])

        for k_A in possible_A_counts:
            k_B = k_draw - k_A
            num_ways = combinations(num_type_A, k_A) * combinations(num_type_B, k_B)
            if num_ways == 0: continue
                
            prob = Fraction(num_ways, total_combinations)
            payout = payouts[k_A]
            
            # Construct descriptive phrase for the outcome
            if k_A == 0:
                desc_phrase = f"取出 ${k_B}$ {unit_base} {item_B_name}"
            elif k_B == 0:
                desc_phrase = f"取出 ${k_A}$ {unit_base} {item_A_name}"
            else:
                desc_phrase = f"取出 ${k_A}$ {unit_base} {item_A_name} 及 ${k_B}$ {unit_base} {item_B_name}"
                
            outcomes_desc.append(f"{desc_phrase} 時，可得獎金 ${payout}$ 元")
            expected_value += payout * prob
            
        question_text = (f"{container}裝有大小相同的 ${num_type_A}${unit_base} {item_A_name} 與 ${num_type_B}${unit_base} {item_B_name}。"
                         f"從{container}{action}{k_draw}{unit_plural}，已知" + "；".join(outcomes_desc) + "。求獎金的期望值。")
        
    else: # problem_focus == "count" (e.g., expected number of certain items)
        target_item_name = item_A_name # The problem asks for the count of item A
        
        for k_A in possible_A_counts:
            k_B = k_draw - k_A
            num_ways = combinations(num_type_A, k_A) * combinations(num_type_B, k_B)
            if num_ways == 0: continue
            prob = Fraction(num_ways, total_combinations)
            expected_value += k_A * prob # The "value" for expectation is the count k_A
        
        # Adapt question wording based on the specific item type
        if "商品卡" in item_A_name: 
             question_text = (f"{container}裝有大小相同的 ${num_type_A}$ {item_A_name} 與 ${num_type_B}$ {item_B_name}。"
                              f"從{container}{action}{k_draw}{unit_plural}，求取出 {target_item_name.split('元')[0].strip()} 商品卡個數的期望值。")
        elif "哈密瓜" in item_A_name:
             question_text = (f"老闆準備外形相近的 ${item_A_name} {num_type_A}$ {unit_base}與 ${item_B_name} {num_type_B}$ {unit_base}，"
                              f"要求此人從中{action}{k_draw}{unit_base}哈密瓜。已知此人對這兩種哈密瓜沒有鑑別能力，完全靠運氣選取，"
                              f"求此人選出 {target_item_name} 個數的期望值。")
        elif "蛋" in item_A_name:
            question_text = (f"{container}裝有 ${num_type_A}$ {unit_base} {item_A_name} 及 ${num_type_B}$ {unit_base} {item_B_name} 所做成滷蛋。"
                              f"從{container}{action}{k_draw}{unit_plural}，求取出由 {target_item_name} 所做成滷蛋的個數之期望值。")
        else: # Generic wording for balls, tangyuan etc.
             question_text = (f"{container}裝有 ${num_type_A}$ {unit_base} {item_A_name} 及 ${num_type_B}$ {unit_base} {item_B_name}。"
                              f"從{container}{action}{k_draw}{unit_plural}，求舀取到 {target_item_name} 個數的期望值。")
    
    correct_answer = f"{expected_value:.2f}".rstrip('0').rstrip('.')

    return {
        "question_text": question_text,
        "answer": str(expected_value),
        "correct_answer": correct_answer
    }

def generate_insurance_problem(level):
    """
    Generates a mathematical expectation problem for an insurance scenario.
    Calculates the expected profit for the insurance company or expected gain/loss for policyholder.
    """
    event_name_options = [
        "住宅房屋發生火災", "一位50歲的人在一年內死亡", "發生嚴重交通意外"
    ]
    event_name = random.choice(event_name_options)
    policy_term = random.choice(["一年期", "兩年期"])
    
    prob_event_occur = random.uniform(0.0001, 0.0025) # Probability of the insured event occurring (usually small)
    prob_event_occur = round(prob_event_occur, 4)
    if prob_event_occur == 0: prob_event_occur = 0.0001 # Ensure non-zero probability
    
    claim_amount = random.randint(10, 50) * 100_000 # Claim amount (e.g., 1,000,000 to 5,000,000)

    # Ensure premium generates a positive expected profit for the company
    min_premium_for_profit = claim_amount * prob_event_occur
    premium = random.randint(math.ceil(min_premium_for_profit) + 100, math.ceil(min_premium_for_profit) + 5000)
    
    profit_event_not_occur = premium # Company keeps premium if event does not occur
    profit_event_occur = premium - claim_amount # Company's profit if event occurs (usually a loss)
    
    prob_event_not_occur = 1 - prob_event_occur
    
    expected_profit_company = (profit_event_not_occur * prob_event_not_occur) + \
                              (profit_event_occur * prob_event_occur)
    
    # Randomly choose perspective: company's profit or policyholder's gain/loss
    if random.random() < 0.7 or level < 3: 
        # Most common: Ask for company's expected profit
        question_text = (f"根據統計資料得知，{event_name}的機率為 ${prob_event_occur}$。保險公司推出「投保{policy_term}人壽保險，"
                         f"在投保期間{event_name.split('在一年內')[-1].strip()}，保戶可獲理賠金 ${claim_amount}$ 元；否則不予理賠。」"
                         f"已知此{policy_term}保險的保費為 ${premium}$ 元，求保險公司對於每份保單的利潤期望值。")
        final_expected_value = expected_profit_company
    else: 
        # More challenging: Ask for policyholder's expected gain/loss
        question_text = (f"根據統計資料得知，{event_name}的機率為 ${prob_event_occur}$。某人投保{policy_term}人壽保險，"
                         f"在投保期間{event_name.split('在一年內')[-1].strip()}，可獲理賠金 ${claim_amount}$ 元；否則不予理賠。"
                         f"已知此{policy_term}保險的保費為 ${premium}$ 元，求此保戶玩這個遊戲一次的所得金額期望值是多少？")
        final_expected_value = -expected_profit_company # Policyholder's gain is company's loss

    correct_answer = f"{final_expected_value:.2f}".rstrip('0').rstrip('.')

    return {
        "question_text": question_text,
        "answer": str(final_expected_value),
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    Generates a mathematical expectation problem based on the specified level.
    """
    problem_types = {
        1: [generate_dice_problem, generate_coin_flip_problem],
        2: [generate_coin_flip_problem, generate_bag_draw_problem],
        3: [generate_bag_draw_problem, generate_insurance_problem]
    }
    
    # Select problem types based on the level
    selected_type_generators = problem_types.get(level, problem_types[1]) # Default to level 1 if invalid level
    
    # Choose a random problem generator from the selected types
    problem_func = random.choice(selected_type_generators)
    return problem_func(level)

def check(user_answer, correct_answer):
    """
    Checks if the user's answer is correct for a mathematical expectation problem.
    Compares float values for accuracy and provides feedback.
    """
    is_correct = False
    feedback = ""
    
    user_answer_stripped = user_answer.strip()
    
    try:
        user_float = float(user_answer_stripped)
        correct_float = float(correct_answer)
        
        # Check for near equality due to potential floating point precision issues
        if abs(user_float - correct_float) < 1e-6:
            is_correct = True
            feedback = f"完全正確！答案是 ${correct_answer}$。"
        else:
            feedback = (f"答案不正確。您的答案是 ${user_answer_stripped}$，"
                        f"但正確答案應為：${correct_answer}$")
    except ValueError:
        feedback = (f"答案格式不正確，請輸入一個數字。您輸入的是 ${user_answer_stripped}$。")

    return {"correct": is_correct, "result": feedback, "next_question": True}