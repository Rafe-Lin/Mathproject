# skills/vertex_max_min.py
import random

def format_general_form(a, b, c):
    """將 y = ax² + bx + c 格式化為字串"""
    terms = []
    # x^2 term
    if a == 1:
        terms.append("x²")
    elif a == -1:
        terms.append("-x²")
    else:
        terms.append(f"{a}x²")
    
    # x term
    if b != 0:
        sign = " + " if b > 0 else " - "
        abs_b = abs(b)
        terms.append(f"{sign}{abs_b}x")

    # constant term
    if c != 0:
        sign = " + " if c > 0 else " - "
        abs_c = abs(c)
        terms.append(f"{sign}{abs_c}")
        
    return "y = " + "".join(terms).lstrip(" +")
def format_vertex_form(a, h, k):
    """將 y = a(x-h)² + k 格式化為字串"""
    # a part
    if a == 1:
        a_str = ""
    elif a == -1:
        a_str = "-"
    else:
        a_str = str(a)

    # (x-h) part
    if h == 0:
        h_part = "x²"
    else:
        sign = "-" if h > 0 else "+"
        abs_h = abs(h)
        h_part = f"(x {sign} {abs_h})²"

    # k part
    if k == 0:
        k_str = ""
    else:
        sign = "+" if k > 0 else "-"
        abs_k = abs(k)
        k_str = f" {sign} {abs_k}"

    return f"y = {a_str}{h_part}{k_str}".strip()

def generate(level=1):
    """
    生成一道「頂點式與極值計算」題目
    根據頂點式，判斷並求出函數的最大值或最小值 k。
    """
    # level 參數暫時未使用，但保留以符合架構
    # 隨機決定題目類型：已配方 (vertex) 或未配方 (general)
    question_type = random.choice(['vertex', 'general'])

    # 隨機生成頂點式 y = a(x-h)^2 + k 的參數
    a = random.choice([-4, -3, -2, -1, 1, 2, 3, 4])
    h = random.randint(-5, 5)
    k = random.randint(-10, 10)

    # 根據 a 的正負決定是最大值還是最小值
    if a > 0:
        extreme_type = "最小值"
    else:
        extreme_type = "最大值"

    if question_type == 'vertex':
        # 題目類型：已配方好的頂點式
        vertex_form_str = format_vertex_form(a, h, k)
        question_text = f"請問二次函數 {vertex_form_str} 的{extreme_type}是多少？"
        context_string = f"求二次函數 {vertex_form_str} 的{extreme_type}。"
    else: # 'general'
        # 題目類型：未配方的一般式，需要學生自己配方
        # 展開 y = a(x^2 - 2hx + h^2) + k = ax^2 - 2ahx + ah^2 + k
        b = -2 * a * h
        c = a * h**2 + k

        general_form_str = format_general_form(a, b, c)
        question_text = f"請問二次函數 {general_form_str} 的{extreme_type}是多少？\n\n(請先使用配方法將其轉換為頂點式，再判斷極值)"
        context_string = f"將 {general_form_str} 配方後，求其{extreme_type}。"

    # 正確答案就是 k
    correct_answer = str(k)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    """
    檢查使用者輸入的極值是否正確。
    """
    user = user_answer.strip()
    correct = str(correct_answer).strip()
    if user == correct:
        return {"correct": True, "result": f"完全正確！{correct_answer} 就是答案。"}
    else:
        return {"correct": False, "result": f"答案不正確。正確答案是：{correct_answer}"}