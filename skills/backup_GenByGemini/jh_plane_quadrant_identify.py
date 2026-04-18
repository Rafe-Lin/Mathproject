# skills/jh_plane_quadrant_identify.py
import random

def generate(level=1):
    """
    生成一道「象限判斷」的題目。
    """
    x = random.randint(-10, 10)
    y = random.randint(-10, 10)
    # 確保不在座標軸上
    while x == 0 or y == 0:
        x = random.randint(-10, 10)
        y = random.randint(-10, 10)

    if x > 0 and y > 0: quadrant = "一"
    elif x < 0 and y > 0: quadrant = "二"
    elif x < 0 and y < 0: quadrant = "三"
    elif x > 0 and y < 0: quadrant = "四"
    
    correct_answer = quadrant

    question_text = f"請問點 P({x}, {y}) 在第幾象限？ (請回答 一, 二, 三, 或 四)"

    context_string = "根據點的 (x, y) 坐標的正負號，判斷其所在的象限位置。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    """
    檢查使用者輸入的答案是否正確。
    """
    user = user_answer.strip().replace("第", "").replace("象限", "")
    correct = str(correct_answer).strip()

    is_correct = user == correct
    result_text = f"完全正確！答案是第 {correct} 象限。" if is_correct else f"答案不正確。正確答案是：第 {correct} 象限"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}