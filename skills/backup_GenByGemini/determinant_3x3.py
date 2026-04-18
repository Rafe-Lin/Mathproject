import random

def generate_determinant_3x3_question():
    """動態生成一道「三階行列式」的題目"""
    matrix = []
    for _ in range(3):
        matrix.append([random.randint(-3, 3) for _ in range(3)])
    
    # Calculate determinant for a 3x3 matrix
    # | a b c |
    # | d e f |
    # | g h i |
    # det = a(ei - fh) - b(di - fg) + c(dh - eg)
    
    a, b, c = matrix[0]
    d, e, f = matrix[1]
    g, h, i = matrix[2]
    
    determinant = a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)
    
    matrix_str = "\n".join([f"| {row[0]:>2} {row[1]:>2} {row[2]:>2} |" for row in matrix])
    
    question_text = f"計算下列三階行列式的值：\n{matrix_str}"
    
    return {
        "text": question_text,
        "answer": str(determinant),
        "validation_function_name": None
    }

