# skills/jh_gcf_lcm_relation.py
import random
import math

def lcm(a, b):
    return abs(a*b) // math.gcd(a, b) if a != 0 and b != 0 else 0

def generate(level=1):
    """
    生成一道「最大公因數與最小公倍數的關係」的題目。
    a * b = gcd(a, b) * lcm(a, b)
    """
    a = random.randint(10, 30)
    b = random.randint(10, 30)
    while a == b:
        b = random.randint(10, 30)

    gcd_val = math.gcd(a, b)
    lcm_val = lcm(a, b)

    q_type = random.choice(['find_lcm', 'find_prod'])
    if q_type == 'find_lcm':
        question_text = f"已知兩正整數 {a}、{b} 的最大公因數為 {gcd_val}，請問它們的最小公倍數是多少？"
        correct_answer = str(lcm_val)
    else:
        question_text = f"已知兩正整數的最大公因數為 {gcd_val}，最小公倍數為 {lcm_val}，請問這兩數的乘積是多少？"
        correct_answer = str(a * b)

    context_string = f"利用關係式：兩數乘積 = 最大公因數 × 最小公倍數"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    user = user_answer.strip()
    correct = str(correct_answer).strip()
    is_correct = user == correct
    result_text = f"完全正確！答案是 {correct}。" if is_correct else f"答案不正確。正確答案是：{correct}"
    return {"correct": is_correct, "result": result_text, "next_question": True}