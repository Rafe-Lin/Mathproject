# skills/jh_geo_3d_pyramid_def.py
import random

def generate(level=1):
    """
    生成一道「角錐定義」的題目。
    此為概念/圖形題。
    """
    pyramid_type = random.choice(["三", "四", "五"])
    question_text = (
        f"請說明什麼是「{pyramid_type}角錐」？它的底面和側面各有什麼特徵？\n\n"
        f"請在下方的「數位計算紙」上，畫出一個{pyramid_type}角錐的示意圖。\n\n"
        "完成後，請點擊「AI 檢查」按鈕。"
    )

    return {
        "question_text": question_text,
        "answer": None,
        "correct_answer": "graph",
        "context_string": "學習角錐的定義：由一個多邊形底面和多個有共同頂點的三角形側面所組成的立體圖形。",
    }

def check(user_answer, correct_answer):
    return {
        "correct": False, 
        "result": "這是一道觀念題，請在數位計算紙上作答後，點選「AI 檢查」。",
        "next_question": False
    }