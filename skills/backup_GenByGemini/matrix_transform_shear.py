import random

def generate(level=1):
    """
    生成一道「推移變換」的題目。
    """
    k = random.randint(2, 5)
    if level == 1:
        question_text = f"將平面上所有點 (x,y) 變換到 (x+{k}y, y)。請問此水平推移變換對應的矩陣為何？"
        correct_answer = f"[[1,{k}],[0,1]]"
    else: # level 2
        question_text = f"將平面上所有點 (x,y) 變換到 (x, y+{k}x)。請問此垂直推移變換對應的矩陣為何？"
        correct_answer = f"[[1,0],[{k},1]]"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}