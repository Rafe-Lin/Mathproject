# skills/jh_geo_3d_volume_pyramid.py
import random

def generate(level=1):
    """
    生成一道「角錐體積」的題目。
    """
    # 為了讓體積是整數，讓底面積或高是3的倍數
    base_area = random.randint(5, 15)
    height = random.randint(2, 8) * 3

    volume = (1/3) * base_area * height

    question_text = f"一個角錐的底面積為 {base_area} 平方公分，高為 {height} 公分。請問它的體積是多少立方公分？"
    correct_answer = str(int(volume))

    context_string = "角錐的體積 = (1/3) × 底面積 × 高。"

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