import random
import numpy as np

def generate(level=1):
    """
    生成一道「全距、變異數、標準差」的題目。
    level 1: 求全距。
    level 2: 求標準差。
    """
    data = sorted([random.randint(1, 20) for _ in range(5)])
    data_str = ", ".join(map(str, data))
    
    if level == 1:
        question_text = f"一組數據為：{data_str}。請問這組數據的全距是多少？"
        correct_answer = str(np.ptp(data))
    else: # level 2
        # 為了讓答案漂亮，構造一組平均數為整數的數據
        mean = random.randint(5, 15)
        data = [mean-3, mean-1, mean, mean+1, mean+3]
        data_str = ", ".join(map(str, data))
        question_text = f"一組數據為：{data_str}。請問這組數據的母體標準差 (σ) 是多少？ (四捨五入至小數點後兩位)"
        correct_answer = str(round(np.std(data), 2))

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}