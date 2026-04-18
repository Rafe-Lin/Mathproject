import random

def generate_sequence_limits_infinite_series_question():
    """動態生成一道「數列的極限與無窮等比級數」的題目 (求無窮等比級數和)"""
    a = random.randint(1, 10) # 首項
    r_num = random.randint(1, 4) # 公比分子
    r_den = random.randint(5, 9) # 公比分母，確保 |r| < 1
    r = r_num / r_den
    
    # 無窮等比級數和 S = a / (1 - r)
    sum_val = a / (1 - r)
    
    question_text = (
        f"已知一個無窮等比級數的首項為 {a}，公比為 {r_num}/{r_den}。"
        f"請問此無窮等比級數的和是多少？ (請四捨五入到小數點後兩位)"
    )
    answer = f"{sum_val:.2f}"
    
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }
