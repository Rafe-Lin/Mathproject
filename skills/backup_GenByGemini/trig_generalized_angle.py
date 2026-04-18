import random

def generate(level=1):
    """
    生成一道「廣義角與同界角」的題目。
    """
    angle = random.randint(400, 800)
    if level == 1:
        question_text = f"請問 {angle}° 是第幾象限角？"
        min_equiv_angle = angle % 360
        if 0 < min_equiv_angle < 90: quadrant = "一"
        elif 90 < min_equiv_angle < 180: quadrant = "二"
        elif 180 < min_equiv_angle < 270: quadrant = "三"
        else: quadrant = "四"
        correct_answer = quadrant
    else: # level 2
        question_text = f"請問 {angle}° 的最小正同界角是多少度？"
        correct_answer = str(angle % 360)
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}