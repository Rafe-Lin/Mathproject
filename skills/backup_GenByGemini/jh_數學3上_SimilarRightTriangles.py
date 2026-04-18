import random
from fractions import Fraction
import math

def generate(level=1):
    """
    生成關於相似直角三角形與三角比的題目。
    - 'basic_ratio': 給定三邊長，求 sin, cos, tan 的值。
    - 'special_45': 45-45-90 特殊直角三角形的邊長計算。
    - 'special_30_60': 30-60-90 特殊直角三角形的邊長計算。
    - 'application': 生活情境應用題。
    """
    problem_type = random.choice([
        'basic_ratio', 
        'special_45', 
        'special_30_60', 
        'application'
    ])
    
    if problem_type == 'basic_ratio':
        return generate_basic_ratio_problem()
    elif problem_type == 'special_45':
        return generate_special_45_problem()
    elif problem_type == 'special_30_60':
        return generate_special_30_60_problem()
    else: # application
        return generate_application_problem()

def format_sqrt(k, n):
    """將 k * sqrt(n) 格式化為 LaTeX 字串。"""
    if n == 1:
        return str(k)
    if k == 0:
        return "0"
    if k == 1:
        return f"\\sqrt{{{n}}}"
    if k == -1:
        return f"-\\sqrt{{{n}}}"
    return f"{k}\\sqrt{{{n}}}"

def generate_basic_ratio_problem():
    """
    生成一個問題，要求在給定直角三角形三邊長的情況下，求出 sin, cos 或 tan 的值。
    """
    # 使用常見的畢氏三元數組
    triples = [(3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25)]
    legs_and_hyp = random.choice(triples)
    leg1, leg2, hyp = legs_and_hyp

    # 隨機分配兩股為角 A 的對邊 (BC) 和鄰邊 (AC)
    if random.random() < 0.5:
        opposite, adjacent = leg1, leg2
    else:
        opposite, adjacent = leg2, leg1

    ratio_type = random.choice(['sin', 'cos', 'tan'])

    question_text = (
        f"在直角△ABC 中，已知 $\\angle C=90^{{\\circ}}$，"
        f"$\\angle A$ 的對邊長 $\\overline{{BC}}={opposite}$，"
        f"$\\angle A$ 的鄰邊長 $\\overline{{AC}}={adjacent}$，"
        f"斜邊長 $\\overline{{AB}}={hyp}$。<br>"
        f"求 ${ratio_type} A$ 的值為何？ (答案請以最簡分數表示，例如 3/5)"
    )

    if ratio_type == 'sin':
        # sin A = 對邊 / 斜邊
        answer_frac = Fraction(opposite, hyp)
    elif ratio_type == 'cos':
        # cos A = 鄰邊 / 斜邊
        answer_frac = Fraction(adjacent, hyp)
    else: # tan
        # tan A = 對邊 / 鄰邊
        answer_frac = Fraction(opposite, adjacent)

    correct_answer = f"{answer_frac.numerator}/{answer_frac.denominator}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_special_45_problem():
    """
    生成一個基於 45°-45°-90° 直角三角形的問題。
    """
    k = random.randint(3, 12)

    # 在 45°-45°-90° 三角形中，兩股等長。
    # 給定一股，求另一股或斜邊。
    known_side_name = random.choice(['AC', 'BC'])
    to_find_options = ['AB']
    if known_side_name == 'AC':
        to_find_options.append('BC')
    else:
        to_find_options.append('AC')
    to_find_name = random.choice(to_find_options)

    question_text = (
        f"在直角△ABC 中，已知 $\\angle C=90^{{\\circ}}$，$\\angle A=45^{{\\circ}}$。"
        f"若邊長 $\\overline{{{known_side_name}}} = {k}$，求邊長 $\\overline{{{to_find_name}}}$ 的長度？<br>"
        f"（若答案含根號，請以例如 $5\\sqrt{{2}}$ 的形式作答）"
    )

    if to_find_name == 'AB':
        # 斜邊 = 股長 * sqrt(2)
        correct_answer = format_sqrt(k, 2)
    else:
        # 另一股與已知股等長
        correct_answer = str(k)
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_special_30_60_problem():
    """
    生成一個基於 30°-60°-90° 直角三角形的問題。
    """
    k = random.randint(3, 10)
    
    # 三邊比例為 1:sqrt(3):2，對應邊長為 k, k*sqrt(3), 2k
    sides = {'short_leg': k, 'long_leg': format_sqrt(k, 3), 'hyp': 2 * k}
    
    # 決定給定哪個整數邊：短股或斜邊
    given_type = random.choice(['short_leg', 'hypotenuse'])
    angle_A = random.choice([30, 60])

    if given_type == 'short_leg':
        given_val = k
        if angle_A == 30:
            # 短股是角 A 的對邊
            known_side_name = 'BC'
        else: # angle_A == 60
            # 短股是角 A 的鄰邊
            known_side_name = 'AC'
        
        # 決定要求哪一邊
        to_find_type = random.choice(['long_leg', 'hypotenuse'])
        if to_find_type == 'long_leg':
            correct_answer = sides['long_leg']
            to_find_name = 'AC' if angle_A == 30 else 'BC'
        else: # hypotenuse
            correct_answer = str(sides['hyp'])
            to_find_name = 'AB'

    else: # 給定斜邊
        given_val = 2 * k
        known_side_name = 'AB'

        # 決定要求哪一邊
        to_find_type = random.choice(['short_leg', 'long_leg'])
        if to_find_type == 'short_leg':
            correct_answer = str(sides['short_leg'])
            to_find_name = 'BC' if angle_A == 30 else 'AC'
        else: # long_leg
            correct_answer = sides['long_leg']
            to_find_name = 'AC' if angle_A == 30 else 'BC'

    question_text = (
        f"在直角△ABC 中，已知 $\\angle C=90^{{\\circ}}$，$\\angle A={angle_A}^{{\\circ}}$。"
        f"若邊長 $\\overline{{{known_side_name}}} = {given_val}$，求邊長 $\\overline{{{to_find_name}}}$ 的長度？<br>"
        f"（若答案含根號，請以例如 $5\\sqrt{{3}}$ 的形式作答）"
    )

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_application_problem():
    """
    生成使用特殊直角三角形的生活應用問題。
    """
    angle = random.choice([30, 45, 60])
    k = random.randint(3, 8)
    
    problem_template = random.choice(['escalator', 'tree_height'])

    if problem_template == 'escalator':
        # 情境：電扶梯的長度與高度
        if angle == 30:
            vertical_height = k
            escalator_length = 2 * k
            question_text = (
                f"某商場設置一座電扶梯，其傾斜角為 $30^{{\\circ}}$。"
                f"已知一樓與二樓間的垂直高度為 ${vertical_height}$ 公尺，"
                f"則此電扶梯的長度為多少公尺？"
            )
            correct_answer = str(escalator_length)
        elif angle == 60:
            horizontal_dist = k
            escalator_length = 2 * k
            question_text = (
                f"一座無障礙坡道的傾斜角為 $60^{{\\circ}}$ (此為示意角度，非真實坡度)。"
                f"若坡道的水平距離為 ${horizontal_dist}$ 公尺，"
                f"則此坡道的長度為多少公尺？"
            )
            correct_answer = str(escalator_length)
        else: # angle == 45
            vertical_height = k
            escalator_length = format_sqrt(k, 2)
            question_text = (
                f"為校慶活動，從校舍頂樓到地面設置一條三角旗繩，與地面夾角為 $45^{{\\circ}}$。"
                f"已知校舍高度為 ${vertical_height}$ 公尺，"
                f"試求出此三角旗繩的長度為多少公尺？<br>"
                f"（若答案含根號，請以例如 $5\\sqrt{{2}}$ 的形式作答）"
            )
            correct_answer = escalator_length

    else: # tree_height
        # 情境：測量樹高
        if angle == 30:
            height = k
            distance = format_sqrt(k, 3)
            question_text = (
                f"小華想測量一棵樹的高度，他發現當他看樹頂的仰角為 $30^{{\\circ}}$ 時，"
                f"已知樹的高度為 ${height}$ 公尺，請問小華離樹的水平距離是多少公尺？<br>"
                f"（若答案含根號，請以例如 $5\\sqrt{{3}}$ 的形式作答）"
            )
            correct_answer = distance
        elif angle == 60:
            distance = k
            height = format_sqrt(k, 3)
            question_text = (
                f"小明在離一棵樹的樹根 ${distance}$ 公尺遠的地方，測得樹頂的仰角為 $60^{{\\circ}}$。"
                f"假設小明的身高可忽略不計，求樹的高度是多少公尺？<br>"
                f"（若答案含根號，請以例如 $5\\sqrt{{3}}$ 的形式作答）"
            )
            correct_answer = height
        else: # angle == 45
            distance = k
            height = k
            question_text = (
                f"小美在放風箏，當風箏線拉直時，線與地面的夾角為 $45^{{\\circ}}$。"
                f"若風箏在地面的垂直投影點與小美的距離為 ${distance}$ 公尺，"
                f"求風箏的飛行高度為多少公尺？"
            )
            correct_answer = str(height)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查使用者答案是否正確。
    可處理整數、分數及包含根號的答案。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    is_correct = False

    # 狀況 1: 答案包含根號 (例如 "5\\sqrt{3}")
    if '\\sqrt' in correct_answer:
        # 將兩種字串標準化以便比較，允許不同的書寫方式
        # 例如 "5sqrt(3)", "5 sqrt 3", "5√3"
        def normalize_sqrt(s):
            return s.lower().replace(' ', '').replace('\\sqrt', 'sqrt').replace('√', 'sqrt').replace('{', '(').replace('}', ')').replace('*', '')
        
        is_correct = normalize_sqrt(user_answer) == normalize_sqrt(correct_answer)

    # 狀況 2: 答案是分數 (例如 "8/17")
    elif '/' in correct_answer:
        try:
            # 將答案視為 Fraction 物件來比較，可處理未約分的情況 (例如 4/8 vs 1/2)
            user_frac = Fraction(user_answer)
            correct_frac = Fraction(correct_answer)
            is_correct = (user_frac == correct_frac)
        except (ValueError, ZeroDivisionError):
            is_correct = False

    # 狀況 3: 答案是純數字
    else:
        try:
            # 以浮點數比較，允許小數點表示法 (例如 "7.0" 對 "7")
            is_correct = abs(float(user_answer) - float(correct_answer)) < 1e-9
        except ValueError:
            # 若轉換失敗，退回字串比較
            is_correct = (user_answer.lower() == correct_answer.lower())

    # 提供回饋
    if is_correct:
        result_text = f"完全正確！答案是 ${correct_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer}$"
    
    return {"correct": is_correct, "result": result_text, "next_question": True}