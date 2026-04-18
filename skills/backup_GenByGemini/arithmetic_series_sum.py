import random

def generate(level=1):
    """
    生成一道「等差級數求和」的題目。
    Sn = n/2 * (a1 + an) = n/2 * (2a1 + (n-1)d)
    """
    n = random.randint(10, 30)
    a1 = random.randint(-10, 10)
    
    an = random.randint(a1 + n, a1 + n*5)
    # 確保 an-a1 是 n-1 的倍數，這樣 d 才是整數
    while (an - a1) % (n - 1) != 0: an += 1
    question_text = f"一個等差級數共有 {n} 項，首項為 {a1}，末項為 {an}，請求出此級數的和。"
    # Sn = n/2 * (a1 + an)
    total_sum = n * (a1 + an) // 2

    correct_answer = str(total_sum)
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}