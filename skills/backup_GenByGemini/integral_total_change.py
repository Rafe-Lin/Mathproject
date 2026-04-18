# \積分\總變化量 (定積分)
import random

def generate(level=1):
    """
    生成一道「總變化量 (定積分)」的題目。
    """
    if level == 1:
        rate = random.randint(10, 50)
        a, b = random.randint(0, 2), random.randint(3, 5)
        question_text = f"一個水龍頭以每分鐘 {rate} 公升的固定速率注水，請問從第 {a} 分鐘到第 {b} 分鐘，總共注入了多少公升的水？"
        correct_answer = str(rate * (b - a))
    else: # level 2
        v0, acc = random.randint(5, 15), random.randint(2, 5)
        a, b = random.randint(0, 2), random.randint(3, 5)
        question_text = f"一個物體的速度函數為 v(t) = {acc}t + {v0} (公尺/秒)。請問在 t={a} 到 t={b} 秒之間，此物體的位移（位置總變化量）是多少公尺？"
        # ∫[a,b] (acc*t + v0) dt = [acc/2 * t² + v0*t] from a to b
        ans = (acc/2 * b**2 + v0*b) - (acc/2 * a**2 + v0*a)
        correct_answer = str(ans)
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}