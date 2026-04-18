# skills/jh_quad_func_axis_intercepts.py
import random

def generate(level=1):
    """
    生成一道「二次函數圖形與兩軸的交點」的題目。
    """
    # 構造 y = (x-r1)(x-r2) = x^2 - (r1+r2)x + r1r2
    r1 = random.randint(-4, 4)
    r2 = random.randint(-3, 3)
    while r1 == r2: r2 = random.randint(-3, 3)

    a = 1
    b = -(r1 + r2)
    c = r1 * r2

    func_str = f"y = x² {'+' if b > 0 else '-'} {abs(b)}x {'+' if c > 0 else '-'} {abs(c)}"
    if b == 0: func_str = f"y = x² {'+' if c > 0 else '-'} {abs(c)}"

    q_type = random.choice(['x_intercept', 'y_intercept'])

    if q_type == 'x_intercept':
        question_text = f"請問二次函數 {func_str} 的圖形與 x 軸的交點坐標為何？\n若有兩個交點，請用分號 ; 分隔 (例如: (3,0);(-5,0))"
        sols = sorted([r1, r2])
        correct_answer = f"({sols[0]},0);({sols[1]},0)"
    else: # y_intercept
        question_text = f"請問二次函數 {func_str} 的圖形與 y 軸的交點坐標為何？\n(格式: (x,y))"
        correct_answer = f"(0,{c})"

    context_string = "求 x 軸交點，令 y=0 求解 x；求 y 軸交點，令 x=0 求解 y。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = correct_answer.strip().replace(" ", "")
    
    # 處理 x 軸交點順序問題
    if ';' in user:
        user = ";".join(sorted(user.split(';')))
        correct = ";".join(sorted(correct.split(';')))

    is_correct = user == correct
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。參考答案是：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}