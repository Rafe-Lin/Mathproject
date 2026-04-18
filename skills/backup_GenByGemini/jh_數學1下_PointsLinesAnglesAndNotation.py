import random
from fractions import Fraction

def generate(level=1):
    """
    生成「點、線、角與標示」相關題目。
    包含：
    1. 角度計算與分類 (銳角、直角、鈍角)
    2. 幾何符號辨識 (線段、射線、直線)
    """
    problem_type = random.choice(['angle_calc', 'notation_id'])
    
    if problem_type == 'angle_calc':
        return generate_angle_calc_problem()
    else:
        return generate_notation_id_problem()

def generate_angle_calc_problem():
    """生成角度計算與分類問題"""
    # 1. 設定基礎角度，確保有一個和為 90 度 (直角) 的組合
    angle1 = random.randint(20, 70)
    angle2 = 90 - angle1
    angle3 = random.randint(20, 70)

    # 假設三個角共用頂點 A，依序為 ∠BAC, ∠CAD, ∠DAE
    angles = {
        'BAC': angle1,
        'CAD': angle2,
        'DAE': angle3
    }
    
    # 2. 隨機選擇一個要計算的組合角
    # 組合1: ∠BAD = ∠BAC + ∠CAD = 90° (直角)
    # 組合2: ∠CAE = ∠CAD + ∠DAE
    # 組合3: ∠BAE = ∠BAC + ∠CAD + ∠DAE
    choice = random.randint(1, 3)
    
    if choice == 1:
        target_angle_name = 'BAD'
        angle_sum = angles['BAC'] + angles['CAD']
    elif choice == 2:
        target_angle_name = 'CAE'
        angle_sum = angles['CAD'] + angles['DAE']
    else: # choice == 3
        target_angle_name = 'BAE'
        angle_sum = angles['BAC'] + angles['CAD'] + angles['DAE']

    # 3. 根據角度和進行分類
    if angle_sum < 90:
        angle_type_str = "銳角"
    elif angle_sum == 90:
        angle_type_str = "直角"
    elif 90 < angle_sum < 180:
        angle_type_str = "鈍角"
    else: # angle_sum == 180
        angle_type_str = "平角"

    # 4. 隨機決定要問「度數」還是「類型」
    ask_type = random.choice(['degree', 'type'])
    
    # 題目共同的已知條件
    # 使用 HTML <br> 換行，並使用 \\circ 產生 LaTeX 的度數符號
    # 修正後：請將所有 $\angle$ 改為 $\\angle$
    givens = f"假設在一個平面上，數個相鄰的角共用頂點 $A$。<br>已知 $\\angle BAC = {angles['BAC']}^\\circ$, $\\angle CAD = {angles['CAD']}^\\circ$, 且 $\\angle DAE = {angles['DAE']}^\\circ$。"
    
    if ask_type == 'degree':
        question_text = f"{givens}<br>請問 $\\angle {target_angle_name}$ 的度數為多少？(請僅填寫數字)"
        correct_answer = str(angle_sum)
    else: # 'type'
        # 修正後：請將所有 $\angle$ 改為 $\\angle$
        question_text = f"{givens}<br>承上，若 $\\angle {target_angle_name} = {angle_sum}^\\circ$，請問此角為銳角、直角、鈍角或平角？"
        correct_answer = angle_type_str

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_notation_id_problem():
    """生成幾何符號辨識問題"""
    # 1. 隨機選擇兩點的代號
    p1, p2 = random.sample(['A', 'B', 'C', 'P', 'Q', 'X', 'Y'], 2)
    point_str = f"{p1}{p2}"
    
    # 2. 定義幾何物件與其 LaTeX 符號的對應
    # 使用安全的 f-string 格式來產生 LaTeX
    obj_data = {
        '線段': f"\\overline{{{point_str}}}",
        '射線': f"\\overrightarrow{{{point_str}}}",
        '直線': f"\\overleftrightarrow{{{point_str}}}"
    }
    
    obj_type = random.choice(list(obj_data.keys()))
    correct_symbol = obj_data[obj_type]
    
    # 3. 根據選擇的物件類型，產生對應的文字描述
    if obj_type == '線段':
        description = f"連接 ${p1}$ 點與 ${p2}$ 點，所形成的{obj_type}"
    elif obj_type == '射線':
        # 射線有方向性，需明確指出端點
        description = f"以 ${p1}$ 點為端點，通過 ${p2}$ 點並朝 ${p2}$ 的方向無限延伸，所形成的{obj_type}"
    else: # '直線'
        description = f"通過 ${p1}$、${p2}$ 兩點，並向兩端無限延伸的{obj_type}"
        
    question_text = f"請寫出(或畫出)以下描述的幾何圖形之正確符號：<br>{description}"
    
    # 正確答案為 LaTeX 格式的字串，供批改時參考
    correct_answer = correct_symbol
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    此函數針對本模組的題型做了適應性調整。
    """
    # 基礎標準化，移除頭尾空白
    user_answer = user_answer.strip()
    
    # 預設為不正確
    is_correct = False

    # 針對角度類型的題目，允許使用者回答「鈍」或「鈍角」
    if "角" in correct_answer:
        is_correct = (user_answer == correct_answer) or (user_answer == correct_answer.replace("角", ""))
    else:
        # 其他情況（度數、符號）先進行字串比對
        is_correct = (user_answer == correct_answer)

    # 如果比對不成功，嘗試進行數值比對 (適用於度數問題)
    if not is_correct:
        try:
            if float(user_answer) == float(correct_answer):
                is_correct = True
        except (ValueError, TypeError):
            # 若轉換失敗，表示非數值題型，維持原比對結果
            pass

    # 根據比對結果產生回饋文字，答案以 LaTeX 格式呈現
    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}
