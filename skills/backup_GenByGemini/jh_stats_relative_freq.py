# skills/jh_stats_relative_freq.py
import random

def generate(level=1):
    """
    生成一道「相對次數」的題目。
    """
    # 創建一個簡化的次數分配表
    groups = ["40~50", "50~60", "60~70", "70~80"]
    freqs = [random.randint(2, 5), random.randint(5, 10), random.randint(8, 15), random.randint(3, 7)]
    total_freq = sum(freqs)
    
    table_str = "某班學生成績次數分配表如下：\n"
    table_str += "分組(分) | 次數(人)\n"
    table_str += "---|---\n"
    for i, group in enumerate(groups):
        table_str += f"{group} | {freqs[i]}\n"

    # 隨機問某一組的相對次數
    q_index = random.randint(0, len(groups) - 1)
    q_group = groups[q_index]
    q_freq = freqs[q_index]

    question_text = f"{table_str}\n請問「{q_group} 分」這一組的相對次數是多少個百分比(%)？\n(四捨五入到小數點後一位)"
    correct_answer = str(round((q_freq / total_freq) * 100, 1))

    context_string = "相對次數 = (該組的次數 / 總次數) × 100%。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    user = user_answer.strip().replace("%", "")
    correct = correct_answer.strip()
    try:
        # 允許一點點的計算誤差
        is_correct = abs(float(user) - float(correct)) < 0.05
        result_text = f"完全正確！答案是 {correct}%。" if is_correct else f"答案不正確。正確答案是：{correct}%"
    except ValueError:
        is_correct = False
        result_text = f"請輸入數字答案。正確答案是：{correct}%"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}