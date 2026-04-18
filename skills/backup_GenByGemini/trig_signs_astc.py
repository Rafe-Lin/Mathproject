import random

def generate(level=1):
    """
    生成一道「各象限三角函數正負」的題目。
    """
    quadrant_map = {1: "一", 2: "二", 3: "三", 4: "四"}
    quadrant = random.randint(1, 4)
    
    if level == 1:
        question_text = f"在第 {quadrant_map[quadrant]} 象限中，sin(θ) 的值是正的還是負的？ (正/負)"
        correct_answer = "正" if quadrant in [1, 2] else "負"
    else: # level 2
        question_text = f"在哪個象限中，tan(θ) > 0 且 cos(θ) < 0？ (請回答 一, 二, 三, 或 四)"
        correct_answer = "三"

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}