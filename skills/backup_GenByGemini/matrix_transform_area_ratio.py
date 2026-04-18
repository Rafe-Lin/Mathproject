import random
import numpy as np

def generate(level=1):
    """
    生成一道「線性變換與面積比」的題目。
    """
    A = np.random.randint(-5, 6, size=(2, 2))
    
    if level == 1:
        area = random.randint(5, 20)
        question_text = f"平面上一個面積為 {area} 的圖形，經過矩陣 A = \n{A}\n 的線性變換後，新的圖形面積會變為多少？"
    else: # level 2
        question_text = f"一個線性變換由矩陣 A = \n{A}\n 所定義。請問此變換會將平面上任意圖形的面積放大或縮小多少倍？"
    
    area_ratio = abs(np.linalg.det(A))
    correct_answer = str(round(area * area_ratio)) if level == 1 else str(round(area_ratio))
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}