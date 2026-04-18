import random
from core.helpers import format_inequality, check_inequality

def generate_linear_programming_question():
    """動態生成一道「線性規劃」的題目 (判斷點是否滿足不等式組)"""
    num_inequalities = random.choice([2, 3])
    inequalities = []
    inequality_strs = []
    
    # 生成不等式組
    for _ in range(num_inequalities):
        a = random.randint(-3, 3)
        b = random.randint(-3, 3)
        while a == 0 and b == 0:
            a = random.randint(-3, 3)
            b = random.randint(-3, 3)
        
        # 確保不等式有意義
        x_test = random.randint(-5, 5)
        y_test = random.randint(-5, 5)
        c = (a * x_test) + (b * y_test) + random.randint(-2, 2) # 讓點有機會滿足或不滿足
        
        sign = random.choice(['>', '>=', '<', '<='])
        inequalities.append({'a': a, 'b': b, 'c': c, 'sign': sign})
        inequality_strs.append(format_inequality(a, b, c, sign))
        
    # 生成一個測試點
    test_x = random.randint(-5, 5)
    test_y = random.randint(-5, 5)
    
    # 檢查測試點是否滿足所有不等式
    is_solution = True
    for ieq in inequalities:
        if not check_inequality(ieq['a'], ieq['b'], ieq['c'], ieq['sign'], test_x, test_y):
            is_solution = False
            break
            
    correct_answer = "是" if is_solution else "否"
    system_str = "\n".join([f"  {s}" for s in inequality_strs])
    
    question_text = f"請問點 ({test_x}, {test_y}) 是否為下列不等式組的解？ (請回答 '是' 或 '否')\n{system_str}"
    
    return {
        "text": question_text,
        "answer": correct_answer,
        "validation_function_name": None # 可以考慮使用 validate_check_point
    }
