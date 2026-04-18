import random

def generate(level=1):
    """
    生成一道「向量內積性質」的觀念題。
    """
    if level == 1:
        question_text = (
            "關於向量內積，下列敘述何者「正確」？\n\n"
            "A) a · b = b · a (交換律成立)\n"
            "B) (a · b) · c = a · (b · c) (結合律成立)\n"
            "C) a · a = 0"
        )
        correct_answer = "A"
    else: # level 2
        question_text = "若非零向量 a 與 b 互相垂直，則其內積 a · b 的值為何？\n\n" \
                        "A) 1\nB) -1\nC) 0"
        correct_answer = "C"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().upper()
    is_correct = (user == correct_answer)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}