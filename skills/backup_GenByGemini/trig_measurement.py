import random
import math

def generate(level=1):
    """
    生成一道「三角測量」的應用題。
    """
    if level == 1:
        dist = random.randint(50, 100)
        angle = random.choice([30, 45, 60])
        question_text = f"小明在平地上測量一棟大樓的高度。他在地面上一點測得樓頂的仰角為 {angle}°，並測得他與大樓的水平距離為 {dist} 公尺。請問樓高約為多少公尺？ (tan{angle}° ≈ {math.tan(math.radians(angle)):.2f}, 四捨五入至整數位)"
        height = dist * math.tan(math.radians(angle))
    else: # level 2
        h = random.randint(80, 150)
        angle = random.choice([30, 45, 60])
        question_text = f"飛機在 {h} 公尺的高空水平飛行，飛行員觀測到地面目標的俯角為 {angle}°。請問飛機與目標的水平距離約為多少公尺？ (tan{angle}° ≈ {math.tan(math.radians(angle)):.2f}, 四捨五入至整數位)"
        height = h / math.tan(math.radians(angle))
    correct_answer = str(round(height))
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    try:
        user_float = float(user)
        is_correct = abs(user_float - float(correct)) < 2 # 允許一點誤差
        result_text = f"完全正確！答案約為 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
        return {"correct": is_correct, "result": result_text, "next_question": True}
    except ValueError:
        return {"correct": False, "result": f"請輸入有效的數字答案。正確答案應為：{correct_answer}", "next_question": False}