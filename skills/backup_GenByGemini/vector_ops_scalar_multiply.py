import random

def generate(level=1):
    """
    生成一道「平面向量的係數積」的題目。
    """
    v1 = [random.randint(-10, 10) for _ in range(2)]
    k = random.randint(-5, 5)
    while k == 0 or k == 1: k = random.randint(-5, 5)
    
    question_text = f"已知向量 a = {tuple(v1)}，請求出向量 {k}a。"
    ans_vec = [k*c for c in v1]
    correct_answer = f"({ans_vec[0]},{ans_vec[1]})"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip().replace(" ", "")
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}