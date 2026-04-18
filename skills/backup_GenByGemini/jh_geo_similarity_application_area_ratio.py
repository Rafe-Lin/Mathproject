# skills/jh_geo_similarity_application_area_ratio.py
import random

def generate(level=1):
    """
    生成一道「相似形的面積比」的題目。
    """
    # 相似邊長比 a:b
    a = random.randint(2, 5)
    b = a + random.randint(1, 3)
    
    # 面積比 a^2 : b^2
    area_a = a**2 * random.randint(1, 4)
    area_b = b**2 * (area_a / (a**2))

    q_type = random.choice(['find_area', 'find_ratio'])

    if q_type == 'find_area':
        question_text = f"兩個相似三角形，對應邊長比為 {a}:{b}。若小三角形的面積為 {area_a}，請問大三角形的面積是多少？"
        correct_answer = str(int(area_b))
    else:
        question_text = f"兩個相似多邊形，面積分別為 {area_a} 和 {int(area_b)}。請問它們的對應邊長比是多少？ (請以 a:b 的最簡整數比作答)"
        correct_answer = f"{a}:{b}"

    context_string = "相似n邊形的面積比等於對應邊長的平方比。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = correct_answer.strip().replace(" ", "")
    try:
        is_correct = user == correct
        result_text = f"完全正確！答案是 {correct}。" if is_correct else f"答案不正確。正確答案是：{correct}"
    except ValueError:
        is_correct = False
        result_text = f"請輸入正確格式的答案。正確答案是：{correct}"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}