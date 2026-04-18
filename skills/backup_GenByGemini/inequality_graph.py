# skills/inequality_graph.py
import random

def format_linear_equation_lhs(a, b):
    """
    格式化 ax + by 的左邊字串，處理正負號與係數為 1/-1 的情況
    """
    terms = []
    if a != 0:
        if a == 1:
            terms.append("x")
        elif a == -1:
            terms.append("-x")
        else:
            terms.append(f"{a}x" if a > 0 else f"{a}x")
    if b != 0:
        if b == 1:
            terms.append("+ y")
        elif b == -1:
            terms.append("- y")
        else:
            terms.append(f" + {b}y" if b > 0 else f" - {abs(b)}y")
    if not terms:
        return "0"
    return "".join(terms).lstrip(" +")  # 移除開頭多餘的 +

def generate(level=1):
    """
    生成一道「二元一次不等式圖解」題目
    回傳格式與專案相容：
        - question_text: 前端顯示
        - inequality_string: 傳給 AI 判斷正確性
        - correct_answer: "graph"（標記為圖形題）
    """
    # level 參數暫時未使用，但保留以符合架構
    # 隨機生成 a, b, c
    a = random.randint(-5, 5)
    b = random.randint(-5, 5)
    while a == 0 and b == 0:  # 避免 0x + 0y
        a = random.randint(-5, 5)
        b = random.randint(-5, 5)
    c = random.randint(-9, 9)
    while c == 0:  # 避免 =0 太簡單
        c = random.randint(-9, 9)

    sign = random.choice(['>', '<', '>=', '<='])

    # 格式化左邊：ax + by
    inequality_lhs = format_linear_equation_lhs(a, b)

    # 格式化常數項
    c_str = ""
    if c > 0:
        c_str = f" + {c}"
    elif c < 0:
        c_str = f" - {abs(c)}"

    # 完整不等式（顯示用）
    inequality_expression = f"{inequality_lhs}{c_str}"
    full_inequality_string = f"{inequality_expression} {sign} 0"

    # 題目文字
    question_text = (
        f"請在下方的「數位計算紙」上，圖示二元一次不等式：\n\n"
        f"{full_inequality_string}\n\n"
        f"畫完後，請點擊「AI 檢查」按鈕。"
    )

    return {
        "question_text": question_text,
        "inequality_string": full_inequality_string,
        "correct_answer": "graph",
        "answer": None  # ← 必須加這行！
    }

def check(user_answer, correct_answer):
    """
    圖形題不走文字批改，由前端觸發 AI 分析
    """
    return {
        "correct": False,
        "result": "請使用畫筆繪製可行域，然後點選「AI 檢查」",
        "next_question": False
    }