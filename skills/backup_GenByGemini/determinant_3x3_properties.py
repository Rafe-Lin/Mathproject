import random

def generate(level=1):
    """
    生成一道「三階行列式性質」的觀念題。
    """
    if level == 1:
        question_text = (
            "關於三階行列式，若將其中兩行（或兩列）互換，則其值會如何變化？\n\n"
            "A) 值不變\nB) 值變為相反數\nC) 值變為 0"
        )
        correct_answer = "B"
    else: # level 2
        question_text = "關於三階行列式，若其中一行（或一列）是另一行（或一列）的 k 倍，則此行列式的值為何？\n\n" \
                        "A) k\nB) 1\nC) 0"
        correct_answer = "C"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().upper()
    is_correct = (user == correct_answer)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}