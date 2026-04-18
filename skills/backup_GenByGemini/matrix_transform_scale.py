import random

def generate(level=1):
    """
    生成一道「伸縮變換」的題目。
    """
    kx = random.randint(2, 5)
    if level == 1:
        question_text = f"將平面上所有點的 x 坐標伸縮為 {kx} 倍，y 坐標不變。請問此伸縮變換對應的矩陣為何？"
        correct_answer = f"[[{kx},0],[0,1]]"
    else: # level 2
        ky = random.randint(2, 5)
        question_text = f"將平面上所有點的 x 坐標伸縮為 {kx} 倍，y 坐標伸縮為 {ky} 倍。請問此伸縮變換對應的矩陣為何？"
        correct_answer = f"[[{kx},0],[0,{ky}]]"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}