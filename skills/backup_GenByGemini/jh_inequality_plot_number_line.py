# skills/jh_inequality_plot_number_line.py
import random

def generate(level=1):
    """
    生成一道「在數線上圖示不等式的解」的題目。
    此為圖形題。
    """
    num = random.randint(-5, 5)
    op = random.choice(['>', '<', '>=', '<='])
    
    inequality_str = f"x {op} {num}"

    question_text = (
        f"請在下方的「數位計算紙」上，畫出不等式 {inequality_str} 的解在數線上的圖示。\n\n"
        f"提示：注意端點是空心（> 或 <）還是實心（>= 或 <=），以及方向是向右還是向左。\n\n"
        "完成後，請點擊「AI 檢查」按鈕。"
    )

    return {
        "question_text": question_text,
        "answer": None,
        "correct_answer": "graph",
        "context_string": f"學習如何在數線上表示不等式 {inequality_str} 的解。",
    }

def check(user_answer, correct_answer):
    """
    圖形題的 check 函數通常只返回提示，實際批改由前端 AI 完成。
    """
    return {
        "correct": False, 
        "result": "請在數位計算紙上畫出您的解題過程，然後點選「AI 檢查」。",
        "next_question": False
    }