# \機率統計\伯努力試驗
import random

def generate(level=1):
    """
    生成一道「伯努力試驗」的觀念題。
    """
    question_text = (
        "下列哪個選項「不是」伯努力試驗的必要條件？\n\n"
        "A) 每次試驗的結果只有兩種（成功或失敗）\n"
        "B) 每次試驗成功的機率都相同\n"
        "C) 試驗必須重複無限多次"
    )
    correct_answer = "C"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().upper()
    is_correct = (user == correct_answer)
    result_text = f"完全正確！答案是 {correct_answer}。伯努力試驗是重複固定的 n 次，而非無限次。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}