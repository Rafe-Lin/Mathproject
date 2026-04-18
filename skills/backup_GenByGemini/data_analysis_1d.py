import random

def generate_data_analysis_1d_question():
    """動態生成一道「一維數據分析」的題目 (平均數、中位數或眾數)"""
    data = sorted([random.randint(1, 20) for _ in range(random.choice([5, 7]))])
    stat_type = random.choice(['mean', 'median', 'mode'])
    if stat_type == 'mean':
        mean = sum(data) / len(data)
        answer = f"{mean:.1f}" if mean != int(mean) else str(int(mean))
        question_text = f"給定一組數據：{data}，請問這組數據的算術平均數是多少？"
    elif stat_type == 'median':
        median = data[len(data) // 2]
        answer = str(median)
        question_text = f"給定一組數據：{data}，請問這組數據的中位數是多少？"
    else: # mode
        mode_val = random.choice(data)
        data.insert(random.randint(0, len(data)), mode_val)
        data.sort()
        answer = str(mode_val)
        question_text = f"給定一組數據：{data}，請問這組數據的眾數是多少？"
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }
