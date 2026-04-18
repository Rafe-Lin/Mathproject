import random
import math

def generate_binomial_distribution_question():
    """動態生成一道「二項分布」的題目 (求特定成功次數的機率)"""
    n = random.randint(3, 5) # 試驗次數
    k = random.randint(1, n) # 成功次數
    p_val = random.choice([0.2, 0.5, 0.8]) # 成功機率
    
    # 計算二項分布機率 P(X=k) = C(n, k) * p^k * (1-p)^(n-k)
    probability = math.comb(n, k) * (p_val ** k) * ((1 - p_val) ** (n - k))
    
    question_text = (
        f"某次實驗成功機率為 {p_val:.1f}。若進行 {n} 次獨立實驗，"
        f"請問恰好成功 {k} 次的機率是多少？ (請四捨五入到小數點後三位)"
    )
    answer = f"{probability:.3f}"
    
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }
