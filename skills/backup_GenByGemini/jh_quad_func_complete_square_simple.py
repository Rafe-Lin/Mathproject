# skills/jh_quad_func_complete_square_simple.py
import random

def generate(level=1):
    """
    生成一道「二次函數配方法(簡易)」的題目。
    """
    # 構造 y = (x-h)^2 + k
    h = random.randint(-5, 5)
    k = random.randint(-5, 5)

    # 展開 y = x^2 - 2hx + h^2 + k
    b = -2 * h
    c = h**2 + k

    func_str = f"y = x² {'+' if b > 0 else '-'} {abs(b)}x {'+' if c > 0 else '-'} {abs(c)}"

    question_text = f"請利用配方法，將二次函數 {func_str} 化為頂點式 y=(x-h)²+k 的形式。"
    
    correct_answer = f"y=(x{'+' if -h > 0 else ''}{-h})²{'+' if k > 0 else ''}{k}"
    if k == 0: correct_answer = f"y=(x{'+' if -h > 0 else ''}{-h})²"

    context_string = "將一次項係數一半的平方，同時加上再減去，以湊成完全平方式。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").replace("y=", "")
    correct = correct_answer.strip().replace(" ", "").replace("y=", "").replace("²", "^2")
    
    is_correct = user == correct
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。參考答案是：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}