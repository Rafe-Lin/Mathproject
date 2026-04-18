import random

def generate(level=1):
    """
    生成一道「商數關係」的觀念題。
    """
    question_text = (
        "關於三角函數的商數關係，下列何者「正確」？\n\n"
        "A) tan(θ) = sin(θ) / cos(θ)\n"
        "B) tan(θ) = cos(θ) / sin(θ)\n"
        "C) sin(θ) = tan(θ) / cos(θ)"
    )
    correct_answer = "A"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().upper()
    is_correct = (user == correct_answer)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}