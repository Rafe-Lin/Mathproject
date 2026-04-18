# skills/jh_proportion_word_problem.py
import random

def generate(level=1):
    """
    生成一道「比例應用問題」的題目。
    """
    # 範例：地圖比例尺
    scale_map = 1
    scale_real = random.choice([1000, 5000, 20000])
    
    map_dist = random.randint(2, 10) # cm
    real_dist = (map_dist * scale_real) / 100 # m
    
    # 隨機問地圖距離或實際距離
    if random.choice([True, False]):
        question_text = f"在一張比例尺為 {scale_map}:{scale_real} 的地圖上，A、B 兩地的距離為 {map_dist} 公分，請問 A、B 兩地的實際距離是多少公尺？"
        correct_answer = str(int(real_dist))
    else:
        question_text = f"在一張比例尺為 {scale_map}:{scale_real} 的地圖上，A、B 兩地的實際距離為 {int(real_dist)} 公尺，請問在地圖上 A、B 兩地的距離是多少公分？"
        correct_answer = str(map_dist)

    context_string = "利用比例尺「圖上距離：實際距離」的關係來解決問題。"

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
        if float(user) == float(correct):
            is_correct = True
            result_text = f"完全正確！答案是 {correct}。"
        else:
            is_correct = False
            result_text = f"答案不正確。正確答案是：{correct}"
    except ValueError:
        is_correct = False
        result_text = f"請輸入數字答案。正確答案是：{correct}"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}