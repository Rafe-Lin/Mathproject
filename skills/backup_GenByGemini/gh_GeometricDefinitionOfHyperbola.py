import random
import math
from fractions import Fraction
from decimal import Decimal, getcontext

# Set precision for decimal calculations to avoid floating point issues
getcontext().prec = 20

def calculate_distance(p1, p2):
    """Calculates the Euclidean distance between two points."""
    x1, y1 = p1
    x2, y2 = p2
    return Decimal(math.sqrt(Decimal((x2 - x1)**2) + Decimal((y2 - y1)**2)))

def generate(level=1):
    """
    生成「雙曲線的幾何定義」相關題目。
    包含兩種題型：
    1. 判斷點是否在雙曲線上：給定兩焦點和一個雙曲線上的點P，判斷哪個候選點也在雙曲線上。
    2. 計算共軛軸長：已知雙曲線的焦距和貫軸長，計算共軛軸長。
    """
    problem_type = random.choice(['check_point_on_hyperbola', 'find_conjugate_axis'])
    
    if problem_type == 'check_point_on_hyperbola':
        return generate_check_point_on_hyperbola_problem()
    else: # find_conjugate_axis
        return generate_find_conjugate_axis_problem()

def generate_check_point_on_hyperbola_problem():
    """
    生成「判斷點是否在雙曲線上」的題目。
    - 給定兩個焦點 F1, F2。
    - 給定一個在雙曲線上點 P。
    - 給定數個候選點 (A, B, C)，其中一個也可能在雙曲線上。
    - 要求判斷哪個候選點也在雙曲線上。
    """
    
    # 1. 生成焦點 F1, F2
    c_val = random.randint(3, 7) # 焦點距離中心點的距離，確保 c 至少為 3
    center_x = random.randint(-2, 2)
    center_y = random.randint(-2, 2)

    is_horizontal_foci = (random.random() < 0.5)
    if is_horizontal_foci: # 水平排列的焦點，例如 F1(-c, 0), F2(c, 0)
        F1 = (center_x - c_val, center_y)
        F2 = (center_x + c_val, center_y)
        focal_axis_value = center_y # 焦軸的 y 座標
    else: # 垂直排列的焦點，例如 F1(0, -c), F2(0, c)
        F1 = (center_x, center_y - c_val)
        F2 = (center_x, center_y + c_val)
        focal_axis_value = center_x # 焦軸的 x 座標

    # 2. 生成一個在雙曲線上點 P
    # P 點不能是焦點，也不能在焦軸上，以確保反射點與 P 點不同
    P_coords = None
    while True:
        if is_horizontal_foci:
            px = random.randint(center_x - c_val - 3, center_x + c_val + 3)
            # 確保 py 不等於 center_y (即不在焦軸上)
            py = center_y + random.randint(3, 6) * random.choice([-1, 1]) 
        else: # Vertical foci
            # 確保 px 不等於 center_x (即不在焦軸上)
            px = center_x + random.randint(3, 6) * random.choice([-1, 1]) 
            py = random.randint(center_y - c_val - 3, center_y + c_val + 3)
        
        current_P_coords = (px, py)

        # 檢查 P 點是否是焦點，或是否落在焦軸上
        is_on_focal_axis = (current_P_coords[1] == focal_axis_value if is_horizontal_foci else current_P_coords[0] == focal_axis_value)
        if current_P_coords != F1 and current_P_coords != F2 and not is_on_focal_axis:
            P_coords = current_P_coords
            break

    # 計算距離差的絕對值，這就是雙曲線的常數 (2a)
    dist_P_F1 = calculate_distance(P_coords, F1)
    dist_P_F2 = calculate_distance(P_coords, F2)
    two_a = abs(dist_P_F1 - dist_P_F2)

    # 3. 生成候選點 A, B, C
    candidate_labels = ['A', 'B', 'C']
    random.shuffle(candidate_labels) # 隨機分配正確答案的標籤
    
    points_data = {} # 儲存點的座標
    candidate_points_coords = [] # 儲存已生成的候選點座標，用於避免重複

    # 生成正確的點 (其中一個候選點)
    # 通過將 P 點反射到焦軸的另一側來獲得另一個在雙曲線上的點
    correct_candidate_label = candidate_labels[0]
    if is_horizontal_foci: # 水平焦軸，反射 y 座標
        correct_candidate_coords = (P_coords[0], Decimal(2 * focal_axis_value) - P_coords[1])
    else: # 垂直焦軸，反射 x 座標
        correct_candidate_coords = (Decimal(2 * focal_axis_value) - P_coords[0], P_coords[1])
    
    candidate_points_coords.append(correct_candidate_coords)
    points_data[correct_candidate_label] = correct_candidate_coords

    # 生成兩個不正確的點
    for i in range(1, 3):
        label = candidate_labels[i]
        while True:
            # 隨機生成點的座標
            test_x = random.randint(center_x - c_val - 5, center_x + c_val + 5)
            test_y = random.randint(center_y - c_val - 5, center_y + c_val + 5)
            test_coords = (test_x, test_y)

            # 確保不與 P 點或任何已生成的候選點重複
            if test_coords == P_coords or test_coords in candidate_points_coords:
                continue

            # 計算此測試點到兩焦點的距離差的絕對值
            dist_test_F1 = calculate_distance(test_coords, F1)
            dist_test_F2 = calculate_distance(test_coords, F2)
            test_two_a = abs(dist_test_F1 - dist_test_F2)

            # 判斷是否與正確的 two_a 相近 (使用一個小容忍度來比較浮點數)
            # 如果差值顯著不同，則為不正確的點
            if abs(test_two_a - two_a) > Decimal('0.001'): 
                candidate_points_coords.append(test_coords)
                points_data[label] = test_coords
                break
    
    # 構築問題文本 (使用 LaTeX 格式)
    f1_str = f"$F_{{1}}({F1[0]}, {F1[1]})$"
    f2_str = f"$F_{{2}}({F2[0]}, {F2[1]})$"
    p_str = f"$P({P_coords[0]}, {P_coords[1]})$"
    
    candidate_strs = []
    # 通常按字母順序呈現選項
    sorted_labels = sorted(points_data.keys())
    for label in sorted_labels: 
        coords = points_data[label]
        candidate_strs.append(f"${label}({coords[0]}, {coords[1]})$")
        
    question_text = (
        f"已知一雙曲線以 {f1_str} 和 {f2_str} 為焦點，且通過點 {p_str}。"
        f"請問在下列哪些點中，有哪一個點也在此雙曲線上？"
        f"選項：{', '.join(candidate_strs)} (請填入點的代號)"
    )
    
    correct_answer = correct_candidate_label

    return {
        "question_text": question_text,
        "answer": correct_answer, # 這裡的 'answer' 欄位是為了範例格式，實際教學軟體可能只用 'correct_answer'
        "correct_answer": correct_answer
    }

def generate_find_conjugate_axis_problem():
    """
    生成「根據雙曲線的焦距和貫軸長，計算共軛軸長」的題目。
    利用雙曲線的基本關係式：$c^2 = a^2 + b^2$。
    其中 $2c$ 是焦距，$2a$ 是貫軸長，$2b$ 是共軛軸長。
    """
    
    # 1. 生成焦距 (兩焦點間距離) 2c
    # 確保 c > a
    c_val = random.randint(4, 9) # c 必須大於 a，且至少為 4
    two_c_val = 2 * c_val 
    
    # 2. 生成貫軸長 2a
    # 確保 a < c
    a_val = random.randint(2, c_val - 1)
    two_a_val = 2 * a_val 

    # 3. 計算共軛軸長 2b
    # 根據 $c^2 = a^2 + b^2$，可得 $b^2 = c^2 - a^2$
    b_squared = Decimal(c_val**2) - Decimal(a_val**2)
    b_val = Decimal(math.sqrt(b_squared))
    two_b_val = Decimal(2) * b_val # 共軛軸長
    
    question_text = (
        f"已知一雙曲線的兩焦點距離為 ${two_c_val}$ 單位，且其貫軸長為 ${two_a_val}$ 單位。"
        f"請問該雙曲線的共軛軸長為多少？(答案請四捨五入至小數點後兩位)"
    )

    # 將答案四捨五入至小數點後兩位
    correct_answer_decimal = two_b_val.quantize(Decimal('0.01'))
    correct_answer = str(correct_answer_decimal) # 將 Decimal 轉換為字串

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查使用者答案是否正確。
    """
    is_correct = False
    feedback = ""

    # 嘗試將答案轉換為 Decimal 進行數值比較 (適用於計算題)
    try:
        user_dec = Decimal(user_answer.strip())
        correct_dec = Decimal(correct_answer.strip())
        
        # 允許一個小的容忍度來比較浮點數，特別是對於四捨五入後的答案
        if abs(user_dec - correct_dec) < Decimal('0.02'): # 容忍度 0.02 涵蓋小數點後兩位的四捨五入誤差
            is_correct = True
            feedback = f"完全正確！答案是 ${correct_answer}$。"
        else:
            feedback = f"答案不正確。正確答案應為：${correct_answer}$"
    except Exception: # 如果使用者答案不是有效的數字 (例如，點的代號 'A')
        user_ans_processed = user_answer.strip().upper()
        correct_ans_processed = correct_answer.strip().upper()
        
        if user_ans_processed == correct_ans_processed:
            is_correct = True
            feedback = f"完全正確！答案是 ${correct_answer}$。"
        else:
            feedback = f"答案不正確。正確答案應為：${correct_answer}$"

    return {"correct": is_correct, "result": feedback, "next_question": True}