import random

def generate(level=1):
    """
    生成一道「高斯消去法」的觀念題。
    """
    question_text = (
        "在使用高斯消去法解聯立方程式時，我們的目標是將增廣矩陣化為什麼形式？\n\n"
        "A) 單位矩陣 (Identity Matrix)\n"
        "B) 階梯形矩陣 (Row Echelon Form)\n"
        "C) 零矩陣 (Zero Matrix)"
    )
    correct_answer = "B"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().upper()
    is_correct = (user == correct_answer)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}