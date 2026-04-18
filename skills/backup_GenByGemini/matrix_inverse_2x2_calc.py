import random
import numpy as np

def generate(level=1):
    """
    生成一道「2x2 反方陣」的計算題。
    """
    # 構造一個可逆矩陣
    A = np.random.randint(-5, 6, size=(2, 2))
    while np.linalg.det(A) == 0:
        A = np.random.randint(-5, 6, size=(2, 2))
        
    question_text = f"請求出下列矩陣的反方陣：\n{A}"
    
    # A = [[a,b],[c,d]], A⁻¹ = 1/det * [[d,-b],[-c,a]]
    det = A[0,0]*A[1,1] - A[0,1]*A[1,0]
    inv_A = (1/det) * np.array([[A[1,1], -A[0,1]], [-A[1,0], A[0,0]]])
    
    correct_answer = str(np.round(inv_A, 2))
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").replace("\n","")
    correct = str(correct_answer).strip().replace(" ", "").replace("\n","")
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 \n{correct_answer}。" if is_correct else f"答案不正確。正確答案應為：\n{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}