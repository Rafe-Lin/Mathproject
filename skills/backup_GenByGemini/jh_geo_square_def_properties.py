# skills/jh_geo_square_def_properties.py
import random

def generate(level=1):
    """
    生成一道「正方形定義與性質」的題目。
    此為概念題。
    """
    question_text = (
        "正方形是相當特別的四邊形，它同時是矩形也是菱形。\n\n"
        "請回答：正方形擁有所有矩形和菱形的性質嗎？\n"
        "請列舉至少三條正方形的性質（例如：關於邊、角、對角線）。\n\n"
        "請在下方的「數位計算紙」上畫圖並寫下你的解釋。\n\n"
        "完成後，請點擊「AI 檢查」按鈕。"
    )

    return {
        "question_text": question_text,
        "answer": None,
        "correct_answer": "graph",
        "context_string": "學習正方形的定義與性質，並理解它與矩形、菱形的關係。",
    }

def check(user_answer, correct_answer):
    """
    圖形題的 check 函數通常只返回提示，實際批改由前端 AI 完成。
    """
    return {
        "correct": False, 
        "result": "這是一道觀念題，請在數位計算紙上作答後，點選「AI 檢查」。",
        "next_question": False
    }