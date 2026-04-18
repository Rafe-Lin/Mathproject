# skills/jh_pythagorean_theorem_converse.py
import random

def generate(level=1):
    """
    生成一道「畢氏定理逆定理」的題目。
    """
    # 隨機決定是否為直角三角形
    is_right_triangle = random.choice([True, False])
    
    if is_right_triangle:
        triples = [(3, 4, 5), (5, 12, 13), (8, 15, 17)]
        a, b, c = random.choice(triples)
        multiplier = random.randint(1, 2)
        a, b, c = a * multiplier, b * multiplier, c * multiplier
        correct_answer = "是"
    else:
        # 構造一個非直角三角形
        a = random.randint(3, 10)
        b = random.randint(a + 1, 12)
        c = b + random.randint(1, 3) # 確保 c 是最長邊
        while a**2 + b**2 == c**2:
            c += 1
        correct_answer = "否"

    sides = sorted([a, b, c])
    question_text = f"一個三角形的三邊長分別為 {sides[0]}, {sides[1]}, {sides[2]}，請問這是不是一個直角三角形？ (請回答 '是' 或 '否')"

    context_string = "利用畢氏定理的逆定理：如果三角形兩邊的平方和等於第三邊的平方 (a²+b²=c²)，則該三角形為直角三角形。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    user = user_answer.strip()
    correct = str(correct_answer).strip()
    if user in ["是", "Y", "y"] and correct == "是": is_correct = True
    elif user in ["否", "N", "n"] and correct == "否": is_correct = True
    else: is_correct = False
    result_text = f"完全正確！答案是 {correct}。" if is_correct else f"答案不正確。正確答案是：{correct}"
    return {"correct": is_correct, "result": result_text, "next_question": True}