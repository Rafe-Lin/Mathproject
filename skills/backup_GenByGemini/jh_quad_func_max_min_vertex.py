# skills/jh_quad_func_max_min_vertex.py
import random

def generate(level=1):
    """
    生成一道「二次函數的極值與頂點」的題目。
    """
    # 構造 y = a(x-h)^2 + k
    a = random.randint(-3, 3)
    while a == 0: a = random.randint(-3, 3)
    h = random.randint(-5, 5)
    k = random.randint(-10, 10)

    func_str = f"y = {a}(x {'-' if h > 0 else '+'} {abs(h)})² {'+' if k > 0 else '-'} {abs(k)}"
    if a == 1: func_str = func_str.replace("y = 1(", "y = (")
    if a == -1: func_str = func_str.replace("y = -1(", "y = -(")

    if a > 0:
        q_type = "最小值"
        correct_answer = str(k)
    else:
        q_type = "最大值"
        correct_answer = str(k)

    question_text = f"請問二次函數 {func_str} 的{q_type}是多少？"

    context_string = "將二次函數化為頂點式 y=a(x-h)²+k，若 a>0，在 x=h 時有最小值 k；若 a<0，在 x=h 時有最大值 k。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    user = user_answer.strip()
    correct = correct_answer.strip()
    try:
        is_correct = int(user) == int(correct)
        result_text = f"完全正確！答案是 {correct}。" if is_correct else f"答案不正確。正確答案是：{correct}"
    except ValueError:
        is_correct = False
        result_text = f"請輸入數字答案。正確答案是：{correct}"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}