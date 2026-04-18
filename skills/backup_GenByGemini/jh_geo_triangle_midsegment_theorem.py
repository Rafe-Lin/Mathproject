# skills/jh_geo_triangle_midsegment_theorem.py
import random

def generate(level=1):
    """
    生成一道「三角形兩邊中點連線性質」的題目。
    """
    # 構造三角形 ABC，D, E 分別為 AB, AC 中點
    # DE = 1/2 * BC
    
    bc_length = random.randint(5, 20) * 2 # 確保是偶數
    de_length = bc_length // 2

    q_type = random.choice(['find_de', 'find_bc'])

    if q_type == 'find_de':
        question_text = f"在 △ABC 中，D、E 分別為 AB、AC 的中點。若 BC 的長度為 {bc_length}，請問中點連線 DE 的長度是多少？"
        correct_answer = str(de_length)
    else:
        question_text = f"在 △ABC 中，D、E 分別為 AB、AC 的中點。若中點連線 DE 的長度為 {de_length}，請問底邊 BC 的長度是多少？"
        correct_answer = str(bc_length)

    context_string = "利用三角形兩邊中點連線性質：三角形兩邊中點的連線段會平行於第三邊，且長度為第三邊的一半。"

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
        result_text = f"完全正確！答案是 {correct}。" if is_correct else f"答案不正確。正確答案是：{correct}"
    except ValueError:
        is_correct = False
        result_text = f"請輸入數字答案。正確答案是：{correct}"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}