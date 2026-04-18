# skills/parallel_lines_slope.py
import random
import fractions

def format_line_equation(m, c, name):
    """將 y = mx + c 格式化為 L: y = ..."""
    m_str = ""
    if m.denominator == 1:
        if m.numerator == 1: m_str = "x"
        elif m.numerator == -1: m_str = "-x"
        elif m.numerator != 0: m_str = f"{m.numerator}x"
    else:
        # 處理分數，將負號提出
        if m.numerator < 0:
            # 如果斜率是負分數，格式化為 "- (num/den)x"
            m_str = f"- ({abs(m.numerator)}/{m.denominator})x"
        else:
            # 如果斜率是正分數，格式化為 "(num/den)x"
            m_str = f"({m.numerator}/{m.denominator})x"

    c_str = ""
    if c > 0: c_str = f" + {c}"
    elif c < 0: c_str = f" - {abs(c)}"
    
    return f"{name}: y = {m_str}{c_str}".replace("= x +", "= x + ").replace("= -x +", "= -x + ")

def generate(level=1):
    """
    生成一道「平行線斜率條件」題目
    """
    # level 參數暫時未使用，但保留以符合架構
    # 隨機決定兩線是否平行
    are_parallel = random.choice([True, False])

    # 生成第一條線的斜率和截距
    m1 = fractions.Fraction(random.randint(-5, 5), random.randint(1, 3))
    c1 = random.randint(-5, 5)

    if are_parallel:
        m2 = m1
        c2 = random.randint(-5, 5)
        while c2 == c1: # 確保不是同一條線
            c2 = random.randint(-5, 5)
        correct_answer = "是"
    else:
        m2 = fractions.Fraction(random.randint(-5, 5), random.randint(1, 3))
        while m2 == m1: # 確保斜率不同
            m2 = fractions.Fraction(random.randint(-5, 5), random.randint(1, 3))
        c2 = random.randint(-5, 5)
        correct_answer = "否"

    line1_str = format_line_equation(m1, c1, "L₁")
    line2_str = format_line_equation(m2, c2, "L₂")

    question_text = f"請問下列兩直線 {line1_str} 與 {line2_str} 是否互相平行？ (請回答 '是' 或 '否')"
    context_string = f"判斷 {line1_str} 與 {line2_str} 是否平行"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    """檢查使用者輸入的是/否是否正確"""
    user = user_answer.strip().lower()
    user_choice = '是' if user in ['是', 'yes', 'y', 'true', 't'] else '否' if user in ['否', 'no', 'n', 'false', 'f'] else None
    if user_choice is None: return {"correct": False, "result": "請回答 '是' 或 '否'。"}
    if user_choice == correct_answer: return {"correct": True, "result": f"完全正確！答案是「{correct_answer}」。"}
    else: return {"correct": False, "result": f"答案不正確。正確答案是「{correct_answer}」。"}