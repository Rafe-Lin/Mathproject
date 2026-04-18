# skills/jh_arithmetic_series_def.py
import random

def generate(level=1):
    """
    生成一道「等差級數定義」的題目。
    """
    a1 = random.randint(1, 5)
    d = random.randint(1, 3)
    seq = [str(a1 + i * d) for i in range(5)]
    
    seq_str = ", ".join(seq)
    series_str = " + ".join(seq)

    question_text = (
        f"將等差數列 {seq_str}, ... 的各項用「+」號連接起來，形成的式子 {series_str} + ... 稱為等差級數。\n\n"
        f"這是一個觀念題，請點擊「AI 檢查」以確認你已了解。"
    )

    context_string = "學習等差級數的定義，即等差數列各項的總和。"

    return {
        "question_text": question_text,
        "answer": None,
        "correct_answer": "graph", # 使用 graph 類型讓學生直接按鈕確認
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    return {
        "correct": True, 
        "result": "觀念正確！等差級數就是等差數列的和。",
        "next_question": True
    }