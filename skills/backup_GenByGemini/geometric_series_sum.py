import random

def generate(level=1):
    """
    生成一道「等比級數求和」的題目。
    Sn = a1(r^n - 1) / (r-1)
    level 1: r 為正整數。
    level 2: r 為負整數。
    """
    n = random.randint(3, 5)
    a1 = random.randint(1, 5)
    
    if level == 1:
        r = random.randint(2, 4)
    else: # level 2
        r = random.randint(-3, -2)

    question_text = f"一個等比級數共有 {n} 項，首項為 {a1}，公比為 {r}，請求出此級數的和。"
    
    # Sn = a1 * (r^n - 1) / (r - 1)
    total_sum = a1 * (r**n - 1) // (r - 1)
    correct_answer = str(total_sum)

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}