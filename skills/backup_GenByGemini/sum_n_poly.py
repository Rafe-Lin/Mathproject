import random

def generate(level=1):
    """
    生成一道「級數和公式」的題目。
    Σk, Σk², Σk³
    level 1: Σk²
    level 2: Σk³
    """
    n = random.randint(5, 15)
    
    if level == 1:
        question_text = f"請計算 1² + 2² + ... + {n}² 的值。"
        # Σk² = n(n+1)(2n+1)/6
        total_sum = n * (n + 1) * (2 * n + 1) // 6
    else: # level 2
        question_text = f"請計算 1³ + 2³ + ... + {n}³ 的值。"
        # Σk³ = [n(n+1)/2]²
        base_sum = n * (n + 1) // 2
        total_sum = base_sum * base_sum

    correct_answer = str(total_sum)
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}