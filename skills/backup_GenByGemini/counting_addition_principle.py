import random

def generate(level=1):
    """
    生成一道「計數加法原理」的應用題。
    """
    if level == 1:
        a = random.randint(3, 6)
        b = random.randint(3, 6)
        question_text = f"從台北到高雄，搭乘高鐵有 {a} 種班次選擇，搭乘飛機有 {b} 種班次選擇。若小明要從台北到高雄，請問他有多少種交通方式？"
    else: # level 2
        a = random.randint(5, 10)
        b = random.randint(4, 8)
        c = random.randint(2, 5)
        question_text = f"一個社團有 {a} 位高一生、{b} 位高二生、{c} 位高三生。若要選出一位代表，請問有多少種選法？"

    total = a + b if level == 1 else a + b + c
    correct_answer = str(total)

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}