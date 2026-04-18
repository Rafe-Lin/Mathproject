# skills/jh_geo_triangle_incenter_area.py
import random

def generate(level=1):
    """
    生成一道「內心與三角形面積」的題目。
    """
    # 使用畢氏三元數來構造直角三角形，方便計算
    sides_options = [(3, 4, 5), (6, 8, 10), (5, 12, 13)]
    a, b, c = random.choice(sides_options)
    
    # 面積 = 1/2 * 底 * 高
    area = 0.5 * a * b
    # 周長
    perimeter = a + b + c
    # 面積 = rs, r = 面積 / s, s = 周長/2
    s = perimeter / 2
    inradius = area / s

    question_text = f"一個直角三角形的三邊長分別為 {a}, {b}, {c}。\n請問此三角形的內切圓半徑是多少？"
    correct_answer = str(int(inradius) if inradius.is_integer() else round(inradius, 2))

    context_string = "利用三角形面積公式：面積 = (1/2) * 內切圓半徑 * 周長 (A = rs)。對於直角三角形，也可使用 r = (a+b-c)/2。"

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
        is_correct = abs(float(user) - float(correct)) < 0.01
        result_text = f"完全正確！答案是 {correct}。" if is_correct else f"答案不正確。正確答案是：{correct}"
    except ValueError:
        is_correct = False
        result_text = f"請輸入數字答案。正確答案是：{correct}"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}