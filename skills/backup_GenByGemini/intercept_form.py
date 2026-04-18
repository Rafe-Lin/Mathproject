# skills/intercept_form.py
import random

def generate(level=1):
    """
    生成一道「截距式」題目
    """
    # level 參數暫時未使用，但保留以符合架構
    # 隨機生成 x-截距 a 和 y-截距 b，確保不為 0
    a = random.randint(-7, 7)
    while a == 0: a = random.randint(-7, 7)
    b = random.randint(-7, 7)
    while b == 0: b = random.randint(-7, 7)

    question_text = (
        f"已知直線 L 的 x 截距為 {a}，y 截距為 {b}。\n"
        f"請寫出直線 L 的截距式方程式 (x/a + y/b = 1)。"
    )
    
    # 格式化答案
    term1 = f"x/{a}"
    
    if b < 0:
        term2 = f" - y/{abs(b)}"
    else:
        term2 = f" + y/{b}"

    correct_answer = f"{term1}{term2} = 1".replace("+ -", "- ")

    context_string = f"求 x 截距為 {a} 且 y 截距為 {b} 的直線方程式"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    """檢查使用者輸入的方程式是否正確，不受項次順序影響。"""
    import re

    def parse_intercepts(eq_str):
        eq_str = eq_str.replace(" ", "").split('=')[0]
        x_intercept, y_intercept = None, None
        
        # 匹配 x/a
        x_match = re.search(r'x/(-?\d+)', eq_str)
        if x_match: x_intercept = int(x_match.group(1))
        
        # 匹配 y/b
        y_match = re.search(r'y/(-?\d+)', eq_str)
        if y_match: y_intercept = int(y_match.group(1))
        
        return x_intercept, y_intercept

    try:
        user_x, user_y = parse_intercepts(user_answer)
        correct_x, correct_y = parse_intercepts(correct_answer)
        if user_x == correct_x and user_y == correct_y:
            return {"correct": True, "result": f"完全正確！答案是 {correct_answer}。"}
    except (ValueError, TypeError):
        pass

    if user_answer.replace(" ", "") == correct_answer.replace(" ", ""):
        return {"correct": True, "result": f"完全正確！答案是 {correct_answer}。"}
    else:
        return {"correct": False, "result": f"答案不正確。正確答案是：{correct_answer}"}