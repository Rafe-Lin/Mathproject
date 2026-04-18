import random

def generate(level=1):
    """
    生成一道「絕對值方程式 (多項)」的題目。
    |x-a| + |x-b| = c
    """
    a = random.randint(-5, 0)
    b = random.randint(1, 5)
    dist = b - a
    
    if level == 1:
        # c > |a-b|, 兩解
        c = random.randint(dist + 1, dist + 5)
        question_text = f"請求解絕對值方程式：|x - {a}| + |x - {b}| = {c} (若有兩解，請用逗號 , 分隔)"
        # (x-a) + (x-b) = c => 2x = a+b+c => x = (a+b+c)/2
        # -(x-a) - (x-b) = c => -2x = c-a-b => x = (a+b-c)/2
        sol1 = (a + b + c) / 2
        sol2 = (a + b - c) / 2
        correct_answer = f"{sol1},{sol2}"
    else: # level 2
        # c = |a-b|, 無限多解
        c = dist
        question_text = f"請求解絕對值方程式：|x - {a}| + |x - {b}| = {c}"
        correct_answer = f"{a}<=x<={b}"

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    # 簡單比對，移除空白
    user = user_answer.replace(" ", "")
    correct = correct_answer.replace(" ", "")
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案是：{correct_answer}"
    return {"correct": is_correct, "result": result_text}