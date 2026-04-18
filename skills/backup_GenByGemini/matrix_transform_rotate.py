import random

def generate(level=1):
    """
    生成一道「旋轉變換」的題目。
    """
    angle = random.choice([30, 45, 60, 90])
    if level == 1:
        question_text = f"將平面上所有點以原點為中心，逆時針旋轉 90°。請問此旋轉變換對應的矩陣為何？"
        correct_answer = "[[0,-1],[1,0]]"
    else: # level 2
        question_text = f"將平面上所有點以原點為中心，逆時針旋轉 {angle}°。請問此旋轉變換對應的矩陣為何？\n(cos{angle}, sin{angle})"
        correct_answer = f"[[cos{angle},-sin{angle}],[sin{angle},cos{angle}]]"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}