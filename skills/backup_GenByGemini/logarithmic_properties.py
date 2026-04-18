import random

def generate_logarithmic_properties_question():
    """
    Generates a fill-in-the-blank question about the properties of logarithms.
    Covers conceptual links to exponents, basic operations, and algebraic application.
    """
    questions = [
        {
            'question': '指數律 a^m * a^n = a^(m+n) 啟發了對數的運算性質 log_a(XY) = ? (答案請勿包含空格)',
            'answer': 'log_a(X)+log_a(Y)'
        },
        {
            'question': '請計算 log_2(4) + log_2(8) 的值。',
            'answer': '5'
        },
        {
            'question': '3 * log_10(5) + log_10(8) 的值是多少？',
            'answer': '3'
        },
        {
            'question': '已知 log_a(x) = 5 且 log_a(y) = 2，請問 log_a(x^2 / y) 的值是多少？',
            'answer': '8'
        }
    ]
    
    q = random.choice(questions)
    
    # Return format for fill-in-the-blank
    return {
        "text": q['question'],
        "answer": q['answer'],
        "validation_function_name": None # Use default string comparison
    }
