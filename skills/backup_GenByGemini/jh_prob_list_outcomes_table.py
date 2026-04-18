# skills/jh_prob_list_outcomes_table.py
import random

def generate(level=1):
    """
    生成一道「列表法求樣本空間」的題目。
    此為圖形/概念題。
    """
    question_text = (
        "小明和小華兩人玩猜拳（剪刀、石頭、布）的遊戲。\n\n"
        "請利用「列表法」（畫出表格）來表示兩人出拳所有可能的結果。\n\n"
        "請在下方的「數位計算紙」上畫出你的表格。\n\n"
        "完成後，請點擊「AI 檢查」按鈕。"
    )

    return {
        "question_text": question_text,
        "answer": None,
        "correct_answer": "graph",
        "context_string": "學習使用列表法來系統性地列出複合事件的所有可能結果。",
    }

def check(user_answer, correct_answer):
    """
    圖形題的 check 函數通常只返回提示，實際批改由前端 AI 完成。
    """
    return {
        "correct": False, 
        "result": "請在數位計算紙上畫出表格，然後點選「AI 檢查」。",
        "next_question": False
    }