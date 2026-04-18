# skills/jh_geo_3d_surface_area_pyramid.py
import random
import math

def generate(level=1):
    """
    生成一道「角錐表面積」的題目。
    """
    # 以正四角錐為例
    base_side = random.randint(4, 10) * 2 # 偶數底邊
    
    # 為了讓斜高是整數，使用畢氏定理構造
    # slant_height^2 = height^2 + (base_side/2)^2
    h_part = random.randint(3, 5)
    b_part = base_side // 2
    s_part = math.gcd(h_part, b_part)
    h_part //= s_part
    b_part //= s_part
    if h_part == b_part: h_part +=1
    
    slant_height = (h_part**2 + b_part**2) * s_part
    height = (h_part**2 - b_part**2) * s_part
    
    base_area = base_side ** 2
    lateral_area = 4 * (0.5 * base_side * slant_height)
    surface_area = base_area + lateral_area

    question_text = f"一個正四角錐，其底面是邊長為 {base_side} 的正方形，側面等腰三角形的斜高為 {slant_height}。請問此角錐的總表面積是多少？"
    correct_answer = str(int(surface_area))

    context_string = "角錐的表面積 = 底面積 + 側面總面積（所有側面三角形面積的和）。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    user = user_answer.strip()
    correct = correct_answer.strip()
    is_correct = user == correct
    result_text = f"完全正確！答案是 {correct}。" if is_correct else f"答案不正確。正確答案是：{correct}"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}