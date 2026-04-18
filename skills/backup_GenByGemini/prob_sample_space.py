import random

def generate(level=1):
    """
    生成一道「樣本空間」的題目。
    level 1: 擲一顆骰子。
    level 2: 擲兩顆骰子。
    """
    if level == 1:
        question_text = "擲一顆公正的骰子一次，其所有可能的結果（樣本空間）為何？\n(請用逗號分隔)"
        correct_answer = "1,2,3,4,5,6"
    else: # level 2
        question_text = "同時擲兩顆公正的骰子一次，其樣本空間共有幾個元素？"
        correct_answer = "36"

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user_parts = sorted(user_answer.strip().replace(" ", "").split(','))
    correct_parts = sorted(correct_answer.strip().split(','))
    is_correct = (user_parts == correct_parts)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}