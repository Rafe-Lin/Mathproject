import random
import math
import re

def generate(level=1):
    """
    生成「直角坐標平面上兩點距離」相關題目。
    包含：
    1. 與坐標軸平行的特殊情況 (水平線)
    2. 與坐標軸平行的特殊情況 (鉛垂線)
    3. 任意兩點的通用情況 (畢氏定理)
    """
    # 權重分配：特殊情況佔 30%，通用情況佔 70%
    problem_type = random.choices(
        ['horizontal', 'vertical', 'general'],
        weights=[15, 15, 70],
        k=1
    )[0]

    if problem_type == 'horizontal':
        return generate_horizontal_problem()
    elif problem_type == 'vertical':
        return generate_vertical_problem()
    else:
        return generate_general_problem()

def generate_horizontal_problem():
    """
    生成兩點在水平線上的距離問題。
    """
    y = random.randint(-10, 10)
    x1 = random.randint(-15, 15)
    x2 = x1
    while x2 == x1:
        x2 = random.randint(-15, 15)

    # 隨機打亂點的順序
    points = [(x1, y), (x2, y)]
    random.shuffle(points)
    (px1, py1), (px2, py2) = points

    point_a_str = f"A({px1}, {py1})"
    point_b_str = f"B({px2}, {py2})"

    # 修正：確保變數包在 { } 內，且 LaTeX 格式完整
    question_text = f"求出直角坐標平面上兩點 ${point_a_str}$ 與 ${point_b_str}$ 之間的距離。"
    correct_answer = str(abs(x1 - x2))

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_vertical_problem():
    """
    生成兩點在鉛垂線上的距離問題。
    """
    x = random.randint(-10, 10)
    y1 = random.randint(-15, 15)
    y2 = y1
    while y2 == y1:
        y2 = random.randint(-15, 15)

    # 隨機打亂點的順序
    points = [(x, y1), (x, y2)]
    random.shuffle(points)
    (px1, py1), (px2, py2) = points

    point_c_str = f"C({px1}, {py1})"
    point_d_str = f"D({px2}, {py2})"

    # 修正：確保變數包在 { } 內
    question_text = f"求出直角坐標平面上兩點 ${point_c_str}$ 與 ${point_d_str}$ 之間的距離。"
    correct_answer = str(abs(y1 - y2))

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_general_problem():
    """
    生成任意兩點的距離問題，可能為整數或根式答案。
    """
    # 約 40% 的機率產生整數答案 (畢氏三元數)
    if random.random() < 0.4:
        pythagorean_triples = [(3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25)]
        delta_x, delta_y, dist = random.choice(pythagorean_triples)

        if random.choice([True, False]):
            delta_x, delta_y = delta_y, delta_x

        delta_x *= random.choice([-1, 1])
        delta_y *= random.choice([-1, 1])

        x1 = random.randint(-10, 10)
        y1 = random.randint(-10, 10)
        x2 = x1 + delta_x
        y2 = y1 + delta_y

        correct_answer = str(dist)
        answer_format_for_user = correct_answer

    else: # 約 60% 的機率產生根式答案
        # 確保 x, y 座標皆不相同
        while True:
            x1 = random.randint(-10, 10)
            y1 = random.randint(-10, 10)
            x2 = random.randint(-10, 10)
            y2 = random.randint(-10, 10)
            if x1 != x2 and y1 != y2:
                break

        distance_sq = (x1 - x2)**2 + (y1 - y2)**2
        
        # 檢查是否意外產生了完全平方數
        sqrt_dist = math.isqrt(distance_sq)
        if sqrt_dist * sqrt_dist == distance_sq:
            correct_answer = str(sqrt_dist)
            answer_format_for_user = correct_answer
        else:
            correct_answer = f"\\sqrt{{{distance_sq}}}"
            answer_format_for_user = f"sqrt({distance_sq})"

    # 隨機選擇點的標籤
    labels = random.sample(['A', 'B', 'C', 'D', 'P', 'Q', 'M', 'N'], 2)
    label1, label2 = labels[0], labels[1]

    # 隨機打亂點的順序
    points = [(x1, y1), (x2, y2)]
    random.shuffle(points)
    (px1, py1), (px2, py2) = points

    point1_str = f"{label1}({px1}, {py1})"
    point2_str = f"{label2}({px2}, {py2})"

    # --- 關鍵修正區塊 ---
    # 修正前：... $point2_str$ ... (這會直接印出變數名)
    # 修正後：... ${point2_str}$ ... (正確印出數值)
    # 另外將 \n 改為 <br> 以利網頁顯示
    question_text = f"若 ${point1_str}$、${point2_str}$ 為直角坐標平面上的兩點，則 $\\overline{{{label1}{label2}}}$ 的長度為何？"

    if correct_answer.startswith('\\sqrt'):
        question_text += "<br>(答案若為根式，請用 `sqrt(數字)` 的格式作答)"

    return {
        "question_text": question_text,
        "answer": answer_format_for_user,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確，能處理整數與根式 (sqrt) 格式。
    """
    user_answer = user_answer.strip().replace(" ", "").lower()
    correct_answer = correct_answer.strip()
    is_correct = False

    if correct_answer.startswith('\\sqrt{'):
        # 正確答案是根式，例如：\sqrt{202}
        match_correct = re.search(r'\\sqrt\{(\d+)\}', correct_answer)
        if match_correct:
            correct_val_str = match_correct.group(1)
            
            # 使用者可能輸入：sqrt(202), sqrt{202}, sqrt202, \sqrt{202}
            # 用正規表示式簡單地從使用者答案中提取數字
            match_user = re.search(r'(\d+)', user_answer)
            if match_user:
                user_val_str = match_user.group(1)
                if user_val_str == correct_val_str:
                    is_correct = True
    else:
        # 正確答案是數字
        try:
            # 進行數值比較，以處理 '5' vs '5.0' 的情況
            if float(user_answer) == float(correct_answer):
                is_correct = True
        except (ValueError, TypeError):
            # 如果轉換失敗，退回到字串比對
            if user_answer.upper() == correct_answer.upper():
                is_correct = True

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    
    return {"correct": is_correct, "result": result_text, "next_question": True}