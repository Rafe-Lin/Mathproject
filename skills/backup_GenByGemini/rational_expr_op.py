# skills/rational_expr_op.py
import random

def generate(level=1):
    """
    生成一道「分式的四則運算」題目 (圖形題)
    """
    # level 參數暫時未使用，但保留以符合架構
    # 隨機生成兩個簡單的分式
    n1, d1 = random.randint(1, 5), f"x + {random.randint(1, 5)}"
    n2, d2 = random.randint(1, 5), f"x - {random.randint(1, 5)}"
    
    op = random.choice(['+', '-', '*', '÷'])

    expr1 = f"({n1} / ({d1}))"
    expr2 = f"({n2} / ({d2}))"

    question_text = f"請在下方的「數位計算紙」上，計算 {expr1} {op} {expr2} 的結果，並化為最簡分式。\n\n完成後，請點擊「AI 檢查」按鈕。"
    context_string = f"計算 {expr1} {op} {expr2}"

    return {
        "question_text": question_text,
        "answer": None,
        "correct_answer": "graph",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    """圖形題不走文字批改"""
    return {"correct": False, "result": "請在數位計算紙上寫下您的計算過程，然後點選「AI 檢查」。"}