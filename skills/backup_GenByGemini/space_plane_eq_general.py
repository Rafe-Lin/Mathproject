import random

def generate(level=1):
    """
    生成一道「平面一般式」的題目。
    """
    coeffs = [random.randint(-5, 5) for _ in range(4)]
    while coeffs[0]==0 and coeffs[1]==0 and coeffs[2]==0: coeffs = [random.randint(-5, 5) for _ in range(4)]
    
    plane_eq = f"{coeffs[0]}x + {coeffs[1]}y + {coeffs[2]}z + {coeffs[3]} = 0".replace("+-", "-")
    
    if level == 1:
        question_text = f"請問平面 E: {plane_eq} 的一個法向量為何？"
        correct_answer = f"({coeffs[0]},{coeffs[1]},{coeffs[2]})"
    else: # level 2
        question_text = f"請問點 (1, 1, 1) 是否在平面 E: {plane_eq} 上？ (是/否)"
        on_plane = (coeffs[0] + coeffs[1] + coeffs[2] + coeffs[3] == 0)
        correct_answer = "是" if on_plane else "否"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").lower()
    correct = str(correct_answer).strip().replace(" ", "").lower()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}