# skills/jh_lcm_def.py
import random
import math

def get_multiples(n, limit):
    multiples = []
    for i in range(1, limit + 1):
        multiples.append(n * i)
    return multiples

def lcm(a, b):
    return abs(a*b) // math.gcd(a, b) if a != 0 and b != 0 else 0

def generate(level=1):
    """
    生成一道「最小公倍數定義」的題目。
    """
    num1 = random.randint(3, 8)
    num2 = random.randint(3, 8)
    while num1 == num2:
        num2 = random.randint(3, 8)

    limit = 10
    multiples1 = get_multiples(num1, limit)
    multiples2 = get_multiples(num2, limit)
    
    question_text = f"請找出 {num1} 和 {num2} 的最小公倍數。\n提示：\n{num1} 的倍數有：{', '.join(map(str, multiples1))}...\n{num2} 的倍數有：{', '.join(map(str, multiples2))}..."
    
    correct_answer = str(lcm(num1, num2))

    context_string = f"從兩數的公倍數中找出最小的一個。"

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