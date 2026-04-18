import random

def generate(level=1):
    """
    生成一道「鏡射變換」的題目。
    """
    if level == 1:
        axis = random.choice(['x', 'y'])
        question_text = f"將平面上所有點對 {axis} 軸作鏡射。請問此鏡射變換對應的矩陣為何？"
        if axis == 'x': correct_answer = "[[1,0],[0,-1]]"
        else: correct_answer = "[[-1,0],[0,1]]"
    else: # level 2
        line = "y=x"
        question_text = f"將平面上所有點對直線 {line} 作鏡射。請問此鏡射變換對應的矩陣為何？"
        correct_answer = "[[0,1],[1,0]]"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}