# skills/jh_divisibility_rules.py
import random

def generate(level=1):
    """
    生成一道「倍數判別法」的題目。
    """
    rules = {
        2: "個位數是 0, 2, 4, 6, 8",
        3: "各位數字和是 3 的倍數",
        4: "末兩位數是 4 的倍數",
        5: "個位數是 0 或 5",
        9: "各位數字和是 9 的倍數",
        10: "個位數是 0",
        11: "(奇數位數字和) - (偶數位數字和) 是 11 的倍數或 0"
    }
    
    divisor = random.choice(list(rules.keys()))
    is_divisible = random.choice([True, False])
    
    if is_divisible:
        if divisor == 2: num = random.randint(1, 50) * 2
        elif divisor == 3: num = random.randint(1, 33) * 3
        elif divisor == 4: num = random.randint(1, 25) * 4
        elif divisor == 5: num = random.randint(1, 20) * 5
        elif divisor == 9: num = random.randint(1, 11) * 9
        elif divisor == 10: num = random.randint(1, 10) * 10
        elif divisor == 11: num = random.randint(1, 9) * 11
        correct_answer = "是"
    else:
        num = random.randint(10, 200)
        while num % divisor == 0:
            num = random.randint(10, 200)
        correct_answer = "否"

    question_text = f"請問數字 {num} 是否為 {divisor} 的倍數？\n提示：{rules[divisor]}\n(請回答 '是' 或 '否')"

    context_string = f"判斷 {num} 是否為 {divisor} 的倍數"

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

    if user in ["是", "Yes", "Y"] and correct == "是": is_correct = True
    elif user in ["否", "No", "N"] and correct == "否": is_correct = True
    else: is_correct = False

    result_text = f"完全正確！答案是 {correct}。" if is_correct else f"答案不正確。正確答案是：{correct}"
    return {"correct": is_correct, "result": result_text, "next_question": True}