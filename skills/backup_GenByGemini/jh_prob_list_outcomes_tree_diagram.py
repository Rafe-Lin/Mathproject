# skills/jh_prob_list_outcomes_tree_diagram.py
import random

def generate(level=1):
    """
    生成一道「樹狀圖法求樣本空間」的題目。
    此為圖形/概念題。
    """
    question_text = (
        "連續投擲一枚公正的硬幣三次。\n\n"
        "請利用「樹狀圖」來表示所有可能的結果（例如：正正正、正正反...）。\n\n"
        "請在下方的「數位計算紙」上畫出你的樹狀圖。\n\n"
        "完成後，請點擊「AI 檢查」按鈕。"
    )

    return {
        "question_text": question_text,
        "answer": None,
        "correct_answer": "graph",
        "context_string": "學習使用樹狀圖來系統性地列出多步驟隨機試驗的所有可能結果。",
    }

def check(user_answer, correct_answer):
    """
    圖形題的 check 函數通常只返回提示，實際批改由前端 AI 完成。
    """
    return {
        "correct": False, 
        "result": "請在數位計算紙上畫出樹狀圖，然後點選「AI 檢查」。",
        "next_question": False
    }