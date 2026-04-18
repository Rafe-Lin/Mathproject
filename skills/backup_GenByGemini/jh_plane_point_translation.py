# skills/jh_plane_point_translation.py
import random

def generate(level=1):
    """
    生成一道「坐標平面上的點的平移」的題目。
    """
    x_orig = random.randint(-5, 5)
    y_orig = random.randint(-5, 5)
    
    x_trans = random.randint(-3, 3)
    while x_trans == 0: x_trans = random.randint(-3, 3)
    y_trans = random.randint(-3, 3)
    while y_trans == 0: y_trans = random.randint(-3, 3)

    x_dir = "右" if x_trans > 0 else "左"
    y_dir = "上" if y_trans > 0 else "下"

    x_new = x_orig + x_trans
    y_new = y_orig + y_trans

    question_text = f"將坐標平面上的點 P({x_orig}, {y_orig}) 向{x_dir}平移 {abs(x_trans)} 單位，再向{y_dir}平移 {abs(y_trans)} 單位，得到新的點 Q。\n請問 Q 點的坐標是什麼？ (格式: x,y)"
    correct_answer = f"{x_new},{y_new}"

    context_string = "學習點在坐標平面上的平移規則：向右移x加，向左移x減；向上移y加，向下移y減。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").replace("(", "").replace(")", "")
    correct = correct_answer.strip().replace(" ", "")

    is_correct = user == correct
    result_text = f"完全正確！新坐標是 ({correct})。" if is_correct else f"答案不正確。正確答案是：({correct})"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}