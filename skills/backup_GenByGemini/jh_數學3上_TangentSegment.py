import random
from fractions import Fraction
import math

def generate(level=1):
    """
    生成「圓的切線段」相關題目。
    包含：
    1. 單一切線段與畢氏定理
    2. 兩切線段與特殊直角三角形 (30-60-90)
    3. 利用面積求兩切點連線段長
    """
    problem_type = random.choice(['pythagorean', 'special_triangle', 'chord_length'])

    if problem_type == 'pythagorean':
        return generate_pythagorean_problem()
    elif problem_type == 'special_triangle':
        return generate_special_triangle_problem()
    else:  # 'chord_length'
        return generate_chord_length_problem()

def generate_pythagorean_problem():
    """
    題型：利用半徑垂直切線，構成直角三角形，使用畢氏定理解題。
    隨機求股（半徑、切線段長）或斜邊（圓心到外部點的距離）。
    """
    triples = [(3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25)]
    triple = random.choice(triples)
    scale = random.randint(1, 3)

    a, b, c = [x * scale for x in triple]

    # 隨機將 a, b 分配給半徑和切線段長
    if random.random() < 0.5:
        radius = a
        tangent = b
    else:
        radius = b
        tangent = a
    distance_op = c

    # 隨機決定要求解的邊
    find_what = random.choice(['radius', 'tangent', 'distance'])

    if find_what == 'tangent':
        # 給定半徑和斜邊，求切線段長
        question_text = f"直線 $L$ 為圓 $O$ 的切線，切點為 $A$。若圓 $O$ 半徑為 ${radius}$、$\\overline{{OB}}={distance_op}$（$B$ 為 $L$ 上的一點），則切線段 $\\overline{{AB}}$ 的長度為多少？"
        correct_answer = str(tangent)
    elif find_what == 'radius':
        # 給定切線段長和斜邊，求半徑
        question_text = f"直線 $L$ 切圓 $O$ 於 $C$ 點，$D$ 為 $L$ 上的一點。若切線段 $\\overline{{CD}}={tangent}$、$\\overline{{OD}}={distance_op}$，求圓 $O$ 的半徑長為多少？"
        correct_answer = str(radius)
    else:  # find 'distance'
        # 給定半徑和切線段長，求斜邊
        question_text = f"$P$ 為圓 $O$ 外一點，$\\overline{{PM}}$ 為圓 $O$ 的切線，$M$ 為切點。若圓 $O$ 半徑為 ${radius}$ 公分，$\\overline{{PM}}={tangent}$ 公分，則 $\\overline{{OP}}$ 為多少公分？"
        correct_answer = str(distance_op)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_special_triangle_problem():
    """
    題型：利用兩切線段性質，結合 30-60-90 特殊直角三角形求解。
    """
    radius = random.randint(3, 8)
    # △OPM 為 30-60-90 直角三角形
    # 邊長比 OM:PM:OP = 1:sqrt(3):2
    tangent_length_str = f"{radius}\\sqrt{{3}}" if radius != 1 else "\\sqrt{3}"

    # 隨機給定一個角度
    given_angle_type = random.choice(['MOP', 'MPO'])
    if given_angle_type == 'MOP':
        given_angle = 60
        given_angle_str = f"$\\angle MOP = {given_angle}^\\circ$"
    else:  # MPO
        given_angle = 30
        given_angle_str = f"$\\angle MPO = {given_angle}^\\circ$"

    # 隨機決定要求解的項目
    ask_what = random.choice(['perimeter', 'angle_MPN', 'chord_MN', 'tangent_PM'])
    question_base = f"$P$ 為圓 $O$ 外一點，$\\overline{{PM}}$ 與 $\\overline{{PN}}$ 為圓 $O$ 的切線，$M$、$N$ 為切點。已知圓 $O$ 半徑為 ${radius}$ 公分、{given_angle_str}，求"

    if ask_what == 'perimeter':
        # 周長 = 2 * (半徑 + 切線段長)
        perimeter_str = f"{2*radius}+{2*radius}\\sqrt{{3}}"
        question_text = f"{question_base}四邊形 $OMPN$ 的周長為多少公分？"
        correct_answer = perimeter_str
    elif ask_what == 'angle_MPN':
        # ∠MPN = 2 * ∠MPO = 2 * 30° = 60°
        question_text = f"{question_base} $\\angle MPN$ 為多少度？"
        correct_answer = "60"
    elif ask_what == 'chord_MN':
        # 因 ∠MPN=60° 且 PM=PN，△PMN 為正三角形，故 MN = PM
        question_text = f"{question_base} $\\overline{{MN}}$ 的長度為多少公分？"
        correct_answer = tangent_length_str
    else:  # 'tangent_PM'
        question_text = f"{question_base}切線段 $\\overline{{PM}}$ 的長度為多少公分？"
        correct_answer = tangent_length_str

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_chord_length_problem():
    """
    題型：利用面積法求兩切點連線段長 (MN)。
    △OPM 面積 = 1/2 * OM * PM = 1/2 * OP * MR
    """
    triples = [(3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25)]
    triple = random.choice(triples)
    scale = random.randint(1, 2)  # 讓數字小一點

    a, b, c = [x * scale for x in triple]

    # 隨機將 a, b 分配給半徑和切線段長
    if random.random() < 0.5:
        radius = a
        tangent = b
    else:
        radius = b
        tangent = a
    # c 是 OP 的長度

    # MN = 2 * MR = 2 * (radius * tangent) / OP = 2ab/c
    frac = Fraction(2 * a * b, c)

    if frac.denominator == 1:
        answer_str = str(frac.numerator)
    else:
        answer_str = f"\\frac{{{frac.numerator}}}{{{frac.denominator}}}"

    question_text = (
        f"$P$ 為圓 $O$ 外一點，$\\overline{{PM}}$ 與 $\\overline{{PN}}$ 為圓 $O$ 的切線，$M$、$N$ 為切點。"
        f"若圓 $O$ 半徑為 ${radius}$ 公分，$\\overline{{PM}}={tangent}$ 公分，則 $\\overline{{MN}}$ 為多少公分？"
    )

    return {
        "question_text": question_text,
        "answer": answer_str,
        "correct_answer": answer_str
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。能處理整數、分數、以及包含根號的表達式。
    """
    # 將正確答案的 LaTeX 格式標準化
    norm_correct = correct_answer.strip().lower()
    norm_correct = norm_correct.replace('\\circ', '').replace('°', '')
    if '\\frac' in norm_correct:
        # 假設格式為 \\frac{num}{den}
        parts = norm_correct.replace('\\frac{', '').replace('}', '').split('{')
        norm_correct = f"{parts[0]}/{parts[1]}"
    norm_correct = norm_correct.replace('\\sqrt{', 'sqrt(').replace('}', ')')
    norm_correct = norm_correct.replace(' ', '')

    # 將使用者答案標準化
    norm_user = user_answer.strip().lower()
    norm_user = norm_user.replace('*', '')
    norm_user = norm_user.replace(' ', '')

    is_correct = (norm_user == norm_correct)

    # 如果字串比對失敗，嘗試進行數值比對 (處理 72/5 vs 14.4 的情況)
    if not is_correct:
        try:
            # 將字串（可能是分數）轉換為浮點數的輔助函數
            def to_float(s):
                if '/' in s:
                    num, den = s.split('/')
                    return float(num) / float(den)
                else:
                    return float(s)
            
            # 此部分若答案包含 'sqrt' 或 '+' 會引發 ValueError，這是預期行為
            # 在這種情況下，我們僅依賴嚴格的字串比對
            val_correct = to_float(norm_correct)
            val_user = to_float(norm_user)
            
            if math.isclose(val_user, val_correct):
                is_correct = True
        except (ValueError, ZeroDivisionError):
            # 字串不是簡單的數字或分數，維持原來的比對結果
            pass
            
    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}