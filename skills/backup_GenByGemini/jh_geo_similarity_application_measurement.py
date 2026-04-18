# skills/jh_geo_similarity_application_measurement.py
import random

def generate(level=1):
    """
    生成一道「相似形應用(測量)」的題目。
    """
    # 影子問題
    tree_height = random.randint(3, 10) # m
    person_height = round(random.uniform(1.5, 1.8), 1) # m
    
    person_shadow = round(person_height * random.uniform(1, 2), 1)
    
    # tree_height / person_height = tree_shadow / person_shadow
    tree_shadow = (tree_height * person_shadow) / person_height

    q_type = random.choice(['find_tree_height', 'find_tree_shadow'])

    if q_type == 'find_tree_height':
        question_text = f"在同一時間，身高 {person_height} 公尺的人，其影長為 {person_shadow} 公尺。若此時旁邊一棵樹的影長為 {round(tree_shadow, 2)} 公尺，請問樹高是多少公尺？"
        correct_answer = str(tree_height)
    else:
        question_text = f"在同一時間，身高 {person_height} 公尺的人，其影長為 {person_shadow} 公尺。若此時旁邊一棵高為 {tree_height} 公尺的樹，請問其影長是多少公尺？"
        correct_answer = str(round(tree_shadow, 2))

    context_string = "利用太陽光為平行光，物體與其影子會形成相似三角形的原理來求解。"

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
    result_text = f"完全正確！答案是 {correct} 公尺。" if is_correct else f"答案不正確。正確答案是：{correct} 公尺"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}