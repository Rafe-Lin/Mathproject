# skills/point_slope_form.py
import random
import fractions

def format_general_equation(a, b, c):
    """將 ax + by + c = 0 格式化為字串"""
    terms = []
    # 為了標準化，讓 x 項係數為正
    if a < 0 or (a == 0 and b < 0):
        a, b, c = -a, -b, -c
    if a != 0:
        if a == 1: terms.append("x")
        elif a == -1: terms.append("-x")
        else: terms.append(f"{a}x")
    if b != 0:
        sign = " + " if b > 0 else " - "
        abs_b = abs(b)
        if abs_b == 1: terms.append(f"{sign}y")
        else: terms.append(f"{sign}{abs_b}y")
    if c != 0:
        sign = " + " if c > 0 else " - "
        terms.append(f"{sign}{abs(c)}")
    
    # 處理 ax+by=0 的情況
    if not terms: return "0 = 0"
    
    return "".join(terms).lstrip(" +") + " = 0"

def generate(level=1):
    """
    生成一道「點斜式」題目
    """
    # level 參數暫時未使用，但保留以符合架構
    # 隨機生成點 (x1, y1)
    x1 = random.randint(-5, 5)
    y1 = random.randint(-5, 5)

    # 隨機生成斜率 m = num/den
    m = fractions.Fraction(random.randint(-5, 5), random.randint(1, 3))
    m_num = m.numerator
    m_den = m.denominator

    # 點斜式: y - y1 = m(x - x1)
    # 轉換為一般式: m(x - x1) - (y - y1) = 0
    # (num/den)(x - x1) - (y - y1) = 0
    # num(x - x1) - den(y - y1) = 0
    # num*x - den*y - num*x1 + den*y1 = 0
    a = m_num
    b = -m_den
    c = -m_num * x1 + m_den * y1

    # 格式化斜率字串
    m_str = str(m.numerator) if m.denominator == 1 else f"{m.numerator}/{m.denominator}"

    question_text = (
        f"已知直線 L 通過點 P({x1}, {y1})，且斜率為 {m_str}。\n"
        f"請寫出直線 L 的一般式方程式 (ax+by+c=0)。"
    )
    
    correct_answer = format_general_equation(a, b, c)
    context_string = f"求過點 P({x1}, {y1}) 且斜率為 {m_str} 的直線方程式"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    """檢查使用者輸入的方程式是否正確，考慮係數倍數。"""
    import re

    def parse_equation(eq_str):
        eq_str = eq_str.replace(" ", "").replace("=0", "")
        eq_str = eq_str.replace("+", " +").replace("-", " -")
        
        a, b, c = 0, 0, 0
        
        # 匹配 x, y 和常數項
        x_match = re.search(r'([+-]?\d*)x', eq_str)
        if x_match:
            coeff = x_match.group(1)
            if coeff in ['+', '']: a = 1
            elif coeff == '-': a = -1
            else: a = int(coeff)

        y_match = re.search(r'([+-]?\d*)y', eq_str)
        if y_match:
            coeff = y_match.group(1)
            if coeff in ['+', '']: b = 1
            elif coeff == '-': b = -1
            else: b = int(coeff)

        const_match = re.findall(r'([+-]\d+)(?!x)(?!y)', eq_str)
        c = sum(int(num) for num in const_match)

        return a, b, c

    try:
        ua, ub, uc = parse_equation(user_answer)
        ca, cb, cc = parse_equation(correct_answer)

        # 檢查係數是否成比例
        ratios = [ua/ca if ca!=0 else 0, ub/cb if cb!=0 else 0, uc/cc if cc!=0 else 0]
        non_zero_ratios = [r for r in ratios if r != 0]
        if all(abs(r - non_zero_ratios[0]) < 1e-9 for r in non_zero_ratios):
            return {"correct": True, "result": f"完全正確！答案是 {correct_answer}。"}
    except (ValueError, IndexError, ZeroDivisionError):
        pass # 解析失敗或比例計算出錯

    if user_answer.replace(" ", "") == correct_answer.replace(" ", ""):
        return {"correct": True, "result": f"完全正確！答案是 {correct_answer}。"}
    else:
        return {"correct": False, "result": f"答案不正確。正確答案是：{correct_answer}"}