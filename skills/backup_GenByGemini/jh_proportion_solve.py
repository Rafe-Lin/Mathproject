# skills/jh_proportion_solve.py
import random

def generate(level=1):
    """
    生成一道「比例式求解」的題目。
    """
    # 構造 a : b = c : x
    a = random.randint(2, 9)
    b = random.randint(2, 9)
    
    multiplier = random.randint(2, 5)
    c = a * multiplier
    x = b * multiplier
    
    # 隨機將 x 放在四個位置之一
    positions = [f"{a}:{b}={c}:x", f"{a}:{b}=x:{x*b/a}", f"{a}:x={c}:{x*c/a}", f"x:{b}={c}:{x*c/b}"]
    # 為了簡化，我們先只用第一種
    
    question_text = f"請求解比例式中的 x：\n\n{a} : {b} = {c} : x"
    correct_answer = str(x)

    context_string = "利用「內項乘積等於外項乘積」來解比例式。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    user = user_answer.strip().replace("x=", "")
    correct = correct_answer.strip()
    try:
        if float(user) == float(correct):
            is_correct = True
            result_text = f"完全正確！答案是 x = {correct}。"
        else:
            is_correct = False
            result_text = f"答案不正確。正確答案是：x = {correct}"
    except ValueError:
        is_correct = False
        result_text = f"請輸入數字答案。正確答案是：x = {correct}"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}