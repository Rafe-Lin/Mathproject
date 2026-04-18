# skills/jh_ratio_chained_def.py
import random

def generate(level=1):
    """
    生成一道「連比定義」的題目。
    """
    a = random.randint(2, 7)
    b = random.randint(2, 7)
    c = random.randint(2, 7)

    question_text = (
        f"若三個數 x, y, z 的比為 {a} : {b} : {c}，這稱為「連比」。\n"
        f"這表示 x:y = {a}:{b}，y:z = {b}:{c}，且 x:z = {a}:{c}。\n\n"
        f"這是一個觀念題，請點擊「AI 檢查」以確認你已了解。"
    )

    context_string = "學習連比的定義，即多個數量的連續比較關係。"

    return {
        "question_text": question_text,
        "answer": None,
        "correct_answer": "graph", # 使用 graph 類型讓學生直接按鈕確認
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    return {
        "correct": True, 
        "result": "觀念正確！連比是用來表示三個或更多數量的比例關係。",
        "next_question": True
    }