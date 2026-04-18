# skills/always_positive_cond.py
import random
from .utils import poly_to_string

def generate(level=1):
    """
    生成一道「二次函數恆正條件」題目
    """
    # level 參數暫時未使用，但保留以符合架構
    # 隨機決定此函數是否恆正
    is_always_positive = random.choice([True, False])

    if is_always_positive:
        # 構造一個恆正的二次函數 (a > 0, D < 0)
        # 從頂點式 a(x-h)²+k 開始，其中 a>0, k>0
        a = random.randint(1, 4)
        h = random.randint(-5, 5)
        k = random.randint(1, 10) # k > 0 確保頂點在 x 軸上方
        correct_answer = "是"
        context_explanation = "此函數開口向上 (a>0) 且頂點在 x 軸上方 (k>0)，因此判別式 D<0，故恆為正。"
    else:
        # 構造一個不恆正的二次函數
        # 可能是 a < 0 或 D >= 0
        if random.choice([True, False]):
            # 情況1: 開口向下 (a < 0)
            a = random.randint(-4, -1)
            h = random.randint(-5, 5)
            k = random.randint(-10, 10)
            context_explanation = "此函數開口向下 (a<0)，因此不可能恆為正。"
        else:
            # 情況2: 開口向上但與 x 軸有交點 (a > 0, D >= 0)
            # 從頂點式 a(x-h)²+k 開始，其中 a>0, k<=0
            a = random.randint(1, 4)
            h = random.randint(-5, 5)
            k = random.randint(-10, 0) # k <= 0 確保頂點在 x 軸上或下方
            context_explanation = "此函數開口向上 (a>0) 但頂點在 x 軸上或下方 (k<=0)，因此判別式 D>=0，故不恆為正。"
        correct_answer = "否"

    # 展開 y = a(x-h)² + k = ax² - 2ahx + ah² + k
    b = -2 * a * h
    c = a * h**2 + k

    poly_str = f"f(x) = {poly_to_string([a, b, c])}"

    question_text = (
        f"請問二次函數 {poly_str} 的值是否恆為正？\n\n"
        f"提示：請檢查開口方向 (a) 與判別式 (D = b²-4ac) 的正負。\n"
        f"(請回答 '是' 或 '否')"
    )

    context_string = f"判斷 {poly_str} 是否恆正。{context_explanation}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    """
    檢查使用者輸入的是/否是否正確。
    """
    user = user_answer.strip().lower()
    if user in ['是', 'yes', 'y', 'true', 't']:
        user_choice = '是'
    elif user in ['否', 'no', 'n', 'false', 'f']:
        user_choice = '否'
    else:
        return {"correct": False, "result": "請回答 '是' 或 '否'。"}

    if user_choice == correct_answer:
        return {"correct": True, "result": f"完全正確！答案是「{correct_answer}」。"}
    else:
        return {"correct": False, "result": f"答案不正確。正確答案是「{correct_answer}」。"}