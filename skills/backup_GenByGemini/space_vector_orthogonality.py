import random

def generate(level=1):
    """
    生成一道「空間向量垂直」的題目。
    """
    if level == 1:
        v1 = [random.randint(1, 5), random.randint(1, 5), 0]
        v2 = [-v1[1], v1[0], 0] # 構造垂直向量
        question_text = f"已知向量 a = {tuple(v1)}，向量 b = {tuple(v2)}，請問兩向量是否垂直？ (是/否)"
        correct_answer = "是"
    else: # level 2
        v1 = [random.randint(-5, 5) for _ in range(2)]
        v1.append(random.randint(1,5)) # 確保 z 不為 0
        x = random.randint(-5, 5)
        # v1[0]*x + v1[1]*y + v1[2]*z = 0
        y = -(v1[0]*x + v1[2]*random.randint(1,5)) / v1[1] # 構造垂直
        v2 = [x, int(y), random.randint(1,5)]
        question_text = f"已知向量 a = {tuple(v1)} 與向量 b = ({v2[0]}, {v2[1]}, z) 互相垂直，請求出 z 的值。"
        correct_answer = str(v2[2])
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user.lower() == correct.lower())
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}