# \圓錐曲線\拋物線標準式 (頂點(0,0))
import random

def generate(level=1):
    """
    生成一道「拋物線標準式 (頂點(0,0))」的題目。
    """
    c = random.randint(1, 5)
    if level == 1:
        form = random.choice(['y^2=4cx', 'x^2=4cy'])
        if form == 'y^2=4cx':
            question_text = f"已知拋物線方程式為 y² = {4*c}x，請問其焦點坐標為何？"
            correct_answer = f"({c},0)"
        else:
            question_text = f"已知拋物線方程式為 x² = {4*c}y，請問其焦點坐標為何？"
            correct_answer = f"(0,{c})"
    else: # level 2
        question_text = f"已知拋物線的焦點為 ({c}, 0)，準線為 x = {-c}，請問其方程式為何？"
        correct_answer = f"y²={4*c}x"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").replace("^2","²")
    correct = str(correct_answer).strip().replace(" ", "")
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}