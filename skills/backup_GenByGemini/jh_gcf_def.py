# skills/jh_gcf_def.py
import random
import math

def get_factors(n):
    factors = set()
    for i in range(1, int(n**0.5) + 1):
        if n % i == 0:
            factors.add(i)
            factors.add(n//i)
    return sorted(list(factors))

def generate(level=1):
    """
    生成一道「最大公因數定義」的題目。
    """
    num1 = random.randint(10, 30)
    num2 = random.randint(10, 30)
    while num1 == num2 or math.gcd(num1, num2) == 1:
        num2 = random.randint(10, 30)

    factors1 = get_factors(num1)
    factors2 = get_factors(num2)
    
    question_text = f"請找出 {num1} 和 {num2} 的最大公因數。\n提示：\n{num1} 的因數有：{', '.join(map(str, factors1))}\n{num2} 的因數有：{', '.join(map(str, factors2))}"
    
    correct_answer = str(math.gcd(num1, num2))

    context_string = f"從兩數的公因數中找出最大的一個。"

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