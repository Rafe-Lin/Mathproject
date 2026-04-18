import random

def generate(level=1):
    """
    生成一道「迴歸直線」的觀念題。
    """
    if level == 1:
        question_text = (
            "迴歸直線（最適直線）的目的是什麼？\n\n"
            "A) 連接散佈圖中的第一個點和最後一個點\n"
            "B) 穿過散佈圖中盡可能多的點\n"
            "C) 找出最能代表數據趨勢的一條直線，使所有點到此直線的鉛直距離平方和最小"
        )
        correct_answer = "C"
    else: # level 2
        question_text = (
            "迴歸直線 y = ax + b 一定會通過哪個點？\n\n"
            "A) 原點 (0,0)\nB) (x的平均數, y的平均數)\nC) y軸截距 (0,b)"
        )
        correct_answer = "B"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().upper()
    is_correct = (user == correct_answer)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}