# skills/abs_val_ineq_lt.py
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
    """生成「絕對值不等式 (<)」題目"""
    # |ax + b| < c  => -c < ax + b < c
    a = random.choice([1, -1, 2, -2])
    b = random.randint(-5, 5)
    c = random.randint(1, 10)
    # level 參數暫時未使用，但保留以符合架構

    # 解不等式
    # -c < ax + b < c
    # -c - b < ax < c - b
    
    lower_bound_val = -c - b
    upper_bound_val = c - b

    if a > 0:
        sol_lower = lower_bound_val / a
        sol_upper = upper_bound_val / a
    else:
        # a 是負數，不等式方向改變
        sol_lower = upper_bound_val / a
        sol_upper = lower_bound_val / a

    # 格式化為易於閱讀的字串
    sol_lower_str = f"{sol_lower:.2f}".rstrip('0').rstrip('.')
    sol_upper_str = f"{sol_upper:.2f}".rstrip('0').rstrip('.')

    expr = format_linear_expression(a, b)
    question_text = (
        f"請在下方的「數位計算紙」上，解絕對值不等式：|{expr}| < {c}\n\n"
        f"請在數線上標示出解的範圍，畫完後，請點擊「AI 檢查」按鈕。"
    )
    context_string = f"解絕對值不等式 |{expr}| < {c}，其解為 {sol_lower_str} < x < {sol_upper_str}"

    return {
        "question_text": question_text,
        "answer": None,
        "correct_answer": "graph",
        "context_string": context_string,
        "inequality_string": f"{sol_lower_str} < x < {sol_upper_str}"
    }

def check(user_answer, correct_answer):
    """檢查答案"""
    if correct_answer == "graph":
        return {
            "correct": False,
            "result": "請使用畫筆在數線上標示解的範圍，然後點選「AI 檢查」",
            "next_question": False
        }
    
    # 理論上不會執行到這裡，因為這種類型題目都是圖形題
    return {"correct": False, "result": "此題型需要圖形作答。"}