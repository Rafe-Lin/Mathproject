# skills/jh_geo_triangle_side_relation.py
import random

def generate(level=1):
    """
    生成一道「三角形邊的關係」的題目。
    """
    can_form = random.choice([True, False])
    
    if can_form:
        a = random.randint(3, 10)
        b = random.randint(a, 12)
        # 確保 c 滿足兩邊之和>第三邊，兩邊之差<第三邊
        c = random.randint(b - a + 1, a + b - 1)
        correct_answer = "是"
    else:
        a = random.randint(3, 7)
        b = random.randint(a + 1, 8)
        # 構造一個不滿足條件的 c
        c = a + b + random.randint(0, 3)
        correct_answer = "否"

    sides = sorted([a, b, c])
    question_text = f"請問長度為 {sides[0]}, {sides[1]}, {sides[2]} 的三條線段，是否可以組成一個三角形？ (請回答 '是' 或 '否')"

    context_string = "利用三角形的邊長關係判斷：任意兩邊之和必須大於第三邊。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    user = user_answer.strip()
    correct = str(correct_answer).strip()
    if user in ["是", "Y", "y"] and correct == "是": is_correct = True
    elif user in ["否", "N", "n"] and correct == "否": is_correct = True
    else: is_correct = False
    result_text = f"完全正確！答案是 {correct}。" if is_correct else f"答案不正確。正確答案是：{correct}"
    return {"correct": is_correct, "result": result_text, "next_question": True}