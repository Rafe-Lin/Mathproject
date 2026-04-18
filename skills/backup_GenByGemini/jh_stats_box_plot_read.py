# skills/jh_stats_box_plot_read.py
import random
import numpy as np

def generate(level=1):
    """
    生成一道「判讀盒狀圖」的題目。
    """
    # 生成一組數據來計算五數
    data = sorted([random.randint(50, 99) for _ in range(random.choice([9, 11, 13, 15]))])
    min_val, q1, q2, q3, max_val = np.percentile(data, [0, 25, 50, 75, 100])
    
    q_type = random.choice(['q2', 'q3', 'iqr'])

    question_text = (
        f"觀察一個盒狀圖，我們得知其最小值為 {int(min_val)}，第一四分位數(Q1)為 {int(q1)}，中位數(Q2)為 {int(q2)}，第三四分位數(Q3)為 {int(q3)}，最大值為 {int(max_val)}。\n\n"
    )

    if q_type == 'q2':
        question_text += "請問這組數據的中位數是多少？"
        correct_answer = str(int(q2))
    elif q_type == 'q3':
        question_text += "請問這組數據的第三四分位數(Q3)是多少？"
        correct_answer = str(int(q3))
    else: # iqr
        question_text += "請問這組數據的四分位距(IQR)是多少？"
        correct_answer = str(int(q3 - q1))

    context_string = "學習判讀盒狀圖上的五個關鍵數值，並計算四分位距 (IQR = Q3 - Q1)。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    user = user_answer.strip()
    correct = correct_answer.strip()
    is_correct = user == correct
    result_text = f"完全正確！答案是 {correct}。" if is_correct else f"答案不正確。正確答案是：{correct}"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}