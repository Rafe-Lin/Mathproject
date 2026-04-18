# skills/jh_fibonacci_seq_def.py
import random

def generate(level=1):
    """
    生成一道「費波那契數列(遞迴數列)」的題目。
    """
    # 可以是標準費氏數列或變體
    a1 = random.randint(0, 2)
    a2 = random.randint(a1 + 1, 4)
    
    seq = [a1, a2]
    for i in range(4):
        seq.append(seq[-1] + seq[-2])

    question_seq = seq[:-1]
    correct_answer = str(seq[-1])

    seq_str = ", ".join(map(str, question_seq))
    question_text = f"觀察數列的規律，請問下一個數字是多少？\n\n{seq_str}, __?"

    context_string = "觀察遞迴數列的規律，後一項通常由前幾項運算而來。此數列的規律是：後一項等於前兩項的和。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    user = user_answer.strip()
    correct = correct_answer.strip()
    is_correct = user == correct
    result_text = f"完全正確！答案是 {correct}。" if is_correct else f"答案不正確。正確答案是：{correct}"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}