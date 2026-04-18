import random

def generate_space_concepts_question():
    """動態生成一道「空間概念」的題目 (點到平面距離)"""
    x, y, z = random.randint(-5, 5), random.randint(-5, 5), random.randint(-5, 5)
    plane_choice = random.choice(['xy', 'yz', 'xz'])
    if plane_choice == 'xy':
        question_text = f"在三維空間中，點 ({x}, {y}, {z}) 到 xy 平面的距離是多少？"
        answer = str(abs(z))
    elif plane_choice == 'yz':
        question_text = f"在三維空間中，點 ({x}, {y}, {z}) 到 yz 平面的距離是多少？"
        answer = str(abs(x))
    else: # xz
        question_text = f"在三維空間中，點 ({x}, {y}, {z}) 到 xz 平面的距離是多少？"
        answer = str(abs(y))
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }
