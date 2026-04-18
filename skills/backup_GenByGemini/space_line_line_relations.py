import random

def generate(level=1):
    """
    生成一道「空間中兩直線關係」的觀念題。
    """
    if level == 1:
        question_text = (
            "在空間中，兩條「不相交」且「不平行」的直線，其關係為何？\n\n"
            "A) 重合\nB) 歪斜\nC) 垂直"
        )
        correct_answer = "B"
    else: # level 2
        question_text = "在空間中，判斷兩直線 L₁ 與 L₂ 的關係時，第一步通常是檢查兩直線的「方向向量」是否平行。若方向向量不平行，則兩直線的關係「不可能」是下列何者？\n\n" \
                        "A) 相交於一點\nB) 歪斜\nC) 平行"
        correct_answer = "C"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().upper()
    is_correct = (user == correct_answer)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}