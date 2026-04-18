# skills/jh_prob_list_outcomes_simple.py
import random

def generate(level=1):
    """
    生成一道「列舉法求樣本空間」的題目。
    """
    items = random.choice([
        ("投擲一顆公正的骰子", "1, 2, 3, 4, 5, 6"),
        ("投擲一枚硬幣", "正, 反"),
        ("一個袋中有紅、黃、藍三球，抽出一球", "紅, 黃, 藍"),
    ])
    
    event, outcomes = items
    
    question_text = f"請列出以下試驗的所有可能結果：\n\n「{event}」\n\n(請用逗號分隔)"
    correct_answer = outcomes

    context_string = "學習寫出一個隨機試驗中所有可能的結果，這些結果的集合稱為樣本空間。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    user_set = set(item.strip() for item in user_answer.split(','))
    correct_set = set(item.strip() for item in correct_answer.split(','))
    is_correct = user_set == correct_set
    result_text = f"完全正確！所有可能是：{correct_answer}。" if is_correct else f"不完全正確喔。參考答案是：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}