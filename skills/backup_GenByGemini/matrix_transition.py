import random

def generate(level=1):
    """
    生成一道「轉移矩陣」的觀念題。
    """
    if level == 1:
        question_text = (
            "關於轉移矩陣 T，下列敘述何者「正確」？\n\n"
            "A) T 的每個元素都必須是正數\n"
            "B) T 的每個直行（column）元素總和必須為 1\n"
            "C) T 的每個橫列（row）元素總和必須為 1"
        )
        correct_answer = "B"
    else: # level 2
        p1 = round(random.uniform(0.6, 0.9), 1)
        p2 = round(random.uniform(0.1, 0.4), 1)
        question_text = f"一個轉移矩陣 T = [[{p1}, {p2}], [x, y]]，請問 x 的值是多少？"
        correct_answer = str(round(1 - p1, 1))
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().upper()
    is_correct = (user == correct_answer.upper())
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}