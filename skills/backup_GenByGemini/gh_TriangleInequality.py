import random
from fractions import Fraction
import math
import re

def generate(level=1):
    """
    生成「三角不等式」相關題目。
    包含：
    1. 幾何意義：判斷三邊長是否能構成三角形。
    2. 幾何意義：給定兩邊長，求第三邊長的範圍。
    3. 實數形式：比較 $|a+b|$ 和 $|a|+|b|$ 的大小。
    4. 實數形式：求等號成立的條件 ($ab \\ge 0$)。
    """
    problem_type_choices = [
        'geometric_check_sides', 
        'geometric_range_third_side', 
        'absolute_value_compare', 
        'absolute_value_equality_condition'
    ]
    problem_type = random.choice(problem_type_choices)
    
    if problem_type == 'geometric_check_sides':
        return generate_geometric_check_sides_problem()
    elif problem_type == 'geometric_range_third_side':
        return generate_geometric_range_third_side_problem()
    elif problem_type == 'absolute_value_compare':
        return generate_absolute_value_compare_problem()
    elif problem_type == 'absolute_value_equality_condition':
        return generate_absolute_value_equality_condition_problem()

def generate_geometric_check_sides_problem():
    """
    題型：給定三邊長，判斷是否能構成三角形。
    """
    side_a = random.randint(2, 12)
    side_b = random.randint(2, 12)
    
    can_form_triangle = random.choice([True, False])
    
    if can_form_triangle:
        # 生成 side_c 使其能構成一個非退化三角形 (a+b > c, a+c > b, b+c > a)
        # 這意味著 abs(a-b) < c < a+b
        lower_bound = abs(side_a - side_b) + 1
        upper_bound = side_a + side_b - 1
        
        # 確保 random.randint 的範圍有效，避免 lower_bound > upper_bound
        # 雖然在目前的數字範圍下不太會發生，但以防萬一
        if lower_bound > upper_bound:
            # 如果無法找到符合條件的c，則重新生成a和b
            # 這是極端情況，例如a=1, b=1，則範圍是0<c<2，c=1
            # 但我們設定的最小邊長是2，所以此處通常是有效的
            side_c = random.randint(1, 20) # Fallback to a wider range and let conditions below filter
            # Re-calculating to ensure strict non-degenerate triangle
            if not (side_a + side_b > side_c and side_a + side_c > side_b and side_b + side_c > side_a):
                return generate_geometric_check_sides_problem() # Recursive call to retry
        else:
            side_c = random.randint(lower_bound, upper_bound)
        
        correct_answer_str = "是"
        answer_explanation = (
            f"根據三角不等式，三角形任兩邊之和必須嚴格大於第三邊。在此例中，三邊長為 ${side_a}$、${side_b}$、${side_c}$。<br>"
            f"$1) \\quad {side_a} + {side_b} = {side_a + side_b} > {side_c}$ (成立)<br>"
            f"$2) \\quad {side_a} + {side_c} = {side_a + side_c} > {side_b}$ (成立)<br>"
            f"$3) \\quad {side_b} + {side_c} = {side_b + side_c} > {side_a}$ (成立)<br>"
            f"所有條件皆符合，因此可以構成一個非退化三角形。"
        )
    else:
        # 生成 side_c 使其無法構成三角形
        # 可能是 a+b <= c (和太小) 或 c 太小以至於 a+c <= b 或 b+c <= a (差太大)
        violation_choice = random.choice(['sum_too_small', 'side_too_small_relative'])

        if violation_choice == 'sum_too_small': # a+b <= c
            side_c = random.randint(side_a + side_b, side_a + side_b + 5)
            violated_sum_val = side_a + side_b
            violated_side_val = side_c
            violated_sides_pair = f"${side_a}$ 和 ${side_b}$"
            violation_detail = f"${side_a} + {side_b} = {violated_sum_val}$，它不嚴格大於 ${violated_side_val}$ (第三邊)。"
        else: # c too small relative to difference: a+c <= b or b+c <= a
            # 確保 side_a 和 side_b 有足夠的差異以創建明顯的違反情況
            if abs(side_a - side_b) < 2:
                side_a = random.randint(5, 12)
                side_b = random.randint(2, side_a - 3) # 確保 side_a > side_b 且有足夠的差值
            
            # side_c 需要滿足 c <= abs(side_a - side_b)
            upper_bound_for_c = abs(side_a - side_b)
            side_c = random.randint(1, upper_bound_for_c if upper_bound_for_c >= 1 else 1) 
            # 確保 random.randint(1, x) 的 x 至少為 1

            if side_a + side_c <= side_b: # 例如，a=2, b=10, c=3。2+3 <= 10。 (a+c 不 > b)
                violated_sum_val = side_a + side_c
                violated_side_val = side_b
                violated_sides_pair = f"${side_a}$ 和 ${side_c}$"
                violation_detail = f"${side_a} + {side_c} = {violated_sum_val}$，它不嚴格大於 ${violated_side_val}$ (第三邊)。"
            else: # 必須是 side_b + side_c <= side_a
                violated_sum_val = side_b + side_c
                violated_side_val = side_a
                violated_sides_pair = f"${side_b}$ 和 ${side_c}$"
                violation_detail = f"${side_b} + {side_c} = {violated_sum_val}$，它不嚴格大於 ${violated_side_val}$ (第三邊)。"

        correct_answer_str = "否"
        answer_explanation = (
            f"根據三角不等式，三角形任兩邊之和必須嚴格大於第三邊。在此例中，三邊長為 ${side_a}$、${side_b}$、${side_c}$。<br>"
            f"然而，{violated_sides_pair}的和是 ${violated_sum_val}$，而第三邊是 ${violated_side_val}$。<br>"
            f"由於 {violation_detail}，條件不符合，因此無法構成一個非退化三角形。"
        )

    question_text = f"已知三線段長度分別為 ${side_a}$、${side_b}$、${side_c}$，請問它們能否構成一個三角形？(請回答「是」或「否」)"
    
    return {
        "question_text": question_text,
        "answer": correct_answer_str,
        "correct_answer": correct_answer_str,
        "explanation": answer_explanation
    }

def generate_geometric_range_third_side_problem():
    """
    題型：給定兩邊長，求第三邊長的範圍。
    """
    side_a = random.randint(3, 15)
    side_b = random.randint(3, 15)

    # 對於非退化三角形，第三邊 c 的範圍為 |a-b| < c < a+b
    min_c = abs(side_a - side_b)
    max_c = side_a + side_b

    question_text = (
        f"已知三角形的兩邊長分別為 ${side_a}$ 和 ${side_b}$，請問第三邊長 ${r'c'}$ 的範圍為何？"
        f"(請使用不等式表示，例如：$3 < c < 7$，變數請用 ${r'c'}$)"
    )
    
    correct_answer_simplified = f"{min_c} < c < {max_c}"

    explanation = (
        f"根據三角不等式，三角形任兩邊之和必須大於第三邊，任兩邊之差的絕對值必須小於第三邊。<br>"
        f"因此，如果兩邊長為 ${side_a}$ 和 ${side_b}$，則第三邊長 ${r'c'}$ 必須滿足：<br>"
        f"$|{side_a} - {side_b}| < c < {side_a} + {side_b}$<br>"
        f"$|{abs(side_a - side_b)}| < c < {side_a + side_b}$<br>"
        f"所以，第三邊長 ${r'c'}$ 的範圍是 ${min_c} < c < {max_c}$。"
    )

    return {
        "question_text": question_text,
        "answer": correct_answer_simplified,
        "correct_answer": correct_answer_simplified,
        "explanation": explanation
    }

def generate_absolute_value_compare_problem():
    """
    題型：給定兩實數 a, b，比較 $|a+b|$ 和 $|a|+|b|$ 的大小。
    """
    a = random.randint(-10, 10)
    b = random.randint(-10, 10)

    # 避免 a 和 b 同時為 0 的平凡情況
    while a == 0 and b == 0:
        a = random.randint(-10, 10)
        b = random.randint(-10, 10)

    val_abs_sum = abs(a + b)
    val_sum_abs = abs(a) + abs(b)

    if val_abs_sum < val_sum_abs:
        relationship_text = "小於"
    elif val_abs_sum == val_sum_abs:
        relationship_text = "等於"
    # 根據三角不等式，val_abs_sum > val_sum_abs 的情況不會發生

    question_text = (
        f"已知 $a = {a}$，$b = {b}$，請問 $|a+b|$ 和 $|a|+|b|$ 之間有什麼關係？"
        f"(請填寫「大於」、「小於」或「等於」)"
    )
    correct_answer_str = relationship_text

    explanation = (
        f"根據三角不等式的實數形式，對於任意實數 $a$ 和 $b$，有 $|a+b| \\le |a| + |b|$。<br>"
        f"在此例中，$a = {a}$，$b = {b}$：<br>"
        f"$|a+b| = |{a} + {b}| = |{a+b}| = {val_abs_sum}$<br>"
        f"$|a|+|b| = |{a}| + |{b}| = {abs(a)} + {abs(b)} = {val_sum_abs}$<br>"
        f"因此， $|a+b|$ {relationship_text} $|a|+|b|$。"
    )
    
    return {
        "question_text": question_text,
        "answer": correct_answer_str,
        "correct_answer": correct_answer_str,
        "explanation": explanation
    }

def generate_absolute_value_equality_condition_problem():
    """
    題型：求實數形式三角不等式等號成立的條件。
    """
    var1 = random.choice(['x', 'y', 'm', 'n'])
    var2 = random.choice(['p', 'q', 'r', 's'])
    while var1 == var2: # 確保變數不同
        var2 = random.choice(['p', 'q', 'r', 's'])
    
    # 將變數字母按字典順序排序，以便在答案比較時保持一致性 (如 'ab' vs 'ba')
    sorted_vars = sorted([var1, var2])
    prod_vars_str = "".join(sorted_vars)

    question_text = (
        f"對於任意實數 ${var1}$ 和 ${var2}$，三角不等式 $|{var1}+{var2}| \\le |{var1}| + |{var2}|$ 中等號成立的條件為何？"
        f"(請使用不等式表示，例如：$ab \\ge 0$)"
    )
    
    correct_answer_simplified = f"{prod_vars_str} >= 0"

    explanation = (
        f"三角不等式的實數形式為 $|A+B| \\le |A| + |B|$。<br>"
        f"等號成立的條件是 $A$ 和 $B$ 同號或其中一個為零。<br>"
        f"這可以用它們的乘積為非負數來表示，即 $A B \\ge 0$。"
        f"在本題中，即為 ${var1}{var2} \\ge 0$。"
    )
    
    return {
        "question_text": question_text,
        "answer": correct_answer_simplified,
        "correct_answer": correct_answer_simplified,
        "explanation": explanation
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip() # 這是 generate() 傳回的簡化答案字串
    
    is_correct = False
    result_text = ""

    # 將使用者答案和正確答案正規化為小寫並移除空格，以便比較
    user_normalized = user_answer.replace(" ", "").lower()
    correct_normalized = correct_answer.replace(" ", "").lower()

    # 1. "是" / "否" 題型
    if correct_normalized in ["是", "否"]:
        is_correct = (user_normalized == correct_normalized)
        
    # 2. "大於", "小於", "等於" 題型
    elif correct_normalized in ["大於", "小於", "等於"]:
        is_correct = (user_normalized == correct_normalized)
        
    # 3. 不等式範圍題型: "min < var < max"
    # 例如: "3 < c < 7"
    elif re.match(r"(-?\d+)\s*<\s*[a-zA-Z]\s*<\s*(-?\d+)", correct_normalized):
        user_match = re.match(r"(-?\d+)\s*<\s*([a-zA-Z])\s*<\s*(-?\d+)", user_normalized)
        correct_match = re.match(r"(-?\d+)\s*<\s*([a-zA-Z])\s*<\s*(-?\d+)", correct_normalized)
        
        if user_match and correct_match:
            try:
                user_min, user_max = int(user_match.group(1)), int(user_match.group(3))
                correct_min, correct_max = int(correct_match.group(1)), int(correct_match.group(3))
                
                # 比較數值範圍，變數名稱允許不同 (但一般題目會指定變數名稱)
                if user_min == correct_min and user_max == correct_max:
                    is_correct = True
            except ValueError:
                pass # 解析數字失敗
        
    # 4. 等號成立條件題型: "var1var2 >= 0"
    # 例如: "ab >= 0"
    elif re.match(r"([a-zA-Z]{1,2})\s*(>=|=>|=>=)\s*0", correct_normalized):
        # 允許使用者輸入 'x*y >= 0' 或 'yx >= 0' 等形式
        user_match = re.match(r"([a-zA-Z*]{1,3})\s*(>=|=>|=>=)\s*0", user_normalized)
        correct_match = re.match(r"([a-zA-Z]{1,2})\s*(>=|=>|=>=)\s*0", correct_normalized)
        
        if user_match and correct_match:
            user_vars_raw = user_match.group(1)
            correct_vars_raw = correct_match.group(1)

            # 正規化變數字串 (移除 '*' 符號，並排序字母以處理 'ab' vs 'ba' 的情況)
            user_vars_sorted = ''.join(sorted(list(user_vars_raw.replace('*', ''))))
            correct_vars_sorted = ''.join(sorted(list(correct_vars_raw.replace('*', ''))))
            
            if user_vars_sorted == correct_vars_sorted:
                is_correct = True

    # 根據判斷結果生成回饋訊息
    if is_correct:
        # 對於需要 LaTeX 格式的答案，進行轉換以在回饋中顯示
        if re.match(r"(-?\d+)\s*<\s*[a-zA-Z]\s*<\s*(-?\d+)", correct_answer):
            display_answer = correct_answer.replace("<", "< ").replace(">", " >") # 加入空格美化 LaTeX
            result_text = f"完全正確！答案是 ${display_answer}$。"
        elif re.match(r"([a-zA-Z]{1,2})\s*(>=|=>|=>=)\s*0", correct_answer):
            display_answer = correct_answer.replace(">=", r"\\ge ") # 轉換為 LaTeX 的大於等於符號
            result_text = f"完全正確！答案是 ${display_answer}$。"
        else:
            result_text = f"完全正確！答案是 {correct_answer}。"
    else:
        if re.match(r"(-?\d+)\s*<\s*[a-zA-Z]\s*<\s*(-?\d+)", correct_answer):
            display_answer = correct_answer.replace("<", "< ").replace(">", " >")
            result_text = f"答案不正確。正確答案應為：${display_answer}$"
        elif re.match(r"([a-zA-Z]{1,2})\s*(>=|=>|=>=)\s*0", correct_answer):
            display_answer = correct_answer.replace(">=", r"\\ge ")
            result_text = f"答案不正確。正確答案應為：${display_answer}$"
        else:
            result_text = f"答案不正確。正確答案應為：{correct_answer}"

    return {"correct": is_correct, "result": result_text, "next_question": True}