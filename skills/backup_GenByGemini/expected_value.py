import random

def generate_expected_value_question():
    """動態生成一道「數學期望值」的題目"""
    outcomes = [1, 2, 3, 4, 5, 6]
    probabilities = [1/6, 1/6, 1/6, 1/6, 1/6, 1/6]
    expected_value = sum(o * p for o, p in zip(outcomes, probabilities))
    question_text = "擲一顆公正的骰子，其出現點數的數學期望值是多少？"
    answer = str(expected_value)
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }
