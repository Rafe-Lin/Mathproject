import random

def generate(level=1):
    """
    生成一道「可重複排列」的題目。
    level 1: 數字可重複。
    level 2: 物品可重複放入。
    """
    if level == 1:
        n = random.randint(3, 4)
        question_text = f"用 0, 1, 2, 3, 4, 5 組成一個 {n} 位數，數字可以重複使用，共有多少種組合？（首位數不可為0）"
        # 首位有 5 種選擇，其餘各位有 6 種選擇
        correct_answer = str(5 * (6**(n - 1)))
    else: # level 2
        letters = random.randint(3, 4)
        boxes = random.randint(2, 3)
        question_text = f"將 {letters} 封不同的信，投入 {boxes} 個不同的郵筒，共有多少種投法？"
        correct_answer = str(boxes**letters)
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}