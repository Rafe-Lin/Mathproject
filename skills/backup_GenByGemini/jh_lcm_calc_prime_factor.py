# skills/jh_lcm_calc_prime_factor.py
import random
import math

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

def format_factorization(factors):
    return ' * '.join([f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(factors.items())])

def lcm(a, b):
    return abs(a*b) // math.gcd(a, b) if a != 0 and b != 0 else 0

def generate(level=1):
    """
    生成一道「利用質因數分解求最小公倍數」的題目。
    """
    common_base1 = random.choice([2, 3])
    common_base2 = random.choice([5, 7])
    
    a = (common_base1 ** random.randint(1, 3)) * (common_base2 ** random.randint(2, 4)) * random.choice([1, 2])
    b = (common_base1 ** random.randint(2, 4)) * (common_base2 ** random.randint(1, 3)) * random.choice([1, 3])

    factors_a = get_prime_factorization(a)
    factors_b = get_prime_factorization(b)

    question_text = f"已知 A = {format_factorization(factors_a)} 且 B = {format_factorization(factors_b)}，請問 A 和 B 的最小公倍數是多少？"
    
    correct_answer = str(lcm(a, b))

    context_string = f"求最小公倍數，取所有質因數，次方取較大者。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    """
    檢查使用者輸入的答案是否正確。
    """
    user = user_answer.strip()
    correct = str(correct_answer).strip()

    is_correct = user == correct
    result_text = f"完全正確！答案是 {correct}。" if is_correct else f"答案不正確。正確答案是：{correct}"
    return {"correct": is_correct, "result": result_text, "next_question": True}