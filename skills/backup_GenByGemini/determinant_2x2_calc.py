import random
import numpy as np

def generate(level=1):
    """
    生成一道「二階行列式」的計算題。
    """
    if level == 1:
        matrix = [[random.randint(0, 10) for _ in range(2)] for _ in range(2)]
    else: # level 2
        matrix = [[random.randint(-10, 10) for _ in range(2)] for _ in range(2)]

    question_text = f"請計算二階行列式的值：\n| {matrix[0][0]}  {matrix[0][1]} |\n| {matrix[1][0]}  {matrix[1][1]} |"
    det = matrix[0][0]*matrix[1][1] - matrix[0][1]*matrix[1][0]
    correct_answer = str(det)
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}