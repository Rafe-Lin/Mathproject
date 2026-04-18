import random

def generate(level=1):
    """
    生成一道「相關係數性質」的觀念題。
    """
    if level == 1:
        question_text = (
            "關於相關係數 r，下列敘述何者「正確」？\n\n"
            "A) r 的範圍是 [0, 1]\nB) r 的範圍是 [-1, 1]\nC) r 可以大於 1"
        )
        correct_answer = "B"
    else: # level 2
        question_text = (
            "若將一組數據 (X, Y) 的每個 X 值都乘以 2，Y 值不變，新的相關係數 r' 會如何變化？\n\n"
            "A) r' = 2r\nB) r' = r/2\nC) r' = r (不變)"
        )
        correct_answer = "C"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().upper()
    is_correct = (user == correct_answer)
    result_text = f"完全正確！答案是 {correct_answer}。相關係數不受數據的線性變換影響。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}