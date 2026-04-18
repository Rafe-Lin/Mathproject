import random
import math
from fractions import Fraction

# --- Data for problem generation ---
NAMES = ["小翊", "小靖", "亞駿", "雅婷", "小明", "小華", "志文", "美玲"]
ITEMS = [("零用錢", "元"), ("糖果", "顆"), ("郵票", "張"), ("彈珠", "顆"), ("收藏卡", "張")]
MARATHON_CONTEXTS = [
    ("原本跑的公里數", "公里", "增加"),
    ("原本的存款", "元", "存入"),
    ("原本收集的卡片數量", "張", "得到")
]
PLACES = [("花蓮", "臺東"), ("臺北", "高雄"), ("臺中", "嘉義"), ("基隆", "新竹"), ("桃園", "臺南")]

def generate(level=1):
    """
    生成「比與比例式應用」相關題目 (標準 LaTeX 範本)。
    包含：
    1. A的x倍 = B的y倍 (反比關係)
    2. 比例變化問題
    3. 比例尺問題
    """
    problem_type = random.choice(['inverse_ratio', 'ratio_change', 'scale'])
    
    if problem_type == 'inverse_ratio':
        return generate_inverse_ratio_problem()
    elif problem_type == 'ratio_change':
        return generate_ratio_change_problem()
    else: # problem_type == 'scale'
        return generate_scale_problem()

def generate_inverse_ratio_problem():
    """
    題型：已知小翊零用錢的 2 倍和小靖零用錢的 3 倍一樣多...
    分為兩種子題型：
    1. 求兩者數量的最簡整數比。
    2. 給定總和，求其中一人的數量。
    """
    name1, name2 = random.sample(NAMES, 2)
    item, unit = random.choice(ITEMS)
    
    c1 = random.randint(2, 9)
    # [DATA SELECTION LOGIC]
    # Ensure c2 is different from c1. This list comprehension is a safe way to do it.
    c2 = random.choice([i for i in range(2, 10) if i != c1])
    
    # 關係式 c1 * A = c2 * B  => A:B = c2:c1
    ratio_n1 = c2
    ratio_n2 = c1
    
    # Sub-type 1: Ask for the ratio
    if random.random() < 0.4:
        question_text = f"已知{name1}{item}的 ${c1}$ 倍和{name2}{item}的 ${c2}$ 倍一樣多，請問{name1}的{item}與{name2}的{item}之最簡整數比為何？ (格式為 a:b)"
        correct_answer = f"{ratio_n1}:${ratio_n2}"
    
    # Sub-type 2: Ask for a specific amount given the total
    else:
        # To ensure integer amounts, the parameter `r` must be an integer.
        # The total amount = (ratio_n1 + ratio_n2) * r
        ratio_sum = ratio_n1 + ratio_n2
        if unit == "元":
            r = random.randint(5, 50) * 10
        else:
            r = random.randint(5, 30)
            
        total = ratio_sum * r
        amount1 = ratio_n1 * r
        amount2 = ratio_n2 * r
        
        target_person, target_amount = random.choice([(name1, amount1), (name2, amount2)])
        
        question_text = f"已知{name1}和{name2}的{item}數量比為 ${ratio_n1}:${ratio_n2}$，且兩人共有 ${total}$ {unit}，請問{target_person}有多少{unit}？"
        correct_answer = str(target_amount)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_ratio_change_problem():
    """
    題型：兩人原有數量比為 a:b，各增減 c, d 後，新比例為 e:f，求原數量。
    """
    name1, name2 = "亞駿", "雅婷" # Use fixed names as per example
    context, unit, verb = random.choice(MARATHON_CONTEXTS)

    # Reverse-engineer the problem to ensure integer solutions
    while True:
        r = random.randint(3, 10)
        r1_orig, r2_orig = random.sample(range(2, 10), 2)
        
        orig1 = r1_orig * r
        orig2 = r2_orig * r
        
        add1 = random.randint(2, 20)
        add2 = random.randint(2, 20)
        
        # Ensure the change is not proportional to the original ratio
        # i.e., add1/add2 != r1_orig/r2_orig to avoid a degenerate case.
        if add1 * r2_orig == add2 * r1_orig:
            continue
            
        final1 = orig1 + add1
        final2 = orig2 + add2
        
        common_divisor = math.gcd(final1, final2)
        r1_final = final1 // common_divisor
        r2_final = final2 // common_divisor
        
        # Ensure the final ratio is not the same as the original
        if r1_orig * r2_final != r2_orig * r1_final:
            break

    target_person, target_amount = random.choice([(name1, orig1), (name2, orig2)])

    question_text = f"已知{name1}和{name2}兩人{context}的比是 ${r1_orig}：${r2_orig}$，後來兩人分別又{verb}了 ${add1}$ {unit}和 ${add2}$ {unit}，結果總數量的比變為 ${r1_final}：${r2_final}$，則{target_person}原本有多少{unit}？"
    correct_answer = str(target_amount)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_scale_problem():
    """
    題型：地圖比例尺問題
    """
    place1, place2 = random.choice(PLACES)
    
    # Generate a problem with integer solutions
    while True:
        map_scale_dist = random.choice([1, 2, 4, 5])
        actual_scale_dist = random.choice([25, 50, 100, 200])
        # Multiplier to generate the measured distance
        k = random.choice([1.5, 2, 2.5, 3, 4, 5]) 
        
        map_measured = map_scale_dist * k
        actual_answer = actual_scale_dist * k
        
        # Ensure both the measured distance in the question and the final answer are integers
        if map_measured == int(map_measured) and actual_answer == int(actual_answer):
            map_measured = int(map_measured)
            actual_answer = int(actual_answer)
            # Avoid trivial case where measured distance equals scale distance
            if map_measured != map_scale_dist:
                break
    
    question_text = f"地圖的比例尺為 ${map_scale_dist}$ 公分對應 ${actual_scale_dist}$ 公里。若小妍用尺量得{place1}到{place2}的距離約為 ${map_measured}$ 公分，則這兩地的實際距離約為多少公里？"
    correct_answer = str(actual_answer)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    
    is_correct = (user_answer.upper() == correct_answer.upper())
    
    # For numerical answers, attempt a float comparison to be more lenient (e.g., 150 vs 150.0)
    if not is_correct:
        try:
            if float(user_answer) == float(correct_answer):
                is_correct = True
        except (ValueError, TypeError):
            # This handles cases like "3:2" which cannot be converted to float
            pass

    # [教學示範] The f-string uses a single brace {correct_answer} for variable substitution,
    # as per the critical syntax rules.
    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}
