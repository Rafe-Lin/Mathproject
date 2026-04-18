import random
from core.helpers import format_inequality, check_inequality, validate_check_point

def generate_check_point_in_system_question():
    """動態生成一道「判斷點是否為不等式系統解」的題目。"""
    num_inequalities = random.choice([2, 3])
    inequalities = []
    inequality_strs = []
    for _ in range(num_inequalities):
        a = random.randint(-5, 5)
        b = random.randint(-5, 5)
        while a == 0 and b == 0:
            a = random.randint(-5, 5)
            b = random.randint(-5, 5)
        temp_x = random.randint(-3, 3)
        temp_y = random.randint(-3, 3)
        c = (a * temp_x) + (b * temp_y)
        sign = random.choice(['>', '>=', '<', '<='])
        inequalities.append({'a': a, 'b': b, 'c': c, 'sign': sign})
        inequality_strs.append(format_inequality(a, b, c, sign))
    test_x = random.randint(-5, 5)
    test_y = random.randint(-5, 5)
    is_solution = True
    for ieq in inequalities:
        if not check_inequality(ieq['a'], ieq['b'], ieq['c'], ieq['sign'], test_x, test_y):
            is_solution = False
            break
    correct_answer = "是" if is_solution else "否"
    system_str = "\n".join([f"  {s}" for s in inequality_strs])
    question_text = f"請問點 ({test_x}, {test_y}) 是否為下列不等式系統的解？ (請回答 '是' 或 '否')\n{system_str}"
    return {
        "text": question_text,
        "answer": correct_answer,
        "validation_function_name": validate_check_point.__name__
    }
