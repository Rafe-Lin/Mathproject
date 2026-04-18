import random
import numpy as np

def generate(level=1):
    """
    生成一道「平均數、中位數、百分位數」的題目。
    level 1: 求平均數或中位數。
    level 2: 求百分位數。
    """
    data = sorted([random.randint(60, 100) for _ in range(random.choice([9, 11]))]) # 奇數個方便算中位數
    data_str = ", ".join(map(str, data))
    
    if level == 1:
        q_type = random.choice(['mean', 'median'])
        if q_type == 'mean':
            question_text = f"一組數據為：{data_str}。請問這組數據的算術平均數是多少？ (四捨五入至小數點後一位)"
            correct_answer = str(round(np.mean(data), 1))
        else: # median
            question_text = f"一組數據為：{data_str}。請問這組數據的中位數是多少？"
            correct_answer = str(np.median(data))
    else: # level 2
        p = random.choice([25, 50, 75])
        question_text = f"一組數據為：{data_str}。請問這組數據的第 {p} 百分位數 (P{p}) 是多少？"
        # numpy's percentile is equivalent to PR/(N+1) method, may differ from textbook definition
        # For simplicity, we use the textbook method: index = (P/100)*N
        idx = int(np.ceil(p/100 * len(data))) - 1
        correct_answer = str(data[idx])

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}