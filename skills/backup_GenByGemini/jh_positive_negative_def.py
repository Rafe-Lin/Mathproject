# skills/jh_positive_negative_def.py
import random

def generate(level=1):
    """
    生成一道「正負數與相反量」的題目。
    熟練辨識生活中的相反量，並使用正、負號表示。
    """
    # level 參數暫時未使用，但保留以符合架構

    # 定義多種生活情境
    scenarios = [
        {'pos': '收入', 'neg': '支出', 'unit': '元', 'base': '金錢'},
        {'pos': '賺了', 'neg': '賠了', 'unit': '元', 'base': '交易'},
        {'pos': '前進', 'neg': '後退', 'unit': '步', 'base': '移動'},
        {'pos': '零上', 'neg': '零下', 'unit': '度', 'base': '溫度'},
        {'pos': '高於海平面', 'neg': '低於海平面', 'unit': '公尺', 'base': '海拔'},
        {'pos': '向東走', 'neg': '向西走', 'unit': '公里', 'base': '方向(以東為正)'},
        {'pos': '增加', 'neg': '減少', 'unit': '公斤', 'base': '體重變化'},
        {'pos': '得分', 'neg': '失分', 'unit': '分', 'base': '比賽分數'},
    ]

    # 隨機選擇一個情境
    scenario = random.choice(scenarios)
    # 隨機生成一個整數
    num = random.randint(5, 500)

    # 隨機決定是問正向還是負向問題
    is_positive_question = random.choice([True, False])

    if is_positive_question:
        # 生成正向問題
        description = f"{scenario['pos']} {num} {scenario['unit']}"
        # 答案可以接受 +num 或 num
        correct_answer = str(num)
        # 用於 AI 提示的標準答案
        standard_answer = f"+{num}"
    else:
        # 生成負向問題
        description = f"{scenario['neg']} {num} {scenario['unit']}"
        correct_answer = f"-{num}"
        standard_answer = f"-{num}"

    # 組裝題目文字
    question_text = (
        f"在數學中，我們常用正、負號來表示意義相反的量。\n\n"
        f"如果以「{scenario['pos']}」為正，那麼「{description}」應如何表示？"
    )

    # 給 AI 助教的 context
    context_string = f"學習用正負數表示生活中的相反量。情境：{scenario['base']}，題目：以「{scenario['pos']}」為正，如何表示「{description}」。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text", # 答案類型為文字
        "context_string": context_string,
        "standard_answer": standard_answer # 額外提供給 AI prompt 的標準答案
    }

def check(user_answer, correct_answer):
    """
    檢查使用者輸入的答案是否正確。
    """
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()

    # 處理正數情況：使用者可以輸入 "500" 或 "+500"
    if not correct.startswith('-') and user.lstrip('+') == correct:
        is_correct = True
    # 處理負數情況
    elif user == correct:
        is_correct = True
    else:
        is_correct = False

    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {
        "correct": is_correct, 
        "result": result_text,
        "next_question": True
    }