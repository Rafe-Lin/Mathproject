# skills/jh_prime_factorization.py
import random

def get_prime_factorization_str(n):
    factors = []
    d = 2
    temp = n
    while d * d <= temp:
        while temp % d == 0:
            factors.append(str(d))
            temp //= d
        d += 1
    if temp > 1:
        factors.append(str(temp))
    return ' * '.join(factors)

def generate(level=1):
    """
    生成一道「質因數分解」的題目。
    """
    # 構造一個容易分解的數字
    primes = [2, 3, 5, 7]
    num = 1
    for _ in range(random.randint(2, 4)):
        num *= random.choice(primes)
    
    if num > 100 or num < 10: # 重新生成以確保數字大小適中
        return generate(level)

    question_text = f"請將 {num} 做質因數分解。（例如：12 = 2 * 2 * 3）"
    
    correct_answer = get_prime_factorization_str(num)

    context_string = f"將一個合數寫成質因數的連乘積。"

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
    user_factors = sorted([int(f) for f in user_answer.replace(" ", "").split('*')])
    correct_factors = sorted([int(f) for f in correct_answer.replace(" ", "").split('*')])
    is_correct = user_factors == correct_factors
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案是：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}