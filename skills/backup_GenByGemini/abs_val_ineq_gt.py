# skills/abs_val_ineq_gt.py
import random

def format_linear_expression(a, b):
    """格式化線性表達式 ax + b"""
    if a == 0:
        return str(b) if b != 0 else "0"
    
    if a == 1:
        x_term = "x"
    elif a == -1:
        x_term = "-x"
    else:
        x_term = f"{a}x"
    
    if b == 0:
        return x_term
    elif b > 0:
        return f"{x_term} + {b}"
    else:
        return f"{x_term} - {abs(b)}"

def generate(level=1):
    """生成「絕對值不等式 (>=)」題目"""
    # |ax + b| >= c  =>  ax + b >= c  或  ax + b <= -c
    a = random.choice([1, -1, 2, -2])
    b = random.randint(-5, 5)
    c = random.randint(1, 10)
    # level 參數暫時未使用，但保留以符合架構

    # 解不等式
    # ax >= c - b  或  ax <= -c - b
    val1 = c - b
    val2 = -c - b

    if a > 0:
        sol1 = val1 / a  # x >= sol1
        sol2 = val2 / a  # x <= sol2
    else: # a < 0
        sol1 = val1 / a  # x <= sol1
        sol2 = val2 / a  # x >= sol2

    # 確保 sol1 和 sol2 形成兩個分離的區間
    # 如果 |ax+b| >= c 且 c > 0, 則解為 x >= (c-b)/a 或 x <= (-c-b)/a (當 a>0)
    # 這兩個解的邊界點不會重合
    
    # 格式化為易於閱讀的字串
    sol1_str = f"{sol1:.2f}".rstrip('0').rstrip('.')
    sol2_str = f"{sol2:.2f}".rstrip('0').rstrip('.')

    # 確定哪個是上限，哪個是下限
    if sol1 > sol2:
        upper_bound, lower_bound = sol1_str, sol2_str
    else:
        upper_bound, lower_bound = sol2_str, sol1_str

    expr = format_linear_expression(a, b)
    question_text = (
        f"請在下方的「數位計算紙」上，解絕對值不等式：|{expr}| ≥ {c}\n\n"
        f"請在數線上標示出解的範圍，畫完後，請點擊「AI 檢查」按鈕。"
    )
    
    inequality_solution = f"x ≥ {upper_bound} 或 x ≤ {lower_bound}"
    context_string = f"解絕對值不等式 |{expr}| ≥ {c}，其解為 {inequality_solution}"

    return {
        "question_text": question_text,
        "answer": None,
        "correct_answer": "graph",
        "context_string": context_string,
        "inequality_string": inequality_solution
    }

def check(user_answer, correct_answer):
    """檢查答案"""
    if correct_answer == "graph":
        return {
            "correct": False,
            "result": "請使用畫筆在數線上標示解的範圍，然後點選「AI 檢查」",
            "next_question": False
        }
    
    return {"correct": False, "result": "此題型需要圖形作答。"}