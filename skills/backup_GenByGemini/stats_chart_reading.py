# \統計\統計圖表閱讀
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「統計圖表閱讀」的觀念題。
    """
    if level == 1:
        question_text = (
            "若要呈現各類別佔全體的「百分比」關係，使用哪一種統計圖最為合適？\n\n"
            "A) 長條圖 (Bar Chart)\n"
            "B) 折線圖 (Line Chart)\n"
            "C) 圓餅圖 (Pie Chart)"
        )
        correct_answer = "C"
    else: # level 2
        question_text = (
            "若要觀察某個數據在「一段時間內的連續變化趨勢」，例如股價走勢，使用哪一種統計圖最為合適？\n\n"
            "A) 長條圖 (Bar Chart)\n"
            "B) 折線圖 (Line Chart)\n"
            "C) 圓餅圖 (Pie Chart)"
        )
        correct_answer = "B"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    return check_answer(user_answer, correct_answer, check_type='case_insensitive')