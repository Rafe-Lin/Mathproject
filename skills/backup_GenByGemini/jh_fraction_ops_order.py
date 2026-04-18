# skills/jh_fraction_ops_order.py
import random
from fractions import Fraction

def generate(level=1):
    """
    生成一道「分數的四則運算」的題目。
    """
    f1 = Fraction(random.randint(1, 5), random.randint(2, 5))
    f2 = Fraction(random.randint(1, 5), random.randint(2, 5))
    f3 = Fraction(random.randint(1, 5), random.randint(2, 5))

    ops = [random.choice(['+', '-']), random.choice(['*', '/'])]
    random.shuffle(ops)
    op1, op2 = ops

    # 構造表達式
    expr = f"f1 {op1} f2 {op2} f3"
    result = eval(expr)

    def frac_to_str(f):
        return f"\\frac{{{f.numerator}}}{{{f.denominator}}}"

    question_text = f"請計算：${frac_to_str(f1)} {op1.replace('/', '÷')} {frac_to_str(f2)} {op2.replace('/', '÷')} {frac_to_str(f3)}$"
    
    correct_answer = f"{result.numerator}/{result.denominator}" if result.denominator != 1 else str(result.numerator)

    context_string = f"分數的四則運算，注意先乘除後加減。"

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
    try:
        user_frac = Fraction(user_answer.strip())
        correct_frac = Fraction(correct_answer.strip())
        
        if user_frac == correct_frac:
            is_correct = True
            result_text = f"完全正確！答案是 {correct_answer}。"
        else:
            is_correct = False
            result_text = f"答案不正確。正確答案是：{correct_answer}"
    except (ValueError, ZeroDivisionError):
        is_correct = False
        result_text = f"請輸入分數格式，例如 3/4。正確答案是：{correct_answer}"

    return {"correct": is_correct, "result": result_text, "next_question": is_correct}