# skills/jh_geo_3d_prism_def.py
import random

def generate(level=1):
    """
    生成一道「角柱定義」的題目。
    此為概念/圖形題。
    """
    prism_type = random.choice(["三", "四", "五"])
    question_text = (
        f"請說明什麼是「{prism_type}角柱」？它的底面和側面各有什麼特徵？\n\n"
        f"請在下方的「數位計算紙」上，畫出一個{prism_type}角柱的示意圖。\n\n"
        "完成後，請點擊「AI 檢查」按鈕。"
    )

    return {
        "question_text": question_text,
        "answer": None,
        "correct_answer": "graph",
        "context_string": "學習角柱的定義：由兩個全等的平行多邊形底面和多個平行四邊形側面所組成的立體圖形。",
    }

def check(user_answer, correct_answer):
    return {
        "correct": False, 
        "result": "這是一道觀念題，請在數位計算紙上作答後，點選「AI 檢查」。",
        "next_question": False
    }