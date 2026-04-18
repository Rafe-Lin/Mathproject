import random

def generate(level=1):
    """
    生成一道「向量外積性質」的觀念題。
    """
    if level == 1:
        question_text = (
            "關於向量外積 a × b，下列敘述何者「正確」？\n\n"
            "A) a × b = b × a (交換律成立)\n"
            "B) a × b 的結果是一個純量\n"
            "C) a × b 的結果是一個同時垂直於 a 和 b 的向量"
        )
        correct_answer = "C"
    else: # level 2
        question_text = "向量 a 和 b 所張成的平行四邊形面積，其值等於下列何者？\n\n" \
                        "A) |a · b|\nB) |a × b|\nC) |a| + |b|"
        correct_answer = "B"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().upper()
    is_correct = (user == correct_answer)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}