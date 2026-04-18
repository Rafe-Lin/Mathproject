# skills/jh_geo_parallelogram_def_properties.py
import random

def generate(level=1):
    """
    生成一道「平行四邊形定義與性質」的題目。
    此為概念題。
    """
    properties = [
        ("平行四邊形的定義是什麼？", "兩雙對邊分別平行的四邊形。"),
        ("平行四邊形的對邊有什麼關係？", "兩雙對邊分別等長。"),
        ("平行四邊形的對角有什麼關係？", "兩雙對角分別相等。"),
        ("平行四邊形的鄰角有什麼關係？", "鄰角互補（相加為180度）。"),
        ("平行四邊形的對角線有什麼性質？", "兩條對角線互相平分。"),
    ]
    
    question, answer_hint = random.choice(properties)

    question_text = (
        f"請回答關於「平行四邊形」的問題：\n\n{question}\n\n"
        "請在下方的「數位計算紙」上畫圖並寫下你的解釋。\n\n"
        "完成後，請點擊「AI 檢查」按鈕。"
    )

    return {
        "question_text": question_text,
        "answer": None,
        "correct_answer": "graph",
        "context_string": f"學習平行四邊形的定義與性質。提示：{answer_hint}",
    }

def check(user_answer, correct_answer):
    return {
        "correct": False, 
        "result": "這是一道觀念題，請在數位計算紙上作答後，點選「AI 檢查」。",
        "next_question": False
    }