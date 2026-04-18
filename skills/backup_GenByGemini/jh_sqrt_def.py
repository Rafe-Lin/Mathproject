# skills/jh_sqrt_def.py
import random

def generate(level=1):
    """
    生成一道「平方根定義」的題目。
    """
    num = random.randint(2, 15)
    square = num**2

    q_type = random.choice(['ask_sqrt', 'ask_square'])

    if q_type == 'ask_sqrt':
        question_text = f"若 x² = {square}，則 x 是 {square} 的平方根。請問 {square} 的平方根是多少？\n(若有兩解，請用逗號分隔)"
        correct_answer = f"{num},-{num}"
    else: # ask_square
        question_text = f"請問 ({num})² 的值是多少？"
        correct_answer = str(square)

    context_string = "若 x² = a，則 x 稱為 a 的平方根。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    try:
        user_sols = sorted(user_answer.strip().replace(" ", "").split(','))
        correct_sols = sorted(correct_answer.strip().split(','))
        is_correct = user_sols == correct_sols
        result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案是：{correct_answer}"
    except:
        is_correct = False
        result_text = f"答案格式不對喔。正確答案是：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}