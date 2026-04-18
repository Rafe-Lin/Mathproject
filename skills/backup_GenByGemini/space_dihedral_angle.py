import random

def generate(level=1):
    """
    生成一道「兩面角」的觀念題。
    """
    if level == 1:
        question_text = (
            "在一個正立方體中，相鄰兩個面所形成的兩面角是多少度？\n\n"
            "A) 45°\nB) 60°\nC) 90°"
        )
        correct_answer = "C"
    else: # level 2
        question_text = "在一個正四面體中，任意兩個面所形成的兩面角，其 cos 值是多少？\n\n" \
                        "A) 1/2\nB) 1/3\nC) √3/2"
        correct_answer = "B"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().upper()
    is_correct = (user == correct_answer)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}