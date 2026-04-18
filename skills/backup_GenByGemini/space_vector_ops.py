import random

def generate(level=1):
    """
    生成一道「空間向量的加減法與係數積」的題目。
    """
    v1 = [random.randint(-5, 5) for _ in range(3)]
    v2 = [random.randint(-5, 5) for _ in range(3)]
    
    if level == 1:
        op = random.choice(['+', '-'])
        question_text = f"已知向量 a = {tuple(v1)}，向量 b = {tuple(v2)}，請求出向量 a {op} b。"
        if op == '+':
            ans_vec = [v1[i] + v2[i] for i in range(3)]
        else:
            ans_vec = [v1[i] - v2[i] for i in range(3)]
    else: # level 2
        k1 = random.randint(-3, 3)
        k2 = random.randint(-3, 3)
        question_text = f"已知向量 a = {tuple(v1)}，向量 b = {tuple(v2)}，請求出向量 {k1}a + {k2}b。"
        ans_vec = [k1*v1[i] + k2*v2[i] for i in range(3)]
        
    correct_answer = f"({ans_vec[0]},{ans_vec[1]},{ans_vec[2]})"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip().replace(" ", "")
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}