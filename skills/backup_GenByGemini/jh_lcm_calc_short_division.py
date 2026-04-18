# skills/jh_lcm_calc_short_division.py
import random
import math

def lcm(a, b):
    return abs(a*b) // math.gcd(a, b) if a != 0 and b != 0 else 0

def generate(level=1):
    """
    生成一道「用短除法求最小公倍數」的題目。
    """
    # 為了讓短除法有意義，构造有共同質因數的數字
    f1 = random.randint(2, 5)
    f2 = random.randint(2, 5)
    
    n1 = f1 * random.randint(1, 4)
    n2 = f2 * random.randint(1, 4)
    while n1 == n2:
        n2 = f2 * random.randint(1, 4)

    question_text = f"請使用短除法，找出 {n1} 和 {n2} 的最小公倍數。"
    
    correct_answer = str(lcm(n1, n2))

    context_string = f"使用短除法求兩數的最小公倍數。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    """
    檢查使用者輸入的答案是否正確。
    """
    user = user_answer.strip()
    correct = str(correct_answer).strip()

    is_correct = user == correct
    result_text = f"完全正確！答案是 {correct}。" if is_correct else f"答案不正確。正確答案是：{correct}"
    return {"correct": is_correct, "result": result_text, "next_question": True}