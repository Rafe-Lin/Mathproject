# \三角函數\三角函數圖形性質
import random

def generate(level=1):
    """
    生成一道「三角函數圖形性質」的觀念題。
    """
    if level == 1:
        question_text = (
            "函數 y = sin(x) 的週期是多少？\n\n"
            "A) π/2\nB) π\nC) 2π"
        )
        correct_answer = "C"
    else: # level 2
        question_text = (
            "函數 y = 3cos(2x) + 1 的振幅是多少？\n\n"
            "A) 1\nB) 2\nC) 3"
        )
        correct_answer = "C"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().upper()
    is_correct = (user == correct_answer)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}