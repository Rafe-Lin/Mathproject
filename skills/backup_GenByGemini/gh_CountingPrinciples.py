import random
import math
from fractions import Fraction

def generate(level=1):
    """
    生成「計數原理」相關題目。
    包括：窮舉法、乘法原理、加法原理、取捨原理。
    """
    problem_type = random.choice([
        'coin_combinations',
        'game_outcomes',
        'simple_multiplication',
        'divisors_count',
        'addition_principle_scenarios',
        'inclusion_exclusion_2sets'
    ])

    if level == 1:
        problem_type = random.choice([
            'coin_combinations',
            'simple_multiplication',
            'addition_principle_scenarios',
            'inclusion_exclusion_2sets'
        ])
    elif level == 2:
        problem_type = random.choice([
            'game_outcomes',
            'divisors_count',
            'addition_principle_scenarios',
            'inclusion_exclusion_2sets'
        ])
    elif level == 3:
         problem_type = random.choice([
            'divisors_count',
            'inclusion_exclusion_2sets_complex' # A slightly harder version, maybe 3 sets later
        ])

    if problem_type == 'coin_combinations':
        return generate_coin_combinations_problem()
    elif problem_type == 'game_outcomes':
        return generate_game_outcomes_problem()
    elif problem_type == 'simple_multiplication':
        return generate_simple_multiplication_problem()
    elif problem_type == 'divisors_count':
        return generate_divisors_count_problem()
    elif problem_type == 'addition_principle_scenarios':
        return generate_addition_principle_scenarios_problem()
    elif problem_type == 'inclusion_exclusion_2sets':
        return generate_inclusion_exclusion_2sets_problem()
    elif problem_type == 'inclusion_exclusion_2sets_complex':
        return generate_inclusion_exclusion_2sets_complex_problem() # Just a placeholder, using normal 2-sets for now.

def get_prime_factorization(n):
    factors = {}
    d = 2
    temp = n
    while d * d <= temp:
        while temp % d == 0:
            factors[d] = factors.get(d, 0) + 1
            temp //= d
        d += 1
    if temp > 1:
        factors[temp] = factors.get(temp, 0) + 1
    return factors

def generate_coin_combinations_problem():
    """
    題目: 只用X元硬幣或Y元硬幣支付Z元貨款，共有多少種支付方法？
    """
    coin1 = random.choice([5, 10, 20])
    coin2 = random.choice([50, 100])
    
    # Ensure coin values are different
    while coin1 == coin2:
        coin2 = random.choice([50, 100])

    # Target amount should be a multiple of GCD of coin1 and coin2 for integer solutions
    # And large enough to have a few combinations
    # Make sure target is a multiple of smallest coin for simplicity
    min_coin = min(coin1, coin2)
    max_coin = max(coin1, coin2)
    
    target_amount = random.randint(max_coin * 2 // min_coin, max_coin * 5 // min_coin) * min_coin
    
    if target_amount == 0: # Prevent 0 target
        target_amount = max_coin * min_coin

    count = 0
    # Iterate through possible counts of the larger coin
    for num_coin2 in range(target_amount // coin2 + 1):
        remaining_amount = target_amount - (num_coin2 * coin2)
        if remaining_amount >= 0 and remaining_amount % coin1 == 0:
            count += 1
            
    question_text = f"只用 ${coin1}$ 元硬幣或 ${coin2}$ 元硬幣支付 ${target_amount}$ 元貨款，共有多少種支付方法？"
    correct_answer = str(count)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_game_outcomes_problem():
    """
    題目: 甲、乙兩人比賽，約定每局比賽必分出勝負，先勝 N 局者贏得比賽。
    問：共有多少種可能的情形？又其中甲贏得比賽的情形有多少種？
    """
    n_wins = random.randint(2, 3) # First to win 2 or 3 games

    outcomes = []
    player_wins = {'A': 0, 'B': 0}

    def find_outcomes(current_seq, current_wins):
        nonlocal outcomes
        if current_wins['A'] == n_wins or current_wins['B'] == n_wins:
            outcomes.append(current_seq)
            return

        # Player A wins next game
        new_wins_A = current_wins.copy()
        new_wins_A['A'] += 1
        find_outcomes(current_seq + 'A', new_wins_A)

        # Player B wins next game
        new_wins_B = current_wins.copy()
        new_wins_B['B'] += 1
        find_outcomes(current_seq + 'B', new_wins_B)

    find_outcomes("", player_wins)

    total_outcomes = len(outcomes)
    a_wins_count = sum(1 for seq in outcomes if seq.count('A') == n_wins and seq.count('B') < n_wins)
    
    # Adjust for edge case where A could win but B also reaches N wins in same step
    # Example: N=2, AABB - B actually won before the second A
    # The find_outcomes should correctly stop when N wins is reached.

    question_text = (
        f"甲、乙兩人比賽，約定每局比賽必分出勝負，先勝 ${n_wins}$ 局者贏得比賽。<br>"
        f"$1$ 共有多少種可能的情形？<br>"
        f"$2$ 又其中甲贏得比賽的情形有多少種？"
    )
    correct_answer = f"{total_outcomes}, {a_wins_count}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_simple_multiplication_problem():
    """
    題目: 餐廳的主菜有N1種；湯有N2種；飲料有N3種。每位客人須從主菜、湯及飲料各任選一種。請問共有多少種點餐方式？
    """
    num_categories = random.randint(2, 4)
    categories = ['主菜', '湯品', '飲料', '甜點']
    
    choices_per_category = []
    category_descriptions = []

    for i in range(num_categories):
        num_choices = random.randint(2, 6)
        choices_per_category.append(num_choices)
        category_descriptions.append(f"{categories[i]}有${num_choices}$種")

    product = math.prod(choices_per_category)
    
    choices_str = "、".join(category_descriptions)
    question_text = (
        f"餐廳的{choices_str}。每位客人須從各項中任選一種。請問共有多少種點餐方式？"
    )
    correct_answer = str(product)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_divisors_count_problem():
    """
    題目: 關於 N 的正因數，回答下列問題。(1)共有多少個？ (2)有多少個是 M 的倍數？
    """
    # Generate N with a few prime factors
    primes = [2, 3, 5, 7]
    n_factors = random.randint(2, 3)
    
    n_val = 1
    factor_dict = {}
    for _ in range(n_factors):
        p = random.choice(primes)
        exp = random.randint(1, 3)
        n_val *= (p ** exp)
        factor_dict[p] = exp
    
    # Ensure N is not too small or too large
    if n_val < 30:
        n_val *= random.choice([2, 3])
        factor_dict = get_prime_factorization(n_val)

    # Part 1: Total number of divisors
    total_divisors = 1
    for exp in factor_dict.values():
        total_divisors *= (exp + 1)

    # Part 2: Number of divisors that are multiples of M
    # M should be a factor of N and not N itself
    m_factors = {}
    m_val = 1
    
    # Try to build M from some factors of N
    possible_m_primes = list(factor_dict.keys())
    if len(possible_m_primes) > 0:
        m_prime = random.choice(possible_m_primes)
        m_exp = random.randint(1, factor_dict[m_prime])
        m_factors[m_prime] = m_exp
        m_val *= (m_prime ** m_exp)
    
    # If M is 1 or very small, try to add another factor
    if m_val == 1 and len(possible_m_primes) > 1:
        m_prime = random.choice([p for p in possible_m_primes if p != m_prime])
        m_exp = random.randint(1, factor_dict[m_prime])
        m_factors[m_prime] = m_exp
        m_val *= (m_prime ** m_exp)

    if m_val == 1 or m_val == n_val: # Ensure M is a proper factor > 1
        m_val = random.randint(2, n_val // 2)
        while n_val % m_val != 0:
            m_val = random.randint(2, n_val // 2)
        m_factors = get_prime_factorization(m_val)


    divisors_of_m_multiple = 1
    is_valid_m_for_part2 = True
    for p, m_exp in m_factors.items():
        if p not in factor_dict or factor_dict[p] < m_exp:
            is_valid_m_for_part2 = False
            break
        divisors_of_m_multiple *= (factor_dict[p] - m_exp + 1)
    
    if not is_valid_m_for_part2: # Fallback if random M isn't good
        # Create a guaranteed valid M
        m_val = 1
        divisors_of_m_multiple = 1
        remaining_factors = factor_dict.copy()
        for p, exp in factor_dict.items():
            if exp >= 1 and random.random() < 0.5: # Include some factor in M
                m_prime_exp = random.randint(1, exp)
                m_val *= (p ** m_prime_exp)
                remaining_factors[p] -= m_prime_exp
        
        if m_val == 1: # M must be > 1
             m_val = list(factor_dict.keys())[0] ** random.randint(1, factor_dict[list(factor_dict.keys())[0]])
             m_factors = get_prime_factorization(m_val)
             remaining_factors = factor_dict.copy()
             for p, m_exp in m_factors.items():
                 remaining_factors[p] -= m_exp

        for exp_rem in remaining_factors.values():
            divisors_of_m_multiple *= (exp_rem + 1)


    question_text = (
        f"關於 ${n_val}$ 的正因數，回答下列問題。<br>"
        f"$1$ 共有多少個？<br>"
        f"$2$ 有多少個是 ${m_val}$ 的倍數？"
    )
    correct_answer = f"{total_divisors}, {divisors_of_m_multiple}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_addition_principle_scenarios_problem():
    """
    題目: 某班有X位男生Y位女生。要選出A位男生和B位女生組成小組，或選出C位男生和D位女生組成小組。
    請問共有多少種選派方案？
    This is actually a combination of combinations and addition principle, not simple multiplication/addition.
    Let's stick to the "at least one old hand" type problem from examples.
    """
    
    group1_name = "獅頭手"
    group1_old_label = "老手"
    group1_new_label = "新手"

    group2_name = "獅尾手"
    group2_old_label = "老手"
    group2_new_label = "新手"

    g1_old = random.randint(3, 7)
    g1_new = random.randint(1, 3)
    g1_total = g1_old + g1_new

    g2_old = random.randint(2, 6)
    g2_new = random.randint(1, 2)
    g2_total = g2_old + g2_new
    
    scenario = random.choice([
        'at_least_one_old',
        'exactly_one_old',
        'both_old'
    ])
    
    if scenario == 'at_least_one_old':
        # Cases: (Old, New), (New, Old), (Old, Old)
        case1 = g1_old * g2_new
        case2 = g1_new * g2_old
        case3 = g1_old * g2_old
        total_schemes = case1 + case2 + case3
        
        question_text = (
            f"某團體的${group1_name}$有${g1_old}$位{group1_old_label}及${g1_new}$位{group1_new_label}，"
            f"${group2_name}$有${g2_old}$位{group2_old_label}及${g2_new}$位{group2_new_label}。<br>"
            f"今欲選派${group1_name}$與${group2_name}$各一人表演，若選出的兩人中，"
            f"至少要有一人是{group1_old_label}，則共有多少種選派方案？"
        )
    elif scenario == 'exactly_one_old':
        # Cases: (Old, New), (New, Old)
        case1 = g1_old * g2_new
        case2 = g1_new * g2_old
        total_schemes = case1 + case2
        
        question_text = (
            f"某團體的${group1_name}$有${g1_old}$位{group1_old_label}及${g1_new}$位{group1_new_label}，"
            f"${group2_name}$有${g2_old}$位{group2_old_label}及${g2_new}$位{group2_new_label}。<br>"
            f"今欲選派${group1_name}$與${group2_name}$各一人表演，若選出的兩人中，"
            f"恰好有一人是{group1_old_label}，則共有多少種選派方案？"
        )
    else: # 'both_old' (simplified for 'at least' structure)
        # This will be simpler: (Old, Old)
        total_schemes = g1_old * g2_old
        
        question_text = (
            f"某團體的${group1_name}$有${g1_old}$位{group1_old_label}及${g1_new}$位{group1_new_label}，"
            f"${group2_name}$有${g2_old}$位{group2_old_label}及${g2_new}$位{group2_new_label}。<br>"
            f"今欲選派${group1_name}$與${group2_name}$各一人表演，若選出的兩人中，"
            f"兩人皆為{group1_old_label}，則共有多少種選派方案？"
        )
        

    correct_answer = str(total_schemes)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_inclusion_exclusion_2sets_problem():
    """
    題目: 全班U人中，nA人有A，nB人有B，nAnB人同時有A與B。
    問：(1)至少有一種者有多少人？ (2)沒有A，也沒有B者有多少人？
    """
    total_students = random.randint(30, 60)
    
    n_A = random.randint(total_students // 3, total_students * 2 // 3)
    n_B = random.randint(total_students // 4, total_students * 2 // 3)
    
    # Ensure intersection is valid: nA + nB - n(AUB) and n(AUB) <= total_students
    # Also nAnB <= min(nA, nB)
    min_intersection = max(0, n_A + n_B - total_students)
    max_intersection = min(n_A, n_B)

    # Handle cases where min_intersection > max_intersection (shouldn't happen with above, but safety)
    if min_intersection > max_intersection:
        min_intersection = max_intersection

    if max_intersection < 0: # This case indicates nA or nB might be too small for the bounds logic
        max_intersection = 0
    
    n_A_and_B = random.randint(min_intersection, max_intersection)
    
    n_A_or_B = n_A + n_B - n_A_and_B
    n_neither = total_students - n_A_or_B

    item_a = random.choice(['手機', '平板電腦', '籃球', '吉他', '腳踏車'])
    item_b = random.choice(['平板電腦', '手機', '游泳', '鋼琴', '溜冰鞋'])
    
    while item_a == item_b:
        item_b = random.choice(['平板電腦', '手機', '游泳', '鋼琴', '溜冰鞋'])

    question_text = (
        f"全班${total_students}$人中，${n_A}$人有{item_a}，"
        f"${n_B}$人有{item_b}，${n_A_and_B}$人同時有{item_a}與{item_b}。<br>"
        f"$1$ 至少有一種者有多少人？<br>"
        f"$2$ 沒有{item_a}，也沒有{item_b}者有多少人？"
    )
    correct_answer = f"{n_A_or_B}, {n_neither}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_inclusion_exclusion_2sets_complex_problem():
    """
    A slightly more complex version of inclusion-exclusion, perhaps with 3 sets,
    but for now, I'll reuse the 2-set logic with a slightly different wording
    or calculation requirement.
    For the target skill, 2-set is already sufficient.
    The example had a 3-set problem, but it's much more involved. I will stick to 2-set
    for the initial implementation.
    """
    return generate_inclusion_exclusion_2sets_problem()


def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    計數原理的答案通常是整數或以逗號分隔的整數。
    """
    user_answer_parts = [p.strip() for p in user_answer.split(',')]
    correct_answer_parts = [p.strip() for p in correct_answer.split(',')]

    is_correct = False
    result_text = ""

    if len(user_answer_parts) != len(correct_answer_parts):
        result_text = f"答案格式不正確。應為 {len(correct_answer_parts)} 個數字，以逗號分隔。"
        return {"correct": False, "result": result_text, "next_question": False}

    all_parts_correct = True
    for u_ans, c_ans in zip(user_answer_parts, correct_answer_parts):
        try:
            if float(u_ans) != float(c_ans):
                all_parts_correct = False
                break
        except ValueError:
            all_parts_correct = False
            break
    
    is_correct = all_parts_correct

    if is_correct:
        result_text = "完全正確！"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer}$"
    
    return {"correct": is_correct, "result": result_text, "next_question": True}