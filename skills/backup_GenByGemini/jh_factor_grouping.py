# skills/jh_factor_grouping.py
import random

def generate(level=1):
    """
    生成一道「分組提公因式」的題目。
    """
    # 構造 (ax+b)(cy+d) = acxy + adx + bcy + bd
    a = random.randint(1, 3)
    b = random.randint(1, 4)
    c = random.randint(1, 3)
    d = random.randint(1, 4)

    term1 = f"{a*c}xy"
    term2 = f"{a*d}x"
    term3 = f"{b*c}y"
    term4 = f"{b*d}"
    
    terms = [term1, term2, term3, term4]
    random.shuffle(terms)
    
    poly_str = f" {terms[0]} + {terms[1]} + {terms[2]} + {terms[3]}"
    question_text = f"請對多項式{poly_str} 進行因式分解。"

    correct_answer = f"({a}x+{b})({c}y+{d})"

    context_string = "將多項式適當分組，各組分別提公因式後，再提出共同的因式。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").replace("*", "")
    is_correct = user == correct_answer.replace(" ", "").replace("*", "") or user == f"({correct_answer.split(')(')[1]})({correct_answer.split(')(')[0]})".replace(" ", "").replace("*", "")
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。參考答案是：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}