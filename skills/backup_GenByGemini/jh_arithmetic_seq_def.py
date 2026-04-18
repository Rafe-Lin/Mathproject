# skills/jh_arithmetic_seq_def.py
import random

def generate(level=1):
    """
    生成一道「等差數列定義」的題目。
    """
    is_arithmetic = random.choice([True, False])
    
    if is_arithmetic:
        a1 = random.randint(-5, 5)
        d = random.randint(-4, 4)
        while d == 0: d = random.randint(-4, 4)
        seq = [a1 + i * d for i in range(5)]
        correct_answer = "是"
    else:
        # 構造一個非等差數列（例如等比或亂數）
        a1 = random.randint(1, 3)
        r = random.randint(2, 3)
        seq = [a1 * (r**i) for i in range(5)]
        correct_answer = "否"

    seq_str = ", ".join(map(str, seq))
    question_text = f"請問下列數列是不是一個等差數列？\n\n{seq_str}, ...\n\n(請回答 '是' 或 '否')"

    context_string = "判斷一個數列是否為等差數列，檢查任意相鄰兩項的差是否為一個定值（公差）。"

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
    if user in ["是", "Y", "y"] and correct == "是": is_correct = True
    elif user in ["否", "N", "n"] and correct == "否": is_correct = True
    else: is_correct = False
    result_text = f"完全正確！答案是 {correct}。" if is_correct else f"答案不正確。正確答案是：{correct}"
    return {"correct": is_correct, "result": result_text, "next_question": True}