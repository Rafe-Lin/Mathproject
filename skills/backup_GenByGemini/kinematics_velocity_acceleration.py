# \微分\運動學 (微分)
import random

def generate(level=1):
    """
    生成一道「運動學(微分)」的題目。
    """
    a, b, c = random.randint(1, 5), random.randint(1, 10), random.randint(1, 10)
    t = random.randint(1, 5)
    
    s_t = f"{a}t² + {b}t + {c}"
    
    if level == 1:
        question_text = f"一個物體的位置函數為 s(t) = {s_t}，請問在 t={t} 時刻的瞬時速度 v({t}) 是多少？"
        # v(t) = s'(t) = 2at + b
        correct_answer = str(2 * a * t + b)
    else: # level 2
        question_text = f"一個物體的位置函數為 s(t) = {s_t}，請問其加速度 a(t) 是多少？"
        # a(t) = v'(t) = s''(t) = 2a
        correct_answer = str(2 * a)
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}