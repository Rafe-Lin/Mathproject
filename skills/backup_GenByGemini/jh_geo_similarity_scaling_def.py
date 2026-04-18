# skills/jh_geo_similarity_scaling_def.py
import random

def generate(level=1):
    """
    生成一道「相似與縮放」的題目。
    """
    # 邊長
    side1_a = random.randint(2, 5)
    side1_b = side1_a * random.randint(2, 4)
    
    side2_a = random.randint(3, 6)
    side2_b = side2_a * (side1_b / side1_a)

    q_type = random.choice(['find_scale', 'find_length'])

    if q_type == 'find_scale':
        question_text = f"將一個邊長為 {side1_a} 的正方形，放大成一個邊長為 {side1_b} 的正方形。請問放大倍率是多少？"
        correct_answer = str(side1_b // side1_a)
    else:
        scale = side1_b // side1_a
        question_text = f"將一個長為 {side2_a}、寬為 {side1_a} 的長方形，以 {scale} 倍放大。請問放大後的長方形，其對應的長是多少？"
        correct_answer = str(int(side2_b))

    context_string = "相似圖形是指形狀相同，但大小可能不同的圖形。對應邊長的比值稱為縮放倍率或相似比。"

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