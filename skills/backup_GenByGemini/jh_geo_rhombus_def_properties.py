# skills/jh_geo_rhombus_def_properties.py
import random

def generate(level=1):
    """
    生成一道「菱形定義與性質」的題目。
    此為概念題。
    """
    properties = [
        ("菱形的定義是什麼？", "四條邊都等長的四邊形。"),
        ("菱形是平行四邊形嗎？為什麼？", "是，因為它滿足兩雙對邊等長。"),
        ("菱形的對角線有什麼特殊的性質（除了平行四邊形都有的性質外）？", "兩條對角線互相垂直。"),
    ]
    
    question, answer_hint = random.choice(properties)

    question_text = (
        f"請回答關於「菱形」的問題：\n\n{question}\n\n"
        "請在下方的「數位計算紙」上畫圖並寫下你的解釋。\n\n"
        "完成後，請點擊「AI 檢查」按鈕。"
    )

    return {
        "question_text": question_text,
        "answer": None,
        "correct_answer": "graph",
        "context_string": f"學習菱形的定義與性質。提示：{answer_hint}",
    }

def check(user_answer, correct_answer):
    return {
        "correct": False, 
        "result": "這是一道觀念題，請在數位計算紙上作答後，點選「AI 檢查」。",
        "next_question": False
    }