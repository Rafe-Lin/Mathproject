import random
from fractions import Fraction

def generate(level=1):
    """
    生成「無理數與實數」相關題目。
    主要題型：利用無理數的性質，解含有根號的方程組。
    例如：若 $a, b$ 為有理數，且 $(A+B\\sqrt{k})a + (C+D\\sqrt{k})b = E+F\\sqrt{k}$，求 $a, b$ 的值。
    """
    return generate_irrational_equation_problem(level)

def generate_irrational_equation_problem(level):
    """
    生成形如 $(X + Y\\sqrt{k})a + (Z + W\\sqrt{k})b = R + S\\sqrt{k}$ 的方程，
    並要求解有理數 $a, b$ 的值。
    """
    sqrt_k = random.choice([2, 3, 5, 7, 11]) # 選擇一個非完全平方數的根號項

    if level <= 2: # Level 1 and 2 use integer coefficients and answers
        # 選擇期望的整數解 a 和 b
        ans_a_val = random.randint(-3 - (level-1)*2, 3 + (level-1)*2) # 答案範圍隨等級增加
        ans_b_val = random.randint(-3 - (level-1)*2, 3 + (level-1)*2)

        # 確保答案不全為零，且不至於過於簡單 (例如只有其中一個是1且另一個是0)
        while (ans_a_val == 0 and ans_b_val == 0) or \
              (abs(ans_a_val) <= 1 and ans_b_val == 0) or \
              (ans_a_val == 0 and abs(ans_b_val) <= 1):
            ans_a_val = random.randint(-3 - (level-1)*2, 3 + (level-1)*2)
            ans_b_val = random.randint(-3 - (level-1)*2, 3 + (level-1)*2)

        # 生成方程的係數 X, Y, Z, W
        coeff_range = 5 + (level-1)*2 # 係數範圍隨等級增加
        X = random.randint(-coeff_range, coeff_range)
        Y = random.randint(-coeff_range, coeff_range)
        Z = random.randint(-coeff_range, coeff_range)
        W = random.randint(-coeff_range, coeff_range)

        # 確保：
        # 1. 根號項存在 (Y 或 W 不為零，以保證題目為無理數方程)
        # 2. 方程組有唯一解 (行列式 XW - YZ 不為零，以保證 a, b 可唯一求解)
        while (Y == 0 and W == 0) or (X * W - Y * Z == 0):
            X = random.randint(-coeff_range, coeff_range)
            Y = random.randint(-coeff_range, coeff_range)
            Z = random.randint(-coeff_range, coeff_range)
            W = random.randint(-coeff_range, coeff_range)

        ans_a = Fraction(ans_a_val)
        ans_b = Fraction(ans_b_val)

        # 根據選定的 a, b 和係數計算方程右側 (RHS)
        RHS_rational = X * ans_a + Z * ans_b
        RHS_irrational_coeff = Y * ans_a + W * ans_b

        # 格式化數字 (整數或分數)
        def format_num(num_or_frac):
            if isinstance(num_or_frac, Fraction):
                if num_or_frac.denominator == 1:
                    return str(num_or_frac.numerator)
                else:
                    return f"\\frac{{{num_or_frac.numerator}}}{{{num_or_frac.denominator}}}"
            else: # int
                return str(num_or_frac)

        # 格式化根號項係數
        def format_coeff_sqrt(coeff, sqrt_val):
            if coeff == Fraction(0):
                return ""
            elif coeff == Fraction(1):
                return f"\\sqrt{{{sqrt_val}}}"
            elif coeff == Fraction(-1):
                return f"-\\sqrt{{{sqrt_val}}}"
            else:
                return f"{format_num(coeff)}\\sqrt{{{sqrt_val}}}"

        # 構建 LHS 的第一個 term: (X + Y*sqrt_k)a
        lhs_term1_str = ""
        if X == 0 and Y == 0:
            pass # 不應發生，因為 Y 或 W 至少有一個非零
        elif X != 0 and Y == 0: # 只有有理數部分
            lhs_term1_str = f"{format_num(X)}a"
        elif X == 0 and Y != 0: # 只有無理數部分
            lhs_term1_str = f"{format_coeff_sqrt(Y, sqrt_k)}a"
        else: # 兩部分都有
            lhs_term1_str = f"({format_num(X)}{'+' if Y > 0 else ''}{format_coeff_sqrt(Y, sqrt_k)})a"

        # 構建 LHS 的第二個 term: (Z + W*sqrt_k)b
        lhs_term2_str = ""
        if Z == 0 and W == 0:
            pass # 不應發生
        elif Z != 0 and W == 0: # 只有有理數部分
            lhs_term2_str = f"{format_num(Z)}b"
        elif Z == 0 and W != 0: # 只有無理數部分
            lhs_term2_str = f"{format_coeff_sqrt(W, sqrt_k)}b"
        else: # 兩部分都有
            lhs_term2_str = f"({format_num(Z)}{'+' if W > 0 else ''}{format_coeff_sqrt(W, sqrt_k)})b"

        # 組合 LHS 完整表達式
        lhs_expression = lhs_term1_str
        if lhs_term2_str:
            # 判斷第二個 term 的符號，以決定是否加 '+'
            term2_is_negative = False
            if Z < 0 or (Z == 0 and W < 0): # 如果 Z 為負，或 Z 為零且 W 為負
                term2_is_negative = True

            if term2_is_negative:
                lhs_expression += lhs_term2_str
            else:
                if lhs_expression: # 只有當第一個 term 存在時才加 '+'
                    lhs_expression += f"+{lhs_term2_str}"
                else: # 如果第一個 term 為空 (理論上不應發生)，則第二個 term 直接作為第一個
                    lhs_expression = lhs_term2_str

        # 構建 RHS 完整表達式
        rhs_rational_str = format_num(RHS_rational) if RHS_rational != 0 else ""
        rhs_irrational_str = format_coeff_sqrt(RHS_irrational_coeff, sqrt_k) if RHS_irrational_coeff != 0 else ""

        rhs_expression = ""
        if rhs_rational_str and rhs_irrational_str:
            rhs_expression = f"{rhs_rational_str}{'+' if RHS_irrational_coeff > 0 else ''}{rhs_irrational_str}"
        elif rhs_rational_str:
            rhs_expression = rhs_rational_str
        elif rhs_irrational_str:
            rhs_expression = rhs_irrational_str
        else: # 若兩部分都為零，則顯示 "0"
            rhs_expression = "0"

        correct_answer_str = f"a={format_num(ans_a)}, b={format_num(ans_b)}"

    else: # Level 3 uses fractional coefficients and/or answers
        # 生成分數解 a 和 b
        def gen_fraction_val():
            num = random.randint(-5, 5)
            den = random.choice([1, 2, 3, 4, 5])
            if num == 0: return Fraction(0)
            return Fraction(num, den)

        ans_a = gen_fraction_val()
        ans_b = gen_fraction_val()

        while (ans_a == Fraction(0) and ans_b == Fraction(0)) or \
              (abs(ans_a) == Fraction(1) and ans_b == Fraction(0)) or \
              (ans_a == Fraction(0) and abs(ans_b) == Fraction(1)):
            ans_a = gen_fraction_val()
            ans_b = gen_fraction_val()

        # 生成分數係數 X, Y, Z, W
        def gen_fraction_coeff():
            num = random.randint(-5, 5)
            den = random.choice([1, 2, 3, 4]) # 係數分母小一些，避免過於複雜
            if num == 0: return Fraction(0)
            return Fraction(num, den)

        X = gen_fraction_coeff()
        Y = gen_fraction_coeff()
        Z = gen_fraction_coeff()
        W = gen_fraction_coeff()

        # 確保根號項存在且有唯一解
        while (Y == Fraction(0) and W == Fraction(0)) or (X * W - Y * Z == Fraction(0)):
            X = gen_fraction_coeff()
            Y = gen_fraction_coeff()
            Z = gen_fraction_coeff()
            W = gen_fraction_coeff()

        # 計算 RHS
        RHS_rational = X * ans_a + Z * ans_b
        RHS_irrational_coeff = Y * ans_a + W * ans_b

        # 格式化分數
        def format_num(frac):
            if frac.denominator == 1:
                return str(frac.numerator)
            else:
                return f"\\frac{{{frac.numerator}}}{{{frac.denominator}}}"

        # 格式化根號項係數 (分數)
        def format_coeff_sqrt(coeff_frac, sqrt_val):
            if coeff_frac == Fraction(0):
                return ""
            elif coeff_frac == Fraction(1):
                return f"\\sqrt{{{sqrt_val}}}"
            elif coeff_frac == Fraction(-1):
                return f"-\\sqrt{{{sqrt_val}}}"
            else:
                return f"{format_num(coeff_frac)}\\sqrt{{{sqrt_val}}}"

        # 構建 LHS 的第一個 term
        lhs_term1_str = ""
        if X == Fraction(0) and Y == Fraction(0):
            pass
        elif X != Fraction(0) and Y == Fraction(0):
            lhs_term1_str = f"{format_num(X)}a"
        elif X == Fraction(0) and Y != Fraction(0):
            lhs_term1_str = f"{format_coeff_sqrt(Y, sqrt_k)}a"
        else:
            lhs_term1_str = f"({format_num(X)}{'+' if Y > Fraction(0) else ''}{format_coeff_sqrt(Y, sqrt_k)})a"

        # 構建 LHS 的第二個 term
        lhs_term2_str = ""
        if Z == Fraction(0) and W == Fraction(0):
            pass
        elif Z != Fraction(0) and W == Fraction(0):
            lhs_term2_str = f"{format_num(Z)}b"
        elif Z == Fraction(0) and W != Fraction(0):
            lhs_term2_str = f"{format_coeff_sqrt(W, sqrt_k)}b"
        else:
            lhs_term2_str = f"({format_num(Z)}{'+' if W > Fraction(0) else ''}{format_coeff_sqrt(W, sqrt_k)})b"

        # 組合 LHS 完整表達式
        lhs_expression = lhs_term1_str
        if lhs_term2_str:
            term2_is_negative = False
            if Z < Fraction(0) or (Z == Fraction(0) and W < Fraction(0)):
                term2_is_negative = True

            if term2_is_negative:
                lhs_expression += lhs_term2_str
            else:
                if lhs_expression:
                    lhs_expression += f"+{lhs_term2_str}"
                else:
                    lhs_expression = lhs_term2_str

        # 構建 RHS 完整表達式
        rhs_rational_str = format_num(RHS_rational) if RHS_rational != Fraction(0) else ""
        rhs_irrational_str = format_coeff_sqrt(RHS_irrational_coeff, sqrt_k) if RHS_irrational_coeff != Fraction(0) else ""

        rhs_expression = ""
        if rhs_rational_str and rhs_irrational_str:
            rhs_expression = f"{rhs_rational_str}{'+' if RHS_irrational_coeff > Fraction(0) else ''}{rhs_irrational_str}"
        elif rhs_rational_str:
            rhs_expression = rhs_rational_str
        elif rhs_irrational_str:
            rhs_expression = rhs_irrational_str
        else:
            rhs_expression = "0"

        correct_answer_str = f"a={format_num(ans_a)}, b={format_num(ans_b)}"

    question_text = f"已知 $a$, $b$ 是有理數，且 $ {lhs_expression} = {rhs_expression} $，求 $a$, $b$ 的值。"

    return {
        "question_text": question_text,
        "answer": correct_answer_str,
        "correct_answer": correct_answer_str
    }

def check(user_answer, correct_answer):
    """
    檢查用戶答案是否正確。
    用戶答案格式應為 "a=值, b=值" (例如: "a=1, b=-2")。
    支援分數和小數輸入，並會轉換為分數進行比較。
    """
    user_answer = user_answer.strip().replace(" ", "") # 移除空白
    correct_answer = correct_answer.strip().replace(" ", "")

    try:
        # 解析用戶答案
        user_parts = {}
        for part in user_answer.split(','):
            if '=' in part:
                var, val_str = part.split('=')
                # 嘗試將值轉換為分數
                try:
                    user_parts[var] = Fraction(val_str)
                except ValueError: # 如果不能直接轉換為分數，嘗試作為浮點數
                    user_parts[var] = Fraction(float(val_str))
        
        # 解析正確答案
        correct_parts = {}
        for part in correct_answer.split(','):
            if '=' in part:
                var, val_str = part.split('=')
                correct_parts[var] = Fraction(val_str)

        is_correct = True
        feedback_msgs = []

        # 檢查正確答案中的每個變數是否都在用戶答案中且值相符
        for var, correct_val in correct_parts.items():
            if var not in user_parts:
                is_correct = False
                feedback_msgs.append(f"缺少變數 ${var}$ 的值。")
                break
            # 使用分數進行精確比較
            if user_parts[var] != correct_val:
                is_correct = False
                feedback_msgs.append(f"變數 ${var}$ 的值不正確。您的答案是 ${user_parts[var]}$，正確答案應為 ${correct_val}$。")
                break
        
        # 檢查用戶是否提供了額外的變數
        if is_correct and len(user_parts) != len(correct_parts):
            is_correct = False
            feedback_msgs.append("您提供了多餘的變數。")

        if is_correct:
            result_text = f"完全正確！答案是 ${correct_answer}$。"
        else:
            if not feedback_msgs: # 若無特定錯誤訊息，給予通用提示
                result_text = f"答案不正確。請檢查您的計算。正確答案應為：${correct_answer}$。"
            else:
                result_text = " ".join(feedback_msgs) + f" 正確答案應為：${correct_answer}$。"

        return {"correct": is_correct, "result": result_text, "next_question": True}

    except (ValueError, ZeroDivisionError, KeyError):
        # 處理格式錯誤或無法解析的輸入
        return {"correct": False, "result": f"您的答案格式不正確，請以 'a=值, b=值' 的形式輸入。正確答案應為：${correct_answer}$。", "next_question": True}