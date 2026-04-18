# \統計\直方圖繪製
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「直方圖繪製」的觀念題。
    """
    question_text = (
        "關於直方圖 (Histogram) 與長條圖 (Bar Chart) 的差異，下列敘述何者「正確」？\n\n"
        "A) 兩者完全相同，只是名稱不同\n"
        "B) 直方圖的橫軸是連續性的數值分組，長條圖的橫軸則是分類的項目\n"
        "C) 長條圖的長條之間必須相連，直方圖則必須分開"
    )
    correct_answer = "B"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    return check_answer(user_answer, correct_answer, check_type='case_insensitive')