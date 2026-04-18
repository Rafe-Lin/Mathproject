import random
import math
import re

def generate(level=1):
    """
    生成「多邊形的內角與外角」相關題目。
    包含：
    1. 根據邊數求內角和與可分三角形數
    2. 根據內角和求邊數與可分三角形數
    3. 正多邊形，已知邊數求單一內角
    4. 正多邊形，已知邊數求單一外角
    5. 正多邊形，已知單一內角求邊數
    6. 正多邊形，已知單一外角求邊數
    7. 正多邊形，內外角關係求邊數
    """
    problem_types = [
        'sum_of_angles_from_sides',
        'sides_from_sum_of_angles',
        'regular_gon_interior_angle',
        'regular_gon_exterior_angle',
        'regular_gon_n_from_interior_angle',
        'regular_gon_n_from_exterior_angle',
        'regular_gon_int_ext_ratio'
    ]
    problem_type = random.choice(problem_types)

    if problem_type == 'sum_of_angles_from_sides':
        return generate_sum_of_angles_from_sides()
    elif problem_type == 'sides_from_sum_of_angles':
        return generate_sides_from_sum_of_angles()
    elif problem_type == 'regular_gon_interior_angle':
        return generate_regular_gon_interior_angle()
    elif problem_type == 'regular_gon_exterior_angle':
        return generate_regular_gon_exterior_angle()
    elif problem_type == 'regular_gon_n_from_interior_angle':
        return generate_regular_gon_n_from_interior_angle()
    elif problem_type == 'regular_gon_n_from_exterior_angle':
        return generate_regular_gon_n_from_exterior_angle()
    elif problem_type == 'regular_gon_int_ext_ratio':
        return generate_regular_gon_int_ext_ratio()

def get_valid_n_for_regular_polygon():
    """
    選擇一個適合作為正多邊形邊數 n 的值。
    這些值是 360 的因數，確保內角和外角為整數。
    """
    # 選擇常見且角度為整數的邊數
    return random.choice([3, 4, 5, 6, 8, 9, 10, 12, 15, 18, 20, 24, 30, 36, 40, 45])

# --- 題目生成函數 ---

def generate_sum_of_angles_from_sides():
    """
    題目類型：給定邊數 m，求內角和及可分成 n 個三角形。
    例如：「一個 12 邊形中，由一頂點向其他頂點畫對角線可分成 n 個三角形，且內角和為 1800°，則 m＝？n＝？」
    """
    m = random.randint(5, 15) # 邊數
    n_triangles = m - 2
    sum_angles = n_triangles * 180

    question_text = f"一個凸 ${m}$ 邊形，由其中一個頂點畫對角線，可將此多邊形分成幾個三角形？其內角和為多少度？"
    
    # `answer` 是供 `check` 函數內部比對的簡潔答案格式
    answer_for_check = f"{n_triangles}, {sum_angles}"
    # `correct_answer` 是供前端顯示的完整答案格式 (含 LaTeX)
    display_answer = f"可分成 ${n_triangles}$ 個三角形，內角和為 ${sum_angles}\\\\circ$"

    return {
        "question_text": question_text,
        "answer": answer_for_check,
        "correct_answer": display_answer
    }

def generate_sides_from_sum_of_angles():
    """
    題目類型：給定內角和，求邊數 m 及可分成 n 個三角形。
    """
    n_triangles = random.randint(3, 10) # 可分三角形數
    m = n_triangles + 2 # 邊數
    sum_angles = n_triangles * 180

    question_text = f"一個凸多邊形的內角和為 ${sum_angles}\\\\circ$，則此多邊形為幾邊形？由其中一個頂點畫對角線，可將此多邊形分成幾個三角形？"
    answer_for_check = f"{m}, {n_triangles}"
    display_answer = f"此多邊形為 ${m}$ 邊形，可分成 ${n_triangles}$ 個三角形"

    return {
        "question_text": question_text,
        "answer": answer_for_check,
        "correct_answer": display_answer
    }

def generate_regular_gon_interior_angle():
    """
    題目類型：正 n 邊形，已知 n 求每個內角。
    例如：「新版硬幣採用正十二邊形的設計，每一個內角為多少度？」
    """
    n = get_valid_n_for_regular_polygon()
    interior_angle = ((n - 2) * 180) // n

    question_text = f"一個正 ${n}$ 邊形的每一個內角為多少度？"
    answer_for_check = str(interior_angle)
    display_answer = f"${interior_angle}\\\\circ$"

    return {
        "question_text": question_text,
        "answer": answer_for_check,
        "correct_answer": display_answer
    }

def generate_regular_gon_exterior_angle():
    """
    題目類型：正 n 邊形，已知 n 求每個外角。
    """
    n = get_valid_n_for_regular_polygon()
    exterior_angle = 360 // n

    question_text = f"一個正 ${n}$ 邊形的每一個外角為多少度？"
    answer_for_check = str(exterior_angle)
    display_answer = f"${exterior_angle}\\\\circ$"

    return {
        "question_text": question_text,
        "answer": answer_for_check,
        "correct_answer": display_answer
    }

def generate_regular_gon_n_from_interior_angle():
    """
    題目類型：正多邊形，已知每個內角求邊數 n。
    例如：「若一正 n 邊形的每一個內角為 156°，則 n 是多少？」
    """
    n = get_valid_n_for_regular_polygon()
    interior_angle = ((n - 2) * 180) // n

    question_text = f"若一正多邊形的每一個內角為 ${interior_angle}\\\\circ$，則此正多邊形是幾邊形？"
    answer_for_check = str(n)
    display_answer = f"${n}$ 邊形"

    return {
        "question_text": question_text,
        "answer": answer_for_check,
        "correct_answer": display_answer
    }

def generate_regular_gon_n_from_exterior_angle():
    """
    題目類型：正多邊形，已知每個外角求邊數 n。
    """
    n = get_valid_n_for_regular_polygon()
    exterior_angle = 360 // n

    question_text = f"若一正多邊形的每一個外角為 ${exterior_angle}\\\\circ$，則此正多邊形是幾邊形？"
    answer_for_check = str(n)
    display_answer = f"${n}$ 邊形"

    return {
        "question_text": question_text,
        "answer": answer_for_check,
        "correct_answer": display_answer
    }

def generate_regular_gon_int_ext_ratio():
    """
    題目類型：正多邊形，已知內角度數是外角度數的 k 倍，求邊數 n。
    例如：「若正 n 邊形的一個內角度數恰好為一個外角度數的 3 倍，則 n 是多少？」
    關係：n = 2 * (1 + k)
    """
    # 選擇 k 值，使得 n = 2 * (1 + k) 是一個有效的正多邊形邊數 (在 get_valid_n_for_regular_polygon 列表中)
    # k = n/2 - 1
    # 根據 get_valid_n_for_regular_polygon 列表計算出對應的整數 k 值
    # [1, 2, 3, 4, 5, 8, 9, 11, 14, 17, 19]
    k = random.choice([1, 2, 3, 4, 5, 8, 9, 11, 14, 17, 19])
    n = 2 * (1 + k) # 計算邊數 n

    question_text = f"若一正多邊形的一個內角度數恰好為一個外角度數的 ${k}$ 倍，則此正多邊形是幾邊形？"
    answer_for_check = str(n)
    display_answer = f"${n}$ 邊形"

    return {
        "question_text": question_text,
        "answer": answer_for_check,
        "correct_answer": display_answer
    }

def check(user_answer, correct_answer_for_check):
    """
    檢查使用者答案是否正確。
    `correct_answer_for_check` 參數接收的是 `generate` 函數中 `answer` 欄位的值。
    """
    user_answer_cleaned = user_answer.strip().lower()
    correct_answer_for_check_cleaned = correct_answer_for_check.strip().lower()

    is_correct = False
    
    # 輔助函數：解析答案字符串，提取數字列表
    def parse_answer_string(s):
        # 移除常見的非數字字符和單位詞，以便純數字比對
        s = s.replace('°', '').replace('度', '').replace('邊形', '').replace('個三角形', '').replace(' ', '').replace('m=', '').replace('n=', '')
        # 使用逗號或中文逗號分割，處理多個答案的情況
        parts = re.split(r'[,，]', s)
        parsed_values = []
        for part in parts:
            # 使用正則表達式尋找可能包含符號的數字 (例如 -12.5)
            match = re.search(r'[-]?\d+(\.\d+)?', part)
            if match:
                try:
                    parsed_values.append(float(match.group(0)))
                except ValueError:
                    pass # 如果轉換失敗，則跳過此部分
        return parsed_values

    user_values = parse_answer_string(user_answer_cleaned)
    correct_values = parse_answer_string(correct_answer_for_check_cleaned)

    # 比對解析出的數字列表
    if user_values and correct_values and len(user_values) == len(correct_values):
        all_match = True
        for u, c in zip(user_values, correct_values):
            # 浮點數比對使用小誤差範圍
            if abs(u - c) > 1e-6:
                all_match = False
                break
        is_correct = all_match
    # 如果解析失敗或數量不符，則 is_correct 保持為 False

    # 根據比對結果生成回饋訊息。
    # 這裡的 `correct_answer_for_check` 會被直接用在顯示中，
    # 因此 generate 函數的 `answer` 字段應包含可讀性較好的數字或簡潔文字。
    result_text = f"完全正確！答案是 ${correct_answer_for_check}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer_for_check}$"
    
    return {"correct": is_correct, "result": result_text, "next_question": True}