import random

def generate(level=1):
    """
    生成一道「空間向量的平行」的題目。
    """
    v1 = [random.randint(-5, 5) for _ in range(3)]
    # 確保基準向量不是零向量
    while all(c == 0 for c in v1):
        v1 = [random.randint(-5, 5) for _ in range(3)]
    
    k = random.randint(-3, 3)
    while k == 0 or k == 1: k = random.randint(-3, 3)
    
    v2 = [c * k for c in v1]
    
    if level == 1:
        question_text = f"已知向量 a = {tuple(v1)} 與向量 b = {tuple(v2)} 平行，請問 b 是 a 的幾倍？"
        correct_answer = str(k)
    else: # level 2
        idx_to_hide = random.randint(0, 2)
        v2_q = list(v2)
        v2_q[idx_to_hide] = 'x'
        question_text = f"已知向量 a = {tuple(v1)} 與向量 b = {tuple(v2_q)} 平行，請問 x 的值是多少？"
        correct_answer = str(v2[idx_to_hide])
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}