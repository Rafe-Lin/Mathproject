# skills/completing_square.py
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
        if abs_b == 1:
            terms.append(f"{sign}x")
        else:
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
    生成一道「二次函數配方法」題目
    """
    # level 參數暫時未使用，但保留以符合架構
    # 從頂點式 y = a(x-h)^2 + k 開始，反向展開以確保整數係數
    a = random.choice([-4, -3, -2, -1, 1, 2, 3, 4])
    h = random.randint(-5, 5)
    k = random.randint(-10, 10)
    # 展開 y = a(x^2 - 2hx + h^2) + k = ax^2 - 2ahx + ah^2 + k
    b = -2 * a * h
    c = a * h**2 + k

    # 組裝題目和答案
    general_form = format_general_form(a, b, c)
    vertex_form = format_vertex_form(a, h, k)

    question_text = (
        f"請在下方的「數位計算紙」上，使用配方法將二次函數 {general_form} 轉換為頂點式 y = a(x-h)²+k。\n\n"
        f"完成後，請點擊「AI 檢查」按鈕。"
    )
    context_string = f"將 {general_form} 配方成 {vertex_form}"

    return {
        "question_text": question_text,
        "answer": None,
        "correct_answer": "graph",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    """
    圖形題不走文字批改，由前端觸發 AI 分析。
    """
    return {
        "correct": False,
        "result": "請在數位計算紙上寫下您的計算過程，然後點選「AI 檢查」。",
        "next_question": False
    }