import random
import math
from fractions import Fraction

def generate(level=1):
    """
    生成廣義角相關題目。
    包含：
    1. 旋轉量計算廣義角
    2. 象限判斷
    3. 同界角尋找 (最小正同界角)
    4. 機器人移動 (極座標轉直角座標)
    """
    problem_type_choices = [
        'rotation_calculation',
        'quadrant_identification',
        'coterminal_angle_positive',
    ]
    # For higher levels, more complex problems or a wider range of values/types can be introduced.
    if level >= 2:
        problem_type_choices.append('robot_movement_coords')

    problem_type = random.choice(problem_type_choices)
    
    if problem_type == 'rotation_calculation':
        return generate_rotation_calculation_problem()
    elif problem_type == 'quadrant_identification':
        return generate_quadrant_identification_problem()
    elif problem_type == 'coterminal_angle_positive':
        return generate_coterminal_angle_positive_problem()
    elif problem_type == 'robot_movement_coords':
        return generate_robot_movement_coords_problem()

def generate_rotation_calculation_problem():
    """
    生成計算旋轉量後廣義角角度的題目。
    例如：將 360° 平分為 12 等分，若逆時針旋轉 10 份，求此廣義角的角度。
    """
    total_angle = 360
    divisors = [2, 3, 4, 5, 6, 8, 9, 10, 12, 15, 18, 20, 24, 30, 36, 40, 45, 60, 72, 90, 120, 180]
    num_divisions = random.choice(divisors)
    unit_angle = total_angle // num_divisions
    
    steps = random.randint(1, num_divisions * 2 - 1) # 允許超過一圈的旋轉
    direction = random.choice(['逆時針', '順時針'])
    
    angle_value = unit_angle * steps
    
    if direction == '順時針':
        angle_value = -angle_value
        direction_desc = "順時針方向旋轉"
    else:
        direction_desc = "逆時針方向旋轉"
        
    question_text = (
        f"將 ${{total_angle}}\\circ$ 平分為 ${{num_divisions}}$ 等分，以射線 $OA$ 為始邊，<br>"
        f"若 {direction_desc} ${{steps}}$ 份，求此廣義角的角度。"
    )
    correct_answer = str(angle_value)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_quadrant_identification_problem():
    """
    生成判斷廣義角終邊所在象限的題目。
    例如：角 300° 在標準位置時，其終邊落在第幾象限？
    """
    angle_val = random.randint(-1000, 1000)
    
    normalized_angle = angle_val % 360
    if normalized_angle < 0:
        normalized_angle += 360
        
    if normalized_angle == 0 or normalized_angle == 90 or normalized_angle == 180 or normalized_angle == 270:
        quadrant = "象限軸"
    elif 0 < normalized_angle < 90:
        quadrant = "第一象限"
    elif 90 < normalized_angle < 180:
        quadrant = "第二象限"
    elif 180 < normalized_angle < 270:
        quadrant = "第三象限"
    else: # 270 < normalized_angle < 360
        quadrant = "第四象限"
        
    question_text = (
        f"角 ${{angle_val}}\\circ$ 在標準位置時，其終邊落在第幾象限？"
        f"<br>(若終邊落在座標軸上，請回答「象限軸」；請填入如「第一象限」的完整描述)"
    )
    correct_answer = quadrant
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_coterminal_angle_positive_problem():
    """
    生成尋找最小正同界角的題目。
    例如：找出與 -150° 互為同界角且為最小正角的角度。
    """
    initial_angle = random.randint(-1000, 1000)
    
    # 計算與 360° 除法的餘數
    min_positive_coterminal = initial_angle % 360
    
    # 如果餘數為 0 或負數，調整使其在 (0, 360] 範圍內
    if min_positive_coterminal <= 0:
        min_positive_coterminal += 360
    
    # 特殊情況：如果原始角度是 360 的倍數（例如 0, 360, 720, -360），
    # 則 0 是一個同界角，但最小正同界角是 360。
    # initial_angle % 360 得到 0 的情況，將其調整為 360。
    if initial_angle % 360 == 0:
        min_positive_coterminal = 360

    question_text = (
        f"找出與 ${{initial_angle}}\\circ$ 互為同界角且為最小正角的角度。"
    )
    correct_answer = str(int(min_positive_coterminal))
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_robot_movement_coords_problem():
    """
    生成機器人移動問題，將極座標轉換為直角座標。
    例如：機器人輸入指令 [5, 60°] 後，所在位置的坐標為何？
    """
    r_val = random.choice([2, 3, 4, 5, 6, 8, 10])
    # 選擇常見角度，以便學生能利用特殊角知識
    theta_deg = random.choice([0, 30, 45, 60, 90, 120, 135, 150, 180, 210, 225, 240, 270, 300, 315, 330])
    
    # 引入負角度以增加題型變化
    if random.random() < 0.5:
        theta_deg = -theta_deg
    # 避免產生 -0°，若為 0° 則有時替換為 360°
    if theta_deg == 0 and random.random() < 0.5:
        theta_deg = 360 
    
    theta_rad = math.radians(theta_deg)
    
    x_raw = r_val * math.cos(theta_rad)
    y_raw = r_val * math.sin(theta_rad)

    # 先四捨五入到較高精度，再格式化成一位小數，以減少浮點數誤差
    x_rounded = round(x_raw, 5) 
    y_rounded = round(y_raw, 5)

    # 將非常接近零的值設為 0.0，避免顯示如 -1.22e-16
    if abs(x_rounded) < 1e-9: x_rounded = 0.0
    if abs(y_rounded) < 1e-9: y_rounded = 0.0

    # 格式化為一位小數的字串
    x_str = f"{x_rounded:.1f}"
    y_str = f"{y_rounded:.1f}"
    
    question_text = (
        f"機器人從原點出發，面向 $x$ 軸正向，輸入指令 $[{{r_val}}, {{{theta_deg}}}\\circ]$ 後，<br>"
        f"機器人會旋轉 ${{{theta_deg}}}\\circ$ (正逆時針，負順時針)，再往前移動 ${{r_val}}$ 單位。<br>"
        f"請問機器人所在位置的坐標為何？ (答案請以 $(x, y)$ 格式表示，x 和 y 請保留到小數點後一位)"
    )
    correct_answer = f"({x_str}, {y_str})"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    # 標準化使用者答案和正確答案，以進行更穩健的比較
    user_answer_normalized = user_answer.strip().lower().replace(' ', '')
    correct_answer_normalized = correct_answer.strip().lower().replace(' ', '')

    is_correct = False
    feedback_message = ""

    # 1. 嘗試進行簡單的數值比較 (適用於角度計算和同界角問題)
    try:
        user_num = float(user_answer_normalized)
        correct_num = float(correct_answer_normalized)
        if abs(user_num - correct_num) < 1e-6: # 允許浮點數比較時的小誤差
            is_correct = True
    except ValueError:
        pass # 不是簡單數字，繼續檢查其他類型

    # 2. 象限判斷
    if "象限" in correct_answer_normalized or "象限軸" in correct_answer_normalized:
        # 定義映射以靈活處理使用者輸入
        quadrant_map = {
            "第一象限": ["第一象限", "一象限", "第一", "1"],
            "第二象限": ["第二象限", "二象限", "第二", "2"],
            "第三象限": ["第三象限", "三象限", "第三", "3"],
            "第四象限": ["第四象限", "四象限", "第四", "4"],
            "象限軸": ["象限軸", "象限轴", "軸", "轴", "axis", "x軸", "y軸", "x轴", "y轴"],
        }
        
        # 檢查正確答案是否為已知的象限類型之一
        for correct_q_type, allowed_inputs in quadrant_map.items():
            if correct_q_type.lower() == correct_answer_normalized:
                for allowed_input in allowed_inputs:
                    if allowed_input.lower() == user_answer_normalized:
                        is_correct = True
                        break
            if is_correct:
                break # 找到匹配後跳出迴圈
    
    # 如果以上檢查未匹配，嘗試座標比較
    if not is_correct and correct_answer_normalized.startswith('(') and correct_answer_normalized.endswith(')'):
        try:
            # 解析使用者答案的 (x, y) 座標
            user_coords_str = user_answer_normalized.strip('()').split(',')
            user_x = float(user_coords_str[0])
            user_y = float(user_coords_str[1])

            # 解析正確答案的 (x, y) 座標
            correct_coords_str = correct_answer_normalized.strip('()').split(',')
            correct_x = float(correct_coords_str[0])
            correct_y = float(correct_coords_str[1])
            
            # 題目要求保留到小數點後一位，因此將使用者輸入四捨五入至一位小數再進行比較
            # 這是為了確保使用者確實遵循格式要求，同時考慮浮點數誤差。
            user_x_check = round(user_x, 1)
            user_y_check = round(user_y, 1)

            correct_x_check = round(correct_x, 1)
            correct_y_check = round(correct_y, 1)

            if abs(user_x_check - correct_x_check) < 1e-9 and \
               abs(user_y_check - correct_y_check) < 1e-9:
                is_correct = True
        except (ValueError, IndexError):
            pass # 座標格式不正確

    if is_correct:
        feedback_message = f"完全正確！答案是 ${correct_answer}$。"
    else:
        feedback_message = f"答案不正確。正確答案應為：${correct_answer}$"

    return {"correct": is_correct, "result": feedback_message, "next_question": True}