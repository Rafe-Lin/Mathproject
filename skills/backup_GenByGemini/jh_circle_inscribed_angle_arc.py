# skills/jh_circle_inscribed_angle_arc.py
import random

def generate(level=1):
    """
    生成一道「圓周角與弧的關係」的題目。
    """
    arc = random.randint(40, 200)
    # 確保是偶數，這樣角才會是整數
    if arc % 2 != 0:
        arc += 1
    
    angle = arc // 2

    q_type = random.choice(['angle_to_arc', 'arc_to_angle'])

    if q_type == 'angle_to_arc':
        question_text = f"在一個圓中，若一個圓周角為 {angle}°，請問它所對的弧的度數是多少度？"
        correct_answer = str(arc)
    else:
        question_text = f"在一個圓中，若一個弧的度數為 {arc}°，請問它所對的圓周角是多少度？"
        correct_answer = str(angle)

    context_string = "圓周角的度數等於其所對應的弧的度數的一半。"

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