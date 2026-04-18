import random
import math

# Helper function to generate Pythagorean triples for "nice" numbers
def get_pythagorean_triple():
    # Common primitive Pythagorean triples
    primitive_triples = [
        (3, 4, 5),
        (5, 12, 13),
        (8, 15, 17),
        (7, 24, 25),
    ]
    # Randomly select a primitive triple
    a, b, c = random.choice(primitive_triples)
    # Scale it up by a random integer factor to get variety
    scale = random.randint(1, 3)
    return (a * scale, b * scale, c * scale)

# Helper function to get primitive Pythagorean triples for matching purposes
def get_pythagorean_triple_bases():
    return [
        (3, 4, 5),
        (5, 12, 13),
        (8, 15, 17),
        (7, 24, 25),
    ]

def generate(level=1):
    """
    生成「三垂線定理」相關題目。
    包含：
    1. 三垂線定理與畢氏定理直接應用 (AC, CD -> AD)
    2. 三垂線定理與畢氏定理嵌套應用 (AB, BC, CD -> AD)
    3. 三垂線定理在最短距離問題的應用 (OP, OA, OB -> PH)
    """
    problem_type = 'type_1_basic_acd' # Default for level 1
    if level == 1:
        problem_type = random.choice(['type_1_basic_acd', 'type_2_nested_abc_acd'])
    elif level == 2:
        problem_type = random.choice(['type_2_nested_abc_acd', 'type_3_shortest_distance'])
    elif level >= 3:
        problem_type = 'type_3_shortest_distance'

    if problem_type == 'type_1_basic_acd':
        return generate_type_1_basic_acd()
    elif problem_type == 'type_2_nested_abc_acd':
        return generate_type_2_nested_abc_acd()
    else: # type_3_shortest_distance
        return generate_type_3_shortest_distance()

def generate_type_1_basic_acd():
    """
    生成三垂線定理的基本應用題目。
    已知 AC, CD，求 AD 的長度。
    這形成一個直角三角形 ACD，其中 ∠ACD = 90°。
    """
    # 傾向於產生整數答案，但也允許根號答案
    if random.random() < 0.7: # 70% 機率生成整數 AD
        AC_val, CD_val, AD_val = get_pythagorean_triple()
        AD_str = str(int(AD_val))
    else: # 30% 機率生成根號答案
        AC_val = random.randint(3, 15)
        CD_val = random.randint(3, 15)
        AD_squared = AC_val**2 + CD_val**2
        AD_val = math.sqrt(AD_squared)
        if AD_val.is_integer():
            AD_str = str(int(AD_val))
        else:
            AD_str = r"\\sqrt{{" + str(int(AD_squared)) + r"}}"
    
    question_text = (
        r"如右圖，直線 $AB$ 垂直平面 $E$ 於 $B$ 點，$L$ 是平面 $E$ 上一條直線，$D$ 是 $L$ 上一點，直線 $BC$ 垂直 $L$ 於 $C$ 點。<br>"
        r"已知 $AC={AC}$, $CD={CD}$，求 $AD$ 的長度。"
    ).format(AC=AC_val, CD=CD_val) # 使用 .format() 插入變數
    
    correct_answer = AD_str
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_type_2_nested_abc_acd():
    """
    生成三垂線定理的嵌套應用題目。
    已知 AB, BC, CD，求 AD 的長度。
    步驟 1: 在直角三角形 ABC 中求 AC。
    步驟 2: 在直角三角形 ACD 中求 AD。
    """
    # 生成 AB, BC, CD 允許根號答案
    AB_val = random.randint(2, 12)
    BC_val = random.randint(2, 12)
    CD_val = random.randint(2, 12)
    
    AC_squared = AB_val**2 + BC_val**2
    AD_squared = AC_squared + CD_val**2
    
    AD_val = math.sqrt(AD_squared)
    
    if AD_val.is_integer():
        AD_str = str(int(AD_val))
    else:
        AD_str = r"\\sqrt{{" + str(int(AD_squared)) + r"}}"
    
    question_text = (
        r"如右圖，直線 $AB$ 垂直平面 $E$ 於 $B$ 點，$L$ 是平面 $E$ 上一條直線，$D$ 是 $L$ 上一點，直線 $BC$ 垂直 $L$ 於 $C$ 點。<br>"
        r"已知 $AB={AB}$, $BC={BC}$, $CD={CD}$，求 $AD$ 的長度。"
    ).format(AB=AB_val, BC=BC_val, CD=CD_val)
    
    correct_answer = AD_str
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_type_3_shortest_distance():
    """
    生成三垂線定理在最短距離問題的應用題目。
    已知 OP, OA, OB，求蜘蛛與蟑螂的最近距離 PH。
    涉及: 畢氏定理 (OAB -> AB), 面積公式求高 (AB, OA, OB -> OH), 畢氏定理 (OPH -> PH)。
    """
    # 目標是生成整數的 OA, OB, OP 和最終答案 PH。

    # 第一步: 處理底平面上的直角三角形 OAB。
    # OA 和 OB 是股，AB 是斜邊。O 到 AB 的高 OH = (OA * OB) / AB。
    # 為了確保 OH 為整數，我們選擇 (base_a, base_b, base_c) 原始畢氏三元數，
    # 並將 OA, OB 乘以一個 k 值，其中 k 是 base_c 的倍數。
    primitive_triples = [(3, 4, 5), (5, 12, 13)] # 使用常見的原始三元數
    base_a, base_b, base_c = random.choice(primitive_triples)
    
    # 縮放因子，確保 OH 計算後為整數
    scale_factor_OAOB = random.randint(1, 3) * base_c 
    
    OA = base_a * scale_factor_OAOB
    OB = base_b * scale_factor_OAOB
    AB_hyp = base_c * scale_factor_OAOB # AB 為直角三角形 OAB 的斜邊
    
    OH_int = (OA * OB) // AB_hyp # OH (O 到 AB 的投影距離) 必為整數
    
    # 第二步: 處理立體直角三角形 OPH。
    # OH 是 O 到直線 AB 的距離，OP 是 P 到平面 OAB 的距離，PH 是 P 到直線 AB 的最短距離。
    # OH 和 OP 是股，PH 是斜邊。
    
    # 我們有 OH_int，現在需要找到 OP 使 PH 為整數。
    # 嘗試將 OH_int 作為另一個畢氏三元數的股。
    found_triple_for_ph = False
    OP_val = 0
    PH_ans_val = 0

    # 遍歷原始畢氏三元數，看 OH_int 是否能作為其中一個股的倍數
    for x_base, y_base, z_base in get_pythagorean_triple_bases():
        if OH_int % x_base == 0:
            scale_ph = OH_int // x_base
            OP_val = y_base * scale_ph
            PH_ans_val = z_base * scale_ph
            found_triple_for_ph = True
            break
        elif OH_int % y_base == 0:
            scale_ph = OH_int // y_base
            OP_val = x_base * scale_ph
            PH_ans_val = z_base * scale_ph
            found_triple_for_ph = True
            break
            
    if not found_triple_for_ph:
        # 如果 OH_int 無法簡單地配對到一個縮放過的畢氏三元數，
        # 則隨機選擇 OP，並允許 PH 為根號形式。
        OP_val = random.randint(3, 10)
        PH_ans_sq = OH_int**2 + OP_val**2
        PH_val = math.sqrt(PH_ans_sq)
        if PH_val.is_integer():
            PH_ans_str = str(int(PH_val))
        else:
            PH_ans_str = r"\\sqrt{{" + str(int(PH_ans_sq)) + r"}}"
    else:
        PH_ans_str = str(int(PH_ans_val))

    question_text = (
        r"如右圖，兩牆面與地板均互相垂直，在牆角有一隻蜘蛛停在 $P$ 點，注視著從 $A$ 點沿著直線爬到 $B$ 點的蟑螂。<br>"
        r"已知 $OP={OP}$, $OA={OA}$, $OB={OB}$，關於整個注視的過程，回答下列問題。<br>"
        r"(1) 當蟑螂爬到哪一個位置時，蜘蛛與蟑螂的距離最近？（單選）<br>"
        r"A點、AB的中點、$O$ 在直線 $AB$ 上的投影點、$B$ 點。<br>"
        r"(2) 求蜘蛛與蟑螂的最近距離。"
    ).format(OP=OP_val, OA=OA, OB=OB)

    # (1) 答案固定為 O 在直線 AB 上的投影點
    ans1_correct_text = r"$O$ 在直線 $AB$ 上的投影點"
    
    correct_answer = f"(1){ans1_correct_text}, (2){PH_ans_str}"
    
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
    result_text = ""

    # 輔助函數：解析並計算可能包含平方根的字串表達式
    def parse_and_eval(ans_str):
        # 替換 LaTeX 的平方根寫法為 Python math 函數
        ans_str = ans_str.replace(r"\\sqrt{{", "math.sqrt(").replace(r"}}", ")")
        # 替換常見數學符號
        ans_str = ans_str.replace("sqrt(", "math.sqrt(").replace("^", "**")

        try:
            # 安全地評估表達式，限制可用內建函數以防止惡意程式碼
            evaluated_val = float(eval(ans_str, {"__builtins__": None, "math": math}))
            return evaluated_val
        except (ValueError, SyntaxError, NameError):
            return None # 表示無法解析為數值表達式

    # 處理多部分答案 (例如: Type 3 題目有兩小題)
    if correct_answer.startswith("(1)") and "(2)" in correct_answer:
        user_parts = []
        # 嘗試以 "(2)" 分割答案，並處理前面的 "(1)"
        if "(1)" in user_answer and "(2)" in user_answer:
            parts = user_answer.split("(2)", 1)
            user_parts.append(parts[0].replace("(1)", "").strip())
            user_parts.append(parts[1].strip())
        elif "," in user_answer: # 如果用戶以逗號分隔，也嘗試解析
             parts = user_answer.split(",", 1)
             user_parts = [p.strip() for p in parts]
             # 移除可能存在的前綴 "(1)", "(2)"
             if user_parts and user_parts[0].startswith("(1)"): user_parts[0] = user_parts[0][3:].strip()
             if len(user_parts) > 1 and user_parts[1].startswith("(2)"): user_parts[1] = user_parts[1][3:].strip()

        # 解析正確答案的兩部分
        correct_parts = []
        parts = correct_answer.split("(2)", 1)
        correct_parts.append(parts[0].replace("(1)", "").strip())
        correct_parts.append(parts[1].strip())

        if len(user_parts) == 2 and len(correct_parts) == 2:
            ua1_raw = user_parts[0]
            ca1_raw = correct_parts[0]
            ua2_raw = user_parts[1]
            ca2_raw = correct_parts[1]

            # 第一部分答案 (文字選擇題) 進行大小寫不敏感的精確字串比對
            correct1 = (ua1_raw.upper() == ca1_raw.upper())

            # 第二部分答案 (數值計算題) 進行數值比較
            val_ua2 = parse_and_eval(ua2_raw)
            val_ca2 = parse_and_eval(ca2_raw)
            
            correct2 = False
            if val_ua2 is not None and val_ca2 is not None:
                correct2 = abs(val_ua2 - val_ca2) < 1e-9 # 浮點數比較
            elif ua2_raw.upper() == ca2_raw.upper(): # 如果無法數值解析，退回精確字串比對
                correct2 = True

            is_correct = correct1 and correct2
            if is_correct:
                result_text = f"完全正確！答案是 ${correct_answer}$。"
            elif not correct1 and not correct2:
                result_text = f"兩個答案都不正確。正確答案應為：${correct_answer}$"
            elif not correct1:
                result_text = f"第 (1) 題答案不正確。正確答案應為：${correct_answer}$"
            else: # not correct2
                result_text = f"第 (2) 題答案不正確。正確答案應為：${correct_answer}$"
        else:
            result_text = f"答案格式不正確。請提供兩部分答案，例如：(1)O在直線AB上的投影點, (2)13。正確答案應為：${correct_answer}$"
            is_correct = False
    else: # 單部分答案
        val_ua = parse_and_eval(user_answer)
        val_ca = parse_and_eval(correct_answer)

        if val_ua is not None and val_ca is not None:
            is_correct = abs(val_ua - val_ca) < 1e-9
        elif user_answer.upper() == correct_answer.upper(): # 退回精確字串比對
            is_correct = True

        if is_correct:
            result_text = f"完全正確！答案是 ${correct_answer}$。"
        else:
            result_text = f"答案不正確。正確答案應為：${correct_answer}$"
            
    return {"correct": is_correct, "result": result_text, "next_question": True}