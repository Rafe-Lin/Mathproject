# skills/jh_geo_kite_def_properties.py
import random

def generate(level=1):
    """
    生成一道「箏形定義與性質」的題目。
    此為概念題。
    """
    properties = [
        ("箏形的定義是什麼？", "有兩雙鄰邊分別相等的四邊形。"),
        ("箏形的一組對角線有什麼關係？", "其中一條對角線會垂直平分另一條對角線。"),
        ("箏形的對角有什麼特性？", "其中有一組對角會相等（被不對稱的對角線所夾的角）。"),
    ]
    
    question, answer_hint = random.choice(properties)

    question_text = (
        f"請回答關於「箏形」的問題：\n\n{question}\n\n"
        "請在下方的「數位計算紙」上畫圖並寫下你的解釋。\n\n"
        "完成後，請點擊「AI 檢查」按鈕。"
    )

    return {
        "question_text": question_text,
        "answer": None,
        "correct_answer": "graph",
        "context_string": f"學習箏形的定義與性質。提示：{answer_hint}",
    }

def check(user_answer, correct_answer):
    return {
        "correct": False, 
        "result": "這是一道觀念題，請在數位計算紙上作答後，點選「AI 檢查」。",
        "next_question": False
    }