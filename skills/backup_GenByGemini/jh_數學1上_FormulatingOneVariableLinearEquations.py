import random
import re

def generate(level=1):
    """
    生成「列一元一次方程式」相關題目。
    包含：
    1. 購物問題 (買 X 個單價為 y 的物品加上其他花費)
    2. 年齡問題 (簡單關係)
    3. 年齡問題 (過去/未來時間點，選擇題)
    4. 分配問題 (平分後有剩餘或不足)
    """
    problem_type = random.choice(['shopping', 'age_simple', 'age_past_future_mc', 'distribution'])
    
    if problem_type == 'shopping':
        return generate_shopping_problem()
    elif problem_type == 'age_simple':
        return generate_age_simple_problem()
    elif problem_type == 'age_past_future_mc':
        return generate_age_past_future_mc_problem()
    else:
        return generate_distribution_problem()

def _normalize_answer(s):
    """Helper function to normalize an equation string for comparison."""
    # Remove all whitespace
    s = re.sub(r'\s+', '', s)
    # Remove LaTeX $ markers
    s = s.replace('$', '')
    # Replace full-width characters with half-width equivalents
    s = s.replace('＋', '+').replace('－', '-').replace('＝', '=')
    # Standardize multiplication symbol or remove it (e.g., 5*x -> 5x)
    s = s.replace('×', '*').replace('⋅', '*')
    s = re.sub(r'(\d)\*([a-zA-Z])', r'\1\2', s)
    return s

def generate_shopping_problem():
    """
    題型：購物情境
    媽媽買了 6 盒牛奶,每盒都是 x 元,另外又買了 120 元的麵包,總共付了 300 元。
    方程式: 6x + 120 = 300
    """
    variable = random.choice(['x', 'y', 'a'])
    item = random.choice(['牛奶', '鉛筆', '飲料', '原子筆', '冰棒'])
    unit = random.choice(['盒', '枝', '瓶', '打', '個'])
    
    quantity = random.randint(3, 12)
    extra_item = random.choice(['麵包', '橡皮擦', '點心', '雜誌'])
    extra_cost = random.randint(20, 150)
    
    # Ensure x has a reasonable integer solution for context
    x_val = random.randint(10, 50)
    total_cost = quantity * x_val + extra_cost
    
    question_text = f"小明買了 {quantity} {unit}{item}，每{unit}都是 ${variable}$ 元，另外又買了 {extra_cost} 元的{extra_item}，結帳時總共付了 {total_cost} 元。依題意可列出一元一次方程式為何？"
    
    correct_answer = f"${quantity}{variable}+{extra_cost}={total_cost}$"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_age_simple_problem():
    """
    題型：簡單年齡關係
    爸爸的年齡是書萍的 2 倍多 5 歲，若書萍 y 歲，爸爸 35 歲。
    方程式: 2y + 5 = 35
    """
    variable = random.choice(['y', 'x', 'a'])
    person1 = random.choice(['爸爸', '媽媽', '老師', '哥哥'])
    person2 = random.choice(['書萍', '小華', '志明', '弟弟'])
    
    multiplier = random.randint(2, 4)
    relation = random.choice(['多', '少'])
    diff = random.randint(1, 10)
    
    # Calculate a plausible final age
    person2_age = random.randint(7, 15)
    person1_age = multiplier * person2_age + (diff if relation == '多' else -diff)
    
    if relation == '多':
        relation_text = f"的 {multiplier} 倍多 {diff} 歲"
        expression = f"{multiplier}{variable}+{diff}"
    else:
        relation_text = f"的 {multiplier} 倍少 {diff} 歲"
        expression = f"{multiplier}{variable}-{diff}"
    
    question_text = f"今年{person1}的年齡恰好是{person2}年齡{relation_text}。若{person2}今年 ${variable}$ 歲，且{person1}今年 {person1_age} 歲，則依題意可列出一元一次方程式為何？"
    correct_answer = f"${expression}={person1_age}$"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_age_past_future_mc_problem():
    """
    題型：過去/未來時間點的年齡關係 (選擇題)
    媽媽今年 36 歲,意紋今年 x 歲,若三年前,媽媽的年齡是意紋的 3 倍。
    方程式: 36-3 = 3(x-3)
    """
    variable = 'x'
    person1 = random.choice(['媽媽', '爸爸'])
    person2 = random.choice(['意紋', '小莉', '阿德'])
    
    person1_current_age = random.randint(30, 45)
    time_diff = random.randint(2, 5)
    multiplier = random.randint(2, 4)
    
    # Ensure the ages work out to be integers
    person2_current_age_num = (person1_current_age + (multiplier - 1) * time_diff)
    while person2_current_age_num % multiplier != 0:
        person1_current_age = random.randint(30, 45)
        time_diff = random.randint(2, 5)
        person2_current_age_num = (person1_current_age + (multiplier - 1) * time_diff)
        
    direction = random.choice(['前', '後'])
    if direction == '前':
        time_text = f"{time_diff}年{direction}"
        p1_age_expr = f"{person1_current_age}-{time_diff}"
        p2_age_expr = f"{variable}-{time_diff}"
    else: # 後
        time_text = f"{time_diff}年{direction}"
        p1_age_expr = f"{person1_current_age}+{time_diff}"
        p2_age_expr = f"{variable}+{time_diff}"
        
    question_text = f"{person1}今年 {person1_current_age} 歲，{person2}今年 ${variable}$ 歲。若{time_text}，{person1}的年齡是{person2}的 {multiplier} 倍，則依題意可列出一元一次方程式為何？"
    
    # Correct Answer
    correct_eq = f"${p1_age_expr}={multiplier}({p2_age_expr})$"
    
    # Distractors
    distractor1 = f"${person1_current_age}={multiplier}{variable}$" # Ignores time shift
    distractor2 = f"${p1_age_expr}={multiplier}{p2_age_expr}$" # Forgets parentheses
    distractor3 = f"${person1_current_age}={multiplier}({p2_age_expr})$" # Only shifts one person's age
    
    options = [correct_eq, distractor1, distractor2, distractor3]
    random.shuffle(options)
    
    correct_label = chr(ord('A') + options.index(correct_eq))
    
    options_text = "\n".join([f"( {chr(ord('A') + i)} ) {opt}" for i, opt in enumerate(options)])
    
    full_question = f"{question_text}\n{options_text}"

    return {
        "question_text": full_question,
        "answer": correct_label,
        "correct_answer": correct_label
    }

def generate_distribution_problem():
    """
    題型：分配問題
    將一堆糖果分給 x 位學生，每人 5 顆，會剩下 3 顆。若糖果總共 58 顆。
    方程式: 5x + 3 = 58
    """
    variable = random.choice(['x', 'y', 'n'])
    item = random.choice(['糖果', '鉛筆', '餅乾', '蘋果'])
    item_unit = random.choice(['顆', '枝', '片'])
    group = random.choice(['學生', '小朋友', '員工', '組'])
    
    per_person = random.randint(3, 8)
    x_val = random.randint(10, 20) # Number of groups/students
    
    scenario = random.choice(['remainder', 'shortage'])
    
    if scenario == 'remainder':
        change = random.randint(1, per_person - 1)
        total_items = per_person * x_val + change
        relation_text = f"會剩下 {change} {item_unit}"
        equation = f"{per_person}{variable}+{change}={total_items}"
    else: # shortage
        change = random.randint(1, per_person - 1)
        total_items = per_person * x_val - change
        relation_text = f"會不夠 {change} {item_unit}"
        equation = f"{per_person}{variable}-{change}={total_items}"

    question_text = f"將一堆{item}分給 ${variable}$ 位{group}，若每位{group}分 {per_person} {item_unit}，{relation_text}。已知{item}總共有 {total_items} {item_unit}，則依題意可列出一元一次方程式為何？"
    correct_answer = f"${equation}$"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    對於方程式，會正規化後再比對。
    對於選擇題，直接比對選項。
    """
    user_answer = user_answer.strip().upper()
    correct_answer = correct_answer.strip().upper()

    # Check if the correct answer is a single letter (multiple choice)
    if len(correct_answer) == 1 and 'A' <= correct_answer <= 'D':
        is_correct = (user_answer == correct_answer)
    else:
        # It's an equation, normalize and compare
        norm_user = _normalize_answer(user_answer)
        norm_correct = _normalize_answer(correct_answer)
        is_correct = (norm_user == norm_correct)

    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}
