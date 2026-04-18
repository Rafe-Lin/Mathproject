# skills/jh_algebra_symbol_def.py
import random

def generate(level=1):
    """
    生成一道「用符號代表數」的題目。
    """
    scenarios = [
        ("一本書的價格是 x 元，買 5 本書總共需要多少元？", "5x"),
        ("一個蘋果重 y 公克，一打(12個)蘋果總共重多少公克？", "12y"),
        ("小明今年 a 歲，5 年後他幾歲？", "a+5"),
        ("小華有 x 元，買了一本 100 元的書後，還剩下多少元？", "x-100"),
        ("一個長方形的長是 a 公分，寬是 b 公分，面積是多少平方公分？", "ab"),
        ("全班有 30 位學生，其中 x 位是男生，女生有多少位？", "30-x"),
    ]

    question, answer = random.choice(scenarios)

    question_text = f"請學習用符號代表數。\n\n題目：{question}"
    correct_answer = answer

    context_string = "學習用符號（代數）來表示未知數或變量。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    """
    檢查使用者輸入的答案是否正確。
    """
    user = user_answer.strip().replace(" ", "").replace("*", "")
    correct = str(correct_answer).strip().replace(" ", "").replace("*", "")

    # 處理 ab 和 ba 相同的情況
    if len(correct) == 2 and correct.isalpha():
        if user == correct or user == correct[::-1]:
            is_correct = True
        else:
            is_correct = False
    else:
        if user == correct:
            is_correct = True
        else:
            is_correct = False

    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案是：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}