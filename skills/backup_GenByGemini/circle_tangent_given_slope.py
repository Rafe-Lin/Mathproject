# skills/circle_tangent_given_slope.py
import random
import fractions # 修正：導入 fractions 模組
import math

def generate(level=1):
    """
    生成一道「已知斜率求圓的切線方程式」的題目。
    level 1: 圓心在原點 (0,0)。
    level 2: 圓心在任意整數點 (h,k)。
    """
    # 為了讓數字漂亮，使用畢氏三元數來構造斜率 m 和半徑 r
    py_triples = [(3, 4, 5), (5, 12, 13), (8, 15, 17)]
    p, q, r_base = random.choice(py_triples)
    
    m = fractions.Fraction(p, q) * random.choice([-1, 1])
    r = q # 修正：讓半徑等於 q，確保後續計算為整數

    if level == 1:
        h, k = 0, 0
        circle_eq = f"x² + y² = {r**2}"
        # 切線公式: y = mx ± r * sqrt(m^2 + 1)
        # sqrt(m^2 + 1) = sqrt((p/q)^2 + 1) = sqrt((p^2+q^2)/q^2) = r_base / q
        y_intercept_add = fractions.Fraction(r * r_base, q)
        
        # 確保 y 截距是整數
        y_intercept_add = int(y_intercept_add)

        correct_answer = f"y = {m}x + {y_intercept_add} 或 y = {m}x - {y_intercept_add}"

    else: # level 2
        h, k = random.randint(-5, 5), random.randint(-5, 5)
        circle_eq = f"(x - {h})² + (y - {k})² = {r**2}".replace(" - -", " + ")
        
        # 切線公式: y - k = m(x - h) ± r * sqrt(m^2 + 1)
        y_intercept_add = fractions.Fraction(r * r_base, q)
        y_intercept_add = int(y_intercept_add)

        # 整理方程式 y = mx + c
        # y = mx - mh + k ± y_intercept_add
        c1 = -m * h + k + y_intercept_add
        c2 = -m * h + k - y_intercept_add

        correct_answer = f"y = {m}x + {c1} 或 y = {m}x + {c2}".replace(" + -", " - ")

    question_text = f"求與圓 C: {circle_eq} 相切，且斜率為 {m} 的切線方程式。"
    context_string = f"求圓 {circle_eq} 且斜率為 {m} 的切線。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    # 簡單的字串比對，未來可擴充為解析方程式
    user = user_answer.replace(" ", "").lower()
    correct = correct_answer.replace(" ", "").lower()
    
    # 允許答案順序顛倒
    parts = correct.split('或')
    is_correct = (user == f"{parts[0]}或{parts[1]}" or user == f"{parts[1]}或{parts[0]}")
    
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案是：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}