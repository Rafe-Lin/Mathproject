import random

def generate(level=1):
    """
    生成一道「互斥事件」的觀念題。
    """
    if level == 1:
        question_text = (
            "擲一顆骰子，事件 A 為「點數為奇數」，事件 B 為「點數為偶數」。請問 A 和 B 是否為互斥事件？ (是/否)"
        )
        correct_answer = "是"
    else: # level 2
        question_text = (
            "抽一張撲克牌，事件 A 為「抽到紅心」，事件 B 為「抽到 K」。請問 A 和 B 是否為互斥事件？ (是/否)"
        )
        correct_answer = "否" # 可能抽到紅心K
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip()
    is_correct = (user == correct_answer)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}