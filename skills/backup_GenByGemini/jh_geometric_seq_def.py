# skills/jh_geometric_seq_def.py
import random

def generate(level=1):
    """
    生成一道「等比數列定義」的題目。
    """
    is_geometric = random.choice([True, False])
    
    if is_geometric:
        a1 = random.randint(1, 4)
        r = random.randint(2, 3)
        seq = [a1 * (r**i) for i in range(4)]
        correct_answer = "是"
    else:
        # 構造一個非等比數列（例如等差）
        a1 = random.randint(1, 5)
        d = random.randint(1, 5)
        seq = [a1 + i * d for i in range(4)]
        correct_answer = "否"

    seq_str = ", ".join(map(str, seq))
    question_text = f"請問下列數列是不是一個等比數列？\n\n{seq_str}, ...\n\n(請回答 '是' 或 '否')"

    context_string = "判斷一個數列是否為等比數列，檢查任意相鄰兩項的比是否為一個定值（公比）。"

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