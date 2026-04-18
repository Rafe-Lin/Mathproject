# skills/jh_geo_parallel_lines_proportional_segments.py
import random

def generate(level=1):
    """
    生成一道「平行線截比例線段」的題目。
    """
    # 構造 a:b = c:x 的形式
    a = random.randint(2, 8)
    b = random.randint(2, 8)
    
    multiplier = random.randint(2, 4)
    c = a * multiplier
    d = b * multiplier

    # 隨機決定未知數的位置
    unknown = random.choice(['d']) # 簡化問題，只求 d
    
    question_text = (
        f"三條平行線 L1, L2, L3 被兩條截線所截。\n"
        f"若在第一條截線上截出的線段長分別為 {a} 和 {b}。\n"
        f"在第二條截線上對應截出的線段長分別為 {c} 和 x。\n"
        f"請問 x 的長度是多少？"
    )
    correct_answer = str(d)

    context_string = "利用平行線截比例線段性質：對應線段會成比例。"

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