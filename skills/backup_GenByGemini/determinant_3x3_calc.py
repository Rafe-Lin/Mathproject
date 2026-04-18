import random
import numpy as np

def generate(level=1):
    """
    生成一道「三階行列式」的計算題。
    """
    if level == 1:
        # 包含 0，簡化計算
        matrix = [[random.randint(-5, 5) for _ in range(3)] for _ in range(2)]
        matrix.append([random.randint(-2,2), random.randint(-2,2), 0])
        random.shuffle(matrix)
    else: # level 2
        matrix = [[random.randint(-5, 5) for _ in range(3)] for _ in range(3)]

    question_text = f"請計算三階行列式的值：\n| {matrix[0][0]}  {matrix[0][1]}  {matrix[0][2]} |\n| {matrix[1][0]}  {matrix[1][1]}  {matrix[1][2]} |\n| {matrix[2][0]}  {matrix[2][1]}  {matrix[2][2]} |"
    det = np.linalg.det(np.array(matrix))
    correct_answer = str(round(det))
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}