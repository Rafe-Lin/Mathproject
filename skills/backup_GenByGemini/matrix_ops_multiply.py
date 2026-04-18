import random
import numpy as np

def generate(level=1):
    """
    生成一道「矩陣乘法」的題目。
    """
    if level == 1:
        A = np.random.randint(-5, 6, size=(2, 2))
        B = np.random.randint(-5, 6, size=(2, 2))
    else: # level 2
        A = np.random.randint(-5, 6, size=(2, 3))
        B = np.random.randint(-5, 6, size=(3, 2))
    
    question_text = f"請計算下列矩陣乘法：\n{A}\n * \n{B}"
    result = np.dot(A, B)
    correct_answer = str(result)
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").replace("\n","")
    correct = str(correct_answer).strip().replace(" ", "").replace("\n","")
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 \n{correct_answer}。" if is_correct else f"答案不正確。正確答案應為：\n{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}