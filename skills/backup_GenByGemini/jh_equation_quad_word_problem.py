# skills/jh_equation_quad_word_problem.py
import random

def generate(level=1):
    """
    生成一道「一元二次方程式應用問題」的題目。
    """
    # 範例：連續整數乘積問題
    n = random.randint(5, 15)
    product = n * (n + 1)
    
    question = f"兩個連續正整數的乘積為 {product}，請問這兩個數是多少？"
    answer = f"{n},{n+1}"

    question_text = f"請解下列應用問題：\n\n{question}\n\n(請回答較小的數,較大的數，例如: 8,9)"
    correct_answer = answer

    context_string = "學習將應用問題的情境轉化為一元二次方程式並求解。"

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
    correct = str(correct_answer).strip().replace(" ", "")

    try:
        user_sols = sorted(map(int, user.split(',')))
        correct_sols = sorted(map(int, correct.split(',')))
        if user_sols == correct_sols:
            is_correct = True
            result_text = f"完全正確！這兩個數是 {correct_answer}。"
        else:
            is_correct = False
            result_text = f"答案不正確。正確答案是：{correct_answer}"
    except ValueError:
        is_correct = False
        result_text = f"請用逗號分隔兩個數字，例如 8,9。正確答案是：{correct_answer}"

    return {"correct": is_correct, "result": result_text, "next_question": True}