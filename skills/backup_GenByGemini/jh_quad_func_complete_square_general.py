# skills/jh_quad_func_complete_square_general.py
import random
from fractions import Fraction

def generate(level=1):
    """
    生成一道「二次函數配方法(一般式)」的題目。
    """
    # 構造 y = a(x-h)^2 + k
    a = random.randint(2, 4)
    h = random.randint(-3, 3)
    k = random.randint(-5, 5)

    # 展開 y = a(x^2 - 2hx + h^2) + k = ax^2 - 2ahx + ah^2 + k
    coeff_b = -2 * a * h
    coeff_c = a * h**2 + k

    func_str = f"y = {a}x² {'+' if coeff_b > 0 else '-'} {abs(coeff_b)}x {'+' if coeff_c > 0 else '-'} {abs(coeff_c)}"

    question_text = f"請利用配方法，將二次函數 {func_str} 化為頂點式 y=a(x-h)²+k 的形式。"
    
    correct_answer = f"y={a}(x{'+' if -h > 0 else ''}{-h})²{'+' if k > 0 else ''}{k}"
    if k == 0: correct_answer = f"y={a}(x{'+' if -h > 0 else ''}{-h})²"

    context_string = "先提出二次項係數，再對括號內的 x 項配方，最後加上調整項。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").replace("y=", "")
    correct = correct_answer.strip().replace(" ", "").replace("y=", "").replace("²", "^2")
    
    is_correct = user == correct
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。參考答案是：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}