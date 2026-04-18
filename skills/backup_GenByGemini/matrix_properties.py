import random

def generate(level=1):
    """
    生成一道「矩陣性質」的觀念題。
    """
    if level == 1:
        question_text = (
            "關於矩陣乘法，下列敘述何者「不一定」成立？\n\n"
            "A) (AB)C = A(BC) (結合律)\n"
            "B) AB = BA (交換律)\n"
            "C) A(B+C) = AB + AC (分配律)"
        )
        correct_answer = "B"
    else: # level 2
        question_text = "若 A, B, C 皆為 n 階方陣，且 AB = AC，則是否可以推斷 B = C？\n\n" \
                        "A) 可以\nB) 不可以，除非 A 的反方陣存在\nC) 不可以，沒有任何例外"
        correct_answer = "B"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().upper()
    is_correct = (user == correct_answer)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}