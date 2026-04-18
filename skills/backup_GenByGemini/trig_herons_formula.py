import random
import math

def generate(level=1):
    """
    生成一道「海龍公式」的題目。
    """
    if level == 1:
        # 使用畢氏三元數的邊長，確保是三角形
        a, b, c = random.choice([(3,4,5), (5,12,13), (7,24,25)])
    else: # level 2
        a, b, c = random.randint(5,10), random.randint(5,10), random.randint(5,10)
        while not (a+b>c and a+c>b and b+c>a):
            a, b, c = random.randint(5,10), random.randint(5,10), random.randint(5,10)

    question_text = f"已知三角形的三邊長分別為 {a}, {b}, {c}，請問此三角形的面積是多少？ (四捨五入至小數點後一位)"
    s = (a + b + c) / 2
    area = math.sqrt(s * (s - a) * (s - b) * (s - c))
    correct_answer = str(round(area, 1))
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    try:
        # 嘗試將使用者輸入轉換為浮點數
        user_float = float(user)
        is_correct = abs(user_float - float(correct)) < 0.1
        result_text = f"完全正確！答案約為 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
        return {"correct": is_correct, "result": result_text, "next_question": True}
    except ValueError:
        # 如果轉換失敗（例如輸入為空或非數字），回傳錯誤訊息
        return {"correct": False, "result": f"請輸入有效的數字答案。正確答案應為：{correct_answer}", "next_question": False}