import random

def generate_counting_principles_question():
    """動態生成一道「計數原理」的題目 (乘法原理)"""
    items1_count = random.randint(2, 5)
    items1_name = random.choice(["種上衣", "種帽子", "種麵包"])
    items2_count = random.randint(2, 5)
    items2_name = random.choice(["種褲子", "種圍巾", "種飲料"])
    answer = items1_count * items2_count
    question_text = f"小明有 {items1_count} {items1_name}和 {items2_count} {items2_name}，請問他總共可以搭配出幾種不同的組合？"
    return {
        "text": question_text,
        "answer": str(answer),
        "validation_function_name": None
    }
