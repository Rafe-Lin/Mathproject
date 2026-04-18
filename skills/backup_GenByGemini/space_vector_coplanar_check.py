import random
import numpy as np

def generate(level=1):
    """
    生成一道「三向量共平面檢查」的題目。
    """
    is_coplanar = random.choice([True, False])
    
    v1 = [random.randint(1, 5), random.randint(1, 5), 0]
    v2 = [random.randint(1, 5), 0, random.randint(1, 5)]
    
    if is_coplanar:
        # 構造共平面向量
        v3 = [v1[i] + v2[i] for i in range(3)]
        correct_answer = "是"
    else:
        v3 = [0, 0, random.randint(1, 5)] # 構造不共平面
        correct_answer = "否"

    question_text = f"請問向量 a={tuple(v1)}, b={tuple(v2)}, c={tuple(v3)} 是否共平面？ (是/否)"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip()
    is_correct = (user == correct_answer)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}