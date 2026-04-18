# \複數\代數基本定理
import random

def generate(level=1):
    """
    生成一道「代數基本定理」的觀念題。
    """
    n = random.randint(3, 10)
    question_text = (
        f"根據代數基本定理，一個 {n} 次的複係數多項式方程式，在複數系中「恰好」有幾個根（包含重根）？\n\n"
        f"A) 1\n"
        f"B) {n}\n"
        f"C) 無限多個"
    )
    correct_answer = "B"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().upper()
    is_correct = (user == correct_answer)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}