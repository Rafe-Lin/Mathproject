import random

def generate(level=1):
    """
    生成一道「平面法線」的觀念題。
    """
    if level == 1:
        question_text = (
            "若一條直線 L 垂直於平面 E，則 L 與平面 E 上的「所有」直線的關係為何？\n\n"
            "A) L 與 E 上的所有直線都垂直\n"
            "B) L 與 E 上的所有直線都平行\n"
            "C) L 只與 E 上通過交點的特定直線垂直"
        )
        correct_answer = "A"
    else: # level 2
        question_text = "若要證明直線 L 垂直於平面 E，至少需要證明 L 垂直於平面 E 上的幾條「不平行」的相交直線？\n\n" \
                        "A) 一條\nB) 兩條\nC) 無限多條"
        correct_answer = "B"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().upper()
    is_correct = (user == correct_answer)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}