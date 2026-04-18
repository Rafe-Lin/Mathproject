import random
import numpy as np

def generate(level=1):
    """
    生成一道「兩平面交線」的題目。
    """
    # 構造兩個不平行的平面
    n1 = np.array([random.randint(1, 3), random.randint(1, 3), 0])
    n2 = np.array([0, random.randint(1, 3), random.randint(1, 3)])
    d1 = random.randint(-5, 5)
    d2 = random.randint(-5, 5)
    
    plane1_eq = f"{n1[0]}x + {n1[1]}y + {n1[2]}z + {d1} = 0"
    plane2_eq = f"{n2[0]}x + {n2[1]}y + {n2[2]}z + {d2} = 0"
    
    question_text = f"請求出兩平面 E₁: {plane1_eq} 與 E₂: {plane2_eq} 的交線方向向量。"
    
    direction = np.cross(n1, n2)
    correct_answer = str(tuple(direction))
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip().replace(" ", "")
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}