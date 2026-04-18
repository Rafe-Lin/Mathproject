# \機率統計\期望值的線性運算
import random

def generate(level=1):
    """
    生成一道「期望值的線性運算」的題目。
    """
    ex = random.randint(10, 50)
    a = random.randint(2, 5)
    b = random.randint(-10, 10)
    
    if level == 1:
        question_text = f"已知隨機變數 X 的期望值 E(X) = {ex}，請問 E({a}X) 是多少？"
        correct_answer = str(a * ex)
    else: # level 2
        question_text = f"已知隨機變數 X 的期望值 E(X) = {ex}，請問 E({a}X + {b}) 是多少？"
        correct_answer = str(a * ex + b)
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}