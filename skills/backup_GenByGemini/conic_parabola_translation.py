# \圓錐曲線\拋物線平移
import random

def generate(level=1):
    """
    生成一道「拋物線平移」的題目。
    """
    c = random.randint(1, 5)
    h = random.randint(-5, 5)
    k = random.randint(-5, 5)
    
    if level == 1:
        question_text = f"拋物線 (y-{k})² = {4*c}(x-{h}) 的頂點坐標為何？"
        correct_answer = f"({h},{k})"
    else: # level 2
        question_text = f"一個頂點在 ({h},{k})、焦點在 ({h+c},{k}) 的拋物線，其方程式為何？"
        correct_answer = f"(y-{k})²={4*c}(x-{h})"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").replace("^2","²")
    correct = str(correct_answer).strip().replace(" ", "")
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}