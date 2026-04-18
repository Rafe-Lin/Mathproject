import random

def generate(level=1):
    """
    生成一道「線性變換」的定義題。
    """
    if level == 1:
        question_text = (
            "平面上一個點 P(x, y) 經過一個 2x2 矩陣 A 的線性變換後，得到新的點 P'(x', y')。其關係可以表示為：\n\n"
            "A) [x', y'] = A * [x, y] (向量形式)\n"
            "B) x' = x + a, y' = y + b\n"
            "C) x' = x², y' = y²"
        )
        correct_answer = "A"
    else: # level 2
        question_text = "下列何者「不是」線性變換的特性？\n\n" \
                        "A) T(u+v) = T(u) + T(v)\nB) T(cu) = cT(u)\nC) T(u) 的長度等於 u 的長度"
        correct_answer = "C"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().upper()
    is_correct = (user == correct_answer)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}