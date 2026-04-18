import random

# Constants for correlation types
POSITIVE_CORRELATION = "正相關"
NEGATIVE_CORRELATION = "負相關"
ZERO_CORRELATION = "零相關"

def generate(level=1):
    """
    生成「散布圖」相關題目。
    包含：
    1. 根據給定數據判斷關聯性 (正相關、負相關、零相關)
    2. 根據圖形描述判斷關聯性
    """
    problem_type = random.choice(['correlation_from_data', 'correlation_from_description'])

    if problem_type == 'correlation_from_data':
        return generate_correlation_from_data(level)
    else: # correlation_from_description
        return generate_correlation_from_description(level)

def generate_correlated_data(num_points, correlation_type, level, iteration=0):
    """
    生成具有指定關聯性 (正、負、零) 的 (x, y) 數據對。
    使用遞迴來確保生成的數據確實符合預期的關聯性。
    """
    # 設置防止無限遞迴的上限
    if iteration > 50: 
        # 如果經過多次嘗試仍無法生成，則返回一個簡單的零相關數據，避免卡死
        return [(random.randint(10, 90), random.randint(10, 90)) for _ in range(num_points)]
        
    x_coords_raw = random.sample(range(10, 100), num_points)
    x_coords = sorted(x_coords_raw) # 確保 x 值是唯一的且有序，方便生成 y
    y_coords = []

    # 噪音水平根據難度調整，級別越高，噪音可能越大（相關性越不明顯）
    # 但對於 level=1，我們希望關聯性是清晰的
    noise_amplitude = 5 if level == 1 else 10 # Level 1 noise smaller for clearer correlation
    base_offset_y = random.randint(0, 10) # 讓 y 值與 x 值不總是接近

    if correlation_type == 'positive':
        for x in x_coords:
            # y 值大致隨 x 增加，並添加一些隨機噪音
            y = round(x * random.uniform(0.9, 1.1)) + random.randint(-noise_amplitude, noise_amplitude) + base_offset_y
            y_coords.append(max(10, min(100, y))) # 將 y 值限制在合理範圍內
    elif correlation_type == 'negative':
        # y 值大致隨 x 減少
        # 以 x 的中點為參考，y 值與 x 的距離相反
        mid_x_range = (min(x_coords) + max(x_coords)) / 2.0
        for x in x_coords:
            # 將 x 映射到一個與其相反趨勢的數值
            # 例如，如果 x 增加，(mid_x_range - x) 就會減少
            y = round((mid_x_range - (x - mid_x_range)) * random.uniform(0.9, 1.1)) + random.randint(-noise_amplitude, noise_amplitude) + base_offset_y
            y_coords.append(max(10, min(100, y)))
    else: # zero correlation (零相關)
        # y 值獨立於 x 值隨機生成
        y_coords = random.sample(range(10, 100), num_points)

    data_pairs = list(zip(x_coords, y_coords))
    random.shuffle(data_pairs) # 打亂數據點的順序，使表格顯示更自然

    # 驗證實際生成的數據是否符合預期的關聯性
    mean_x = sum(x for x, _ in data_pairs) / num_points
    mean_y = sum(y for _, y in data_pairs) / num_points
    
    # 計算協方差的分子部分，其符號決定了相關性的方向
    numerator = sum((x - mean_x) * (y - mean_y) for x, y in data_pairs)
    
    is_correct_trend = False
    if correlation_type == 'positive' and numerator > 0:
        is_correct_trend = True
    elif correlation_type == 'negative' and numerator < 0:
        is_correct_trend = True
    # 對於零相關，協方差的絕對值應相對較小
    # 閾值設定為 num_points * noise_amplitude，讓其具有一些容忍度
    elif correlation_type == 'zero' and abs(numerator) < num_points * noise_amplitude * 2: 
        is_correct_trend = True

    if not is_correct_trend:
        # 如果生成的數據不符合預期，則遞迴重新生成
        return generate_correlated_data(num_points, correlation_type, level, iteration + 1)

    return data_pairs

def generate_correlation_from_data(level):
    """
    生成「根據給定數據判斷關聯性」的問題。
    """
    num_points = random.randint(5, 7) # Level 1 使用 5-7 個數據點
    
    # 隨機選擇問題的正確答案（正相關、負相關或零相關）
    correlation_type_choice = random.choice(['positive', 'negative', 'zero'])
    
    # 根據選擇的關聯性生成數據
    data_pairs = generate_correlated_data(num_points, correlation_type_choice, level)

    # 將數據格式化為 Markdown 表格
    labels = [chr(65 + i) for i in range(num_points)] # 標籤為 A, B, C...
    
    table_header = "| 項目 | " + " | ".join(labels) + " |\n"
    table_separator = "|---|" + "---|"*num_points + "|\n"
    
    x_row_values = " | ".join(str(p[0]) for p in data_pairs)
    y_row_values = " | ".join(str(p[1]) for p in data_pairs)

    x_row = f"| $x$ | {x_row_values} |\n"
    y_row = f"| $y$ | {y_row_values} |\n"
    
    table_data = table_header + table_separator + x_row + y_row

    # 生成問題文本
    question_text = (
        f"根據下表中的數據，判斷其散布圖最可能呈現何種關聯性？"
        f"({POSITIVE_CORRELATION}, {NEGATIVE_CORRELATION}, {ZERO_CORRELATION} 其中之一)\n"
        f"{table_data}"
    )
    
    # 設定正確答案
    correct_answer = ""
    if correlation_type_choice == 'positive':
        correct_answer = POSITIVE_CORRELATION
    elif correlation_type_choice == 'negative':
        correct_answer = NEGATIVE_CORRELATION
    else: # zero
        correct_answer = ZERO_CORRELATION
    
    return {
        "question_text": question_text,
        "answer": correct_answer, 
        "correct_answer": correct_answer
    }

def generate_correlation_from_description(level):
    """
    生成「根據圖形描述判斷關聯性」的問題。
    """
    correlation_type_choice = random.choice(['positive', 'negative', 'zero'])
    
    # 根據關聯性類型提供相應的圖形描述
    description_map = {
        'positive': '點大致從左下角延伸到右上角',
        'negative': '點大致從左上角延伸到右下角',
        'zero': '點雜亂無章地分佈，沒有明顯的向上或向下趨勢'
    }
    
    description = description_map[correlation_type_choice]
    
    # 生成問題文本
    question_text = (
        f"在一個散布圖中，{description}。這表示兩個變量之間存在何種關聯性？"
        f"({POSITIVE_CORRELATION}, {NEGATIVE_CORRELATION}, {ZERO_CORRELATION} 其中之一)"
    )
    
    # 設定正確答案
    correct_answer = ""
    if correlation_type_choice == 'positive':
        correct_answer = POSITIVE_CORRELATION
    elif correlation_type_choice == 'negative':
        correct_answer = NEGATIVE_CORRELATION
    else: # zero
        correct_answer = ZERO_CORRELATION
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查使用者答案是否正確。
    考慮多種表達方式 (例如「正」或「正相關」)。
    """
    user_answer_normalized = user_answer.strip().replace(" ", "").upper()
    correct_answer_normalized = correct_answer.strip().replace(" ", "").upper()
    
    is_correct = (user_answer_normalized == correct_answer_normalized)
    
    # 為了更友善的檢查，允許部分關鍵字匹配
    if not is_correct:
        if "正" in user_answer_normalized and "正" in correct_answer_normalized:
            is_correct = True
        elif "負" in user_answer_normalized and "負" in correct_answer_normalized:
            is_correct = True
        elif ("零" in user_answer_normalized or "無" in user_answer_normalized) and "零" in correct_answer_normalized:
            # 允許 "零相關" 或 "無相關"
            is_correct = True

    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}