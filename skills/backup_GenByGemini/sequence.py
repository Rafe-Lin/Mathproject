import random

def generate_sequence_question():
    # Arithmetic sequence
    a1 = random.randint(1, 10) # First term
    d = random.randint(-3, 3) # Common difference
    while d == 0: d = random.randint(-3, 3)
    n = random.randint(4, 7) # Term to find

    # Generate first few terms
    terms = [a1 + (i * d) for i in range(n-1)]
    terms_str = ", ".join(map(str, terms))

    correct_answer = a1 + (n-1) * d

    question_text = f"已知一個等差數列的前 {n-1} 項為 {terms_str}，求第 {n} 項。"

    return {
        "text": question_text,
        "answer": str(correct_answer),
        "validation_function_name": None
    }
