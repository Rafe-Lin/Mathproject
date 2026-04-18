# skills/jh_formula_square_of_diff_expand.py
import random

def generate(level=1):
    """
    生成一道「差的平方公式展開」的題目。
    """
    # 構造 (a-b)^2
    # a 可以是 nx 或 ny
    a_coeff = random.randint(2, 7)
    a_var = random.choice(['x', 'y'])
    a_term = f"{a_coeff}{a_var}"
    
    # b 是常數
    b_term = random.randint(2, 9)

    question_text = f"請使用差的平方公式展開 ({a_term} - {b_term})²。"

    # 答案是 a^2 - 2ab + b^2
    correct_answer = f"{(a_coeff**2)}{a_var}²-{2*a_coeff*b_term}{a_var}+{b_term**2}"

    context_string = "利用差的平方公式 (a-b)² = a² - 2ab + b² 展開多項式。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    """
    檢查使用者輸入的答案是否正確。
    """
    user = user_answer.strip().replace(" ", "")
    correct = correct_answer.strip().replace(" ", "").replace("²", "^2")
    is_correct = user == correct
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案是：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}