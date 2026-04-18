# skills/jh_stats_box_plot_draw.py
import random

def generate(level=1):
    """
    生成一道「繪製盒狀圖」的題目。
    此為圖形題。
    """
    # 生成一組數據
    data = sorted([random.randint(50, 99) for _ in range(random.choice([9, 11, 13]))])
    data_str = ", ".join(map(str, data))

    question_text = (
        f"給定一組學生的數學成績數據如下：\n{data_str}\n\n"
        "請計算這組數據的最小值、第一四分位數(Q1)、中位數(Q2)、第三四分位數(Q3)和最大值，並在下方的「數位計算紙」上繪製出對應的盒狀圖（箱形圖）。\n\n"
        "完成後，請點擊「AI 檢查」按鈕。"
    )

    return {
        "question_text": question_text,
        "answer": None,
        "correct_answer": "graph",
        "context_string": "學習如何根據一組數據，找出五數綜合（最小值、Q1、Q2、Q3、最大值），並繪製盒狀圖。",
    }

def check(user_answer, correct_answer):
    return {
        "correct": False, 
        "result": "請在數位計算紙上畫出盒狀圖，然後點選「AI 檢查」。",
        "next_question": False
    }