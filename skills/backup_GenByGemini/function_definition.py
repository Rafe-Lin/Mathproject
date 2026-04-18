import random

def generate(level=1):
    """
    生成一道「函數定義」的題目。
    level 1: 判斷關係是否為函數 (一對一或多對一)。
    level 2: 判斷圖形是否為函數 (垂直線檢驗法)。
    """
    if level == 1:
        is_func = random.choice([True, False])
        x_vals = random.sample(range(1, 10), 4)
        if is_func:
            y_vals = random.sample(range(1, 10), 4)
            relation = list(zip(x_vals, y_vals))
            correct_answer = "是"
        else: # 一對多
            y_vals = random.sample(range(1, 10), 3)
            relation = [(x_vals[0], y_vals[0]), (x_vals[1], y_vals[1]), (x_vals[0], y_vals[2])]
            correct_answer = "否"
        
        relation_str = ", ".join([f"({x},{y})" for x,y in relation])
        question_text = f"給定一個關係 R = {{{relation_str}}}，請問 y 是否為 x 的函數？ (是/否)"
    else: # level 2
        q_type = random.choice(['func', 'not_func'])
        if q_type == 'func':
            question_text = "下列哪個圖形「是」一個函數圖形？\nA) 拋物線 y = x²\nB) 圓 x² + y² = 1"
            correct_answer = "A"
        else:
            question_text = "下列哪個圖形「不是」一個函數圖形？\nA) 直線 y = x\nB) 左右開口的拋物線 x = y²"
            correct_answer = "B"

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().upper()
    is_correct = (user == correct_answer)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}