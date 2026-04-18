import random
import math

# --- 數學輔助函式 ---

def lcm(a, b):
    """計算兩數的最小公倍數"""
    return abs(a * b) // math.gcd(a, b) if a != 0 and b != 0 else 0

def lcm_three(a, b, c):
    """計算三數的最小公倍數"""
    return lcm(lcm(a, b), c)

# --- 主要生成函式 ---

def generate(level=1):
    """
    生成「因數與倍數應用問題」相關題目。
    包含：
    1. 最大公因數：分組/分裝問題 (Grouping/Packaging with GCD)
    2. 最小公倍數：週期問題 (Cycles with LCM)
    3. 最小公倍數：拼貼問題 (Tiling with LCM)
    4. 最大公因數：周長問題 (Perimeter with GCD)
    """
    problem_type = random.choice([
        'gcd_grouping', 
        'lcm_cycle', 
        'lcm_tiling', 
        'gcd_perimeter'
    ])
    
    if problem_type == 'gcd_grouping':
        return generate_gcd_grouping_problem()
    elif problem_type == 'lcm_cycle':
        return generate_lcm_cycle_problem()
    elif problem_type == 'lcm_tiling':
        return generate_lcm_tiling_problem()
    else: # 'gcd_perimeter'
        return generate_gcd_perimeter_problem()

# --- 題型生成函式 ---

def generate_gcd_grouping_problem():
    """
    題型：分裝/分組問題 (最大公因數)
    範例：將 n1 個 A 和 n2 個 B 平均分組，每組的 A 和 B 數量需相同。
          問：最多可分成幾組？每組共有多少個？
    """
    items = random.choice([
        {'name1': '蘋果', 'name2': '橘子', 'unit_item': '個', 'unit_group': '堆'},
        {'name1': '男生', 'name2': '女生', 'unit_item': '位', 'unit_group': '組'},
        {'name1': '紅色串珠', 'name2': '藍色串珠', 'unit_item': '顆', 'unit_group': '串'}
    ])
    
    common_factor = random.randint(3, 12)
    f1 = random.randint(2, 5)
    f2 = random.randint(2, 5)
    while f1 == f2:
        f2 = random.randint(2, 5)
        
    n1 = common_factor * f1
    n2 = common_factor * f2
    
    if random.random() > 0.5:
        n1, n2 = n2, n1
        
    the_gcd = math.gcd(n1, n2)
    total_per_group = (n1 // the_gcd) + (n2 // the_gcd)
    
    q_type = random.choice(['groups_only', 'groups_and_total'])
    
    if q_type == 'groups_only':
        question_text = (f"要將 {n1} {items['unit_item']}{items['name1']}和 {n2} {items['unit_item']}{items['name2']} 平均分{items['unit_group']}，"
                         f"使得每{items['unit_group']}的{items['name1']}數量相同，{items['name2']}數量也相同，且全部分完。"
                         f"請問最多可以分成幾{items['unit_group']}？")
        correct_answer = str(the_gcd)
    else:
        question_text = (f"要將 {n1} {items['unit_item']}{items['name1']}和 {n2} {items['unit_item']}{items['name2']} 混合分組，"
                         f"使得每組的{items['name1']}人數一樣多，{items['name2']}人數也一樣多，且全部分完。"
                         f"請問：\n(1) 最多可分成幾組？\n(2) 此時每組共有多少{items['unit_item']}？\n(請依序回答，並用逗號分隔)")
        correct_answer = f"{the_gcd},{total_per_group}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_lcm_cycle_problem():
    """
    題型：週期問題 (最小公倍數)
    範例：A 每 c1 天、B 每 c2 天做某事。今天一起做了，下次一起做是幾天後？
    """
    people = random.sample(['小翊', '小妍', '小靖', '小倫'], 3)
    action = random.choice(['到圖書館', '去運動中心', '澆花'])
    unit = random.choice(['天', '小時', '分鐘'])
    
    num_count = random.choice([2, 3])
    
    if num_count == 2:
        c1 = random.randint(4, 10)
        c2 = random.randint(4, 10)
        while math.gcd(c1, c2) < 2 or c1 == c2:
            c1 = random.randint(4, 15)
            c2 = random.randint(4, 15)
        
        the_lcm = lcm(c1, c2)
        question_text = (f"{people[0]}每 {c1} {unit}{action}一次，{people[1]}每 {c2} {unit}{action}一次。"
                         f"如果今天兩人都{action}了，那麼最少要再過幾{unit}，兩人會再度在同一{unit}{action}？")
        correct_answer = str(the_lcm)
    else:
        cycles = sorted(list(set([random.randint(6, 12), random.randint(8, 15), random.randint(10, 20)])))
        while len(cycles) < 3:
            cycles.append(random.randint(6, 20))
            cycles = sorted(list(set(cycles)))
        c1, c2, c3 = cycles[0], cycles[1], cycles[2]

        the_lcm = lcm_three(c1, c2, c3)
        question_text = (f"{people[0]}每 {c1} {unit}{action}一次，{people[1]}每 {c2} {unit}{action}一次，而{people[2]}每 {c3} {unit}{action}一次。"
                         f"今天三人都{action}，那麼最少要再幾{unit}，三人才會再度在同一{unit}{action}？")
        correct_answer = str(the_lcm)
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_lcm_tiling_problem():
    """
    題型：拼貼問題 (最小公倍數)
    範例：用長 L 寬 W 的磁磚拼成一個正方形，最小邊長為何？面積為何？
    """
    item = random.choice(['磁磚', '海報紙', '木板'])
    unit = '公分'
    
    f = random.randint(5, 15)
    d1 = random.randint(2, 5)
    d2 = random.randint(2, 5)
    while d1 == d2:
        d2 = random.randint(2, 5)
        
    length = f * d1
    width = f * d2
    
    the_lcm = lcm(length, width)
    area = the_lcm * the_lcm
    
    q_type = random.choice(['side_only', 'side_and_area'])
    
    if q_type == 'side_only':
        question_text = (f"使用長 {length} {unit}、寬 {width} {unit}的長方形{item}，"
                         f"想在不切割的情況下，緊密地拼貼成一個實心的正方形。"
                         f"請問所能拼出的最小正方形邊長為多少{unit}？")
        correct_answer = str(the_lcm)
    else:
        question_text = (f"使用長 {length} {unit}、寬 {width} {unit}的長方形{item}，"
                         f"想在不切割的情況下，緊密地拼貼成一個實心的正方形。"
                         f"請問：\n(1) 所拼貼的最小正方形邊長為何({unit})？\n(2) 此時面積是多少平方{unit}？\n(請依序回答，並用逗號分隔)")
        correct_answer = f"{the_lcm},{area}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_gcd_perimeter_problem():
    """
    題型：周長問題 (最大公因數)
    範例：在長 L 寬 W 的長方形周圍種樹，四頂點要種，最大間距為何？共需幾棵？
    """
    area_type = random.choice(['土地', '公園', '花圃'])
    item_map = {'樹': '棵', '旗子': '面', '路燈': '盞'}
    item_name = random.choice(list(item_map.keys()))
    item_unit = item_map[item_name]
    verb_map = {'樹': '種', '旗子': '插', '路燈': '裝設'}
    verb = verb_map[item_name]
    unit = '公尺'
    
    f = random.randint(10, 25)
    d1 = random.randint(3, 8)
    d2 = random.randint(3, 8)
    while d1 == d2:
        d2 = random.randint(3, 8)
    
    length = f * d1
    width = f * d2
    
    the_gcd = math.gcd(length, width)
    perimeter = 2 * (length + width)
    total_items = perimeter // the_gcd
    
    q_type = random.choice(['distance_only', 'distance_and_total'])
    
    if q_type == 'distance_only':
        question_text = (f"有一塊長 {length} {unit}、寬 {width} {unit}的長方形{area_type}，"
                         f"想在其周圍每隔相同距離{verb}一{item_unit}{item_name}，"
                         f"且四個頂點都要{verb}。請問相鄰兩{item_unit}{item_name}之間的最大距離是多少{unit}？")
        correct_answer = str(the_gcd)
    else:
        question_text = (f"有一塊長 {length} {unit}、寬 {width} {unit}的長方形{area_type}，"
                         f"想在其周圍每隔相同距離{verb}一{item_unit}{item_name}，"
                         f"且四個頂點都要{verb}。請問：\n(1) 相鄰兩{item_unit}{item_name}之間的最大距離是多少{unit}？\n"
                         f"(2) 承上題，總共需要{verb}幾{item_unit}{item_name}？\n"
                         f"(請依序回答，並用逗號分隔)")
        correct_answer = f"{the_gcd},{total_items}"
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

# --- 答案檢查函式 ---

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    支援單一答案或以逗號分隔的多重答案。
    """
    user_answer = user_answer.strip().replace('，', ',')
    correct_answer = correct_answer.strip()

    user_parts = [part.strip() for part in user_answer.split(',') if part]
    correct_parts = [part.strip() for part in correct_answer.split(',') if part]

    is_correct = False
    if len(user_parts) == len(correct_parts):
        try:
            is_correct = all(abs(float(u) - float(c)) < 1e-9 for u, c in zip(user_parts, correct_parts))
        except (ValueError, TypeError):
            # 如果無法轉換為浮點數，則保持 is_correct 為 False
            pass

    display_answer = ", ".join(correct_parts)

    if is_correct:
        result_text = f"完全正確！答案是 {display_answer}。"
    else:
        result_text = f"答案不正確。正確答案應為：{display_answer}"
    
    return {"correct": is_correct, "result": result_text, "next_question": True}
