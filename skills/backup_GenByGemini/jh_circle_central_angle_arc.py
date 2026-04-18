# skills/jh_circle_central_angle_arc.py
import random

def generate(level=1):
    """
    生成一道「圓心角與弧的關係」的題目。
    """
    angle = random.randint(30, 150)

    q_type = random.choice(['angle_to_arc', 'arc_to_angle'])

    if q_type == 'angle_to_arc':
        question_text = f"在一個圓中，若一個圓心角為 {angle}°，請問它所對的弧的度數是多少度？"
        correct_answer = str(angle)
    else:
        question_text = f"在一個圓中，若一個弧的度數為 {angle}°，請問它所對的圓心角是多少度？"
        correct_answer = str(angle)

    context_string = "圓心角的度數等於其所對應的弧的度數。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    user = user_answer.strip().replace("°", "")
    correct = correct_answer.strip()
    try:
        is_correct = int(user) == int(correct)
        result_text = f"完全正確！答案是 {correct}°。" if is_correct else f"答案不正確。正確答案是：{correct}°"
    except ValueError:
        is_correct = False
        result_text = f"請輸入數字答案。正確答案是：{correct}°"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}