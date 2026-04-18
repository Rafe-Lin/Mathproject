import random

def generate_matrix_applications_question():
    """動態生成一道「矩陣的應用」的題目 (矩陣乘法)"""
    # 生成兩個 2x2 矩陣
    matrix_a = [[random.randint(-3, 3) for _ in range(2)] for _ in range(2)]
    matrix_b = [[random.randint(-3, 3) for _ in range(2)] for _ in range(2)]
    
    # 計算乘積矩陣 C = A * B
    matrix_c = [[0, 0], [0, 0]]
    matrix_c[0][0] = matrix_a[0][0] * matrix_b[0][0] + matrix_a[0][1] * matrix_b[1][0]
    matrix_c[0][1] = matrix_a[0][0] * matrix_b[0][1] + matrix_a[0][1] * matrix_b[1][1]
    matrix_c[1][0] = matrix_a[1][0] * matrix_b[0][0] + matrix_a[1][1] * matrix_b[1][0]
    matrix_c[1][1] = matrix_a[1][0] * matrix_b[0][1] + matrix_a[1][1] * matrix_b[1][1]
    
    # 隨機選擇詢問的元素位置
    row_idx = random.choice([0, 1])
    col_idx = random.choice([0, 1])
    
    question_text = (
        f"已知矩陣 A = [[{matrix_a[0][0]}, {matrix_a[0][1]}], [{matrix_a[1][0]}, {matrix_a[1][1]}]] "
        f"和矩陣 B = [[{matrix_b[0][0]}, {matrix_b[0][1]}], [{matrix_b[1][0]}, {matrix_b[1][1]}]]. "
        f"請問矩陣 C = A * B 中，位於第 {row_idx + 1} 列第 {col_idx + 1} 行的元素是多少？"
    )
    answer = str(matrix_c[row_idx][col_idx])
    
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }
