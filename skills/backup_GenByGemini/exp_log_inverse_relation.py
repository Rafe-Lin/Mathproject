import random

def generate(level=1):
    """
    生成一道「指數與對數的反函數關係」的觀念題。
    """
    a = random.randint(2, 10)
    question_text = (
        f"函數 y = {a}ˣ 與 y = log_{a}(x) 的圖形對稱於哪一條直線？\n\n"
        "A) x 軸\n"
        "B) y 軸\n"
        "C) 直線 y = x"
    )
    correct_answer = "C"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().upper()
    is_correct = (user == correct_answer)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}