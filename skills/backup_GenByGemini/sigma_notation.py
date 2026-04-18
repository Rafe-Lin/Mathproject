import random

def generate(level=1):
    """
    生成一道「Sigma (Σ) 符號」的計算題。
    level 1: 一般項為 k 或常數。
    level 2: 一般項為 ak+b。
    """
    start = 1
    end = random.randint(5, 15)
    
    if level == 1:
        c = random.randint(2, 10)
        question_text = f"請計算 Σ (從 k=1 到 {end}) {c}k 的值。"
        # c * n(n+1)/2
        total_sum = c * end * (end + 1) // 2
    else: # level 2
        a = random.randint(2, 5)
        b = random.randint(-5, 5)
        question_text = f"請計算 Σ (從 k=1 到 {end}) ({a}k + {b}) 的值。"
        # a * n(n+1)/2 + b*n
        total_sum = a * end * (end + 1) // 2 + b * end

    correct_answer = str(total_sum)
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}