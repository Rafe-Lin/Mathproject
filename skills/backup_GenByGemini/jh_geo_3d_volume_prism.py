# skills/jh_geo_3d_volume_prism.py
import random

def generate(level=1):
    """
    生成一道「角柱體積」的題目。
    """
    # 以長方體或正方體為例
    length = random.randint(3, 10)
    width = random.choice([length, random.randint(3, 10)])
    height = random.randint(5, 12)

    volume = length * width * height

    question_text = f"一個底面為長方形的四角柱（長方體），其長、寬、高分別為 {length}、{width}、{height} 公分。請問它的體積是多少立方公分？"
    correct_answer = str(volume)

    context_string = "角柱的體積 = 底面積 × 高。"

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
        result_text = f"完全正確！答案是 {correct} 立方公分。" if is_correct else f"答案不正確。正確答案是：{correct} 立方公分"
    except ValueError:
        is_correct = False
        result_text = f"請輸入數字答案。正確答案是：{correct} 立方公分"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}