# skills/jh_factor_common_factor.py
import random

def generate(level=1):
    """
    生成一道「提公因式」的題目。
    """
    # 構造 ax + ay 或 axy + axz
    var1, var2 = random.sample(['x', 'y', 'z', 'a', 'b'], 2)
    
    common_coeff = random.randint(2, 9)
    common_var_power = random.randint(1, 3)
    common_var = 'x'
    
    term1_coeff = random.randint(2, 5)
    term2_coeff = random.randint(2, 5)
    
    # ax + ay = a(x+y)
    a = common_coeff * (common_var * common_var_power)
    x = term1_coeff
    y = term2_coeff * var2
    
    # 展開
    # (common_coeff * x^p) * term1_coeff + (common_coeff * x^p) * term2_coeff * y
    final_term1 = f"{common_coeff * term1_coeff}{common_var}{'^' + str(common_var_power) if common_var_power > 1 else ''}"
    final_term2 = f"{common_coeff * term2_coeff}{common_var}{'^' + str(common_var_power) if common_var_power > 1 else ''}{var2}"
    
    question_text = f"請對多項式 {final_term1} + {final_term2} 進行因式分解。"
    
    correct_answer = f"{common_coeff}{common_var}{'^' + str(common_var_power) if common_var_power > 1 else ''}({term1_coeff}+{term2_coeff}{var2})"
    if common_var_power == 1:
        correct_answer = f"{common_coeff}{common_var}({term1_coeff}+{term2_coeff}{var2})"

    context_string = "找出各項共同的因式，並將其提出。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").replace("*", "")
    correct = correct_answer.strip().replace(" ", "").replace("*", "")
    is_correct = user == correct # 簡化檢查，未來可引入符號運算庫
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。參考答案是：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}