import random
from fractions import Fraction
import re

def generate(level=1):
    """
    生成「加減消去法」解二元一次聯立方程式相關題目。
    包含：
    1. 恰有一組解 (Unique solution)
    2. 無解 (No solution)
    3. 無限多組解 (Infinite solutions)
    """
    # Adjust difficulty based on level if needed.
    # For now, level doesn't significantly change coefficient ranges.
    
    problem_type = random.choice(['unique', 'no_solution', 'infinite_solutions'])
    
    if problem_type == 'unique':
        return generate_unique_solution_problem()
    elif problem_type == 'no_solution':
        return generate_no_solution_problem()
    else: # infinite_solutions
        return generate_infinite_solutions_problem()

def generate_unique_solution_problem():
    """
    生成恰有一組解的二元一次聯立方程式題目。
    策略：先設定整數解 (x0, y0)，再生成係數 a1, b1, a2, b2，
    然後計算 c1, c2。確保係數行列式 (a1*b2 - a2*b1) 不為零。
    """
    
    x0 = random.randint(-5, 5)
    y0 = random.randint(-5, 5)

    # 避免解為 (0,0) 時係數可能過於簡化，確保至少一個非零解或確保係數不全為零
    # 如果 (x0, y0) 為 (0,0)，通常方程式會變成 ax+by=0，比較特殊。
    # 這裡我們允許 (0,0) 作為解，但會確保係數本身足夠多樣。
    
    # 生成係數，確保行列式不為零且每個方程式至少有一個變數係數非零
    while True:
        a1 = random.randint(-5, 5)
        b1 = random.randint(-5, 5)
        a2 = random.randint(-5, 5)
        b2 = random.randint(-5, 5)

        # 確保每個方程式至少有一個變數的係數不為零
        if (a1 == 0 and b1 == 0) or (a2 == 0 and b2 == 0):
            continue

        # 確保係數行列式不為零，這樣才能保證有唯一解
        det = a1 * b2 - a2 * b1
        if det != 0:
            break
            
    c1 = a1 * x0 + b1 * y0
    c2 = a2 * x0 + b2 * y0

    # LaTeX 方程式字串生成
    eq1_str = _format_equation(a1, b1, c1, 'x', 'y')
    eq2_str = _format_equation(a2, b2, c2, 'x', 'y')

    question_text = (
        f"解下列二元一次聯立方程式：<br>"
        r"$\begin{cases} "
        f"{eq1_str} \\\\ "
        f"{eq2_str} "
        r"\end{cases}$"
    )
    
    # 儲存精確分數解
    correct_x = Fraction(x0)
    correct_y = Fraction(y0)
    
    # 呈現給使用者的答案形式
    answer_text = f"$x={correct_x}, y={correct_y}$"

    return {
        "question_text": question_text,
        "answer": answer_text,
        "correct_answer": {"x": correct_x, "y": correct_y, "type": "unique"}
    }

def generate_no_solution_problem():
    """
    生成無解的二元一次聯立方程式題目 (平行線)。
    策略：生成一個基礎方程式 ax + by = c。
    第二個方程式為 k*(ax + by) = k*c + diff，其中 diff 不為零。
    """
    
    a = random.randint(-5, 5)
    b = random.randint(-5, 5)
    c = random.randint(-10, 10)

    # 確保 a 和 b 不會同時為零
    while a == 0 and b == 0:
        a = random.randint(-5, 5)
        b = random.randint(-5, 5)

    k = random.choice([-3, -2, -1, 2, 3]) # 第二個方程式的乘數，避免為0或1
    
    # 確保 diff 不為零，這樣方程式才會無解 (平行但不重合)
    diff = random.randint(1, 5) * random.choice([-1, 1])
    
    a1, b1, c1 = a, b, c
    a2, b2, c2 = a * k, b * k, c * k + diff

    # LaTeX 方程式字串生成
    eq1_str = _format_equation(a1, b1, c1, 'x', 'y')
    eq2_str = _format_equation(a2, b2, c2, 'x', 'y')

    question_text = (
        f"解下列二元一次聯立方程式：<br>"
        r"$\begin{cases} "
        f"{eq1_str} \\\\ "
        f"{eq2_str} "
        r"\end{cases}$"
    )
    
    answer_text = "無解" 
    
    return {
        "question_text": question_text,
        "answer": answer_text,
        "correct_answer": {"type": "no_solution"}
    }

def generate_infinite_solutions_problem():
    """
    生成無限多組解的二元一次聯立方程式題目 (重合線)。
    策略：生成一個基礎方程式 ax + by = c。
    第二個方程式為 k*(ax + by) = k*c，其中 k 不為零。
    """
    
    a = random.randint(-5, 5)
    b = random.randint(-5, 5)
    c = random.randint(-10, 10)

    # 確保 a 和 b 不會同時為零
    while a == 0 and b == 0:
        a = random.randint(-5, 5)
        b = random.randint(-5, 5)
    
    k = random.choice([-3, -2, -1, 2, 3]) # 第二個方程式的乘數，避免為0或1
    
    a1, b1, c1 = a, b, c
    a2, b2, c2 = a * k, b * k, c * k

    # LaTeX 方程式字串生成
    eq1_str = _format_equation(a1, b1, c1, 'x', 'y')
    eq2_str = _format_equation(a2, b2, c2, 'x', 'y')

    question_text = (
        f"解下列二元一次聯立方程式：<br>"
        r"$\begin{cases} "
        f"{eq1_str} \\\\ "
        f"{eq2_str} "
        r"\end{cases}$"
    )
    
    correct_params = {"type": "infinite_solutions"}

    # 依據係數表達 y 關於 x 或 x 關於 y
    if b1 != 0: # 如果 y 的係數不為零，表達 y 關於 x。x 為參數 't'
        correct_params["expr_var"] = "y"
        correct_params["param_var"] = "x"
        correct_params["slope"] = -Fraction(a1, b1)
        correct_params["intercept"] = Fraction(c1, b1)
        
        # 構造 y 關於 t 的表達式 (x=t)
        expr_parts = []
        if correct_params["slope"] != 0:
            if correct_params["slope"].denominator == 1:
                coeff_str = str(correct_params["slope"].numerator)
                if coeff_str == "1": expr_parts.append("t")
                elif coeff_str == "-1": expr_parts.append("-t")
                else: expr_parts.append(f"{coeff_str}t")
            else:
                expr_parts.append(r"\\frac{{{}}}{{{}}}t".format(correct_params["slope"].numerator, correct_params["slope"].denominator))
        
        if correct_params["intercept"] != 0:
            if correct_params["intercept"] > 0 and expr_parts and expr_parts[-1] != '-' : # Avoid "t+-2"
                expr_parts.append("+")
            if correct_params["intercept"].denominator == 1:
                expr_parts.append(str(correct_params["intercept"].numerator))
            else:
                expr_parts.append(r"\\frac{{{}}}{{{}}}".format(correct_params["intercept"].numerator, correct_params["intercept"].denominator))
        
        if not expr_parts: # 例如，如果 y=0
            expr_y_str = "0"
        else:
            expr_y_str = "".join(expr_parts)
            
        answer_text = f"$x=t, y={expr_y_str}$ ($t$為任意實數)"

    elif a1 != 0: # 如果 x 的係數不為零，表達 x 關於 y。y 為參數 't'
        correct_params["expr_var"] = "x"
        correct_params["param_var"] = "y"
        correct_params["slope"] = -Fraction(b1, a1)
        correct_params["intercept"] = Fraction(c1, a1)

        # 構造 x 關於 t 的表達式 (y=t)
        expr_parts = []
        if correct_params["slope"] != 0:
            if correct_params["slope"].denominator == 1:
                coeff_str = str(correct_params["slope"].numerator)
                if coeff_str == "1": expr_parts.append("t")
                elif coeff_str == "-1": expr_parts.append("-t")
                else: expr_parts.append(f"{coeff_str}t")
            else:
                expr_parts.append(r"\\frac{{{}}}{{{}}}t".format(correct_params["slope"].numerator, correct_params["slope"].denominator))
        
        if correct_params["intercept"] != 0:
            if correct_params["intercept"] > 0 and expr_parts and expr_parts[-1] != '-' : # Avoid "t+-2"
                expr_parts.append("+")
            if correct_params["intercept"].denominator == 1:
                expr_parts.append(str(correct_params["intercept"].numerator))
            else:
                expr_parts.append(r"\\frac{{{}}}{{{}}}".format(correct_params["intercept"].numerator, correct_params["intercept"].denominator))
        
        if not expr_parts: # 例如，如果 x=0
            expr_x_str = "0"
        else:
            expr_x_str = "".join(expr_parts)

        answer_text = f"$y=t, x={expr_x_str}$ ($t$為任意實數)"
    
    else: # 程式邏輯應避免此情況 (a1和b1同時為零且c1不為零)
        answer_text = "錯誤：無法形成解。" # Fallback, should not be reached
        
    correct_params["answer_text"] = answer_text # Store for feedback
    
    return {
        "question_text": question_text,
        "answer": answer_text,
        "correct_answer": correct_params
    }

def _format_equation(a, b, c, var_x='x', var_y='y'):
    """
    內部輔助函數：將係數格式化為 LaTeX 方程式字串 (例如：$3x+2y=8$)。
    """
    parts = []
    
    if a != 0:
        if a == 1:
            parts.append(f"{var_x}")
        elif a == -1:
            parts.append(f"-{var_x}")
        else:
            parts.append(f"{a}{var_x}")
            
    if b != 0:
        if b > 0 and parts: # 如果不是第一個項，則添加 '+'
            parts.append("+")
        if b == 1:
            parts.append(f"{var_y}")
        elif b == -1:
            parts.append(f"-{var_y}")
        else:
            parts.append(f"{b}{var_y}")
            
    if not parts: # 如果 a 和 b 都為 0
        return f"0 = {c}"
    
    return f"{''.join(parts)} = {c}"


def check(user_answer, correct_answer_dict):
    """
    檢查使用者答案是否正確。
    """
    user_answer = user_answer.strip().lower()
    feedback_text = ""
    is_correct = False

    ans_type = correct_answer_dict["type"]

    if ans_type == "unique":
        # 預期格式：x=VAL, y=VAL (順序可變，可含分數或小數)
        x_match = re.search(r"x\s*=\s*([+-]?\s*\d+(?:/\d+)?(?:\.\d+)?)", user_answer)
        y_match = re.search(r"y\s*=\s*([+-]?\s*\d+(?:/\d+)?(?:\.\d+)?)", user_answer)

        user_x = None
        user_y = None

        if x_match:
            try:
                user_x = Fraction(x_match.group(1).replace(' ', ''))
            except ValueError:
                pass
        if y_match:
            try:
                user_y = Fraction(y_match.group(1).replace(' ', ''))
            except ValueError:
                pass

        if user_x is not None and user_y is not None:
            if user_x == correct_answer_dict["x"] and user_y == correct_answer_dict["y"]:
                is_correct = True
                feedback_text = "完全正確！"
            else:
                feedback_text = f"答案不正確。正確答案應為：${correct_answer_dict['answer']}$"
        else:
            feedback_text = "請確認您的答案格式為 $x=值, y=值$。"
    
    elif ans_type == "no_solution":
        # 預期答案包含關鍵字 "無解" 或 "no solution"
        if "無解" in user_answer or "no solution" in user_answer.replace(" ", ""):
            is_correct = True
            feedback_text = "完全正確！此聯立方程式無解。"
        else:
            feedback_text = "答案不正確。此聯立方程式無解。"

    elif ans_type == "infinite_solutions":
        # 預期格式：x=t, y=f(t) 或 y=t, x=f(t)
        
        correct_expr_var = correct_answer_dict["expr_var"] 
        correct_param_var = correct_answer_dict["param_var"]
        correct_slope = correct_answer_dict["slope"]
        correct_intercept = correct_answer_dict["intercept"]

        # 嘗試解析使用者答案中的參數變數設定 (例如：x=t 或 y=t)
        param_t_match = re.search(r"({})\s*=\s*[tT]".format(correct_param_var), user_answer)
        
        if param_t_match: # 匹配到正確的參數變數
            # 尋找另一個變數的表達式
            other_var = 'y' if correct_param_var == 'x' else 'x'
            expr_match = re.search(r"({})\s*=\s*([+-]?\s*(?:(?:(?:\d+(?:/\d+)?(?:\.\d+)?)\s*\*)?[tT])|(?:(?:\d+(?:/\d+)?(?:\.\d+)?)\s*[tT])|(?:(?:\d+(?:/\d+)?(?:\.\d+)?)))".format(other_var), user_answer)
            
            if expr_match:
                user_expr_main = expr_match.group(2).replace(' ', '') # 清除空格
                
                # 為了穩健地從使用者表達式中提取斜率和截距，我們使用在 t=0 和 t=1 處求值的方法
                def evaluate_expr_for_t(expr_str, t_val):
                    try:
                        # 將分數形式例如 "1/2" 轉換為 Fraction(1,2)
                        expr_str = re.sub(r'(\d+)/(\d+)', r'Fraction(\1,\2)', expr_str)
                        # 將 't' 替換為實際數值
                        expr_str = expr_str.replace('t', f"({t_val})").replace('T', f"({t_val})")
                        # 執行求值，確保 Fraction 在 eval 環境中可用
                        return eval(expr_str, {}, {'Fraction': Fraction})
                    except Exception:
                        return None
                
                # 在 t=0 和 t=1 處求值
                val_at_0 = evaluate_expr_for_t(user_expr_main, 0)
                val_at_1 = evaluate_expr_for_t(user_expr_main, 1)

                if val_at_0 is not None and val_at_1 is not None:
                    user_intercept = Fraction(val_at_0)
                    user_slope = Fraction(val_at_1 - val_at_0)
                    
                    if user_slope == correct_slope and user_intercept == correct_intercept:
                        is_correct = True
                        feedback_text = "完全正確！此聯立方程式有無窮多組解。"
                    else:
                        feedback_text = f"答案不正確。正確答案應為：${correct_answer_dict['answer_text']}$"
                else:
                    feedback_text = "請確認您的答案格式為 $X=t, Y=f(t)$ 或 $Y=t, X=f(t)$，且 $f(t)$ 為線性的函數。"
            else:
                feedback_text = "請確認您的答案格式為 $X=t, Y=f(t)$ 或 $Y=t, X=f(t)$。"
        elif "無窮多組解" in user_answer or "無限多組解" in user_answer or "infinite solutions" in user_answer.replace(" ", ""):
            # 如果使用者只寫「無窮多組解」，雖然知道答案類型，但未提供特定形式的解
            feedback_text = f"雖然您知道有無窮多組解，但請以參數形式 ($x=t, y=f(t)$ 或 $y=t, x=f(t)$) 提供答案。正確答案應為：${correct_answer_dict['answer_text']}$"
        else:
            feedback_text = f"答案不正確。正確答案應為：${correct_answer_dict['answer_text']}$"

    # 若尚未生成反饋，則給出通用錯誤訊息
    if not feedback_text:
        feedback_text = f"答案不正確。正確答案應為：${correct_answer_dict['answer']}$"

    return {"correct": is_correct, "result": feedback_text, "next_question": True}