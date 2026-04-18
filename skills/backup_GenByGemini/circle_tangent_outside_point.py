import random

def generate(level=1):
    """
    生成一道「求過圓外一點的切線方程式」的題目。
    此為觀念/作圖題。
    level 1: 圓心在原點。
    level 2: 圓心不在原點。
    """
    r = random.randint(2, 4)
    if level == 1:
        h, k = 0, 0
        circle_eq = f"x² + y² = {r**2}"
    else: # level 2
        h, k = random.randint(-2, 2), random.randint(-2, 2)
        circle_eq = f"(x-{h})² + (y-{k})² = {r**2}"
    
    # 選一個在圓外的點
    px, py = h + r + random.randint(1,3), k + random.randint(1,3)

    question_text = (
        f"給定圓 C: {circle_eq} 與圓外一點 P({px}, {py})。\n"
        "要求過點 P 的切線，通常有以下步驟：\n"
        "1. 假設切線方程式為 y - py = m(x - px)\n"
        "2. 利用「圓心到切線的距離等於半徑」來解 m。\n"
        "這是一個概念題，請點擊「AI 檢查」以確認你已了解此方法。"
    )
    return {"question_text": question_text, "answer": None, "correct_answer": "graph"}

def check(user_answer, correct_answer):
    return {"correct": True, "result": "觀念正確！這個方法是解決這類問題的標準流程。", "next_question": True}