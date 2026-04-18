# skills/jh_quad_func_discriminant_intercepts.py
import random

def generate(level=1):
    """
    生成一道「利用判別式判斷二次函數與x軸交點個數」的題目。
    """
    # 隨機決定交點數量
    num_intercepts_type = random.choice(['two', 'one', 'zero'])
    
    if num_intercepts_type == 'two':
        # b^2 - 4ac > 0
        a, c = random.randint(1, 3), random.randint(-3, -1)
        b = random.randint(-4, 4)
        correct_answer = "2"
    elif num_intercepts_type == 'one':
        # b^2 - 4ac = 0
        a = 1
        root = random.randint(2, 5)
        b, c = -2 * root, root**2
        correct_answer = "1"
    else: # 'zero'
        # b^2 - 4ac < 0
        a, b = random.randint(2, 4), random.randint(1, 3)
        c = random.randint(2, 4)
        correct_answer = "0"

    equation_str = f"y = {a}x² {'+' if b > 0 else '-'} {abs(b)}x {'+' if c > 0 else '-'} {abs(c)}"

    question_text = f"請問二次函數 {equation_str} 的圖形與 x 軸有幾個交點？"

    context_string = f"利用判別式 D = b² - 4ac 的值來判斷。D>0 有兩交點；D=0 有一交點；D<0 無交點。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    user = user_answer.strip()
    correct = correct_answer.strip()
    is_correct = user == correct
    result_text = f"完全正確！答案是 {correct} 個交點。" if is_correct else f"答案不正確。正確答案是：{correct} 個交點"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}