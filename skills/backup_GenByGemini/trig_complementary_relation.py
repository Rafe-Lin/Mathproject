import random

def generate(level=1):
    """
    生成一道「餘角關係」的題目。
    """
    angle = random.randint(10, 40)
    if level == 1:
        question_text = (
            f"sin({angle}°) 和下列哪個選項相等？\n\n"
            f"A) sin({90-angle}°)\nB) cos({angle}°)\nC) cos({90-angle}°)"
        )
        correct_answer = "C"
    else: # level 2
        question_text = (
            f"tan({angle}°) * tan({90-angle}°) 的值是多少？"
        )
        correct_answer = "1"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().upper()
    is_correct = (user == correct_answer)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}