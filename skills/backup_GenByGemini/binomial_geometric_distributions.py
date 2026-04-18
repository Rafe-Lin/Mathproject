import random

def generate_binomial_geometric_distributions_question():
    """動態生成一道「二項分布與幾何分布」的題目 (判斷類型)"""
    scenario_type = random.choice(['binomial', 'geometric'])
    
    if scenario_type == 'binomial':
        n = random.randint(5, 10)
        p = random.choice([0.2, 0.5, 0.8])
        question_text = (
            f"小明投籃命中率為 {p*100:.0f}%。他投籃 {n} 次，請問他投進 3 球的機率，"
            f"適合用哪種機率分布來計算？ (請回答 '二項分布' 或 '幾何分布')"
        )
        answer = "二項分布"
    else: # geometric
        p = random.choice([0.2, 0.5, 0.8])
        question_text = (
            f"小華每次射擊命中靶心的機率為 {p*100:.0f}%。"
            f"請問他第一次命中靶心需要射擊幾次的機率，適合用哪種機率分布來計算？ (請回答 '二項分布' 或 '幾何分布')"
        )
        answer = "幾何分布"
        
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }
