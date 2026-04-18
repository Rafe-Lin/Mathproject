import random

def generate(level=1):
    """
    生成一道「笛摩根定律」的觀念題。
    """
    if level == 1:
        question_text = (
            "根據笛摩根定律，(A ∩ B)' 等於什麼？\n\n"
            "A) A' ∩ B'\n"
            "B) A' ∪ B'\n"
            "C) A ∪ B"
        )
        correct_answer = "B"
    else: # level 2
        question_text = (
            "根據笛摩根定律，(A ∪ B)' 等於什麼？\n\n"
            "A) A' ∩ B'\n"
            "B) A' ∪ B'\n"
            "C) A ∩ B"
        )
        correct_answer = "A"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().upper()
    is_correct = (user == correct_answer)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}