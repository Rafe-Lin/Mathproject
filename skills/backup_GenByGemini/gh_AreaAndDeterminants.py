import random
from fractions import Fraction
import math
import re

# Helper function to calculate determinant of two 2D vectors
def _calculate_determinant(v1, v2):
    """Calculates the determinant of a 2x2 matrix formed by two vectors."""
    return v1[0] * v2[1] - v1[1] * v2[0]

def generate(level=1):
    """
    生成「二階行列式與面積」相關題目。
    包含：
    1. 由兩個向量計算平行四邊形面積
    2. 已知平行四邊形面積，求向量中未知數 k 的值
    3. 由三點坐標計算三角形面積
    4. 由向量線性組合所形成區域的面積
    """
    
    # Adjust ranges and problem types based on level
    if level == 1:
        coord_range = (-5, 5) # Smaller coordinates for simpler calculations
        k_range = (-3, 3)     # Smaller k values
        xy_max_range = (1, 2) # Smaller factors for linear combination
        problem_types = [
            'parallelogram_area_from_vectors',
            'triangle_area_from_points'
        ]
    else: # level 2 and above
        coord_range = (-8, 8) # Larger coordinates
        k_range = (-7, 7)     # Larger k values
        xy_max_range = (2, 4) # Larger factors for linear combination
        problem_types = [
            'parallelogram_area_from_vectors',
            'parallelogram_area_find_k',
            'triangle_area_from_points',
            'area_from_vector_linear_combination'
        ]
        
    problem_type = random.choice(problem_types)
    
    if problem_type == 'parallelogram_area_from_vectors':
        return _generate_parallelogram_area_from_vectors(coord_range)
    elif problem_type == 'parallelogram_area_find_k':
        return _generate_parallelogram_area_find_k(coord_range, k_range)
    elif problem_type == 'triangle_area_from_points':
        return _generate_triangle_area_from_points(coord_range)
    else: # area_from_vector_linear_combination
        return _generate_area_from_vector_linear_combination(coord_range, xy_max_range)

def _generate_parallelogram_area_from_vectors(coord_range):
    """
    生成「求向量所決定的平行四邊形面積」題目。
    題目範例: 求向量 $\\vec{{a}}=(5,2)$ 與 $\\vec{{b}}=(3,-2)$ 所決定的平行四邊形面積。
    """
    x_min, x_max = coord_range
    while True:
        x1 = random.randint(x_min, x_max)
        y1 = random.randint(x_min, x_max)
        x2 = random.randint(x_min, x_max)
        y2 = random.randint(x_min, x_max)
        
        # 確保向量不平行 (行列式值不為 0)，避免面積為 0 的平凡情況
        determinant = _calculate_determinant((x1, y1), (x2, y2))
        if determinant != 0:
            break
            
    question_text = f"求向量 $\\vec{{a}}=({x1},{y1})$ 與 $\\vec{{b}}=({x2},{y2})$ 所決定的平行四邊形面積。"
    correct_answer = str(abs(determinant))
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def _generate_parallelogram_area_find_k(coord_range, k_range):
    """
    生成「已知平行四邊形面積，求向量中未知數 k」題目。
    題目範例: 已知向量 $\\vec{{a}}=(k,4)$ 與 $\\vec{{b}}=(3,-2)$ 所決定的平行四邊形面積為24，求實數k的值。
    """
    x_min, x_max = coord_range
    k_min, k_max = k_range
    
    while True:
        y1 = random.randint(x_min, x_max)
        x2 = random.randint(x_min, x_max)
        y2 = random.randint(x_min, x_max)
        
        # 確保 y2 不為 0，以便 k 有解
        if y2 == 0:
            continue
        
        # 選擇一個目標 k 值
        k_val = random.randint(k_min, k_max)
        
        # 計算基於這個 k 值所得到的面積
        determinant = _calculate_determinant((k_val, y1), (x2, y2))
        area = abs(determinant)
        
        # 確保面積不為 0
        if area == 0:
            continue
        
        # 解方程式: |k*y2 - y1*x2| = area
        # 情況一: k*y2 - y1*x2 = area  => k1 = (area + y1*x2) / y2
        # 情況二: k*y2 - y1*x2 = -area => k2 = (-area + y1*x2) / y2
        
        k1 = Fraction(area + y1 * x2, y2)
        k2 = Fraction(-area + y1 * x2, y2)
        
        # 篩選，確保解為整數或較簡單的分數，且在合理範圍內
        # 至少有一個解是整數，或兩個解都是簡單分數，且兩個解是不同的。
        if (k1.denominator == 1 and k_min <= k1.numerator <= k_max) or \
           (k2.denominator == 1 and k_min <= k2.numerator <= k_max) or \
           (k1.denominator <= 5 and abs(k1.numerator) <= 20 and 
            k2.denominator <= 5 and abs(k2.numerator) <= 20 and k1 != k2):
            break
            
    k_options = []
    # 將分數轉換為 LaTeX 格式或整數
    if k1.denominator == 1:
        k_options.append(str(k1.numerator))
    else:
        k_options.append(f"\\frac{{{k1.numerator}}}{{{k1.denominator}}}")
        
    if k2 != k1: # 如果有第二個不同的解，則加入
        if k2.denominator == 1:
            k_options.append(str(k2.numerator))
        else:
            k_options.append(f"\\frac{{{k2.numerator}}}{{{k2.denominator}}}")
            
    # 正確答案格式: "k=X 或 k=Y"
    correct_answer_str = " 或 ".join([f"k={k_opt}" for k_opt in k_options])
    
    question_text = f"已知向量 $\\vec{{a}}=(k,{y1})$ 與 $\\vec{{b}}=({x2},{y2})$ 所決定的平行四邊形面積為 ${area}$，求實數 $k$ 的值。"
    
    return {
        "question_text": question_text,
        "answer": correct_answer_str, # 內部檢查使用
        "correct_answer": correct_answer_str # 顯示給用戶的正確答案
    }

def _generate_triangle_area_from_points(coord_range):
    """
    生成「求三點坐標所決定的三角形面積」題目。
    題目範例: 設 A(1, 0), B(3, 2), C(0, 4) 為坐標平面上三點。求 △ABC 的面積。
    """
    x_min, x_max = coord_range
    while True:
        ax, ay = random.randint(x_min, x_max), random.randint(x_min, x_max)
        bx, by = random.randint(x_min, x_max), random.randint(x_min, x_max)
        cx, cy = random.randint(x_min, x_max), random.randint(x_min, x_max)
        
        # 計算向量 AB 和 AC
        vec_AB = (bx - ax, by - ay)
        vec_AC = (cx - ax, cy - ay)
        
        # 確保三點不共線 (行列式值不為 0)，避免面積為 0 的平凡情況
        determinant = _calculate_determinant(vec_AB, vec_AC)
        if determinant != 0:
            break
            
    # 三角形面積是平行四邊形面積的一半
    triangle_area = Fraction(abs(determinant), 2)
    
    # 將分數轉換為 LaTeX 格式或整數
    if triangle_area.denominator == 1:
        correct_answer = str(triangle_area.numerator)
    else:
        correct_answer = f"\\frac{{{triangle_area.numerator}}}{{{triangle_area.denominator}}}"
    
    question_text = (
        f"設 $A({ax}, {ay})$, $B({bx}, {by})$, $C({cx}, {cy})$ 為坐標平面上三點。求 $\\triangle ABC$ 的面積。"
    )
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def _generate_area_from_vector_linear_combination(coord_range, xy_max_range):
    """
    生成「由向量線性組合所形成區域的面積」題目。
    題目範例: 設 A(1, 0), B(3, 2), C(0, 4) 為坐標平面上三點。(2) 已知 $\\vec{{AP}}=x\\vec{{AB}}+y\\vec{{AC}}$ ，其中 $0 \\le x \\le 2$ ， $0 \\le y \\le 2$ ，求所有P點所形成區域的面積。
    """
    x_min, x_max = coord_range
    x_max_factor_min, x_max_factor_max = xy_max_range
    
    while True:
        ax, ay = random.randint(x_min, x_max), random.randint(x_min, x_max)
        bx, by = random.randint(x_min, x_max), random.randint(x_min, x_max)
        cx, cy = random.randint(x_min, x_max), random.randint(x_min, x_max)
        
        vec_AB = (bx - ax, by - ay)
        vec_AC = (cx - ax, cy - ay)
        
        # 確保 vec_AB 和 vec_AC 不平行 (行列式值不為 0)
        original_parallelogram_area = abs(_calculate_determinant(vec_AB, vec_AC))
        if original_parallelogram_area != 0:
            break
            
    X_max = random.randint(x_max_factor_min, x_max_factor_max) # 係數 x 的最大值
    Y_max = random.randint(x_max_factor_min, x_max_factor_max) # 係數 y 的最大值
    
    # 形成的平行四邊形面積為原平行四邊形面積的 X_max * Y_max 倍
    total_area = X_max * Y_max * original_parallelogram_area
    
    question_text = (
        f"設 $A({ax}, {ay})$, $B({bx}, {by})$, $C({cx}, {cy})$ 為坐標平面上三點。<br>"
        f"已知 $\\vec{{AP}}=x\\vec{{AB}}+y\\vec{{AC}}$ ，其中 $0 \\le x \\le {X_max}$ ， $0 \\le y \\le {Y_max}$ ，"
        f"求所有 $P$ 點所形成區域的面積。"
    )
    correct_answer = str(total_area)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer_str):
    """
    檢查使用者答案是否正確。
    user_answer: 使用者輸入的答案，可能是單一數值或包含 "k="。
    correct_answer_str: generate 函數返回的正確答案字符串，可能包含 " 或 " 以及 LaTeX 分數格式。
    """
    user_answer = user_answer.strip().replace("k=", "") # 移除 "k=" 前綴

    # 輔助函數：將字符串（包括分數或 LaTeX 分數）解析為 Fraction 對象
    def parse_fraction_string(s):
        try:
            # 處理 LaTeX 分數格式，例如 \\frac{1}{2}
            if r'\\frac' in s:
                # 使用正則表達式提取分子和分母
                match = re.search(r'\\frac{{?(-?\d+)}}{{?(-?\d+)}', s)
                if match:
                    return Fraction(int(match.group(1)), int(match.group(2)))
            
            # 處理標準分數格式，例如 1/2
            if '/' in s:
                num_str, den_str = s.split('/')
                return Fraction(int(num_str), int(den_str))
            
            # 處理整數
            return Fraction(int(s))
        except (ValueError, ZeroDivisionError, TypeError):
            return None # 解析失敗

    user_val = parse_fraction_string(user_answer)
    
    if user_val is None:
        is_correct = False
        result_text = f"答案格式不正確，請輸入數字或分數。例如：3, -5, 1/2, 或使用LaTeX格式$\\frac{{1}}{{2}}$。"
        return {"correct": is_correct, "result": result_text, "next_question": True}

    # 將 `correct_answer_str` 分割成所有可能的正確值
    # 例如："k=6 或 k=-18" 會變成 ["6", "-18"]
    correct_parts_raw = [part.strip().replace("k=", "") for part in correct_answer_str.split(" 或 ")]
    
    correct_values = []
    for part in correct_parts_raw:
        parsed_val = parse_fraction_string(part)
        if parsed_val is not None:
            correct_values.append(parsed_val)

    is_correct = False
    for val in correct_values:
        if user_val == val:
            is_correct = True
            break
            
    display_correct_answer = correct_answer_str # 顯示給用戶的正確答案保持原始格式
    
    if is_correct:
        result_text = f"完全正確！答案是 ${display_correct_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${display_correct_answer}$"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}