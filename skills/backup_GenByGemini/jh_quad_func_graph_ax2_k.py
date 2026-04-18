# skills/jh_quad_func_graph_ax2_k.py
import random

def generate(level=1):
    """
    生成一道「二次函數 y=ax²+k 圖形」的題目。
    此為圖形題。
    """
    a = random.choice([-2, -1, 1, 2])
    k = random.randint(-4, 4)
    while k == 0: k = random.randint(-4, 4)
    
    func_str = f"y = {a}x² {'+' if k > 0 else '-'} {abs(k)}"
    if a == 1: func_str = func_str.replace("y = 1x²", "y = x²")
    if a == -1: func_str = func_str.replace("y = -1x²", "y = -x²")

    question_text = (
        f"請在下方的「數位計算紙」上，畫出二次函數 {func_str} 的圖形。\n\n"
        f"提示：這個圖形是 y={a}x² 的圖形向上或向下平移得到的，頂點在哪裡呢？\n\n"
        "完成後，請點擊「AI 檢查」按鈕。"
    )

    return {
        "question_text": question_text,
        "answer": None,
        "correct_answer": "graph",
        "context_string": f"學習二次函數 y=ax²+k 的圖形，其頂點為 (0, {k})。",
    }

def check(user_answer, correct_answer):
    return { "correct": False, "result": "請在數位計算紙上畫出圖形，然後點選「AI 檢查」。", "next_question": False }