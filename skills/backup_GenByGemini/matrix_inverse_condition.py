import random

def generate(level=1):
    """
    生成一道「反方陣存在條件」的觀念題。
    """
    question_text = (
        "一個 n 階方陣 A，其反方陣 A⁻¹ 存在的充要條件是什麼？\n\n"
        "A) A 的所有元素皆不為 0\n"
        "B) A 的行列式值 det(A) 不等於 0\n"
        "C) A 是一個對稱矩陣"
    )
    correct_answer = "B"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().upper()
    is_correct = (user == correct_answer)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}