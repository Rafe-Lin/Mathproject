import random
import numpy as np

def generate(level=1):
    """
    生成一道「克拉瑪公式解二元一次聯立方程式」的題目。
    """
    # 構造一個解為整數的方程組
    sol = [random.randint(-5, 5) for _ in range(2)]
    
    A = np.array([[random.randint(1,5) for _ in range(2)] for _ in range(2)])
    while np.linalg.det(A) == 0:
        A = np.array([[random.randint(1,5) for _ in range(2)] for _ in range(2)])
            
    B = np.dot(A, sol)
    
    eq1 = f"{A[0,0]}x + {A[0,1]}y = {B[0]}"
    eq2 = f"{A[1,0]}x + {A[1,1]}y = {B[1]}"
    
    var_to_solve = random.choice(['x', 'y'])
    question_text = f"請使用克拉瑪公式解下列聯立方程式，並求出 {var_to_solve} 的值：\n{eq1}\n{eq2}"
    correct_answer = str(sol[0] if var_to_solve == 'x' else sol[1])
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}