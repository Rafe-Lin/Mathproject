import random

def generate(level=1):
    """
    生成一道「特殊角三角函數值」的題目。
    """
    angle = random.choice([30, 45, 60])
    if level == 1:
        func = random.choice(['sin', 'cos'])
    else: # level 2
        func = 'tan'
        
    question_text = f"請求出 {func}({angle}°) 的值。\n(若答案有根號，請用 √ 表示，例如 1/√2)"
    
    if angle == 30:
        if func == 'sin': correct_answer = "1/2"
        elif func == 'cos': correct_answer = "√3/2"
        else: correct_answer = "1/√3"
    elif angle == 45:
        if func == 'sin': correct_answer = "1/√2"
        elif func == 'cos': correct_answer = "1/√2"
        else: correct_answer = "1"
    else: # 60
        if func == 'sin': correct_answer = "√3/2"
        elif func == 'cos': correct_answer = "1/2"
        else: correct_answer = "√3"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").replace("sqrt", "√")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}