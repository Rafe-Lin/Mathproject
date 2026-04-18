import random
import numpy as np

def generate(level=1):
    """
    生成一道「馬可夫鏈」的題目。
    """
    # 構造一個轉移矩陣
    p1 = round(random.uniform(0.6, 0.9), 1)
    p2 = round(random.uniform(0.1, 0.4), 1)
    T = np.array([[p1, p2], [1-p1, 1-p2]])
    
    # 初始狀態
    s0 = np.array([random.randint(20, 80), random.randint(20, 80)])
    s0 = s0 / np.sum(s0) # 正規化
    
    question_text = f"某地區的選民結構，初始狀態（第0期）為 S₀ = {np.round(s0, 2)}。若選舉的轉移矩陣為 T = \n{T}\n，請問經過一期後，新的狀態 S₁ 為何？ (四捨五入至小數點後兩位)"
    
    s1 = np.dot(T, s0)
    correct_answer = str(np.round(s1, 2))
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").replace("\n","")
    correct = str(correct_answer).strip().replace(" ", "").replace("\n","")
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}