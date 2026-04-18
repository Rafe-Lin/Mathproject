import random
import math
from itertools import combinations

def gcd(a, b):
    """Euclidean algorithm to find the greatest common divisor."""
    while b:
        a, b = b, a % b
    return a

def lcm(a, b):
    """Calculate the least common multiple of two integers."""
    if a == 0 or b == 0:
        return 0
    # Use gcd helper, ensure integer division
    return abs(a * b) // gcd(a, b)

def dict_to_latex(factors):
    """Converts a dictionary of prime factors to a LaTeX string."""
    if not factors:
        return "1"
    parts = []
    # Sort by prime base for consistent output
    for p in sorted(factors.keys()):
        exp = factors[p]
        if exp == 1:
            parts.append(str(p))
        else:
            # Adhere to the strict LaTeX rule: ^{...}
            parts.append(f"{p}^{{{exp}}}")
    # Use \times for multiplication
    return " \\times ".join(parts)

def generate(level=1):
    """
    生成「公倍數與最小公倍數」相關題目。
    包含：
    1. 整數求最小公倍數 (generate_lcm_from_integers)
    2. 標準分解式求最小公倍數之值 (generate_lcm_from_prime_factors_value)
    3. 從標準分解式判斷倍數關係 (generate_identify_multiple_from_prime_factors)
    4. 利用公式 a*b = gcd*lcm 求最大公因數 (generate_find_gcd_from_product_and_lcm)
    """
    problem_type = random.choice([
        'lcm_from_integers',
        'lcm_from_prime_factors_value',
        'identify_multiple_from_prime_factors',
        'find_gcd_from_product_and_lcm'
    ])
    
    if problem_type == 'lcm_from_integers':
        return generate_lcm_from_integers()
    elif problem_type == 'lcm_from_prime_factors_value':
        return generate_lcm_from_prime_factors_value()
    elif problem_type == 'identify_multiple_from_prime_factors':
        return generate_identify_multiple_from_prime_factors()
    else:
        return generate_find_gcd_from_product_and_lcm()

def generate_lcm_from_integers():
    """題型：求 2 或 3 個整數的最小公倍數。"""
    num_count = random.choice([2, 3])
    nums = random.sample(range(12, 61), num_count)
    
    if num_count == 2:
        lcm_val = lcm(nums[0], nums[1])
    else:
        lcm_val = lcm(lcm(nums[0], nums[1]), nums[2])
        
    nums_str = '、'.join(map(str, nums))
    
    question_text = f"求下列各組數的最小公倍數：${nums_str}$"
    correct_answer = str(lcm_val)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_lcm_from_prime_factors_value():
    """題型：給定標準分解式，求最小公倍數的數值。"""
    primes = random.sample([2, 3, 5, 7], k=3)
    
    num1_factors = {p: random.randint(1, 3) for p in random.sample(primes, k=2)}
    num2_factors = {p: random.randint(1, 3) for p in random.sample(primes, k=2)}
    
    num1_latex = dict_to_latex(num1_factors)
    num2_latex = dict_to_latex(num2_factors)
    
    all_primes = set(num1_factors.keys()) | set(num2_factors.keys())
    lcm_factors = {p: max(num1_factors.get(p, 0), num2_factors.get(p, 0)) for p in all_primes}
    
    lcm_val = 1
    for p, exp in lcm_factors.items():
        lcm_val *= (p ** exp)
        
    question_text = f"求 ${num1_latex}$ 與 ${num2_latex}$ 的最小公倍數之值為何？"
    correct_answer = str(lcm_val)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_identify_multiple_from_prime_factors():
    """題型：從選項中判斷哪些是給定數的倍數(皆以標準分解式表示)。"""
    base_primes = random.sample([2, 3, 5, 7], k=random.randint(2, 3))
    base_factors = {p: random.randint(1, 3) for p in base_primes}
    base_latex = dict_to_latex(base_factors)

    options = []
    correct_labels_list = []
    labels = ['(A)', '(B)', '(C)', '(D)']
    # Aim for 2 correct, 2 incorrect
    is_correct_flags = random.sample([True, True, False, False], k=4)

    for i in range(4):
        is_correct = is_correct_flags[i]
        option_factors = base_factors.copy()

        if is_correct:
            # To be a multiple, exponents must be >= base exponents
            # Method 1: Increase an existing exponent
            p_to_increase = random.choice(list(option_factors.keys()))
            option_factors[p_to_increase] += random.randint(1, 2)
            # Method 2 (optional): Add a new prime factor
            if random.random() < 0.5:
                new_prime = random.choice([p for p in [2,3,5,7,11] if p not in option_factors])
                option_factors[new_prime] = random.randint(1, 2)
            correct_labels_list.append(labels[i][1]) # Get 'A' from '(A)'
        else:
            # To not be a multiple, at least one exponent must be smaller or a factor missing
            p_to_modify = random.choice(list(option_factors.keys()))
            if random.random() < 0.6 and option_factors[p_to_modify] > 1:
                # Method 1: Lower an exponent
                option_factors[p_to_modify] -= 1
            else:
                # Method 2: Remove a factor entirely
                del option_factors[p_to_modify]

        options.append(f"{labels[i]} ${dict_to_latex(option_factors)}$")

    question_text = f"下列各數中，哪些是 ${base_latex}$ 的倍數？（若有多個答案，請用逗號分隔，例如：A,C）\n" + "\n".join(options)
    correct_answer = ",".join(sorted(correct_labels_list))

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_find_gcd_from_product_and_lcm():
    """題型：已知 a*b 和 [a,b]，求 (a,b)。"""
    a, b = 0, 0
    # Ensure a and b are not equal and have a non-trivial gcd
    while a == b or gcd(a, b) == 1:
        a = random.randint(4, 30)
        b = random.randint(4, 30)
        
    prod = a * b
    lcm_val = lcm(a, b)
    gcd_val = gcd(a, b)
    
    # Standard notation: [a,b] for LCM, (a,b) for GCD
    question_text = f"已知兩正整數 $a$、$b$，其中 $a \\times b = {prod}$ 且兩數的最小公倍數 $[ a , b ] = {lcm_val}$，則此兩數的最大公因數 $( a , b )$ 為何？"
    correct_answer = str(gcd_val)
    
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

    # Check for multiple choice answers like "A, C"
    if ',' in correct_answer:
        # Normalize by removing spaces, uppercasing, splitting, and sorting
        user_parts = sorted([part.strip() for part in user_answer.upper().split(',')])
        correct_parts = sorted([part.strip() for part in correct_answer.upper().split(',')])
        is_correct = (user_parts == correct_parts)
    else:
        # Standard numerical comparison
        if user_answer.upper() == correct_answer.upper():
            is_correct = True
        else:
            try:
                # Check for floating point equivalence for numerical answers
                if float(user_answer) == float(correct_answer):
                    is_correct = True
            except ValueError:
                # Cannot convert to float, not a number
                pass

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}
