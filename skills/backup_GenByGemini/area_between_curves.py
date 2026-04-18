# \積分應用\兩曲線間面積
import random

def generate(level=1):
    """
    生成一道「兩曲線間面積」的題目。
    """
    a, b = 0, random.randint(2, 4)
    question_text = f"請求出 y=x² 與 y=x 在區間 [0, 1] 所圍成的面積。"
    # ∫[0,1] (x - x²) dx = [x²/2 - x³/3] from 0 to 1 = 1/2 - 1/3
    correct_answer = "1/6"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}