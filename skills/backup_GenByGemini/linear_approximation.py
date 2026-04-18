# \微分\一次估計
import random

def generate(level=1):
    """
    生成一道「一次估計(線性近似)」的題目。
    """
    a = random.randint(1, 4)
    a_sq = a*a
    x = a_sq + 0.1
    
    if level == 1:
        question_text = f"請利用線性近似，在 x={a_sq} 處估計 f(x) = x² 在 x={x} 的近似值。"
        # f(x) ≈ f(a) + f'(a)(x-a)
        # f(a_sq) = a_sq², f'(x)=2x, f'(a_sq)=2a_sq
        # f(x) ≈ a_sq² + 2a_sq * (x-a_sq)
        approx_val = a_sq**2 + 2*a_sq * (x - a_sq)
    else: # level 2
        question_text = f"請利用線性近似，在 x={a_sq} 處估計 f(x) = √x 在 x={x} 的近似值。"
        # f(x) ≈ f(a) + f'(a)(x-a)
        # f(a_sq) = a, f'(x)=1/(2√x), f'(a_sq)=1/(2a)
        approx_val = a + (1/(2*a)) * (x - a_sq)
    correct_answer = str(round(approx_val, 3))
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = abs(float(user) - float(correct)) < 0.01
    result_text = f"完全正確！答案約為 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}