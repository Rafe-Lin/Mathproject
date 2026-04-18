# skills/jh_geo_def_line_symmetry.py
import random

def generate(level=1):
    """
    生成一道「線對稱圖形」的題目。
    此為概念題/圖形題。
    """
    shapes = ["正方形", "長方形", "圓形", "等腰三角形", "英文字母 H", "英文字母 A"]
    shape = random.choice(shapes)

    question_text = (
        f"請思考「{shape}」是不是一個線對稱圖形？\n\n"
        f"如果是，請在下方的「數位計算紙」上畫出「{shape}」以及它的一條對稱軸。\n\n"
        "完成後，請點擊「AI 檢查」按鈕。"
    )

    return {
        "question_text": question_text,
        "answer": None,
        "correct_answer": "graph",
        "context_string": "學習辨識線對稱圖形，並找出其對稱軸。",
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