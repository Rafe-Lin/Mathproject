import random

def generate(level=1):
    """
    生成一道「線性規劃(二元一次不等式組的圖形)」的題目。
    此為觀念題，要求學生辨識可行解區域。
    """
    x_b = random.randint(1, 5)
    y_b = random.randint(1, 5)
    c = random.randint(8, 15)

    question_text = (
        f"聯立不等式組：\n"
        f"x ≥ 0\n"
        f"y ≥ 0\n"
        f"x + y ≤ {c}\n"
        f"其圖形在直角坐標平面上是什麼形狀？\n\n"
        "A) 一個矩形\n"
        "B) 一個三角形\n"
        "C) 一條線段\n"
        "D) 無界區域"
    )
    correct_answer = "B"

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().upper()
    is_correct = (user == correct_answer)
    result_text = f"完全正確！答案是 {correct_answer}。此區域由 x=0, y=0 和 x+y={c} 三條線圍成一個三角形區域。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}