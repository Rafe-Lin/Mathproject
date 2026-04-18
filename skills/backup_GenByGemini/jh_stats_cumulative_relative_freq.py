# skills/jh_stats_cumulative_relative_freq.py
import random

def generate(level=1):
    """
    生成一道「累積相對次數」的題目。
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

    # 計算累積次數和累積相對次數
    cum_freq = 0
    cum_rel_freqs = []
    for f in freqs:
        cum_freq += f
        cum_rel_freqs.append(round((cum_freq / total_freq) * 100, 1))

    # 隨機問某一組的累積相對次數
    q_index = random.randint(1, len(groups) - 1)
    q_group_upper = groups[q_index].split('~')[1]

    question_text = f"{table_str}\n請問「未滿 {q_group_upper} 分」的累積相對次數是多少個百分比(%)？\n(四捨五入到小數點後一位)"
    correct_answer = str(cum_rel_freqs[q_index])

    context_string = "累積相對次數 = (該組的累積次數 / 總次數) × 100%。"

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
        is_correct = abs(float(user) - float(correct)) < 0.05 # 允許一點誤差
        result_text = f"完全正確！答案是 {correct}%。" if is_correct else f"答案不正確。正確答案是：{correct}%"
    except ValueError:
        is_correct = False
        result_text = f"請輸入數字答案。正確答案是：{correct}%"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}