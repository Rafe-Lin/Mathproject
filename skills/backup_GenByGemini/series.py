import random

def generate_series_question():
    # Sum of arithmetic series
    a1 = random.randint(1, 10) # First term
    d = random.randint(-3, 3) # Common difference
    while d == 0: d = random.randint(-3, 3)
    n = random.randint(3, 6) # Number of terms

    # Sum = n/2 * (2*a1 + (n-1)*d)
    correct_answer = (n / 2) * (2 * a1 + (n - 1) * d)

    question_text = f"已知一個等差數列的首項為 {a1}，公差為 {d}，求前 {n} 項的和。"

    return {
        "text": question_text,
        "answer": str(int(correct_answer)), # Ensure integer answer
        "validation_function_name": None
    }
