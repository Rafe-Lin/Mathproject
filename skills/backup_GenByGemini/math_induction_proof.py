import random

def generate(level=1):
    """
    生成一道「數學歸納法」的觀念題。
    """
    if level == 1:
        question_text = (
            "使用數學歸納法證明一個關於正整數 n 的命題時，第一個步驟是什麼？\n\n"
            "A) 假設 n=k 時命題成立\n"
            "B) 證明 n=1 時命題成立\n"
            "C) 證明對於所有 n 命題都成立"
        )
        correct_answer = "B"
    else: # level 2
        question_text = (
            "在使用數學歸納法證明時，若已假設 n=k 時命題成立，下一步（歸納步驟）的目標是什麼？\n\n"
            "A) 證明 n=1 時命題成立\n"
            "B) 利用 n=k 的假設，證明 n=k+1 時命題也成立\n"
            "C) 證明 n=k-1 時命題成立"
        )
        correct_answer = "B"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().upper()
    is_correct = (user == correct_answer)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}