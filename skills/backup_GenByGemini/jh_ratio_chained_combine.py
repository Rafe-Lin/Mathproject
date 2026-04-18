# skills/jh_ratio_chained_combine.py
import random
import math

def generate(level=1):
    """
    生成一道「連比的合併」的題目。
    """
    # 構造 a:b 和 b:c
    a = random.randint(2, 5)
    b1 = random.randint(2, 5)
    
    b2 = random.randint(2, 5)
    c = random.randint(2, 5)

    # 找出 b1 和 b2 的最小公倍數
    lcm_b = (b1 * b2) // math.gcd(b1, b2)
    
    # 擴分
    mult1 = lcm_b // b1
    mult2 = lcm_b // b2
    
    final_a = a * mult1
    final_b = lcm_b
    final_c = c * mult2

    # 約分到最簡整數比
    common_divisor = math.gcd(math.gcd(final_a, final_b), final_c)
    final_a //= common_divisor
    final_b //= common_divisor
    final_c //= common_divisor

    question_text = f"若 x : y = {a}:{b1}，且 y : z = {b2}:{c}，請問 x : y : z 的最簡整數比是多少？"
    correct_answer = f"{final_a}:{final_b}:{final_c}"

    context_string = "合併連比時，需要將共同項的數值變為它們的最小公倍數，再進行擴分。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = correct_answer.strip().replace(" ", "")
    is_correct = user == correct
    result_text = f"完全正確！答案是 {correct}。" if is_correct else f"答案不正確。正確答案是：{correct}"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}