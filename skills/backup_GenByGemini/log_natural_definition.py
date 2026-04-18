# \函數\自然對數定義
import random

def generate(level=1):
    """
    生成一道「自然對數」的觀念題。
    """
    if level == 1:
        question_text = (
            "自然對數 (ln) 是以哪個數為底的對數？\n\n"
            "A) 10\nB) 2\nC) e (自然常數)"
        )
        correct_answer = "C"
    else: # level 2
        question_text = "請求出 ln(e³) 的值。"
        correct_answer = "3"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().upper()
    correct = str(correct_answer).strip().upper()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}