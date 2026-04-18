import random
import math

# A helper function to check for perfect squares
def is_perfect_square(n):
    if n < 0:
        return False
    if n == 0:
        return True
    x = int(math.sqrt(n))
    return x * x == n

# Problem Type 1: Number/Age Problems
def generate_age_problem():
    """Generates a word problem related to age or numbers."""
    name = random.choice(["小翊", "小妍", "小鈺", "阿賢", "小歐"])
    
    # We need roots r1 (valid answer) and r2 (extraneous, negative)
    # Equation form: x(x - diff) = product
    # x^2 - diff*x - product = 0
    # From roots: diff = r1 + r2, product = -r1*r2
    # We need r1 > diff, which means r1 > r1+r2 -> r2 < 0. This is always true if r2 is negative.
    # We also set r1 > |r2| to make diff positive, which is more common.
    
    r1 = random.randint(12, 25)
    r2 = -random.randint(2, r1 - 2)

    diff = r1 + r2
    product = -r1 * r2
    
    context_type = random.choice(['age', 'number'])
    if context_type == 'age':
        subject = f"{name}的年齡"
        unit = "歲"
        invalid_reason = "年齡不可能為負數"
        question_text = f"有個謎題是這樣：「將{name}今年的年齡和 ${diff}$ 年前的年齡相乘，得到的數字是 ${product}$。」請問{name}今年是幾歲？"
    else:
        subject = "這個數字"
        unit = ""
        invalid_reason = "數字需為正數"
        question_text = f"{name}在玩一個數字遊戲。規則是「將一個正數和比該數字小 ${diff}$ 的另一個數相乘，結果為 ${product}$」。如果{name}成功找到了這個數字，請問這個數字是多少？"

    correct_answer = str(r1)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

# Problem Type 2: Price/Quantity/Revenue Problems
def generate_price_revenue_problem():
    """Generates a word problem about price, quantity, and revenue."""
    item = random.choice(["鬆餅", "雞排", "紀念吊飾", "筆記本"])
    
    # Equation: x(ax+b) = R => ax^2 + bx - R = 0
    # From roots r1 (price > 0), r2 < 0:
    # b = -a(r1+r2), R = -a*r1*r2
    a = random.randint(2, 4)
    r1 = random.randint(4, 10) * 5 # Price is a multiple of 5
    r2 = -random.randint(2, 6) * 5

    b = -a * (r1 + r2)
    R = -a * r1 * r2

    if b > 0:
        relation_str = f"是單價的 ${a}$ 倍多 ${b}$"
    else:
        relation_str = f"是單價的 ${a}$ 倍少 ${abs(b)}$"

    question_text = (
        f"某園遊會攤位販賣{item}，已知當天賣出{item}的數量{relation_str}個，"
        f"並獲得總收入 ${R}$ 元。試問{item}每個賣多少元？"
    )
    correct_answer = str(r1)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

# Problem Type 3: Geometry/Area Problems
def generate_area_problem():
    """Generates a word problem about the area of a rectangle."""
    place = random.choice(["農地", "客廳", "花園", "畫布"])
    unit = "公尺"
    
    # Equation: x(x+k) = A => x^2 + kx - A = 0
    # Roots r1 > 0 (length), r2 < 0
    # From roots: k = -(r1+r2), A = -r1*r2
    r1 = random.randint(5, 20)
    r2 = -random.randint(2, r1-1)
    
    k = -(r1 + r2)
    A = -r1 * r2
    
    if k > 0:
        relation_str = f"寬比長多 ${k}$ {unit}"
    else:
        relation_str = f"寬比長少 ${abs(k)}$ {unit}"

    question_text = (
        f"有一塊長方形{place}，其{relation_str}，且面積為 ${A}$ 平方{unit}。"
        f"試問此{place}的長是多少{unit}？"
    )
    correct_answer = str(r1)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

# Problem Type 4: Discount/Group Pricing Problems
def generate_group_pricing_problem():
    """Generates a group pricing problem that results in a perfect square quadratic equation."""
    activity = random.choice(["旅遊活動", "下午茶餐券", "團購商品"])
    
    # Recipe for perfect square solution (x-r)^2=0:
    # d: discount per unit, Q: base quantity, r: extra quantity
    # P = d * (Q + 2*r) (base price)
    # R = (Q+r)*(P-d*r) (total revenue)
    d = random.choice([50, 100])
    Q = random.randint(10, 40)
    r = random.randint(5, 15)
    
    P = d * (Q + 2 * r)
    R = (Q + r) * (P - d * r)

    question_text = (
        f"某單位舉辦{activity}，預定人數為 ${Q}$ 人，每人收費 ${P}$ 元。"
        f"當人數到達 ${Q}$ 人後，每增加 1 人，每人可便宜 ${d}$ 元。"
        f"若此次活動的總收入為 ${R}$ 元，則共有多少人參加？"
    )
    
    total_participants = Q + r
    correct_answer = str(total_participants)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

# Problem Type 5: "No Solution" / Quadratic Formula
def generate_no_solution_problem():
    """Generates a problem where the quadratic equation has no integer solutions."""
    item = random.choice(["水蜜桃", "蘋果", "紀念品", "書本"])
    
    # Equation: x^2 + bx - R = 0. We need D = b^2 + 4R to be non-square.
    b = 0
    R = 0
    discriminant = 0
    while True:
        b = random.randint(-4, 4) * 2 # Make b even for simpler roots
        R = random.randint(10, 50)
        discriminant = b**2 + 4*R
        if not is_perfect_square(discriminant):
            break
            
    # Story: x * (x + k1 - k2) = R, so b = k1 - k2
    k2 = random.randint(abs(b) + 2, abs(b) + 6)
    k1 = b + k2
    
    question_text = (
        f"廠商將一批{item}分裝成數個禮盒，已知每盒裝有相同顆數的{item}，"
        f"且禮盒的總數量比每盒{item}的顆數多 ${k1}$。若賣出 ${k2}$ 盒後，剩下 ${R}$ 顆{item}，"
        f"請問每盒裝有幾顆{item}？(若無正整數解，請回答「無解」)"
    )
    correct_answer = "無解"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    生成利用一元二次方程式解決應用問題的題目。
    介紹利用一元二次方程式解決應用問題的通用四個步驟：1. 設未知數：根據題意假設適當的未知數。2. 列方程式：依據問題情境列出一元二次方程式。3. 解方程式：使用因式分解、配方法或公式解來求解。4. 檢查並寫答案：驗證解是否符合現實情境的合理性，捨去不合理的解並寫出最終答案。此方法可應用於數字、價格、面積、收費等各種類型的問題。
    """
    problem_generators = [
        generate_age_problem,
        generate_price_revenue_problem,
        generate_area_problem,
        generate_group_pricing_problem,
        generate_no_solution_problem
    ]
    
    return random.choice(problem_generators)()

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip()
    
    is_correct = False
    # Case-insensitive check for '無解'
    if correct_answer == "無解":
        if user_answer in ["無解", "无解", "no solution"]:
            is_correct = True
    else:
        try:
            # Compare numerically
            if float(user_answer) == float(correct_answer):
                is_correct = True
        except (ValueError, TypeError):
            # Handle other potential string mismatches if needed
            is_correct = (user_answer.upper() == correct_answer.upper())

    if is_correct:
        result_text = f"完全正確！答案是 ${correct_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer}$。"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}