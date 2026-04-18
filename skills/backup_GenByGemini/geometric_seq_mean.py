import random

def generate(level=1):
    """
    生成一道「等比中項」的題目。
    level 1: 給定 a, c，求 b (b²=ac)。
    level 2: 給定三項，其中一項為 x，求 x。
    """
    if level == 1:
        # 構造 b^2 = ac
        b = random.randint(2, 10)
        a = random.randint(1, 5)
        if (b*b) % a != 0: return generate(level) # 確保 c 是整數
        c = (b*b) // a
        question_text = f"若 {a}, b, {c} 三正數成等比數列，請問 b 的值是多少？"
        correct_answer = str(b)
    else: # level 2
        a1 = random.choice([1, 2, 3])
        r = random.choice([2, 3, 4])
        x = a1 * r
        c = a1 * r * r
        question_text = f"若 {a1}, x, {c} 三數成等比數列，請問 x 的可能值為何？ (若有兩解，請用逗號 , 分隔)"
        correct_answer = f"{x},-{x}"

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user_parts = sorted(user_answer.strip().replace(" ", "").split(','))
    correct_parts = sorted(correct_answer.strip().split(','))
    is_correct = (user_parts == correct_parts)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}