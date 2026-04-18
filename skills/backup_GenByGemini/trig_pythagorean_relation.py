import random

def generate(level=1):
    """
    生成一道「平方關係」的觀念題。
    """
    question_text = (
        "關於三角函數的平方關係，下列何者「正確」？\n\n"
        "A) sin²(θ) - cos²(θ) = 1\n"
        "B) sin(θ) + cos(θ) = 1\n"
        "C) sin²(θ) + cos²(θ) = 1"
    )
    correct_answer = "C"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().upper()
    is_correct = (user == correct_answer)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}