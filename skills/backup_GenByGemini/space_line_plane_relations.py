import random

def generate(level=1):
    """
    生成一道「空間中直線與平面關係」的觀念題。
    """
    if level == 1:
        question_text = (
            "在空間中，一條直線 L 與一個平面 E，若它們沒有任何交點，則它們的關係為何？\n\n"
            "A) 直線 L 平行於平面 E\n"
            "B) 直線 L 落在平面 E 上\n"
            "C) 直線 L 垂直於平面 E"
        )
        correct_answer = "A"
    else: # level 2
        question_text = "在空間中，若一條直線 L 與一個平面 E 恰有一個交點，則下列敘述何者「不可能」？\n\n" \
                        "A) 直線 L 垂直於平面 E\n" \
                        "B) 直線 L 與平面 E 斜交\n" \
                        "C) 直線 L 平行於平面 E"
        correct_answer = "C"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().upper()
    is_correct = (user == correct_answer)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}