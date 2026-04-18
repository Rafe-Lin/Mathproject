import random
import math

def generate_permutations_question():
    """動態生成一道「排列」的題目 (P(n,k))"""
    n = random.randint(4, 7)
    k = random.randint(2, n - 1)
    answer = math.perm(n, k)
    question_text = f"從 {n} 個相異物中取出 {k} 個進行排列，請問有幾種排法？ (即 P({n}, {k}))"
    return {
        "text": question_text,
        "answer": str(answer),
        "validation_function_name": None
    }
