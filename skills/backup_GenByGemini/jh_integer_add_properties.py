# skills/jh_integer_add_properties.py
import random

def generate(level=1):
    """
    生成一道「整數加法性質」的題目（交換律、結合律）。
    """
    prop = random.choice(['commutative', 'associative'])
    
    a = random.randint(-10, 10)
    b = random.randint(-10, 10)
    c = random.randint(-10, 10)

    if prop == 'commutative':
        # 交換律: a + b = b + a
        question_text = f"根據加法交換律，({a}) + ({b}) = ({b}) + ( ? )"
        correct_answer = str(a)
        context_string = "加法交換律：a + b = b + a"
    else: # associative
        # 結合律: (a + b) + c = a + (b + c)
        question_text = f"根據加法結合律，(({a}) + ({b})) + ({c}) = ({a}) + ( ? )"
        correct_answer = f"({b})+({c})"
        context_string = "加法結合律：(a + b) + c = a + (b + c)"

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

    # 結合律的答案可能有多種寫法，例如 b+c, (b)+(c)
    # 這裡做簡化檢查
    if correct.startswith('(') and correct.endswith(')'):
        # 假設是結合律 (b)+(-c)
        # 移除括號後直接比較
        user = user.replace("(", "").replace(")", "")
        correct = correct.replace("(", "").replace(")", "")

    is_correct = user == correct
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案是：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}