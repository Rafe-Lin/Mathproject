import random
import math

# Helper function for "四捨五入" (round half up)
def round_half_up(n, decimals=0):
    """
    Rounds a number 'n' to 'decimals' decimal places using the "round half up" rule.
    (e.g., 2.5 rounds to 3, 2.4 rounds to 2).
    """
    multiplier = 10 ** decimals
    return math.floor(n * multiplier + 0.5) / multiplier

def generate(level=1):
    """
    生成「利用三角形的兩邊長及其夾角計算面積」相關題目。

    Args:
        level (int): 題目難度等級 (目前未實作差異化，均為基礎難度)。

    Returns:
        dict: 包含題目文字、正確答案（用於顯示）和用於檢查的正確答案。
    """
    side_a = random.randint(5, 15)
    side_b = random.randint(5, 15)
    
    # 增加兩邊長不同的機率
    if random.random() < 0.4:
        side_b = random.randint(5, 15)
        while side_b == side_a: # 確保兩邊長不同
            side_b = random.randint(5, 15)
            
    # 隨機選擇夾角是特殊角還是非特殊角
    is_special_angle = random.choice([True, False])
    
    angle_choices_special = [30, 45, 60, 90, 120, 135, 150]
    # 非特殊角，避免選擇太靠近特殊角的度數，以減少計算混淆
    angle_choices_general = [20, 25, 35, 40, 50, 55, 65, 70, 75, 80, 85, 95, 100, 105, 110, 115, 125, 130, 140, 145, 155, 160]
    
    if is_special_angle:
        angle_c = random.choice(angle_choices_special)
    else:
        angle_c = random.choice(angle_choices_general)

    # 計算三角形的實際面積
    area_float = 0.5 * side_a * side_b * math.sin(math.radians(angle_c))
    
    # 決定答案的四捨五入位數
    rounding_options = [
        {'places': 0, 'text': "四捨五入到整數位"},
        {'places': 1, 'text': "四捨五入到小數點以下第1位"},
        {'places': 2, 'text': "四捨五入到小數點以下第2位"}
    ]
    selected_rounding = random.choice(rounding_options)
    
    decimal_places = selected_rounding['places']
    rounding_text = selected_rounding['text']
    
    # 使用 round_half_up 函數對面積進行四捨五入
    area_rounded = round_half_up(area_float, decimal_places)
    
    # 將四捨五入後的答案格式化為字串，確保小數點位數正確顯示
    correct_answer_str = f"{area_rounded:.{decimal_places}f}"

    # 生成題目文字，使用 LaTeX 語法包裹數學表達式
    question_text = (
        f"求下列各$\\triangle ABC$的面積。<br>"
        f"已知兩邊長為 ${side_a}$ 和 ${side_b}$，夾角為 ${angle_c}$${r'^{\\circ}'}$。<br>"
        f"({rounding_text})"
    )
    
    return {
        "question_text": question_text,
        "answer": correct_answer_str,
        "correct_answer": correct_answer_str
    }

def check(user_answer, correct_answer):
    """
    檢查使用者答案是否正確。

    Args:
        user_answer (str): 使用者輸入的答案。
        correct_answer (str): 系統生成的正確答案。

    Returns:
        dict: 包含檢查結果的字典，`correct` 為布林值，`result` 為回饋文字。
    """
    try:
        user_num = float(user_answer)
        correct_num = float(correct_answer)
        
        # 從 `correct_answer` 字串中判斷所需的小數點位數
        if '.' in correct_answer:
            decimal_places = len(correct_answer.split('.')[1])
        else:
            decimal_places = 0
            
        # 將使用者答案依據題目要求的小數點位數進行「四捨五入」
        rounded_user_num = round_half_up(user_num, decimal_places)
        
        # 比較四捨五入後的使用者答案與正確答案，考慮浮點數誤差
        is_correct = math.isclose(rounded_user_num, correct_num, rel_tol=1e-9, abs_tol=1e-9)
        
        if is_correct:
            result_text = f"完全正確！答案是 ${correct_answer}$。"
        else:
            result_text = f"答案不正確。正確答案應為：${correct_answer}$。"
            
    except ValueError:
        is_correct = False
        result_text = f"請輸入有效的數字格式。正確答案應為：${correct_answer}$。"
    except TypeError: # 處理使用者答案為 None 或空字串等情況
        is_correct = False
        result_text = f"請輸入有效的數字格式。正確答案應為：${correct_answer}$。"
    
    return {"correct": is_correct, "result": result_text, "next_question": True}