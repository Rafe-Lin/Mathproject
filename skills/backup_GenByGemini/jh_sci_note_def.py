# skills/jh_sci_note_def.py
import random

def generate(level=1):
    """
    生成一道「科學記號表示法」的題目。
    """
    # 隨機問正向或反向問題
    if random.choice([True, False]):
        # 將數字轉為科學記號
        exponent = random.randint(2, 6)
        mantissa = round(random.uniform(1, 9.99), 2)
        num = mantissa * (10**exponent)
        # 轉為整數或漂亮的小數
        num = int(num) if random.choice([True, False]) else round(num, random.randint(0,2))
        
        question_text = f"請將數字 {num} 表示為科學記號。（係數取到小數點後兩位，四捨五入）"
        
        # 計算正確答案
        exp_ans = 0
        temp_num = num
        while temp_num >= 10:
            temp_num /= 10
            exp_ans += 1
        while temp_num < 1 and temp_num != 0:
            temp_num *= 10
            exp_ans -= 1
        mant_ans = round(temp_num, 2)
        correct_answer = f"{mant_ans}*10^{exp_ans}"

    else:
        # 將科學記號轉為數字
        mantissa = round(random.uniform(1, 9.9), random.randint(1, 2))
        exponent = random.randint(-3, 4)
        
        question_text = f"請將科學記號 ${mantissa} \\times 10^{{{exponent}}}$ 寫成一般數字。"
        correct_answer = f"{mantissa * (10**exponent):.10f}".rstrip('0').rstrip('.')

    context_string = f"學習科學記號的表示法與轉換。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").replace("x", "*").replace("X", "*")
    correct = str(correct_answer).strip().replace(" ", "")
    is_correct = user == correct
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案是：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}