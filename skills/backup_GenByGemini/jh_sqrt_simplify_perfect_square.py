# skills/jh_sqrt_simplify_perfect_square.py
import random

def generate(level=1):
    """
    生成一道「化簡平方根」的題目。
    """
    # 構造 √(a^2 * b)
    a = random.randint(2, 7)
    b = random.choice([2, 3, 5, 6, 7]) # 質數或無平方因數的數
    
    radicand = (a**2) * b

    question_text = f"請將 √{radicand} 化為最簡根式。"
    
    # 答案是 a√b
    correct_answer = f"{a}sqrt({b})"

    context_string = "將根號內的數質因數分解，把成對的因數提出根號外。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    """
    檢查使用者輸入的答案是否正確。
    接受 "a sqrt(b)" 或 "a根號b"
    """
    user = user_answer.strip().replace(" ", "").replace("根號", "sqrt")
    correct = correct_answer.strip().replace(" ", "")
    
    is_correct = user == correct
    result_text = f"完全正確！答案是 {correct_answer.replace('sqrt(', '√').replace(')', '')}。" if is_correct else f"答案不正確。參考答案是：{correct_answer.replace('sqrt(', '√').replace(')', '')}"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}