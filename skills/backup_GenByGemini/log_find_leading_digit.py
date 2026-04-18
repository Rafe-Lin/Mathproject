import random
import math

def generate(level=1):
    """
    生成一道「由對數求最高位數字」的題目。
    log(N) 的尾數 m，10^m 的整數部分即為最高位數字。
    level 1: 給定 log(N) 的值，求最高位數字。
    level 2: 給定 N = a^b，求 N 的最高位數字。
    """
    log_base_values = {
        2: 0.3010, 3: 0.4771, 4: 0.6020, 5: 0.6990, 
        6: 0.7781, 7: 0.8451, 8: 0.9030, 9: 0.9542
    }
    
    if level == 1:
        log_val = random.uniform(5, 15)
        mantissa = log_val - math.floor(log_val)
        question_text = f"已知 log(N) ≈ {log_val:.4f}，請問 N 的最高位數字是多少？ (參考: log2≈0.3010, log3≈0.4771, ...)"
    else: # level 2
        base = random.choice([2, 3, 7])
        power = random.randint(10, 20)
        log_base = log_base_values[base]
        log_val = power * log_base
        mantissa = log_val - math.floor(log_val)
        question_text = f"試求 {base}^{power} 的最高位數字是多少？ (參考: log2≈0.3010, log3≈0.4771, log7≈0.8451)"

    for i in range(1, 10):
        if mantissa < math.log10(i + 1):
            correct_answer = str(i)
            break

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}