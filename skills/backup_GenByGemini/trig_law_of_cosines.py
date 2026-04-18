import random
import math

def generate(level=1):
    """
    生成一道「餘弦定理」的題目。
    c² = a² + b² - 2ab*cosC
    """
    a = random.randint(5, 10)
    b = random.randint(5, 10)
    
    if level == 1:
        angle_C = random.choice([60, 120])
        question_text = f"在三角形ABC中，已知兩邊長 a={a}, b={b}，其夾角 ∠C = {angle_C}°，請問第三邊長 c 是多少？ (四捨五入至小數點後一位)"
        # c² = a² + b² - 2ab*cosC
        c_sq = a**2 + b**2 - 2*a*b*math.cos(math.radians(angle_C))
        correct_answer = str(round(math.sqrt(c_sq), 1))
    else: # level 2
        c = random.randint(max(a,b)-min(a,b)+1, a+b-1)
        question_text = f"在三角形ABC中，已知三邊長 a={a}, b={b}, c={c}，請問最大角 ∠C (c邊的對角) 的角度約為多少度？ (四捨五入至整數位)"
        # cosC = (a² + b² - c²) / 2ab
        cos_C = (a**2 + b**2 - c**2) / (2 * a * b)
        correct_answer = str(round(math.degrees(math.acos(cos_C))))
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    try:
        user_float = float(user)
        is_correct = abs(user_float - float(correct)) < 1 # 允許較大誤差
        result_text = f"完全正確！答案約為 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
        return {"correct": is_correct, "result": result_text, "next_question": True}
    except ValueError:
        return {"correct": False, "result": f"請輸入有效的數字答案。正確答案應為：{correct_answer}", "next_question": False}