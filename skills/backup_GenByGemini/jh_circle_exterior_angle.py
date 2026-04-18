# skills/jh_circle_exterior_angle.py
import random

def generate(level=1):
    """
    生成一道「圓外角」的題目。
    """
    # 圓外角 = (大弧 - 小弧) / 2
    # 為了讓數字漂亮，反向構造
    exterior_angle = random.randint(20, 60)
    small_arc = random.randint(10, 80)
    
    # angle = (large - small) / 2  => large = 2*angle + small
    large_arc = 2 * exterior_angle + small_arc
    
    # 確保大弧小於360
    while large_arc >= 360:
        exterior_angle = random.randint(20, 60)
        small_arc = random.randint(10, 80)
        large_arc = 2 * exterior_angle + small_arc

    question_text = f"圓外一點 P 向圓作兩條割線，與圓相交所截出的兩弧度數分別為 {large_arc}° 和 {small_arc}°，請問這兩條割線所夾的圓外角是多少度？"
    correct_answer = str(exterior_angle)

    context_string = "圓外角的度數等於其所夾兩弧度數差的一半。"

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