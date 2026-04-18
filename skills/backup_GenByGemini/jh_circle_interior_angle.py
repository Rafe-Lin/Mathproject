# skills/jh_circle_interior_angle.py
import random

def generate(level=1):
    """
    生成一道「圓內角」的題目。
    """
    # 圓內角 = (所對弧 + 對頂角所對弧) / 2
    # 為了讓數字漂亮，反向構造
    arc1 = random.randint(20, 100)
    arc2 = random.randint(20, 100)
    
    # 確保和為偶數
    if (arc1 + arc2) % 2 != 0:
        arc1 += 1
        
    interior_angle = (arc1 + arc2) // 2

    question_text = f"圓內的兩弦相交，所形成的其中一個圓內角，其所對的弧與其對頂角所對的弧，度數分別為 {arc1}° 和 {arc2}°。請問這個圓內角是多少度？"
    correct_answer = str(interior_angle)

    context_string = "圓內角的度數等於其所對的弧與其對頂角所對的弧，兩弧度數和的一半。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    user = user_answer.strip().replace("°", "")
    correct = correct_answer.strip()
    is_correct = user == correct
    result_text = f"完全正確！答案是 {correct}°。" if is_correct else f"答案不正確。正確答案是：{correct}°"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}