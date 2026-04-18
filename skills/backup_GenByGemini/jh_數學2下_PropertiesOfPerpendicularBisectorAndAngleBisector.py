import random
import re

def generate(level=1):
    """
    生成關於「中垂線與角平分線性質」的題目。
    - 中垂線性質：線段中垂線上任一點到線段兩端點的距離相等。
    - 角平分線性質：角平分線上任一點到角兩邊的距離相等。
    - 逆性質（判別性質）亦成立。
    """
    problem_generators = [
        generate_perp_bisector_perimeter_problem,
        generate_isosceles_from_equidistance_problem,
        generate_angle_bisector_area_problem,
        generate_angle_bisector_converse_angle_problem
    ]
    
    selected_generator = random.choice(problem_generators)
    return selected_generator()

def generate_perp_bisector_perimeter_problem():
    """
    題型：利用中垂線性質求三角形周長相關問題。
    如例題一：直線 L 為 BC 的中垂線，交 AB 於 E。△AEC 周長 = AE+EC+AC = AE+EB+AC = AB+AC。
    """
    ac_len = random.randint(5, 15)
    ab_len = random.randint(ac_len + 3, 30)
    perimeter = ab_len + ac_len

    # 隨機交換邊的角色，使題目更多樣
    side1, side2, side3 = random.sample(['A', 'B', 'C'], 3)
    
    question_text = f"在 △{side1}{side2}{side3} 中，已知直線 L 為 $\\overline{{{side2}{side3}}}$ 的中垂線，且交 $\\overline{{{side1}{side2}}}$ 於 E 點。若 △{side1}E{side3} 的周長為 ${perimeter}$，且 $\\overline{{{side1}{side3}}} = {ac_len}$，則 $\\overline{{{side1}{side2}}}$ 的長度為多少？"
    
    final_answer = str(ab_len)
    # 傳遞參數給 check 函數以生成詳解
    params = f"type=perp_perimeter;perimeter={perimeter};ac={ac_len};s1={side1};s2={side2};s3={side3}"
    answer_bundle = f"{final_answer}|{params}"
    
    return {
        "question_text": question_text,
        "answer": answer_bundle,
        "correct_answer": answer_bundle
    }

def generate_isosceles_from_equidistance_problem():
    """
    題型：利用「到兩端點等距的點，必在中垂線上」的逆性質（或其根本的等腰三角形性質）求角度。
    在 △ABC 中，D 在 AC 上，DB=DC，求角度。
    """
    angle_c = random.randint(30, 50)
    angle_abd = random.randint(20, 40)
    
    # 計算角度
    angle_dbc = angle_c # 因為 DB=DC, △DBC 為等腰三角形
    angle_abc = angle_abd + angle_dbc
    angle_a = 180 - angle_abc - angle_c
    
    question_text = f"在 △ABC 中，D 點在 $\\overline{{AC}}$ 上，且 $\\overline{{DB}} = \\overline{{DC}}$。若 $\\angle ABD = {angle_abd}°$，$\\angle C = {angle_c}°$，則 $\\angle A$ 的度數為多少？"
    
    final_answer = str(angle_a)
    params = f"type=perp_converse_iso;angle_c={angle_c};angle_abd={angle_abd}"
    answer_bundle = f"{final_answer}|{params}"

    return {
        "question_text": question_text,
        "answer": answer_bundle,
        "correct_answer": answer_bundle
    }

def generate_angle_bisector_area_problem():
    """
    題型：利用角平分線性質求面積。
    如例題四：△ABC 中，∠C=90°，BD 為角平分線，DE⊥AB。則 DE=CD。求 △ABD 面積。
    """
    cd_len = random.randint(2, 6)
    # 確保 AB 長度為偶數，使面積為整數
    ab_len = random.randint(5, 12) * 2
    
    de_len = cd_len
    area = int(0.5 * ab_len * de_len)
    
    question_text = f"如圖，在 △ABC 中，$\\angle C = 90°$，$\\overline{{BD}}$ 為 $\\angle ABC$ 的角平分線，交 $\\overline{{AC}}$ 於 D 點，且 $\\overline{{DE}} \\perp \\overline{{AB}}$ 於 E 點。若 $\\overline{{AB}} = {ab_len}$，$\\overline{{CD}} = {cd_len}$，則 △ABD 的面積為多少？"
    
    final_answer = str(area)
    params = f"type=angle_prop_area;cd={cd_len};ab={ab_len}"
    answer_bundle = f"{final_answer}|{params}"

    return {
        "question_text": question_text,
        "answer": answer_bundle,
        "correct_answer": answer_bundle
    }

def generate_angle_bisector_converse_angle_problem():
    """
    題型：利用角平分線的逆性質求角度。
    如例題六：DE⊥AB, DF⊥AC, DE=DF。則 AD 為角平分線。
    """
    angle_a_half = random.randint(25, 40)
    angle_c = random.randint(30, 60)
    
    # 確保第三個角為正數且合理
    while 2 * angle_a_half + angle_c >= 170:
        angle_a_half = random.randint(25, 40)
        angle_c = random.randint(30, 60)
        
    angle_bac = 2 * angle_a_half
    angle_b = 180 - angle_bac - angle_c
    
    question_text = f"在 △ABC 中，D 點在 $\\overline{{BC}}$ 上，$\\overline{{DE}} \\perp \\overline{{AB}}$ 於 E 點、$\\overline{{DF}} \\perp \\overline{{AC}}$ 於 F 點，且 $\\overline{{DE}} = \\overline{{DF}}$。若 $\\angle BAD = {angle_a_half}°$，$\\angle C = {angle_c}°$，則 $\\angle B$ 的度數為多少？"
    
    final_answer = str(angle_b)
    params = f"type=angle_converse_angle;angle_bad={angle_a_half};angle_c={angle_c}"
    answer_bundle = f"{final_answer}|{params}"

    return {
        "question_text": question_text,
        "answer": answer_bundle,
        "correct_answer": answer_bundle
    }

def check(user_answer, correct_answer_bundle):
    """
    檢查答案是否正確，並提供詳細解說。
    """
    try:
        # 解析答案包
        parts = correct_answer_bundle.split('|')
        correct_answer = parts[0]
        params_str = parts[1]
        
        # 解析參數
        params = dict(re.findall(r'(\w+)=([^;]+)', params_str))
        problem_type = params.get('type')
    except (IndexError, AttributeError):
        # 如果答案包格式不對，則進行基本比較
        is_correct = user_answer.strip() == correct_answer_bundle.strip()
        result_text = f"完全正確！答案是 ${correct_answer_bundle}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer_bundle}$"
        return {"correct": is_correct, "result": result_text, "next_question": True}

    # 標準化使用者答案
    user_answer_clean = user_answer.strip()
    
    is_correct = (user_answer_clean == correct_answer)
    if not is_correct:
        try:
            if float(user_answer_clean) == float(correct_answer):
                is_correct = True
        except ValueError:
            pass

    # 根據題型生成詳解
    solution_text = ""
    if problem_type == 'perp_perimeter':
        perimeter = int(params['perimeter'])
        ac = int(params['ac'])
        s1, s2, s3 = params['s1'], params['s2'], params['s3']
        ab = perimeter - ac
        solution_text = (
            f"∵ 直線 L 為 $\\overline{{{s2}{s3}}}$ 的中垂線，根據中垂線性質，E 點到 ${s2}$、${s3}$ 兩點的距離相等。<br>"
            f"∴ $\\overline{{E{s2}}} = \\overline{{E{s3}}}$<br>"
            f"△{s1}E{s3} 的周長 = $\\overline{{{s1}E}} + \\overline{{E{s3}}} + \\overline{{{s1}{s3}}}$<br>"
            f"將 $\\overline{{E{s3}}}$ 替換為 $\\overline{{E{s2}}}$，得周長 = $\\overline{{{s1}E}} + \\overline{{E{s2}}} + \\overline{{{s1}{s3}}}$<br>"
            f"又 $\\overline{{{s1}E}} + \\overline{{E{s2}}}$ 即為 $\\overline{{{s1}{s2}}}$ 的長度。<br>"
            f"∴ △{s1}E{s3} 的周長 = $\\overline{{{s1}{s2}}} + \\overline{{{s1}{s3}}}$<br>"
            f"故 $\\overline{{{s1}{s2}}}$ = (△{s1}E{s3} 周長) - $\\overline{{{s1}{s3}}}$ = ${perimeter} - {ac} = {ab}$。"
        )
    elif problem_type == 'perp_converse_iso':
        angle_c = int(params['angle_c'])
        angle_abd = int(params['angle_abd'])
        angle_abc = angle_c + angle_abd
        angle_a = 180 - angle_abc - angle_c
        solution_text = (
            f"∵ 在 △DBC 中，$\\overline{{DB}} = \\overline{{DC}}$，<br>"
            f"∴ △DBC 為等腰三角形，故 $\\angle DBC = \\angle C = {angle_c}°$。<br>"
            f"整個 $\\angle ABC = \\angle ABD + \\angle DBC = {angle_abd}° + {angle_c}° = {angle_abc}°$。<br>"
            f"在 △ABC 中，三個內角和為 180°。<br>"
            f"∴ $\\angle A = 180° - \\angle ABC - \\angle C = 180° - {angle_abc}° - {angle_c}° = {angle_a}°$。"
        )
    elif problem_type == 'angle_prop_area':
        cd = int(params['cd'])
        ab = int(params['ab'])
        area = int(0.5 * ab * cd)
        solution_text = (
            f"∵ $\\overline{{BD}}$ 為 $\\angle ABC$ 的角平分線，且 D 點在 $\\overline{{BD}}$ 上，<br>"
            f"又 $\\overline{{DC}} \\perp \\overline{{BC}}$ (因 $\\angle C=90°$)，且 $\\overline{{DE}} \\perp \\overline{{AB}}$。<br>"
            f"根據角平分線性質，角平分線上任一點到角兩邊的距離相等。<br>"
            f"∴ $\\overline{{DE}} = \\overline{{CD}} = {cd}$。<br>"
            f"△ABD 的面積 = $\\frac{{1}}{{2}} \\times$ 底 $\\times$ 高 = $\\frac{{1}}{{2}} \\times \\overline{{AB}} \\times \\overline{{DE}}$。<br>"
            f"面積 = $\\frac{{1}}{{2}} \\times {ab} \\times {cd} = {area}$。"
        )
    elif problem_type == 'angle_converse_angle':
        angle_bad = int(params['angle_bad'])
        angle_c = int(params['angle_c'])
        angle_bac = 2 * angle_bad
        angle_b = 180 - angle_bac - angle_c
        solution_text = (
            f"∵ D 點到 $\\overline{{AB}}$ 和 $\\overline{{AC}}$ 的距離相等 ($\\overline{{DE}} = \\overline{{DF}}$)，<br>"
            f"根據角平分線的判別性質，可知 $\\overline{{AD}}$ 是 $\\angle BAC$ 的角平分線。<br>"
            f"∴ $\\angle CAD = \\angle BAD = {angle_bad}°$。<br>"
            f"整個 $\\angle BAC = \\angle BAD + \\angle CAD = {angle_bad}° + {angle_bad}° = {angle_bac}°$。<br>"
            f"在 △ABC 中，三個內角和為 180°。<br>"
            f"∴ $\\angle B = 180° - \\angle BAC - \\angle C = 180° - {angle_bac}° - {angle_c}° = {angle_b}°$。"
        )

    if is_correct:
        result_text = f"完全正確！答案是 ${correct_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer}$。<br><br><b>【詳解】</b><br>{solution_text}"

    return {"correct": is_correct, "result": result_text, "next_question": True}