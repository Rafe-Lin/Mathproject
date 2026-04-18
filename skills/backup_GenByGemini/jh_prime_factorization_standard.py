# skills/jh_prime_factorization_standard.py
import random

def get_standard_factorization(n):
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
    
    return ' * '.join([f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(factors.items())])

def generate(level=1):
    """
    生成一道「質因數分解的標準分解式」的題目。
    """
    primes = [2, 3, 5, 7]
    num = 1
    for _ in range(random.randint(3, 5)):
        num *= random.choice(primes)

    if num > 200 or num < 20:
        return generate(level)

    question_text = f"請將 {num} 寫成標準分解式。（例如：12 = 2^2 * 3）"
    
    correct_answer = get_standard_factorization(num)

    context_string = f"將質因數分解的結果用指數形式表示。"

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
    user_clean = user_answer.replace(" ", "").replace("**", "^")
    correct_clean = correct_answer.replace(" ", "")
    is_correct = user_clean == correct_clean
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案是：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}