import random

# --- Helper Functions ---

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

def get_prime_factors(n):
    """Returns a dictionary of prime factors and their powers."""
    factors = {}
    d = 2
    temp = n
    while d * d <= temp:
        while (temp % d) == 0:
            factors[d] = factors.get(d, 0) + 1
            temp //= d
        d += 1
    if temp > 1:
        factors[temp] = factors.get(temp, 0) + 1
    return factors

def get_divisors_count(n):
    """Calculates the total number of divisors for a number."""
    if n == 0:
        return 0
    if n == 1:
        return 1
    factors = get_prime_factors(n)
    count = 1
    for p in factors:
        count *= (factors[p] + 1)
    return count

# --- Main Generator ---

def generate(level=1):
    """
    生成「質數與質因數分解」相關題目。
    包含：
    1. 判斷質數或合數
    2. 因數與矩形排列問題
    3. 列出所有質因數
    4. 標準分解式的應用 (密碼題)
    """
    problem_type = random.choice([
        'prime_or_composite',
        'rectangle_packing',
        'list_prime_factors',
        'factorization_password'
    ])
    
    if problem_type == 'prime_or_composite':
        return generate_prime_or_composite_problem()
    elif problem_type == 'rectangle_packing':
        return generate_rectangle_packing_problem()
    elif problem_type == 'list_prime_factors':
        return generate_list_prime_factors_problem()
    else: # factorization_password
        return generate_factorization_password_problem()

# --- Problem Type Generators ---

def generate_prime_or_composite_problem():
    """
    題型：判斷一個數字是質數還是合數。 (對應例題 1, 2)
    """
    # 50% 機率選質數，50% 選合數
    if random.random() < 0.5:
        # 選一個質數
        primes = [11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
        num = random.choice(primes)
        correct_answer = "質數"
    else:
        # 構造一個合數
        factor1 = random.randint(4, 11)
        factor2 = random.randint(4, 11)
        num = factor1 * factor2
        # 避免選到質數 (雖然機率很低)
        while is_prime(num):
            factor1 = random.randint(4, 11)
            factor2 = random.randint(4, 11)
            num = factor1 * factor2
        correct_answer = "合數"
        
    question_text = f"請問 {num} 是質數還是合數？"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "input_type": "text"
    }

def generate_rectangle_packing_problem():
    """
    題型：給定 n 個小正方形，可以拼出幾種矩形。 (對應例題 3, 4)
    """
    num_squares = random.randint(15, 70)
    
    divisors_count = get_divisors_count(num_squares)
    is_square = int(num_squares**0.5)**2 == num_squares
    
    if is_square:
        num_shapes = (divisors_count + 1) // 2
    else:
        num_shapes = divisors_count // 2
        
    question_text = f"欲將 {num_squares} 個邊長為 1 的小正方形緊密排列拼成一個實心矩形，且不會剩下任何小正方形，請問可以拼出幾種不同形狀的矩形？"
    correct_answer = str(num_shapes)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "input_type": "text"
    }

def generate_list_prime_factors_problem():
    """
    題型：列出一個數字的所有質因數。 (對應例題 5, 6)
    """
    primes = [2, 3, 5, 7, 11]
    # 隨機選 2 或 3 個質因數
    num_factors = random.choice([2, 3])
    base_primes = sorted(random.sample(primes, num_factors))
    
    n = 1
    # 為了讓數字不要太大，限制總次方數
    total_power_budget = random.randint(3, 5) 
    powers = [1] * num_factors
    total_power_budget -= num_factors

    while total_power_budget > 0:
        idx_to_increment = random.randrange(num_factors)
        powers[idx_to_increment] += 1
        total_power_budget -= 1

    for p, power in zip(base_primes, powers):
        n *= (p ** power)

    question_text = f"請寫出 {n} 的所有相異質因數。(請由小到大排列，並用半形逗號分隔)"
    correct_answer = ",".join(map(str, base_primes))

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "input_type": "text"
    }


def generate_factorization_password_problem():
    """
    題型：利用標準分解式設計密碼。 (對應例題 8)
    """
    a = random.randint(2, 4)
    c = random.randint(2, 3)
    
    # b 是質數 3
    b_prime = 3
    
    # d 是質數 5 或 7
    d_prime = random.choice([5, 7])
    
    N = (2**a) * (b_prime**c) * d_prime
    
    question_text = f"小翊設定手機解鎖的密碼為 abcd 四碼，若他是利用 {N} 的標準分解式 $2^a \\times b^c \\times d$ 來設計密碼（其中質因數 b 和 d 需由小到大排列），則此組密碼為何？"
    correct_answer = f"{a}{b_prime}{c}{d_prime}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "input_type": "text"
    }

# --- Checker Function ---

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    # 標準化輸入：去除頭尾空白、全形逗號轉半形、移除中間空白
    user_answer = user_answer.strip().replace("，", ",").replace(" ", "")
    correct_answer = correct_answer.strip().replace(" ", "")
    
    is_correct = (user_answer == correct_answer)
    
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    
    return {"correct": is_correct, "result": result_text, "next_question": True}
