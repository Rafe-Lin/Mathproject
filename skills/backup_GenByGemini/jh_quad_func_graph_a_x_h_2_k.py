# skills/jh_quad_func_graph_a_x_h_2_k.py
import random

def generate(level=1):
    """
    生成一道「二次函數 y=a(x-h)²+k 圖形」的題目。
    此為圖形題。
    """
    a = random.choice([-2, -1, 1, 2])
    h = random.randint(-3, 3)
    k = random.randint(-3, 3)
    while h == 0 and k == 0: k = random.randint(-3, 3)
    
    func_str = f"y = {a}(x {'-' if h > 0 else '+'} {abs(h)})² {'+' if k > 0 else '-'} {abs(k)}"
    if a == 1: func_str = func_str.replace("y = 1(", "y = (")
    if a == -1: func_str = func_str.replace("y = -1(", "y = -(")

    question_text = (
        f"請在下方的「數位計算紙」上，畫出二次函數 {func_str} 的圖形。\n\n"
        f"提示：找出這個拋物線的頂點和開口方向。\n\n"
        "完成後，請點擊「AI 檢查」按鈕。"
    )

    return {
        "question_text": question_text,
        "answer": None,
        "correct_answer": "graph",
        "context_string": f"學習二次函數 y=a(x-h)²+k 的圖形，其頂點為 ({h}, {k})。",
    }

def check(user_answer, correct_answer):
    return { "correct": False, "result": "請在數位計算紙上畫出圖形，然後點選「AI 檢查」。", "next_question": False }