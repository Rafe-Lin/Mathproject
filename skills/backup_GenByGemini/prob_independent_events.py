import random

def generate(level=1):
    """
    生成一道「獨立事件」的觀念題。
    """
    if level == 1:
        question_text = (
            "若 A, B 為兩獨立事件，則下列何者「恆成立」？\n\n"
            "A) P(A∩B) = P(A) + P(B)\n"
            "B) P(A∩B) = P(A) * P(B)\n"
            "C) P(A∪B) = P(A) + P(B)"
        )
        correct_answer = "B"
    else: # level 2
        question_text = "擲一顆公正骰子兩次，事件 A 為「第一次擲出 6 點」，事件 B 為「第二次擲出 1 點」。請問 A 和 B 是否為獨立事件？ (是/否)"
        correct_answer = "是"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().upper()
    is_correct = (user == correct_answer.upper())
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}