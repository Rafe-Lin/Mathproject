# skills/jh_equation_quad_discriminant.py
import random

def generate(level=1):
    """
    生成一道「一元二次方程式根的判別式」的題目。
    """
    # 隨機決定根的數量
    num_roots_type = random.choice(['two_distinct', 'one_repeated', 'no_real'])
    
    if num_roots_type == 'two_distinct':
        # b^2 - 4ac > 0
        a, c = random.randint(1, 3), random.randint(1, 3)
        b = random.randint(5, 8)
        correct_answer = "兩相異實根"
    elif num_roots_type == 'one_repeated':
        # b^2 - 4ac = 0
        a = 1
        root = random.randint(2, 5)
        b, c = -2 * root, root**2
        correct_answer = "重根"
    else: # 'no_real'
        # b^2 - 4ac < 0
        a, b = random.randint(2, 4), random.randint(1, 3)
        c = random.randint(2, 4)
        correct_answer = "無實數解"

    equation_str = f"{a}x² {'+' if b > 0 else '-'} {abs(b)}x {'+' if c > 0 else '-'} {abs(c)} = 0"

    question_text = f"請問一元二次方程式 {equation_str} 有幾個實數解？\n(請回答：兩相異實根、重根、或 無實數解)"

    context_string = f"利用判別式 D = b² - 4ac 的值來判斷根的性質。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = correct_answer.strip().replace(" ", "")
    
    is_correct = user == correct
    result_text = f"完全正確！答案是「{correct}」。" if is_correct else f"答案不正確。正確答案是：「{correct}」"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}