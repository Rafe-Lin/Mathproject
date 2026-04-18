import random

def generate(level=1):
    """
    生成一道「向量內積的坐標表示」的計算題。
    """
    if level == 1:
        v1 = [random.randint(-5, 5) for _ in range(2)]
        v2 = [random.randint(-5, 5) for _ in range(2)]
    else: # level 2
        v1 = [random.randint(-10, 10) for _ in range(2)]
        v2 = [random.randint(-10, 10) for _ in range(2)]

    question_text = f"已知向量 a = {tuple(v1)}，向量 b = {tuple(v2)}，請求出其內積 a · b。"
    dot_product = sum(v1[i] * v2[i] for i in range(2))
    correct_answer = str(dot_product)
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}