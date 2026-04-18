# skills/jh_circle_tangent_chord_angle.py
import random

def generate(level=1):
    """
    生成一道「弦切角」的題目。
    """
    # 弦切角 = 所夾弧度數 / 2
    # 為了讓數字漂亮，反向構造
    tangent_chord_angle = random.randint(30, 100)
    arc = tangent_chord_angle * 2

    q_type = random.choice(['angle_to_arc', 'arc_to_angle'])

    if q_type == 'angle_to_arc':
        question_text = f"過圓上一點的切線與一弦的夾角為 {tangent_chord_angle}°，請問此角所夾的弧度數是多少度？"
        correct_answer = str(arc)
    else:
        question_text = f"過圓上一點的切線與一弦所夾的弧度數為 {arc}°，請問此弦切角是多少度？"
        correct_answer = str(tangent_chord_angle)

    context_string = "弦切角的度數等於其所夾弧度數的一半。"

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