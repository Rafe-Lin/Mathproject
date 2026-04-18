# skills/jh_geo_def_3d_views.py
import random

def generate(level=1):
    """
    生成一道「立體圖形三視圖」的題目。
    此為概念題/圖形題。
    """
    question_text = (
        "觀察一個由數個正方體堆疊成的立體圖形。\n\n"
        "請在下方的「數位計算紙」上，畫出這個立體圖形的前視圖、上視圖和右視圖。\n\n"
        "（這是一個概念題，你可以畫一個簡單的例子，例如由3個方塊組成的L形，然後畫出它的三視圖。）\n\n"
        "完成後，請點擊「AI 檢查」按鈕。"
    )

    return {
        "question_text": question_text,
        "answer": None,
        "correct_answer": "graph",
        "context_string": "學習從不同視角（前、上、右）觀察立體圖形，並畫出對應的平面視圖。",
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