# skills/jh_proportion_direct_def.py
import random

def generate(level=1):
    """
    生成一道「正比定義」的題目。
    """
    scenarios = [
        ("固定時速下，行駛的時間和距離", True),
        ("購買單價固定的商品，購買的數量和總價", True),
        ("正方形的邊長和周長", True),
        ("圓形的半徑和圓周長", True),
        ("固定面積的長方形，長和寬", False),
        ("固定距離下，移動的速率和時間", False),
        ("一個人的年齡和身高", False),
    ]

    description, is_direct = random.choice(scenarios)
    
    correct_answer = "是" if is_direct else "否"

    question_text = f"請問以下敘述中的兩個數量關係是否成「正比」？\n\n「{description}」\n\n(請回答 '是' 或 '否')"

    context_string = "判斷兩個變數 x 和 y 的關係是否為 y = kx (k為定值)，即 y/x 的比值是否固定。"

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