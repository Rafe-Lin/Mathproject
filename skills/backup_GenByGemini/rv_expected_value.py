# \機率統計\隨機變數期望值
import random

def generate(level=1):
    """
    生成一道「隨機變數期望值」的題目。
    """
    if level == 1:
        question_text = "擲一顆公正骰子一次，令隨機變數 X 為擲出的點數。請問 X 的期望值 E(X) 是多少？"
        correct_answer = "3.5"
    else: # level 2
        x_vals = [0, 1, 2]
        p_vals = [0.2, 0.5, 0.3]
        question_text = f"已知隨機變數 X 的機率分布如下：\nX | {x_vals[0]} | {x_vals[1]} | {x_vals[2]}\n--|---|---|--\nP(X) | {p_vals[0]} | {p_vals[1]} | {p_vals[2]}\n請問 X 的期望值 E(X) 是多少？"
        ev = sum(x * p for x, p in zip(x_vals, p_vals))
        correct_answer = str(round(ev, 2))
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}