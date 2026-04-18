import random

def generate(level=1):
    """
    生成一道「數據標準化 (Z-score)」的題目。
    Z = (X - μ) / σ
    level 1: 求 Z-score。
    level 2: 已知 Z-score，反求原始分數。
    """
    mean = 70
    std = 10
    
    if level == 1:
        score = random.randint(50, 90)
        question_text = f"某次考試全班平均分數為 {mean} 分，標準差為 {std} 分。若小明考了 {score} 分，請問他的 Z-score 是多少？"
        z_score = (score - mean) / std
        correct_answer = str(z_score)
    else: # level 2
        z_score = random.choice([-2, -1.5, -1, 1, 1.5, 2])
        question_text = f"某次考試全班平均分數為 {mean} 分，標準差為 {std} 分。若小華的 Z-score 為 {z_score}，請問他的原始分數是多少分？"
        score = z_score * std + mean
        correct_answer = str(int(score))
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}