import random
from fractions import Fraction
import re

def generate(level=1):
    """
    生成「克拉瑪公式」相關題目。
    使用二階行列式解二元一次聯立方程式。
    """
    
    # 嘗試生成係數和解，直到找到一個有效的方程組 (即 Delta != 0)
    while True:
        if level == 1:
            # 等級 1: 簡單的整數解，小整數係數
            x_sol = random.randint(-4, 4)
            y_sol = random.randint(-4, 4)
            # 確保解不全為零，以避免過於簡單的問題
            if x_sol == 0 and y_sol == 0:
                continue 
            
            a = random.randint(-5, 5)
            b = random.randint(-5, 5)
            d = random.randint(-5, 5)
            e = random.randint(-5, 5)
            
        elif level == 2:
            # 等級 2: 略大的係數，可能產生分數解
            x_sol = random.randint(-6, 6)
            y_sol = random.randint(-6, 6)
            if x_sol == 0 and y_sol == 0:
                continue

            a = random.randint(-10, 10)
            b = random.randint(-10, 10)
            d = random.randint(-10, 10)
            e = random.randint(-10, 10)
        else: # 等級 3 或更高，目前與等級 2 相似
            x_sol = random.randint(-7, 7)
            y_sol = random.randint(-7, 7)
            if x_sol == 0 and y_sol == 0:
                continue

            a = random.randint(-12, 12)
            b = random.randint(-12, 12)
            d = random.randint(-12, 12)
            e = random.randint(-12, 12)

        # 確保方程組不是退化的 (例如，整行係數為零)
        # 例如，0x + 0y = C 的形式
        if (a == 0 and b == 0) or (d == 0 and e == 0):
            continue 

        # 計算行列式 Delta
        delta = a * e - b * d

        # 確保 Delta 不為零，以保證有唯一解
        if delta != 0:
            break # 找到有效的方程組
            
    # 根據預設的解 x_sol, y_sol 和係數計算常數項 c 和 f
    c = a * x_sol + b * y_sol
    f = d * x_sol + e * y_sol

    # 計算 Delta_x 和 Delta_y (用於答案的計算)
    delta_x = c * e - b * f
    delta_y = a * f - c * d
    
    # 格式化係數項，處理 1x, -1x 等情況
    def format_coeff_term(coeff, var):
        if coeff == 1:
            return var
        elif coeff == -1:
            return f"-{var}"
        elif coeff == 0: # 如果係數為 0，則該項被跳過
            return ""
        return f"{coeff}{var}"

    eq1_terms = []
    term_ax = format_coeff_term(a, 'x')
    term_by = format_coeff_term(b, 'y')

    if term_ax:
        eq1_terms.append(term_ax)
    if term_by:
        if eq1_terms and b > 0: # 如果前面有項且 b 為正，添加 '+'
            eq1_terms.append(f"+ {term_by}")
        else: # b 為負或它是第一項
            eq1_terms.append(term_by)
    
    eq2_terms = []
    term_dx = format_coeff_term(d, 'x')
    term_ey = format_coeff_term(e, 'y')

    if term_dx:
        eq2_terms.append(term_dx)
    if term_ey:
        if eq2_terms and e > 0:
            eq2_terms.append(f"+ {term_ey}")
        else:
            eq2_terms.append(term_ey)

    # 如果經過格式化後某方程的左側為空 (這在 delta != 0 的情況下不應發生)
    if not eq1_terms or not eq2_terms:
         # 繼續生成題目以避免這種情況
         return generate(level) # 遞迴調用以生成新的題目

    eq1_str = " ".join(eq1_terms).replace("+-", "- ") # 清理 "a + -by" 為 "a - by"
    eq2_str = " ".join(eq2_terms).replace("+-", "- ") # 清理 "a + -by" 為 "a - by"

    # LaTeX 格式的方程組
    question_text = (
        r"使用克拉瑪公式解二元一次聯立方程式 "
        r"$\begin{{cases}} "
        f"{eq1_str} = {c} \\\\ "
        f"{eq2_str} = {f} "
        r"\end{{cases}}$"
        r"。"
    )

    # 將正確答案格式化為分數 (如果需要)
    x_ans = Fraction(delta_x, delta)
    y_ans = Fraction(delta_y, delta)

    # 轉換為字串，整數形式時保持簡潔
    if x_ans.denominator == 1:
        x_ans_str = str(x_ans.numerator)
    else:
        x_ans_str = f"\\frac{{{x_ans.numerator}}}{{{x_ans.denominator}}}"

    if y_ans.denominator == 1:
        y_ans_str = str(y_ans.numerator)
    else:
        y_ans_str = f"\\frac{{{y_ans.numerator}}}{{{y_ans.denominator}}}"

    formatted_correct_answer = f"x={x_ans_str}, y={y_ans_str}"

    return {
        "question_text": question_text,
        "answer": formatted_correct_answer, 
        "correct_answer": formatted_correct_answer 
    }


def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    user_answer 和 correct_answer 格式預期為 "x=val_x, y=val_y"。
    """
    user_answer = user_answer.strip().replace(" ", "") # 移除所有空格以方便解析
    correct_answer = correct_answer.strip().replace(" ", "")

    # 正則表達式用於提取 x 和 y 的值
    # 處理 "x=2,y=-1" 或 "x=1/2,y=3" 等格式。
    # `correct_answer` 可能包含 LaTeX 分數 (例如, "\\frac{1}{2}")。
    # `user_answer` 假定為普通數字或分數格式，不含 LaTeX。
    
    # 匹配模式：Group 1 用於 x 的值，Group 2 用於 y 的值。
    # 對 x 的值使用非貪婪匹配，直到遇到逗號。
    pattern = r"x=([^,]+),y=(.+)" 
    
    user_match = re.match(pattern, user_answer)
    correct_match = re.match(pattern, correct_answer)

    if not user_match or not correct_match:
        # 如果解析失敗，則假定為不正確的格式。
        return {"correct": False, "result": "請確保您的答案格式為 'x=值,y=值' (例如: x=2,y=-1 或 x=1/2,y=3)。", "next_question": True}

    user_x_str, user_y_str = user_match.groups()
    correct_x_str, correct_y_str = correct_match.groups()

    try:
        # 將用戶輸入的潛在分數 (例如 "1/2") 轉換為 Fraction 對象
        user_x = Fraction(user_x_str)
        user_y = Fraction(user_y_str)
        
        # 將正確答案中的 LaTeX 分數字串 (例如 "\\frac{1}{2}") 轉換為 "1/2" 以便 Fraction 構造函數處理
        correct_x = Fraction(correct_x_str.replace(r"\\frac{", "").replace("}{", "/").replace("}", ""))
        correct_y = Fraction(correct_y_str.replace(r"\\frac{", "").replace("}{", "/").replace("}", ""))

        is_correct = (user_x == correct_x) and (user_y == correct_y)

    except ValueError:
        # 捕獲因用戶輸入不是有效數字或分數而引起的錯誤
        return {"correct": False, "result": "您的答案值包含無效的數字或分數格式，請檢查。", "next_question": True}

    result_text = f"完全正確！答案是 $x={correct_x_str}$, $y={correct_y_str}$。" if is_correct else f"答案不正確。正確答案應為：$x={correct_x_str}$, $y={correct_y_str}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}