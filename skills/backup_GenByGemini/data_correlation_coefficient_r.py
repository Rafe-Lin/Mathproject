import random

def generate(level=1):
    """
    生成一道「相關係數」的觀念題。
    """
    if level == 1:
        question_text = (
            "若兩組數據的相關係數 r = 0.9，這代表什麼？\n\n"
            "A) 兩者為高度正相關\nB) 兩者為高度負相關\nC) 兩者無關"
        )
        correct_answer = "A"
    else: # level 2
        question_text = (
            "若兩組數據的相關係數 r = -0.1，這代表什麼？\n\n"
            "A) 兩者為高度負相關\nB) 兩者為低度負相關\nC) 兩者為低度正相關"
        )
        correct_answer = "B"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().upper()
    is_correct = (user == correct_answer)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}