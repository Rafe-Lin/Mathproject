# skills/jh_algebra_2var_substitute_check.py
import random

def generate(level=1):
    """
    生成一道「二元一次式求值」的題目。
    """
    a = random.randint(2, 5)
    b = random.randint(2, 5)
    x_val = random.randint(-5, 5)
    y_val = random.randint(-5, 5)

    expr_str = f"{a}x + {b}y"
    
    question_text = f"當 x = {x_val}，y = {y_val} 時，請計算代數式 {expr_str} 的值。"

    # 計算答案
    correct_answer = str(a * x_val + b * y_val)

    context_string = f"將 x = {x_val}, y = {y_val} 代入 {expr_str} 求值"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string
    }

def check(user_answer, correct_answer):
    """
    檢查使用者輸入的答案是否正確。
    """
    user = user_answer.strip()
    correct = str(correct_answer).strip()

    try:
        if int(user) == int(correct):
            is_correct = True
            result_text = f"完全正確！答案是 {correct}。"
        else:
            is_correct = False
            result_text = f"答案不正確。正確答案是：{correct}"
    except ValueError:
        is_correct = False
        result_text = f"請輸入數字答案。正確答案是：{correct}"

    return {
        "correct": is_correct, 
        "result": result_text, 
        "next_question": is_correct
    }