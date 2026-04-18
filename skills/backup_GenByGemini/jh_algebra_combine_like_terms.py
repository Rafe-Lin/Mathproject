# skills/jh_algebra_combine_like_terms.py
import random

def generate(level=1):
    """
    生成一道「合併同類項」的題目。
    """
    # 生成兩個同類項
    coeff1 = random.randint(-10, 10)
    while coeff1 == 0:
        coeff1 = random.randint(-10, 10)
    
    coeff2 = random.randint(-10, 10)
    while coeff2 == 0:
        coeff2 = random.randint(-10, 10)

    var = "x"
    
    term1_str = f"{coeff1}{var}" if coeff1 != 1 else var
    term1_str = f"-{var}" if coeff1 == -1 else term1_str

    term2_str = f"+ {coeff2}{var}" if coeff2 > 0 else f"- {abs(coeff2)}{var}"
    if coeff2 == 1:
        term2_str = f"+ {var}"
    if coeff2 == -1:
        term2_str = f"- {var}"

    # 隨機加入常數項
    const1 = random.randint(-10, 10)
    const2 = random.randint(-10, 10)
    
    question_text = f"請化簡下列式子：{term1_str} {'+ ' + str(const1) if const1 > 0 else '- ' + str(abs(const1)) if const1 != 0 else ''} {term2_str} {'+ ' + str(const2) if const2 > 0 else '- ' + str(abs(const2)) if const2 != 0 else ''}"

    # 計算答案
    final_coeff = coeff1 + coeff2
    final_const = const1 + const2

    if final_coeff == 1:
        final_coeff_str = "x"
    elif final_coeff == -1:
        final_coeff_str = "-x"
    else:
        final_coeff_str = f"{final_coeff}x"

    if final_const > 0:
        correct_answer = f"{final_coeff_str}+{final_const}"
    elif final_const < 0:
        correct_answer = f"{final_coeff_str}{final_const}"
    else: # final_const == 0
        correct_answer = final_coeff_str

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": f"化簡 {question_text.split('：')[1].strip()}"
    }

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = correct_answer.strip().replace(" ", "")
    is_correct = user == correct
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案是：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}