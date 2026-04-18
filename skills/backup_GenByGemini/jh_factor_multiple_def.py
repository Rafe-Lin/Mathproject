# skills/jh_factor_multiple_def.py
import random

def generate(level=1):
    """
    生成一道「因數與倍數的定義」的題目。
    """
    a = random.randint(2, 10)
    b = random.randint(2, 10)
    c = a * b

    # 隨機問因數或倍數
    if random.choice([True, False]):
        # 問因數
        q_num = random.choice([a, b])
        question_text = f"請問 {q_num} 是不是 {c} 的因數？ (請回答 '是' 或 '否')"
        correct_answer = "是"
    else:
        # 問倍數
        q_num = random.choice([a, b])
        question_text = f"請問 {c} 是不是 {q_num} 的倍數？ (請回答 '是' 或 '否')"
        correct_answer = "是"

    context_string = f"因為 {c} = {a} * {b}，所以 {a} 和 {b} 都是 {c} 的因數，{c} 是 {a} 和 {b} 的倍數。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    """
    檢查使用者輸入的答案是否正確。
    """
    user = user_answer.strip()
    correct = str(correct_answer).strip()

    # 接受多種肯定與否定回答
    if user in ["是", "Yes", "Y", "y"] and correct == "是":
        is_correct = True
    elif user in ["否", "No", "N", "n"] and correct == "否":
        is_correct = True
    else:
        is_correct = False

    result_text = f"完全正確！答案是 {correct}。" if is_correct else f"答案不正確。正確答案是：{correct}"
    return {"correct": is_correct, "result": result_text, "next_question": True}