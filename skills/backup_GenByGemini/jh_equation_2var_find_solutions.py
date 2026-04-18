# skills/jh_equation_2var_find_solutions.py
import random

def generate(level=1):
    """
    生成一道「找二元一次方程式的解」的題目。
    """
    a = random.randint(1, 3)
    b = random.randint(1, 3)
    
    # 為了讓 y 是整數，反向構造
    x_given = random.randint(-5, 5)
    y_sol = random.randint(-5, 5)
    
    c = a * x_given + b * y_sol
    
    equation_str = f"{a}x + {b}y = {c}"
    question_text = f"在方程式 {equation_str} 中，如果 x = {x_given}，請問 y 是多少？"

    correct_answer = str(y_sol)

    context_string = f"將 x = {x_given} 代入方程式 {equation_str}，解出 y 的值。"

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
    user = user_answer.strip().replace("y=", "")
    correct = str(correct_answer).strip()

    try:
        if int(user) == int(correct):
            is_correct = True
            result_text = f"完全正確！答案是 y = {correct}。"
        else:
            is_correct = False
            result_text = f"答案不正確。正確答案是：y = {correct}"
    except ValueError:
        is_correct = False
        result_text = f"請輸入數字答案。正確答案是：y = {correct}"

    return {"correct": is_correct, "result": result_text, "next_question": is_correct}