import random
import numpy as np

def generate(level=1):
    """
    生成一道「矩陣係數積」的題目。
    """
    rows, cols = (2, 2) if level == 1 else (2, 3)
    A = np.random.randint(-9, 10, size=(rows, cols))
    k = random.randint(-5, 5)
    while k == 0 or k == 1: k = random.randint(-5, 5)
    
    question_text = f"請計算下列矩陣運算：\n{k} * \n{A}"
    result = k * A
    correct_answer = str(result)
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").replace("\n","")
    correct = str(correct_answer).strip().replace(" ", "").replace("\n","")
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 \n{correct_answer}。" if is_correct else f"答案不正確。正確答案應為：\n{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}