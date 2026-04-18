# skills/jh_algebra_2var_def.py
import random

def generate(level=1):
    """
    生成一道「二元一次式定義」的題目。
    """
    item1 = random.choice(["鉛筆", "蘋果", "書"])
    item2 = random.choice(["橡皮擦", "橘子", "筆記本"])
    while item1 == item2:
        item2 = random.choice(["橡-皮擦", "橘子", "筆記本"])
        
    price1 = "x"
    price2 = "y"
    
    qty1 = random.randint(2, 7)
    qty2 = random.randint(2, 7)

    question_text = f"假設一個{item1} {price1} 元，一個{item2} {price2} 元。\n請問買 {qty1} 個{item1}和 {qty2} 個{item2}，總共需要多少元？\n(請寫出代數式)"
    
    correct_answer = f"{qty1}x+{qty2}y"

    context_string = "學習使用兩個未知數（x 和 y）來表示生活情境中的數量關係。"

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
    user = user_answer.strip().replace(" ", "").replace("*", "")
    correct = str(correct_answer).strip().replace(" ", "").replace("*", "")
    
    # 允許 3x+2y 和 2y+3x 兩種寫法
    parts_user = sorted(user.split('+'))
    parts_correct = sorted(correct.split('+'))

    if parts_user == parts_correct:
        is_correct = True
        result_text = f"完全正確！答案是 {correct_answer}。"
    else:
        is_correct = False
        result_text = f"答案不正確。參考答案是：{correct_answer}"

    return {"correct": is_correct, "result": result_text, "next_question": True}