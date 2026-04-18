# skills/jh_exponent_def_integer.py
import random

def generate(level=1):
    """
    生成一道「整數指數定義」的題目。
    """
    base = random.randint(2, 10)
    exponent = random.randint(2, 4)
    
    # 隨機選擇正負底數
    if random.choice([True, False]):
        base = -base

    if base < 0:
        question_text = f"請問 ({base})^{exponent} 的值是多少？"
    else:
        question_text = f"請問 {base}^{exponent} 的值是多少？"
        
    correct_answer = str(base ** exponent)

    context_string = f"計算 {base} 的 {exponent} 次方。"

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

    if user == correct:
        is_correct = True
        result_text = f"完全正確！答案是 {correct}。"
    else:
        is_correct = False
        result_text = f"答案不正確。正確答案是：{correct}"

    return {"correct": is_correct, "result": result_text, "next_question": True}