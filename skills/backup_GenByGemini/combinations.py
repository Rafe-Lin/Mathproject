import random
import math

def generate_combinations_question():
    """動態生成一道「組合」的題目 (C(n,k))"""
    n = random.randint(5, 9)
    k = random.randint(2, n - 2)
    answer = math.comb(n, k)
    question_text = f"從 {n} 個相異物中取出 {k} 個，請問有幾種取法？ (即 C({n}, {k}))"
    return {
        "text": question_text,
        "answer": str(answer),
        "validation_function_name": None
    }
