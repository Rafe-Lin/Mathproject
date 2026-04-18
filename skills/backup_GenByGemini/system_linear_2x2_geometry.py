import random

def generate(level=1):
    """
    生成一道「二元一次聯立方程式的幾何意義」的觀念題。
    """
    if level == 1:
        question_text = (
            "二元一次聯立方程式若「恰有一組解」，其解在幾何上代表什麼？\n\n"
            "A) 兩條平行線\n"
            "B) 兩條重合的直線\n"
            "C) 兩條相交於一點的直線"
        )
        correct_answer = "C"
    else: # level 2
        question_text = "二元一次聯立方程式若「無解」，其解在幾何上代表什麼？\n\n" \
                        "A) 兩條平行線\nB) 兩條重合的直線\nC) 兩條相交於一點的直線"
        correct_answer = "A"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().upper()
    is_correct = (user == correct_answer)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}