import random
from math import gcd

def generate_conditional_probability_question():
    """動態生成一道「條件機率」的題目"""
    # 簡單情境：從袋中取球
    red_balls = random.randint(2, 5)
    blue_balls = random.randint(2, 5)
    total_balls = red_balls + blue_balls
    
    # 假設第一次取出紅球，第二次再取球是藍球的機率
    # P(B|R) = P(B and R) / P(R)
    # P(R) = red_balls / total_balls
    # P(B and R) = (red_balls / total_balls) * (blue_balls / (total_balls - 1))
    # P(B|R) = blue_balls / (total_balls - 1)
    
    question_text = (
        f"一個袋中有 {red_balls} 顆紅球和 {blue_balls} 顆藍球。"
        f"如果第一次取出紅球後不放回，請問第二次取出藍球的機率是多少？ (請以 a/b 的形式表示)"
    )
    
    answer_num = blue_balls
    answer_den = total_balls - 1
    
    common = gcd(answer_num, answer_den)
    answer = f"{answer_num // common}/{answer_den // common}"
    
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }
