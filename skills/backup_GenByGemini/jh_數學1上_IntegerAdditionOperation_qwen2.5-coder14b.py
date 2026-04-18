# ==============================================================================
# ID: jh_數學1上_IntegerAdditionOperation
# Model: qwen2.5-coder:14b | Strategy: General Math Pedagogy v7.3 (Chinese)
# Duration: 248.60s | RAG: 4 examples
# Created At: 2025-12-31 11:17:12
# Fix Status: [Clean Pass]
# ==============================================================================

import random

def generate_concept_problem():
    # Type: Concept (Explicit Options)
    target = -5
    others = [3, 0, 8]
    options = [target] + others
    random.shuffle(options)
    opt_str = ', '.join([str(x) for x in options])
    return {'question_text': f'在 {opt_str} 中，何者為負數？', 'answer': str(target), 'correct_answer': str(target)}

def generate_calc_problem():
    val1 = random.randint(-10, -1)
    val2 = random.randint(-10, -1)
    return {'question_text': f'請計算 $|{val1}| + |{val2}|$ 的值為何？', 'answer': str(abs(val1) + abs(val2)), 'correct_answer': str(abs(val1) + abs(val2))}

def generate_reverse_problem():
    result = random.randint(5, 10)
    val1 = random.randint(-10, -1)
    val2 = result - abs(val1)
    return {'question_text': f'已知 $|{val1}| + |x| = {result}$，請計算 x 的值為何？', 'answer': str(val2), 'correct_answer': str(val2)}

def generate_app_problem():
    distance1 = random.randint(5, 10)
    distance2 = random.randint(5, 10)
    total_distance = distance1 + distance2
    return {'question_text': f'小明從家走到學校需要走 {distance1} 公里，再從學校走到圖書館需要走 {distance2} 公里。請問小明總共走了多少公里？', 'answer': str(total_distance), 'correct_answer': str(total_distance)}

def generate(level=1):
    type = random.choice(['concept', 'calc', 'reverse', 'app'])
    if type == 'concept': return generate_concept_problem()
    elif type == 'calc': return generate_calc_problem()
    elif type == 'reverse': return generate_reverse_problem()
    else: return generate_app_problem()

# Example usage