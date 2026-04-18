# skills/jh_equation_word_problem_solve.py
import random

def generate(level=1):
    """
    生成一道「解應用問題」的題目。
    """
    # 為了確保解是整數，反向構造
    pen_price = random.randint(10, 30)
    num_pens = random.randint(3, 8)
    total_cost = pen_price * num_pens
    
    question = f"小明買了 {num_pens} 支相同的筆，總共花了 {total_cost} 元。請問一支筆多少元？"
    answer = str(pen_price)

    question_text = f"請解下列應用問題：\n\n{question}\n\n(請先在心中或計算紙上列式，再填入最後答案)"
    correct_answer = answer

    context_string = "學習解讀應用問題，列出方程式並求解。"

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
    user = user_answer.strip()
    correct = str(correct_answer).strip()

    if user == correct:
        is_correct = True
        result_text = f"完全正確！答案是 {correct} 元。"
    else:
        is_correct = False
        result_text = f"答案不正確。正確答案是：{correct} 元"

    return {"correct": is_correct, "result": result_text, "next_question": True}