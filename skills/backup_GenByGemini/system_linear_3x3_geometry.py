import random

def generate(level=1):
    """
    生成一道「三元一次聯立方程式的幾何意義」的觀念題。
    """
    if level == 1:
        question_text = (
            "三元一次聯立方程式若「恰有一組解」，其解在幾何上代表什麼？\n\n"
            "A) 三個平面交於一條直線\n"
            "B) 三個平面交於一個點\n"
            "C) 三個平面兩兩平行"
        )
        correct_answer = "B"
    else: # level 2
        question_text = "三元一次聯立方程式若「無限多組解」，其解在幾何上「不可能」代表什麼？\n\n" \
                        "A) 三個平面重合\nB) 三個平面交於一條直線\nC) 三個平面兩兩平行"
        correct_answer = "C"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().upper()
    is_correct = (user == correct_answer)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}