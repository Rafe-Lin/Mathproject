import random
import math

def generate(level=1):
    """
    生成一道「由對數求位數」的題目。
    N 的位數 = floor(log(N)) + 1
    level 1: 給定 log(N) 的值，求 N 的位數。
    level 2: 給定 N = a^b，求 N 的位數 (需查表 log a)。
    """
    if level == 1:
        log_val = random.uniform(5, 20)
        log_val_str = f"{log_val:.4f}"
        question_text = f"已知 log(N) ≈ {log_val_str}，請問 N 是幾位數的整數？"
        correct_answer = str(math.floor(log_val) + 1)
    else: # level 2
        base = random.randint(2, 9)
        power = random.randint(10, 30)
        log_base_values = {2: 0.3010, 3: 0.4771, 6: 0.7781, 7: 0.8451}
        log_base = log_base_values.get(base, math.log10(base)) # Fallback for other bases
        
        question_text = f"試求 {base}^{power} 是幾位數的整數？ (參考數值: log{base} ≈ {log_base:.4f})"
        log_val = power * log_base
        correct_answer = str(math.floor(log_val) + 1)

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}