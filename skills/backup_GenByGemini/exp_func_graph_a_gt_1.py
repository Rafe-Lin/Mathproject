import random

def generate(level=1):
    """
    生成一道「指數函數圖形 (a>1)」的觀念題。
    """
    a = random.randint(2, 5)
    question_text = (
        f"請在計算紙上畫出指數函數 y = {a}ˣ 的圖形。\n"
        f"提示：圖形通過 (0,1)，且為嚴格遞增函數。\n"
        "完成後請點擊「AI 檢查」。"
    )
    return {"question_text": question_text, "answer": None, "correct_answer": "graph"}

def check(user_answer, correct_answer):
    return {"correct": True, "result": "觀念正確！當底數 a>1 時，指數函數圖形是遞增的。", "next_question": True}