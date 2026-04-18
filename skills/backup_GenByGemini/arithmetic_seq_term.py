import random

def generate(level=1):
    """
    生成一道「等差數列一般項」的題目。
    an = a1 + (n-1)d
    """
    a1 = random.randint(-10, 10)
    d = random.randint(-5, 5)
    while d == 0: d = random.randint(-5, 5)

    m = random.randint(3, 8)
    n = random.randint(m + 2, 15)
    am = a1 + (m - 1) * d
    an = a1 + (n - 1) * d
    
    p = random.randint(n + 2, 20)
    ap = a1 + (p - 1) * d
    
    question_text = f"已知一等差數列的第 {m} 項為 {am}，第 {n} 項為 {an}，請求出第 {p} 項的值。"
    correct_answer = str(ap)

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}