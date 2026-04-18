import random

def generate_trig_sine_cosine_combination_question():
    """動態生成一道「正餘弦的疊合」的題目 (求最大/最小值)"""
    a, b, r = random.choice([(3, 4, 5), (5, 12, 13), (8, 15, 17)])
    a, b = random.sample([a, b], 2)
    max_or_min = random.choice(['max', 'min'])
    if max_or_min == 'max':
        question_text = f"請問函數 f(x) = {a}*sin(x) + {b}*cos(x) 的最大值是多少？"
        answer = str(r)
    else:
        question_text = f"請問函數 f(x) = {a}*sin(x) + {b}*cos(x) 的最小值是多少？"
        answer = str(-r)
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }
