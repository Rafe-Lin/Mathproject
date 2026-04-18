# skills/jh_sqrt_ops_divide.py
import random

def generate(level=1):
    """
    生成一道「方根的除法」的題目。
    """
    # 構造 √a / √b = √(a/b)
    # 為了讓結果能化簡，讓 a/b 是個整數
    b = random.choice([2, 3, 5])
    quotient_sq = random.randint(2, 5)
    a = b * (quotient_sq**2)

    question_text = f"請計算 √{a} ÷ √{b}"
    
    correct_answer = str(quotient_sq)

    context_string = "利用根式除法性質 √a / √b = √(a/b) 來計算。"

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
        is_correct = int(user) == int(correct)
        result_text = f"完全正確！答案是 {correct}。" if is_correct else f"答案不正確。正確答案是：{correct}"
    except ValueError:
        is_correct = False
        result_text = f"請輸入數字答案。正確答案是：{correct}"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}