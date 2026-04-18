import random

def generate(level=1):
    """
    生成一道「向量三角不等式」的觀念題。
    """
    if level == 1:
        question_text = (
            "關於向量的三角不等式，下列何者「恆正確」？\n\n"
            "A) |a + b| ≤ |a| + |b|\n"
            "B) |a + b| = |a| + |b|\n"
            "C) |a + b| ≥ |a| + |b|"
        )
        correct_answer = "A"
    else: # level 2
        question_text = "在什麼情況下，向量三角不等式 |a + b| ≤ |a| + |b| 的等號會成立？\n\n" \
                        "A) 當 a, b 互相垂直時\nB) 當 a, b 為零向量或同向時\nC) 恆不成立"
        correct_answer = "B"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().upper()
    is_correct = (user == correct_answer)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}