# skills/jh_geo_3d_surface_area_prism.py
import random

def generate(level=1):
    """
    生成一道「角柱表面積」的題目。
    """
    # 以長方體為例
    length = random.randint(3, 8)
    width = random.randint(3, 8)
    height = random.randint(5, 12)

    # 表面積 = 2 * (lw + lh + wh)
    surface_area = 2 * (length * width + length * height + width * height)

    question_text = f"一個長方體的長、寬、高分別為 {length}、{width}、{height} 公分。請問它的總表面積是多少平方公分？"
    correct_answer = str(surface_area)

    context_string = "角柱的表面積 = 兩個底面積 + 側面積。對於長方體，表面積 = 2 × (長×寬 + 長×高 + 寬×高)。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    user = user_answer.strip()
    correct = correct_answer.strip()
    try:
        is_correct = int(user) == int(correct)
        result_text = f"完全正確！答案是 {correct} 平方公分。" if is_correct else f"答案不正確。正確答案是：{correct} 平方公分"
    except ValueError:
        is_correct = False
        result_text = f"請輸入數字答案。正確答案是：{correct} 平方公分"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}