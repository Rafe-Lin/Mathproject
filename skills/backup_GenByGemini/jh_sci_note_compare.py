# skills/jh_sci_note_compare.py
import random

def generate(level=1):
    """
    生成一道「科學記號比較大小」的題目。
    """
    # 生成第一個數
    mantissa1 = round(random.uniform(1, 9.9), random.randint(1, 2))
    exponent1 = random.randint(-5, 5)
    
    # 生成第二個數
    mantissa2 = round(random.uniform(1, 9.9), random.randint(1, 2))
    exponent2 = random.randint(-5, 5)

    # 確保兩數不相等
    while exponent1 == exponent2 and mantissa1 == mantissa2:
        exponent2 = random.randint(-5, 5)

    num1_str = f"{mantissa1} \\times 10^{{{exponent1}}}"
    num2_str = f"{mantissa2} \\times 10^{{{exponent2}}}"

    if exponent1 > exponent2: correct_answer = ">"
    elif exponent1 < exponent2: correct_answer = "<"
    else: # 指數相同，比較係數
        if mantissa1 > mantissa2: correct_answer = ">"
        else: correct_answer = "<"

    question_text = f"請比較 A = ${num1_str}$ 和 B = ${num2_str}$ 的大小。\n請在下方填入 > 或 <。"

    context_string = f"比較科學記號，先比較指數，指數相同再比較係數。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    user = user_answer.strip()
    correct = str(correct_answer).strip()
    is_correct = user == correct
    result_text = f"完全正確！答案是 {correct}。" if is_correct else f"答案不正確。正確答案是：{correct}"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}