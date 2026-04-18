# skills/jh_function_def_check.py
import random

def generate(level=1):
    """
    生成一道「函數定義判斷」的題目。
    """
    is_function = random.choice([True, False])
    
    x_values = random.sample(range(1, 6), 4)
    y_values = random.sample(range(1, 10), 4)
    
    if is_function:
        # 一個 x 對應一個 y
        pairs = list(zip(x_values, y_values))
        correct_answer = "是"
    else:
        # 構造一個 x 對應多個 y
        pairs = list(zip(x_values, y_values))
        # 替換其中一個 x，使其重複
        idx_to_replace = random.randint(1, 3)
        pairs[idx_to_replace] = (pairs[0][0], y_values[idx_to_replace] + 1) # 確保 y 不同
        correct_answer = "否"

    random.shuffle(pairs)
    pairs_str = ", ".join([str(p) for p in pairs])

    question_text = f"給定一組對應關係（x, y）：{{{pairs_str}}}。\n請問這個對應關係中，y 是不是 x 的函數？ (請回答 '是' 或 '否')"

    context_string = "判斷是否為函數，要檢查每一個 x 值是否都只對應到「唯一」一個 y 值。如果有一個 x 對應到兩個或多個不同的 y，就不是函數。"

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