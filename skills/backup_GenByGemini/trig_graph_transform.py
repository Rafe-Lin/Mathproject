# \三角函數\三角函數圖形平移與伸縮
import random

def generate(level=1):
    """
    生成一道「三角函數圖形平移與伸縮」的觀念題。
    """
    if level == 1:
        question_text = (
            "函數 y = sin(x) + 2 的圖形，是由 y = sin(x) 的圖形如何平移得到？\n\n"
            "A) 向上平移 2 單位\nB) 向下平移 2 單位\nC) 向右平移 2 單位"
        )
        correct_answer = "A"
    else: # level 2
        question_text = (
            "函數 y = cos(x - π/2) 的圖形，是由 y = cos(x) 的圖形如何平移得到？\n\n"
            "A) 向左平移 π/2 單位\nB) 向右平移 π/2 單位\nC) 向上平移 π/2 單位"
        )
        correct_answer = "B"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().upper()
    is_correct = (user == correct_answer)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}