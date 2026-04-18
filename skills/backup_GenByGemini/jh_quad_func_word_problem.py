# skills/jh_quad_func_word_problem.py
import random

def generate(level=1):
    """
    生成一道「二次函數應用問題」的題目。
    """
    # 範例：利潤問題
    # 利潤 y = -a(x-h)^2 + k
    # x 是售價，h 是最佳售價，k 是最高利潤
    h = random.randint(20, 50) # 最佳售價
    k = random.randint(500, 2000) # 最高利潤
    a = random.randint(1, 5)
    
    # y = -a(x^2 - 2hx + h^2) + k = -ax^2 + 2ahx -ah^2+k
    coeff_b = 2 * a * h
    coeff_c = -a * h**2 + k

    func_str = f"y = -{a}x² + {coeff_b}x + {coeff_c}"

    question_text = (
        f"某商品的利潤 y (元) 與其售價 x (元) 的關係為二次函數 {func_str}。\n"
        f"請問售價訂為多少元時，可以獲得最大利潤？"
    )
    correct_answer = str(h)

    context_string = "二次函數應用問題通常與求最大值或最小值有關，可以透過配方法找出頂點坐標來求解。"

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
    result_text = f"完全正確！答案是 {correct} 元。" if is_correct else f"答案不正確。正確答案是：{correct} 元"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}