import random

def generate(level=1):
    """
    生成一道「等比數列一般項」的題目。
    an = a1 * r^(n-1)
    level 1: a1, r, n 為整數，求 an。
    level 2: 給定兩項，求另一項。
    """
    if level == 1:
        a1 = random.choice([-3, -2, -1, 1, 2, 3])
        r = random.choice([-3, -2, 2, 3])
        n = random.randint(3, 5)
        question_text = f"已知一等比數列的首項為 {a1}，公比為 {r}，請求出第 {n} 項的值。"
        correct_answer = str(a1 * (r**(n - 1)))
    else: # level 2
        a1 = random.choice([-2, -1, 1, 2])
        r = random.choice([-2, 2, 3])
        m = random.randint(2, 4)
        n = random.randint(m + 1, 6)
        am = a1 * (r**(m - 1))
        an = a1 * (r**(n - 1))
        
        p = random.randint(1, m-1)
        ap = a1 * (r**(p - 1))
        
        question_text = f"已知一等比數列的第 {m} 項為 {am}，第 {n} 項為 {an}，且公比為正數，請求出第 {p} 項的值。"
        correct_answer = str(ap)

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}