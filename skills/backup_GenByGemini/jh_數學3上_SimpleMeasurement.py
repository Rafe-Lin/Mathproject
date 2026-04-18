import random
from fractions import Fraction

def generate(level=1):
    """
    生成「相似三角形應用：間接測量」相關題目。
    包含：
    1. 影子問題
    2. 測量河寬（類型一）
    3. 測量河寬（類型二）
    """
    problem_type = random.choice(['shadow', 'river_width_1', 'river_width_2'])

    if problem_type == 'shadow':
        return generate_shadow_problem()
    elif problem_type == 'river_width_1':
        return generate_river_width_type1_problem()
    else: # river_width_2
        return generate_river_width_type2_problem()

def generate_shadow_problem():
    """
    生成利用影子長度計算物體高度的問題。
    原理：同一時間，太陽光可視為平行光，物體與其影長構成的直角三角形會相似。
    身高 / 影長 = 物高 / 物影長
    """
    name = random.choice(['小妍', '小翊', '小明', '小華'])
    object_type = random.choice(['樹', '電線桿', '建築物', '旗杆'])

    # 產生一個乾淨的比例關係 person_height / person_shadow = a / b
    a = random.randint(2, 5)
    b = random.randint(2, 5)
    # 避免比例為1
    while a == b:
        b = random.randint(2, 5)

    # 根據比例決定身高乘數，讓身高看起來較真實
    if a > b: # 身高 > 影長 (太陽角度較高)
        person_multiplier = random.randint(30, 50) 
    else: # 身高 < 影長 (太陽角度較低)
        person_multiplier = random.randint(40, 60)
    
    person_height_cm = a * person_multiplier
    person_shadow_cm = b * person_multiplier
    
    # 生成物體的影長 (單位: 公尺)，並確保能整除
    object_multiplier = random.randint(2, 6)
    object_shadow_m = b * object_multiplier

    # 計算物體高度 (單位: 公尺)
    # 比例式: person_height / person_shadow = object_height / object_shadow
    # (a * p_mult) / (b * p_mult) = object_height / (b * o_mult)
    # a / b = object_height / (b * o_mult)
    # object_height = (a / b) * (b * o_mult) = a * o_mult
    object_height_m = a * object_multiplier
    
    question_text = f"{name}的身高 {person_height_cm} 公分，如果在某時刻測得他被太陽照出的影長是 {person_shadow_cm} 公分，同時身旁一棵{object_type}的影長是 {object_shadow_m} 公尺，那麼這棵{object_type}的高度為多少公尺？"
    
    correct_answer = str(object_height_m)
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_river_width_type1_problem():
    """
    生成測量河寬的問題（類型一，背對背的兩個相似三角形）。
    原理：△ABC ~ △DEC (AA 相似)
    AB / DE = AC / CD
    """
    name = random.choice(['小妍', '小翊', '小明', '小華'])
    
    # 設定比例 AC/CD，讓計算結果為整數
    ratio = random.randint(2, 5)
    
    # 設定已知長度
    cd_steps = random.randint(3, 10)
    ac_steps = cd_steps * ratio
    de_meters = random.randint(2, 5)
    
    # 計算未知長度 AB (河寬)
    # AB = DE * (AC / CD)
    ab_meters = de_meters * ratio
    
    # 修正：將所有 \overline{XX} 的花括號改為雙花括號 {{XX}}
    question_text = (
        f"小{name}站在岸邊 $A$ 點，望向對岸的一點 $B$ 來測量河寬。他沿著與視線 $\\overline{{AB}}$ 垂直的岸邊走 {ac_steps} 步到達 $C$ 點，"
        f"並在地上做個標記，再繼續往前走 {cd_steps} 步到 $D$ 點。接著，他轉身沿著與岸邊垂直的方向，"
        f"朝離開河的方向前進直到 $E$ 點，此時他發現對岸的 $B$ 點、岸邊的標記 $C$ 點與自己所在的 $E$ 點正好成一直線。"
        f"若小{name}走的每一步距離都相等，且他測得 $\\overline{{DE}}$ 的長度為 {de_meters} 公尺，則河寬 $\\overline{{AB}}$ 為多少公尺？"
    )
    
    correct_answer = str(ab_meters)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_river_width_type2_problem():
    """
    生成測量河寬的問題（類型二，內嵌的兩個相似三角形）。
    原理：△ABE ~ △CDE (AA 相似)
    AB / CD = BE / DE = (BD + DE) / DE
    """
    name = random.choice(['小妍', '小翊', '小明', '小華'])
    
    # 為了產生整數解 x = (CD * BD) / (AB - CD)，進行以下設計
    
    # 產生比例 AB/CD = k/l
    l = random.randint(2, 5)
    k = random.randint(l + 1, l + 4)
    factor = random.randint(1, 4)
    
    cd_meters = l * factor
    ab_meters = k * factor
    
    # 確保 BD 是 (k-l) 的倍數
    bd_multiple = random.randint(2, 5)
    bd_meters = (k - l) * bd_multiple
    
    # 計算河寬 DE (x)
    # x = (l*factor * (k-l)*bd_multiple) / ((k-l)*factor)
    # x = l * bd_multiple
    de_meters = l * bd_multiple
    
    # 修正：將所有 \overline{XX} 的花括號改為雙花括號 {{XX}}
    question_text = (
        f"小{name}利用三角形的相似性質測量河寬 $\\overline{{DE}}$。"
        f"已知 $\\angle B = \\angle CDE = 90^\\circ$ 且 $A, C, E$ 三點共線。"
        f"若他測量出 $\\overline{{AB}} = {ab_meters}$ 公尺、$\\overline{{CD}} = {cd_meters}$ 公尺、"
        f"$\\overline{{BD}} = {bd_meters}$ 公尺，則河寬 $\\overline{{DE}}$ 為多少公尺？"
    )
    
    correct_answer = str(de_meters)
    
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
    
    is_correct = False
    
    try:
        # 嘗試將答案轉換為浮點數進行比較
        user_float = float(user_answer)
        correct_float = float(correct_answer)
        
        # 使用一個小的容錯範圍來比較浮點數
        if abs(user_float - correct_float) < 1e-9:
            is_correct = True
    except ValueError:
        # 如果無法轉換為浮點數，則進行字串比較
        is_correct = (user_answer.upper() == correct_answer.upper())

    if is_correct:
        result_text = f"完全正確！答案是 ${correct_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer}$"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}