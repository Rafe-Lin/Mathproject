import random

LOG2_APPROX = 0.3010
LOG3_APPROX = 0.4771

def generate_common_logarithm_question():
    # 80% 的機率出新的困難題型
    if random.random() < 0.8:
        # 類型四：結合科學記號與估計值
        a = random.randint(1, 3)  # 2 的次方
        b = random.randint(0, 2)  # 3 的次方
        c = random.randint(0, 2)  # 10 的次方

        # 確保題目不會太簡單 (至少包含 2^2 或 3)
        if b == 0 and a == 1:
            a = random.randint(2, 3)
        if a == 0 and b == 1: # a=0 的情況在目前邏輯不會發生，但保留以防萬一
            b = 2
        if a == 0 and b == 0: # 避免題目變成 log(10^c)，這太簡單了
            a = random.randint(1, 2)
            b = random.randint(1, 2)

        number_core = (2**a) * (3**b)
        final_number = number_core * (10**c)

        log_core = a * LOG2_APPROX + b * LOG3_APPROX
        final_answer = log_core + c

        # 決定要在題目中提供哪些提示
        hints = []
        if a > 0:
            hints.append("log(2) ≈ 0.3010")
        if b > 0:
            hints.append("log(3) ≈ 0.4771")
        
        question_text = f"給定 {' 且 '.join(hints)}，請計算 log({final_number}) 的近似值。(答案四捨五入至小數點後第四位)"
        answer = f"{final_answer:.4f}"  # 格式化到小數點後四位

        return {
            "text": question_text,
            "answer": answer,
            "validation_function_name": None
        }
    else:
        # 20% 的機率出舊的簡單題型
        power = random.randint(-3, 3) # 擴大範圍，加入負數和 0
        if power == 0:
            power = random.randint(1, 3) # 避免 log(1)
        number = 10 ** power
        question_text = f"計算 log({number}) = ?"
        return {
            "text": question_text,
            "answer": str(power),
            "validation_function_name": None
        }
