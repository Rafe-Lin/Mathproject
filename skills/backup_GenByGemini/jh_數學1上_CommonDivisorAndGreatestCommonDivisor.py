import random
import math
from fractions import Fraction

def gcd_list(numbers):
    """
    計算一個數字列表的最大公因數。
    """
    if not numbers:
        return 0
    result = numbers[0]
    for i in range(1, len(numbers)):
        result = math.gcd(result, numbers[i])
    return result

def format_prime_factorization(factors_dict):
    """
    將質因數分解的字典格式化為 LaTeX 字串。
    例如 {2: 3, 5: 1} -> '2^3 \\times 5'
    """
    if not factors_dict or all(v == 0 for v in factors_dict.values()):
        return "1"
    parts = []
    # 根據質因數大小排序
    for base in sorted(factors_dict.keys()):
        exp = factors_dict[base]
        if exp == 0:
            continue
        if exp == 1:
            parts.append(str(base))
        else:
            # f-string 中 LaTeX 的大括號需要雙寫
            parts.append(f"{base}^{{{exp}}}")
    return " \\times ".join(parts)

def generate(level=1):
    """
    生成「公因數與最大公因數」相關題目。
    包含：
    1. 求整數的最大公因數
    2. 判斷兩數是否互質
    3. 從標準分解式求最大公因數
    4. 從標準分解式判斷因數
    """
    problem_type = random.choice(['gcd_integers', 'coprime', 'gcd_prime_factors', 'identify_factors'])

    if problem_type == 'gcd_integers':
        return generate_gcd_of_integers_problem()
    elif problem_type == 'coprime':
        return generate_coprime_problem()
    elif problem_type == 'gcd_prime_factors':
        return generate_gcd_from_prime_factorization_problem()
    else:
        return generate_identify_factors_from_prime_factorization_problem()

def generate_gcd_of_integers_problem():
    """
    題型：求 2 或 3 個整數的最大公因數。
    """
    num_count = random.choice([2, 3])
    
    # 為了確保有 > 1 的公因數，先產生一個公因數
    common_factor = random.randint(2, 20)
    
    # 再產生彼此互質的乘數
    multipliers = []
    while len(multipliers) < num_count:
        m = random.randint(2, 10)
        is_coprime_with_others = all(math.gcd(m, other) == 1 for other in multipliers)
        if is_coprime_with_others:
            multipliers.append(m)

    numbers = [common_factor * m for m in multipliers]
    random.shuffle(numbers)

    correct_gcd = gcd_list(numbers)

    question_text = f"求下列各數的最大公因數： {', '.join(map(str, numbers))}"
    correct_answer = str(correct_gcd)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "input_type": "text"
    }

def generate_coprime_problem():
    """
    題型：判斷兩數是否互質。
    """
    is_coprime = random.choice([True, False])

    if is_coprime:
        a, b = random.randint(10, 100), random.randint(10, 100)
        while math.gcd(a, b) != 1:
            a, b = random.randint(10, 100), random.randint(10, 100)
        correct_answer = "互質"
    else:
        common_factor = random.randint(2, 10)
        m1, m2 = random.randint(2, 15), random.randint(2, 15)
        while math.gcd(m1, m2) != 1: # 確保最大公因數就是 common_factor
            m1, m2 = random.randint(2, 15), random.randint(2, 15)
        a = common_factor * m1
        b = common_factor * m2
        correct_answer = "不互質"

    question_text = f"判斷 {a} 和 {b} 是否互質？ (請回答「互質」或「不互質」)"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "input_type": "text"
    }

def generate_gcd_from_prime_factorization_problem():
    """
    題型：從標準分解式求最大公因數。
    """
    primes = [2, 3, 5, 7, 11]
    num_count = random.choice([2, 3])
    
    # 所有數字都會有的共同質因數
    common_primes = random.sample(primes, random.randint(1, 2))
    all_primes = set(common_primes)
    
    factors_list = []
    for _ in range(num_count):
        factors = {}
        # 加入共同質因數
        for p in common_primes:
            factors[p] = random.randint(1, 4)
        # 加入獨有質因數
        unique_prime = random.choice([p for p in primes if p not in common_primes])
        if random.random() < 0.7:
             factors[unique_prime] = random.randint(1, 4)
             all_primes.add(unique_prime)
        factors_list.append(factors)

    # 計算正確答案
    gcd_factors = {}
    for p in common_primes:
        min_exp = min(f.get(p, 0) for f in factors_list)
        if min_exp > 0:
            gcd_factors[p] = min_exp

    num_labels = ["a", "b", "c"]
    question_parts = []
    for i in range(num_count):
        formatted_num = format_prime_factorization(factors_list[i])
        question_parts.append(f"{num_labels[i]} = ${formatted_num}$")

    question_text = f"求下列各數的最大公因數，並以標準分解式表示：\n" + " , ".join(question_parts)
    correct_answer = f"${format_prime_factorization(gcd_factors)}$"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "input_type": "handwriting" # 答案包含 LaTeX
    }

def generate_identify_factors_from_prime_factorization_problem():
    """
    題型：從標準分解式判斷因數。
    """
    primes = [2, 3, 5, 7]
    target_factors = {}
    base_primes = random.sample(primes, random.randint(2, 3))
    for p in base_primes:
        target_factors[p] = random.randint(3, 6)
    
    target_str = format_prime_factorization(target_factors)
    
    options = []
    correct_labels = []
    labels = ["⑴", "⑵", "⑶", "⑷", "⑸"]
    num_options = 4
    num_correct = random.randint(2, 3)

    # 生成正確的因數選項
    for i in range(num_correct):
        option_factors = {}
        for p, max_exp in target_factors.items():
            if random.random() > 0.2: # 70% 機率包含該質因數
                option_factors[p] = random.randint(1, max_exp)
        if not option_factors: # 避免產生空選項 (即 1)
             p = random.choice(list(target_factors.keys()))
             option_factors[p] = random.randint(1, target_factors[p])
        options.append(f"${format_prime_factorization(option_factors)}$")
        correct_labels.append(labels[len(options)-1])

    # 生成錯誤的選項
    while len(options) < num_options:
        option_factors = {}
        error_type = random.choice(['extra_prime', 'high_exponent'])
        
        if error_type == 'extra_prime':
            p_extra = random.choice([p for p in primes if p not in target_factors])
            option_factors = {p_extra: random.randint(1, 2)}
            # 隨機加入一個合法的質因數
            p_legal = random.choice(list(target_factors.keys()))
            option_factors[p_legal] = random.randint(1, target_factors[p_legal])

        elif error_type == 'high_exponent':
            p_high = random.choice(list(target_factors.keys()))
            option_factors[p_high] = target_factors[p_high] + random.randint(1, 2)
            # 隨機加入另一個合法的質因數
            other_legal_primes = [p for p in target_factors.keys() if p != p_high]
            if other_legal_primes:
                p_legal = random.choice(other_legal_primes)
                option_factors[p_legal] = random.randint(1, target_factors[p_legal])

        options.append(f"${format_prime_factorization(option_factors)}$")

    # 打亂選項順序
    shuffled_indices = list(range(len(options)))
    random.shuffle(shuffled_indices)
    shuffled_options = [options[i] for i in shuffled_indices]
    # 更新正確答案的標籤
    correct_labels = [labels[shuffled_indices.index(i)] for i, opt in enumerate(options) if labels[i] in correct_labels]
    correct_labels.sort()

    options_str = "\n".join([f"{labels[i]} {shuffled_options[i]}" for i in range(num_options)])
    question_text = f"下列各數中，哪些是 ${target_str}$ 的因數？(請填入所有正確的代號)\n{options_str}"
    correct_answer = ",".join(correct_labels)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "input_type": "text"
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    # 統一處理答案格式
    user_ans_norm = user_answer.strip().replace(' ', '').replace('$', '').replace('，', ',')
    correct_ans_norm = correct_answer.strip().replace(' ', '').replace('$', '').replace('，', ',')

    # 處理多選題答案 (例如 "⑴,⑶" or "⑶,⑴")
    if '⑴' in correct_ans_norm or (',' in correct_ans_norm and not correct_ans_norm.isdigit()):
        # 將選項排序後比對，忽略順序
        user_parts = sorted(user_ans_norm.split(','))
        correct_parts = sorted(correct_ans_norm.split(','))
        is_correct = user_parts == correct_parts
    else:
        # 處理標準分解式 (例如 2^3*3 vs 3*2^3)
        # 透過 helper function 重新標準化排序
        if "\\times" in user_ans_norm or "^" in user_ans_norm:
             # 這部分較複雜，暫時以字串完全比對為主，因產生答案時已排序
             is_correct = user_ans_norm == correct_ans_norm
        else:
            # 處理一般數字或文字答案
            is_correct = user_ans_norm == correct_ans_norm

    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}
