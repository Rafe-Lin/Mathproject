import random
from fractions import Fraction

def generate(level=1):
    """
    生成一道「古典機率」的題目。
    level 1: 擲一顆骰子。
    level 2: 抽球問題。
    """
    if level == 1:
        event = random.choice(["點數為偶數", "點數大於4", "點數為質數"])
        question_text = f"擲一顆公正的骰子一次，出現「{event}」的機率是多少？ (請以最簡分數 a/b 表示)"
        if event == "點數為偶數": correct_answer = "1/2"
        elif event == "點數大於4": correct_answer = "1/3"
        else: correct_answer = "1/2" # 質數 2,3,5
    else: # level 2
        red = random.randint(3, 6)
        white = random.randint(3, 6)
        total = red + white
        question_text = f"袋中有 {red} 顆紅球、{white} 顆白球。隨機抽取一球，抽中紅球的機率是多少？ (請以最簡分數 a/b 表示)"
        frac = Fraction(red, total)
        correct_answer = f"{frac.numerator}/{frac.denominator}"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}