import random

def generate_discrete_random_variables_question():
    """動態生成一道「離散型隨機變數」的題目 (求期望值)"""
    # 簡單的機率分佈
    values = [random.randint(1, 5) for _ in range(3)]
    probabilities = [0.2, 0.3, 0.5] # 固定機率，確保和為 1
    
    # 計算期望值 E(X) = sum(x * P(x))
    expected_value = sum(v * p for v, p in zip(values, probabilities))
    
    question_text = (
        f"已知離散型隨機變數 X 的機率分佈如下：\n"
        f"  P(X={values[0]}) = {probabilities[0]:.1f}\n"
        f"  P(X={values[1]}) = {probabilities[1]:.1f}\n"
        f"  P(X={values[2]}) = {probabilities[2]:.1f}\n"
        f"請問 X 的期望值是多少？"
    )
    answer = str(expected_value)
    
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }

