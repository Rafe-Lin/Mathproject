# skills/jh_geo_parallelogram_tests.py
import random

def generate(level=1):
    """
    生成一道「平行四邊形的判別」的題目。
    此為概念題。
    """
    conditions = [
        ("一個四邊形滿足「兩雙對邊分別平行」，它是不是平行四邊形？", "是（此為定義）"),
        ("一個四邊形滿足「兩雙對邊分別等長」，它是不是平行四邊形？", "是"),
        ("一個四邊形滿足「兩雙對角分別相等」，它是不是平行四邊形？", "是"),
        ("一個四邊形滿足「兩條對角線互相平分」，它是不是平行四邊形？", "是"),
        ("一個四邊形滿足「一雙對邊平行且等長」，它是不是平行四邊形？", "是"),
        ("一個四邊形滿足「一雙對邊平行，另一雙對邊等長」，它是不是平行四邊形？", "不一定（可能是等腰梯形）"),
    ]
    
    question, answer_hint = random.choice(conditions)

    question_text = (
        f"請判斷以下敘述是否正確：\n\n「{question}」\n\n"
        "請在下方的「數位計算紙」上回答「是」或「不一定」，並簡述理由或畫出反例。\n\n"
        "完成後，請點擊「AI 檢查」按鈕。"
    )

    return {
        "question_text": question_text,
        "answer": None,
        "correct_answer": "graph",
        "context_string": f"學習判斷一個四邊形是否為平行四邊形的條件。提示：{answer_hint}",
    }

def check(user_answer, correct_answer):
    return {
        "correct": False, 
        "result": "這是一道觀念題，請在數位計算紙上作答後，點選「AI 檢查」。",
        "next_question": False
    }